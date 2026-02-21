#!/usr/bin/env python3
"""
Generate embeddings for user and posts using sentence-transformers.
Fallback script when FlagEmbedding is not available.
"""

import os
import sys
from pathlib import Path
from datetime import datetime

# Add backend to path
project_root = Path(__file__).resolve().parent.parent.parent
backend_path = project_root / "backend"
sys.path.insert(0, str(backend_path))

from database import UserProfileRepository, UserSnapshotRepository, UserEmbeddingRepository, PostEmbeddingRepository
from sentence_transformers import SentenceTransformer

def generate_embeddings_for_user(username: str, model_name: str = 'all-MiniLM-L6-v2'):
    """
    Generate user and post embeddings using sentence-transformers.
    
    Args:
        username: Instagram username
        model_name: SentenceTransformer model name
    """
    print(f"\n{'='*80}")
    print(f"🎯 Generating Embeddings for: {username}")
    print(f"   Model: {model_name}")
    print(f"{'='*80}")
    
    # Load model
    print("\n📦 Loading embedding model...")
    model = SentenceTransformer(model_name)
    print(f"✅ Model loaded (dimension: 384)")
    
    # Get repositories
    profile_repo = UserProfileRepository()
    snapshot_repo = UserSnapshotRepository()
    embedding_repo = UserEmbeddingRepository()
    post_repo = PostEmbeddingRepository()
    
    # 1. Get user profile
    print("\n📥 Step 1: Loading user profile...")
    profile = profile_repo.get_by_user_id(username, platform='instagram')
    if not profile:
        print(f"❌ No profile found for {username}")
        return False
    
    categories = profile.get('profile_data', {}).get('categories', ['Lifestyle'])
    topics = profile.get('profile_data', {}).get('content_topics', [])
    user_style = profile.get('profile_data', {}).get('user_style', {})
    
    print(f"✅ Profile loaded")
    print(f"   Categories: {', '.join(categories)}")
    print(f"   Topics: {len(topics)}")
    
    # 2. Generate user embedding
    print("\n🤖 Step 2: Generating user embedding...")
    
    # Build text from user style
    persona = user_style.get('persona', '')
    tone = user_style.get('tone', '')
    interests = user_style.get('interests', [])
    interests_text = ', '.join(interests) if isinstance(interests, list) else str(interests)
    
    user_text = f"{persona} {tone} {interests_text}".strip()
    if not user_text:
        user_text = ' '.join(topics[:5])  # Fallback to topics
    
    user_embedding = model.encode([user_text])[0].tolist()
    print(f"✅ User embedding generated ({len(user_embedding)} dimensions)")
    
    # Save user embedding
    embedding_doc = {
        'platform': 'instagram',
        'user_id': username,
        'user_style_embedding': user_embedding,
        'model': model_name,
        'dimension': len(user_embedding),
        'created_at': datetime.now(),
        'updated_at': datetime.now()
    }
    
    existing = embedding_repo.get_by_user_id(username, platform='instagram')
    if existing:
        embedding_repo.collection.update_one(
            {"user_id": username, "platform": 'instagram'},
            {"$set": {
                "user_style_embedding": user_embedding,
                "model": model_name,
                "dimension": len(user_embedding),
                "updated_at": datetime.now()
            }}
        )
        print("✅ Updated user_embeddings collection")
    else:
        embedding_repo.create_embedding(embedding_doc)
        print("✅ Created user_embeddings collection")
    
    # Also update profile_data with embedding
    profile_repo.collection.update_one(
        {"user_id": username, "platform": "instagram"},
        {"$set": {
            "profile_data.user_style_embedding": user_embedding,
            "updated_at": datetime.now()
        }}
    )
    print("✅ Updated user_profiles with embedding")
    
    # 3. Get snapshot posts
    print("\n📥 Step 3: Loading posts...")
    snapshot = snapshot_repo.get_by_user_id(username, platform='instagram')
    if not snapshot:
        print(f"❌ No snapshot found for {username}")
        return False
    
    posts = snapshot.get('posts', [])
    print(f"✅ Found {len(posts)} posts")
    
    # 4. Embed all posts
    print(f"\n🤖 Step 4: Embedding {len(posts)} posts...")
    embedded_count = 0
    updated_count = 0
    skipped_count = 0
    
    for i, post in enumerate(posts, 1):
        post_id = post.get('id', post.get('post_id', ''))
        if not post_id:
            skipped_count += 1
            continue
        
        # Build post text - extract text from caption dict
        caption_raw = post.get('caption', '')
        
        # Caption is often a dict with 'text' field - extract it
        if isinstance(caption_raw, dict):
            caption = caption_raw.get('text', '')
        elif isinstance(caption_raw, str):
            caption = caption_raw
        else:
            caption = str(caption_raw) if caption_raw else ''
        
        hashtags = post.get('hashtags', [])
        if isinstance(hashtags, list):
            hashtags_text = ' '.join(hashtags)
        else:
            hashtags_text = str(hashtags)
        
        post_text = f"{caption} {hashtags_text}".strip()
        
        if not post_text:
            skipped_count += 1
            continue
        
        # Check if already exists
        existing_post = post_repo.get_by_post_id(post_id, platform='instagram')
        
        # Generate embedding
        try:
            post_embedding = model.encode([post_text])[0].tolist()
        except Exception as e:
            print(f"   ⚠️  Failed to embed post {i}/{len(posts)}: {e}")
            skipped_count += 1
            continue
        
        # Create/update post document
        post_doc = {
            'post_id': post_id,
            'user_id': username,
            'username': username,
            'platform': 'instagram',
            'embedding': post_embedding,
            'caption': caption if isinstance(caption, str) else str(caption),  # Store only text
            'categories': categories,  # Inherit from user
            'like_count': post.get('like_count', 0),  # Fixed: use correct field name
            'comment_count': post.get('comment_count', 0),  # Fixed: use correct field name
            'post_data': {  # Store full post data for trend analysis
                'like_count': post.get('like_count', 0),
                'comment_count': post.get('comment_count', 0),
                'caption': caption if isinstance(caption, str) else str(caption),
                'taken_at': post.get('taken_at'),
                'media_type': post.get('media_type')
            },
            'model': model_name,
            'dimension': len(post_embedding),
            'created_at': datetime.now() if not existing_post else existing_post.get('created_at', datetime.now()),
            'updated_at': datetime.now()
        }
        
        if existing_post:
            post_repo.collection.update_one(
                {"post_id": post_id, "platform": "instagram"},
                {"$set": post_doc}
            )
            updated_count += 1
        else:
            post_repo.create_embedding(post_doc)
            embedded_count += 1
        
        # Progress indicator
        if i % 10 == 0:
            print(f"   Progress: {i}/{len(posts)} posts processed...")
    
    print(f"\n✅ Post embedding complete!")
    print(f"   - New: {embedded_count}")
    print(f"   - Updated: {updated_count}")
    print(f"   - Skipped: {skipped_count}")
    
    # 5. Summary
    print(f"\n{'='*80}")
    print("📊 Final Summary")
    print(f"{'='*80}")
    print(f"User: {username}")
    print(f"Categories: {', '.join(categories)}")
    print(f"User embedding: {len(user_embedding)} dimensions")
    print(f"Post embeddings: {embedded_count + updated_count} total")
    print(f"\n✨ All embeddings saved with categories!")
    print(f"{'='*80}")
    
    return True


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Generate embeddings for user and posts")
    parser.add_argument("--username", required=True, help="Instagram username")
    parser.add_argument("--model", default="all-MiniLM-L6-v2", help="SentenceTransformer model name")
    
    args = parser.parse_args()
    
    success = generate_embeddings_for_user(args.username, args.model)
    sys.exit(0 if success else 1)
