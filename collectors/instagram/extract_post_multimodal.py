"""
Extract multimodal info from posts in user_snapshots:
- For each post: download all images, run YOLOv8 object detection, EasyOCR, combine with caption, and generate embedding.
- Collect and print: all extracted objects, OCR text, caption, engagement, and metadata.
- Save results to MongoDB post_embeddings collection.
"""
import os
import sys
import json
import argparse
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv
from pymongo import MongoClient
import requests
from PIL import Image
from io import BytesIO
from ultralytics import YOLO
import easyocr
from sentence_transformers import SentenceTransformer
import random

# Add backend to path
project_root = Path(__file__).resolve().parent.parent.parent
backend_path = project_root / "backend"
sys.path.insert(0, str(backend_path))

from database import PostEmbeddingRepository

def get_posts_from_user(username: str = None, n: int = 10):
    """
    Get posts from specified user or 'tinx' by default
    
    Args:
        username: Instagram username to get posts from
        n: Number of posts to retrieve
        
    Returns:
        List of (user_id, post, user_info) tuples
    """
    load_dotenv(Path('collectors/instagram/.env'))
    client = MongoClient(os.environ['MONGO_URI'])
    db = client[os.environ.get('DATABASE_NAME','ig_raw')]
    col = db['user_snapshots']
    posts = []
    
    # Use provided username or default to 'tinx'
    target_username = username or 'tinx'
    
    # Find user by username
    doc = col.find_one({'platform': 'instagram', 'username': target_username, 'posts': {'$exists': True, '$ne': []}})
    
    if not doc:
        # Try finding by user_id if username doesn't match
        doc = col.find_one({'platform': 'instagram', 'user_id': target_username, 'posts': {'$exists': True, '$ne': []}})
    
    if doc:
        for p in doc.get('posts', []):
            has_media = False
            if p.get('image_versions2') and isinstance(p['image_versions2'], dict):
                if any(c.get('url') for c in p['image_versions2'].get('candidates', [])):
                    has_media = True
            if p.get('display_uri'):
                has_media = True
            if p.get('video_versions') and isinstance(p['video_versions'], list):
                if any(v.get('url') for v in p['video_versions']):
                    has_media = True
            if has_media:
                posts.append((doc.get('user_id') or doc.get('username'), p, doc.get('user_info', {})))
            if len(posts) >= n:
                break
    else:
        print(f"❌ No data found for user: {target_username}")
    
    client.close()
    return posts

def download_image(url):
    headers = {'User-Agent': 'Mozilla/5.0', 'Referer': 'https://www.instagram.com'}
    r = requests.get(url, timeout=30, headers=headers)
    r.raise_for_status()
    return Image.open(BytesIO(r.content)).convert('RGB')

def extract_images(post):
    images = []
    # image_versions2 candidates
    if post.get('image_versions2') and isinstance(post['image_versions2'], dict):
        for c in post['image_versions2'].get('candidates', []):
            if c.get('url'):
                images.append(c['url'])
    # fallback: display_uri
    if post.get('display_uri'):
        images.append(post['display_uri'])
    # deduplicate
    return list(dict.fromkeys(images))

def run_object_detection(image, yolo_model):
    results = yolo_model(image)
    objects = []
    for r in results:
        for box in r.boxes:
            cls = int(box.cls[0])
            conf = float(box.conf[0])
            label = r.names[cls]
            objects.append({'label': label, 'confidence': conf})
    return objects

def run_ocr(image, ocr_reader):
    results = ocr_reader.readtext(image)
    texts = [t[1] for t in results if t[2] > 0.3]
    return texts

