#!/usr/bin/env python3
"""
Generate user embeddings from existing user_profiles in MongoDB
从MongoDB中已有的user_profiles生成user_embeddings
"""
import sys
from pathlib import Path
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from database.connection import get_database
from sentence_transformers import SentenceTransformer

# Embedding model
MODEL_NAME = "BAAI/bge-small-en-v1.5"  # 384 dimensions, English-optimized


def build_profile_text(profile_data: dict) -> str:
    """
    构建用于embedding的文本
    
    Args:
        profile_data: 用户档案数据
        
    Returns:
        文本字符串
    """
    parts = []
    
    # User style
    user_style = profile_data.get('user_style', {})
    if isinstance(user_style, dict):
        if 'persona' in user_style:
            parts.append(user_style['persona'])
        if 'tone' in user_style:
            parts.append(f"Tone: {user_style['tone']}")
        if 'interests' in user_style:
            interests = user_style['interests']
            if isinstance(interests, list):
                parts.append(f"Interests: {', '.join(interests)}")
    
    # Content topics
    content_topics = profile_data.get('content_topics', [])
    if content_topics:
        parts.append(f"Topics: {', '.join(content_topics)}")
    
    # Posting pattern
    posting_pattern = profile_data.get('posting_pattern', {})
    if isinstance(posting_pattern, dict):
        content_mix = posting_pattern.get('content_mix', [])
        if content_mix:
            parts.append(f"Content types: {', '.join(content_mix)}")
    
    # Audience type
    audience_type = profile_data.get('audience_type', [])
    if audience_type:
        parts.append(f"Audience: {', '.join(audience_type)}")
    
    # Engagement style
    engagement_style = profile_data.get('engagement_style', '')
    if engagement_style:
        parts.append(f"Engagement: {engagement_style}")
    
    # Brand fit
    brand_fit = profile_data.get('brand_fit', [])
    if brand_fit:
        parts.append(f"Brand fit: {', '.join(brand_fit)}")
    
    return ' | '.join(parts)


def main():
    print("🚀 Starting User Embedding Generation")
    print("=" * 60)
    
    # 1. Connect to MongoDB
    print("\n📊 Connecting to MongoDB...")
    db = get_database()
    user_profiles = db['user_profiles']
    user_embeddings = db['user_embeddings']
    
    # 2. Load Instagram profiles
    print("📥 Loading Instagram user profiles...")
    profiles = list(user_profiles.find({'platform': 'instagram'}))
    print(f"   Found {len(profiles)} Instagram profiles")
    
    if not profiles:
        print("❌ No Instagram profiles found")
        return 1
    
    # 3. Load embedding model
    print(f"\n🤖 Loading embedding model: {MODEL_NAME}...")
    print("   This may take a moment on first run...")
    model = SentenceTransformer(MODEL_NAME)
    print(f"✅ Model loaded: {model.get_sentence_embedding_dimension()} dimensions")
    
    # 4. Generate embeddings
    print("\n🔨 Generating embeddings...")
    embeddings_created = 0
    embeddings_updated = 0
    embeddings_skipped = 0
    
    for profile in profiles:
        user_id = profile.get('user_id')
        profile_data = profile.get('profile_data', {})
        
        # Check if embedding already exists
        existing = user_embeddings.find_one({
            'user_id': user_id,
            'platform': 'instagram'
        })
        
        # Build text for embedding
        profile_text = build_profile_text(profile_data)
        
        if not profile_text:
            print(f"   ⚠️  {user_id}: No profile data, skipping")
            embeddings_skipped += 1
            continue
        
        # Generate embedding
        print(f"   🔄 {user_id}: Generating embedding...")
        embedding_vector = model.encode(profile_text).tolist()
        
        embedding_doc = {
            'user_id': user_id,
            'platform': 'instagram',
            'embedding': embedding_vector,
            'embedding_model': MODEL_NAME,
            'embedding_dim': len(embedding_vector),
            'updated_at': datetime.now()
        }
        
        if existing:
            # Update existing
            user_embeddings.update_one(
                {'user_id': user_id, 'platform': 'instagram'},
                {'$set': embedding_doc}
            )
            print(f"   ✅ {user_id}: Updated ({len(embedding_vector)} dims)")
            embeddings_updated += 1
        else:
            # Create new
            embedding_doc['created_at'] = datetime.now()
            user_embeddings.insert_one(embedding_doc)
            print(f"   ✅ {user_id}: Created ({len(embedding_vector)} dims)")
            embeddings_created += 1
    
    print("\n" + "=" * 60)
    print("✅ User Embedding Generation Complete!")
    print(f"   Created: {embeddings_created}")
    print(f"   Updated: {embeddings_updated}")
    print(f"   Skipped: {embeddings_skipped}")
    print(f"   Total: {embeddings_created + embeddings_updated}")
    
    # 5. Verify
    total_embeddings = user_embeddings.count_documents({'platform': 'instagram'})
    print(f"\n📊 Total Instagram embeddings in database: {total_embeddings}")
    
    return 0


if __name__ == '__main__':
    exit(main())
