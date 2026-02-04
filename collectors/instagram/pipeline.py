#!/usr/bin/env python3
"""
Instagram Data Pipeline
Reads raw Instagram data from MongoDB, analyzes it using ChatGPT/Gemini, and saves results back to MongoDB
"""

import os
import sys
import json
import argparse
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv
# Try to import FlagEmbedding; if unavailable, proceed without local embeddings
try:
    from FlagEmbedding import FlagModel
    FLAG_EMBEDDING_AVAILABLE = True
except Exception as e:
    FlagModel = None
    FLAG_EMBEDDING_AVAILABLE = False
    print("⚠️  Warning: FlagEmbedding import failed; embeddings will be skipped or generated elsewhere.\n  Reason:", e)

# Add backend to path
project_root = Path(__file__).resolve().parent.parent.parent
backend_path = project_root / "backend"
sys.path.insert(0, str(backend_path))

# Load environment variables (check project root, then local collectors/.env, then backend/.env)
env_file = project_root / '.env'
local_env = Path(__file__).resolve().parent / '.env'
backend_env = backend_path / '.env'
if env_file.exists():
    load_dotenv(env_file)
elif local_env.exists():
    load_dotenv(local_env)
elif backend_env.exists():
    load_dotenv(backend_env)

from database import UserSnapshotRepository, UserProfileRepository, UserEmbeddingRepository

# Import analyzer module
sys.path.insert(0, str(Path(__file__).parent))
from analyzer import analyze_user_profile


def run_diagnostics():
    """Run quick environment & connectivity checks and return a dict of results."""
    results = {}
    # Env checks
    results['MONGO_URI'] = bool(os.environ.get('MONGO_URI'))
    # Check TikHub token/base
    try:
        from fetcher import _get_tikhub_base, _get_tikhub_token, _get_mongo
        try:
            _get_tikhub_base()
            results['TIKHUB_BASE'] = True
        except Exception as e:
            results['TIKHUB_BASE'] = str(e)
        try:
            _get_tikhub_token()
            results['TIKHUB_TOKEN'] = True
        except Exception as e:
            results['TIKHUB_TOKEN'] = str(e)
        try:
            _get_mongo()
            results['MONGO_CONNECT'] = True
        except Exception as e:
            results['MONGO_CONNECT'] = str(e)
    except Exception as e:
        results['fetcher_import'] = str(e)

    results['FLAG_EMBEDDING_AVAILABLE'] = FLAG_EMBEDDING_AVAILABLE
    return results