def main():
    parser = argparse.ArgumentParser(description="Extract multimodal embeddings from Instagram posts")
    parser.add_argument('--username', type=str, default='tinx', help='Instagram username to process')
    parser.add_argument('--count', type=int, default=10, help='Number of posts to process')
    args = parser.parse_args()
    
    print(f"\n{'='*60}")
    print(f"🎬 Extracting multimodal embeddings for: {args.username}")
    print(f"📊 Processing up to {args.count} posts")
    print(f"{'='*60}\n")
    
    # Get posts
    posts = get_posts_from_user(args.username, args.count)
    
    if not posts:
        print("❌ No posts found to process")
        return
    
    print(f"✅ Found {len(posts)} posts with media\n")
    
    # Initialize models
    print("📦 Loading models...")
    yolo_model = YOLO('yolov8n.pt')
    ocr_reader = easyocr.Reader(['en'], gpu=False)
    embedder = SentenceTransformer('all-MiniLM-L6-v2')
    print("✅ Models loaded\n")
    
    # Initialize repository
    post_embedding_repo = PostEmbeddingRepository()
    
    # Create output directory for JSON backups
    out_dir = Path('outputs/post_multimodal')
    out_dir.mkdir(parents=True, exist_ok=True)
    
    success_count = 0
    
    for idx, (uid, post, user_info) in enumerate(posts):
        print(f"\n{'='*60}")
        print(f"📸 Processing post {idx+1}/{len(posts)}")
        print(f"{'='*60}")
        
        post_id = post.get('pk') or post.get('id') or f'post{idx}'
        username = user_info.get('username') or uid
        
        images = extract_images(post)
        all_objects = []
        all_ocr = []
        
        for img_url in images:
            local_path = None
            try:
                # Download image locally for YOLOv8
                img = download_image(img_url)
                # Save to temp file
                local_path = f'tmp_{os.path.basename(img_url.split("?")[0])}'
                img.save(local_path)
                # Run YOLOv8 on local file
                objects = run_object_detection(local_path, yolo_model)
                ocr_texts = run_ocr(img, ocr_reader)
                all_objects.extend(objects)
                all_ocr.extend(ocr_texts)
            except Exception as e:
                print(f"[Warning] Failed to process image {img_url}: {e}")
            finally:
                if local_path and os.path.exists(local_path):
                    try:
                        os.remove(local_path)
                    except Exception as cleanup_e:
                        print(f"[Warning] Failed to delete temp file {local_path}: {cleanup_e}")
        
        # Compose text for embedding
        caption = post.get('caption')
        if isinstance(caption, dict):
            caption = caption.get('text', '')
        elif not isinstance(caption, str):
            caption = str(caption) if caption else ''
        
        # Show pre-embedding info
        print(f"\n=== Post {idx+1} ({username}) PRE-EMBEDDING ===")
        print(json.dumps({
            'user_id': uid,
            'username': username,
            'post_id': post_id,
            'caption': caption,
            'objects': [o['label'] for o in all_objects],
            'ocr_text': all_ocr,
            'like_count': post.get('like_count'),
            'comment_count': post.get('comment_count'),
            'play_count': post.get('play_count') or post.get('view_count'),
            'media_urls': images,
        }, ensure_ascii=False, indent=2)[:2000] + '\n...')
        
        # Combine text for embedding
        combined_text = '\n'.join([
            ' '.join(sorted(set([o['label'] for o in all_objects]))),
            ' '.join(all_ocr),
            caption
        ]).strip()
        
        embedding = embedder.encode(combined_text, convert_to_numpy=True).tolist()
        
        # Show post-embedding info
        print(f"\n=== Post {idx+1} ({username}) POST-EMBEDDING ===")
        print(json.dumps({
            'embedding_dim': len(embedding),
            'embedding': embedding[:10],  # show only first 10 dims for brevity
        }, ensure_ascii=False, indent=2) + '\n...')
        
        # Prepare embedding document
        embedding_doc = {
            'platform': 'instagram',
            'post_id': str(post_id),
            'user_id': uid,
            'username': username,
            'embedding': embedding,
            'caption': caption,
            'objects': [o['label'] for o in all_objects],
            'ocr_text': all_ocr,
            'like_count': post.get('like_count', 0),
            'comment_count': post.get('comment_count', 0),
            'play_count': post.get('play_count') or post.get('view_count'),
            'media_urls': images,
            'model': 'all-MiniLM-L6-v2',
            'dimension': len(embedding),
            'created_at': datetime.now()
        }
        
        # Save to MongoDB
        try:
            post_embedding_repo.upsert_embedding(str(post_id), 'instagram', embedding_doc)
            print(f"✅ Saved to MongoDB: post_embeddings")
            success_count += 1
        except Exception as e:
            print(f"❌ Failed to save to MongoDB: {e}")
        
        # Save backup JSON
        try:
            out_path = out_dir / f'{username}_{post_id}.json'
            with open(out_path, 'w', encoding='utf-8') as fh:
                json.dump(embedding_doc, fh, ensure_ascii=False, indent=2, default=str)
            print(f"✅ Saved backup JSON: {out_path}")
        except Exception as e:
            print(f"⚠️  Failed to save backup JSON: {e}")
    
    print(f"\n{'='*60}")
    print(f"✨ Processing complete!")
    print(f"   - Processed: {success_count}/{len(posts)} posts")
    print(f"   - Success rate: {success_count/len(posts)*100:.1f}%")
    print(f"{'='*60}\n")

if __name__ == '__main__':
    main()
