"""Extract visual information from a post in `user_snapshots`.

Steps:
- Load local .env to get MONGO_URI
- Query `user_snapshots` for one post with image(s)
- Download the first image URL
- Run image captioning (nlpconnect/vit-gpt2-image-captioning)
- Generate an image embedding using sentence-transformers `clip-ViT-B-32` model
- Save results to `outputs/visual_analysis/{user_id}_{post_pk}.json`

Run: python extract_visual_info.py --user_id herfirst100k --limit 1
"""
import os
import json
import argparse
from pathlib import Path
from dotenv import load_dotenv
from pymongo import MongoClient
import requests
from PIL import Image
from io import BytesIO

# Transformers imports are lazy to avoid heavy import on module load

def load_one_post_with_image(user_id: str = None):
    # Load local env
    local_env = Path(__file__).resolve().parent / '.env'
    if local_env.exists():
        load_dotenv(local_env)

    uri = os.environ.get('MONGO_URI')
    if not uri:
        raise RuntimeError('MONGO_URI not set in environment')

    client = MongoClient(uri)
    db = client[os.environ.get('DATABASE_NAME', 'ig_raw')]
    col = db['user_snapshots']

    query = {'platform': 'instagram', 'posts': {'$exists': True, '$ne': []}}
    if user_id:
        query['user_id'] = user_id

    doc = col.find_one(query)
    client.close()
    return doc


def download_image(url: str) -> Image.Image:
    # Use headers to mimic a browser; Instagram CDN often rejects requests without referer/UA
    headers = {
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36',
        'Referer': 'https://www.instagram.com'
    }
    r = requests.get(url, timeout=30, headers=headers)
    r.raise_for_status()
    return Image.open(BytesIO(r.content)).convert('RGB')


def generate_caption(image: Image.Image):
    # Use VisionEncoderDecoderModel + ViT processor and tokenizer from the HF model
    from transformers import VisionEncoderDecoderModel, ViTImageProcessor, AutoTokenizer
    model_name = 'nlpconnect/vit-gpt2-image-captioning'
    model = VisionEncoderDecoderModel.from_pretrained(model_name)
    feature_extractor = ViTImageProcessor.from_pretrained(model_name)
    tokenizer = AutoTokenizer.from_pretrained(model_name)

    pixel_values = feature_extractor(images=image, return_tensors='pt').pixel_values
    gen_kwargs = {"max_length": 64, "num_beams": 4}
    output_ids = model.generate(pixel_values, **gen_kwargs)
    caption = tokenizer.decode(output_ids[0], skip_special_tokens=True).strip()
    return caption


def image_embedding(image: Image.Image):
    # Use sentence-transformers CLIP model
    from sentence_transformers import SentenceTransformer
    model = SentenceTransformer('clip-ViT-B-32')
    emb = model.encode(image, convert_to_numpy=True)
    return emb.tolist()


def run(user_id: str = None, limit: int = 1):
    doc = load_one_post_with_image(user_id=user_id)
    if not doc:
        print('No snapshot with posts found')
        return

    posts = doc.get('posts', [])
    # Find first post with image candidates
    chosen = None
    for p in posts:
        # media_type == 1 indicates image
        if p.get('media_type') in (1, None) and p.get('image_versions2'):
            chosen = p
            break
        # fallback: display_uri
        if p.get('display_uri'):
            chosen = p
            break

    if not chosen:
        print('No post with image URL found')
        return

    post_pk = chosen.get('pk') or chosen.get('id') or 'post'
    user = doc.get('user_info', {}).get('username') or doc.get('user_id')
    # get image url
    img_url = None
    if chosen.get('image_versions2') and isinstance(chosen.get('image_versions2'), dict):
        cands = chosen['image_versions2'].get('candidates', [])
        if cands:
            img_url = cands[0].get('url')
    if not img_url:
        img_url = chosen.get('display_uri')

    if not img_url:
        print('No image URL accessible for chosen post')
        return

    print('Downloading image:', img_url)
    image = download_image(img_url)

    print('Generating caption... (this will download model if needed)')
    caption = generate_caption(image)
    print('Caption:', caption)

    print('Generating image embedding (CLIP)...')
    emb = image_embedding(image)
    print('Embedding dimension:', len(emb))

    out = {
        'platform': 'instagram',
        'user_id': doc.get('user_id'),
        'username': user,
        'post_pk': post_pk,
        'image_url': img_url,
        'caption': caption,
        'image_embedding_dim': len(emb),
        'image_embedding': emb[:512],  # store a slice for readability (full saved below)
    }

    out_dir = Path('outputs/visual_analysis')
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / f"{user}_{post_pk}.json"
    with open(path, 'w', encoding='utf-8') as fh:
        json.dump(out, fh, ensure_ascii=False, indent=2)

    # Save full embedding to a separate file
    emb_path = out_dir / f"{user}_{post_pk}_embedding.json"
    with open(emb_path, 'w', encoding='utf-8') as fh:
        json.dump({'embedding': emb}, fh)

    print('Saved visual analysis to:', path)
    print('Saved embedding to:', emb_path)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--user_id', type=str, help='user_id to filter snapshots')
    parser.add_argument('--limit', type=int, default=1)
    args = parser.parse_args()
    run(user_id=args.user_id, limit=args.limit)