def process_instagram_user(user_id: str, embedding_model: FlagModel = None):
    """
    Process a single Instagram user's data
    
    Args:
        user_id: Instagram user ID
        embedding_model: FlagModel instance for embeddings
        
    Returns:
        True if successful, False otherwise
    """
    print(f"\n{'='*60}")
    print(f"🎯 Processing Instagram user: {user_id}")
    print(f"{'='*60}")
    
    # 1. Read from MongoDB
    print("\n📥 Step 1: Reading data from MongoDB...")
    snapshot_repo = UserSnapshotRepository()
    snapshot = snapshot_repo.get_by_user_id(user_id, platform="instagram")
    
    if not snapshot:
        print(f"❌ No data found for user {user_id}")
        return False
    
    posts = snapshot.get('posts', [])
    if not posts:
        print(f"❌ User {user_id} has no posts")
        return False
    
    # Extract user information
    user_info = snapshot.get('user_info', {})
    if not user_info:
        print(f"❌ No user information found")
        return False
    
    username = user_info.get('username', user_id)
    print(f"✅ Found user: {username}")
    print(f"   - Posts: {len(posts)}")
    print(f"   - Followers: {user_info.get('followers', 0)}")
    
    # 2. Analyze using ChatGPT/Gemini
    print("\n🤖 Step 2: Analyzing user profile...")
    try:
        # Limit to 50 most recent posts for analysis
        profile_data = analyze_user_profile(user_info, posts[:50], embedding_model)
        
        if not profile_data:
            print(f"❌ Analysis failed")
            return False
        
        print(f"✅ Analysis complete")
        print(f"   - Topics: {len(profile_data.get('content_topics', []))}")
        print(f"   - Embedding: {len(profile_data.get('user_style_embedding', []))} dimensions")
        
    except Exception as e:
        print(f"❌ Analysis failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # 3. Save to MongoDB
    print("\n💾 Step 3: Saving to MongoDB...")
    
    # Save user_profile with upsert to prevent duplicates
    profile_repo = UserProfileRepository()
    
    profile_doc = {
        'platform': 'instagram',
        'user_id': user_id,
        'username': username,
        'profile_data': profile_data,
        'created_at': datetime.now(),
        'updated_at': datetime.now()
    }
    
    # Use upsert to prevent duplicate profiles
    existing_profile = profile_repo.get_by_user_id(user_id, platform='instagram')
    if existing_profile:
        # Update existing profile
        profile_repo.collection.update_one(
            {"user_id": user_id, "platform": "instagram"},
            {"$set": {
                'profile_data': profile_data,
                'username': username,
                'updated_at': datetime.now()
            }}
        )
        print(f"✅ Updated user_profiles")
    else:
        # Create new profile
        profile_repo.create_profile(profile_doc)
        print(f"✅ Created user_profiles")
    
    # Save embedding with upsert to prevent duplicates
    if 'user_style_embedding' in profile_data:
        embedding_repo = UserEmbeddingRepository()
        
        embedding_doc = {
            'platform': 'instagram',
            'user_id': username,
            'user_style_embedding': profile_data['user_style_embedding'],
            'model': os.environ.get('EMBEDDING_MODEL', 'BAAI/bge-small-zh-v1.5'),
            'dimension': len(profile_data['user_style_embedding']),
            'created_at': datetime.now(),
            'updated_at': datetime.now()
        }
        
        existing_embedding = embedding_repo.get_by_user_id(username, platform='instagram')
        if existing_embedding:
            embedding_repo.collection.update_one(
                {"user_id": username, "platform": 'instagram'},
                {"$set": {
                    "user_style_embedding": profile_data['user_style_embedding'],
                    "updated_at": datetime.now()
                }}
            )
            print(f"✅ Updated user_embeddings")
        else:
            embedding_repo.create_embedding(embedding_doc)
            print(f"✅ Created user_embeddings")
    
    print(f"\n✨ User {username} processing complete!")
    return True


def process_all_instagram_users(limit: int = None):
    """
    Process all Instagram users in MongoDB
    
    Args:
        limit: Maximum number of users to process (None = all)
    """
    print("\n🚀 Starting to process all Instagram users...")
    
    # Preload embedding model (avoid reloading)
    embedding_model = None
    if FLAG_EMBEDDING_AVAILABLE:
        try:
            print("\n📦 Loading FlagEmbedding model...")
            embedding_model = FlagModel(
                os.environ.get('EMBEDDING_MODEL', 'BAAI/bge-small-zh-v1.5'),
                query_instruction_for_retrieval="",
                use_fp16=True
            )
            print("✅ FlagEmbedding model loaded")
        except Exception as e:
            print("⚠️  Failed to load FlagModel, embeddings will be skipped:\n", e)
            embedding_model = None
    else:
        # Try a lightweight local fallback using sentence-transformers if available
        try:
            from .embedding_backend import SentenceTransformersWrapper
            print("\n📦 Loading local embedding model (sentence-transformers)...")
            embedding_model = SentenceTransformersWrapper(os.environ.get('EMBEDDING_MODEL', 'all-MiniLM-L6-v2'))
            print("✅ Local embedding model loaded")
        except Exception as e:
            print("⚠️  Local sentence-transformers not available; embeddings will be skipped:", e)
            embedding_model = None
    
    # Get all user IDs from snapshots
    snapshot_repo = UserSnapshotRepository()
    # Note: This assumes your repository has a method to get all users
    # If not, you may need to query MongoDB directly
    
    # Example: Get from MongoDB directly
    db = snapshot_repo.db
    collection = db['user_snapshots']
    
    users = collection.find(
        {"platform": "instagram"},
        {"user_id": 1}
    ).distinct("user_id")
    
    if limit:
        users = users[:limit]
    
    print(f"📊 Found {len(users)} Instagram users to process")
    
    success_count = 0
    for i, user_id in enumerate(users, 1):
        print(f"\n📊 Progress: {i}/{len(users)}")
        if process_instagram_user(user_id, embedding_model):
            success_count += 1
    
    print(f"\n{'='*60}")
    print(f"✅ Processing complete!")
    print(f"   - Processed: {success_count}/{len(users)} users")
    print(f"   - Success rate: {success_count/len(users)*100:.1f}%")
    print(f"{'='*60}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Instagram data pipeline")
    parser.add_argument(
        "--user_id",
        type=str,
        help="Process specific user by ID"
    )
    parser.add_argument(
        "--diagnose",
        action='store_true',
        help="Run diagnostics to check env vars, MongoDB and TikHub access"
    )
    parser.add_argument(
        "--fetch_username",
        type=str,
        help="Fetch raw data for username from TikHub and process it (fetch -> snapshot -> analyze)"
    )
    parser.add_argument(
        "--fetch_username_paged",
        type=str,
        help="Fetch raw data for username from TikHub with pagination and store pages (no analysis)"
    )
    parser.add_argument(
        "--post_pages",
        type=int,
        default=2,
        help="Number of post pages to fetch when using --fetch_username_paged (default 2)"
    )
    parser.add_argument(
        "--reel_pages",
        type=int,
        default=2,
        help="Number of reel pages to fetch when using --fetch_username_paged (default 2)"
    )
    parser.add_argument(
        "--page_count",
        type=int,
        default=12,
        help="Number of items per page when using --fetch_username_paged (default 12)"
    )
    parser.add_argument(
        "--store_local_first",
        action='store_true',
        help="Store fetched pages as local files first, then upload to DB after all pages are fetched"
    )
    parser.add_argument(
        "--local_file_limit",
        type=int,
        default=5,
        help="Maximum number of local files to collect before stopping (default 5)"
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="Process all users"
    )
    parser.add_argument(
        "--limit",
        type=int,
        help="Limit number of users to process (with --all)"
    )
    
    args = parser.parse_args()
    
    if args.user_id:
        # Process single user
        success = process_instagram_user(args.user_id)
        exit(0 if success else 1)
    elif args.diagnose:
        print("🔍 Running diagnostics...")
        res = run_diagnostics()
        for k, v in res.items():
            print(f" - {k}: {v}")
        # Exit 0 only if basic checks pass
        ok = res.get('MONGO_URI') and res.get('TIKHUB_TOKEN') and res.get('MONGO_CONNECT')
        exit(0 if ok else 1)
    elif getattr(args, 'fetch_username', None):
        # Fetch raw data for given username, upsert snapshot, then process
        from fetcher import fetch_and_store
        print(f"🔄 Fetching raw data for username: {args.fetch_username}")
        try:
            res = fetch_and_store(args.fetch_username)
            if not res.get('snapshot_upserted'):
                print(f"⚠️  Snapshot upsert for {args.fetch_username} did not run or failed: {res.get('snapshot_error')}")
        except Exception as e:
            print(f"❌ Fetch failed for {args.fetch_username}: {e}")
            import traceback
            traceback.print_exc()
            exit(1)

        print(f"🚀 Running pipeline for {args.fetch_username}")
        success = process_instagram_user(args.fetch_username)
        exit(0 if success else 1)
    elif getattr(args, 'fetch_username_paged', None):
        # Fetch multiple pages of posts/reels and store them, do not analyze
        from fetcher import fetch_and_store_paged
        print(f"🔄 Fetching paged raw data for username: {args.fetch_username_paged}")
        try:
            res = fetch_and_store_paged(
                args.fetch_username_paged,
                post_pages=args.post_pages,
                reel_pages=args.reel_pages,
                count=args.page_count,
                store_local_first=args.store_local_first,
                local_file_limit=args.local_file_limit
            )
            print("✅ Fetch paged result:")
            print(res)
            exit(0)
        except Exception as e:
            print(f"❌ Paged fetch failed for {args.fetch_username_paged}: {e}")
            import traceback
            traceback.print_exc()
            exit(1)
    elif args.all:
        # Process all users
        process_all_instagram_users(limit=args.limit)
    else:
        print("❌ Please specify --user_id <id>, --fetch_username <username>, or --all")
        parser.print_help()
        exit(1)
