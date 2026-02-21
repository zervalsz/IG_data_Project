#!/usr/bin/env python3
"""
Test script to fetch data for a single Instagram account.

This will collect 5 JSON files:
1. User info (1 file)
2. Posts list - page 1 (using max_id from API response)
3. Posts list - page 2 (using max_id from page 1)
4. Reels list - page 1 (using max_id from API response)
5. Reels list - page 2 (using max_id from page 1)

All raw API responses are saved to:
- MongoDB: raw_api_responses collection
- Local files: outputs/raw/instagram/<username>/

After fetching, the data is normalized into a snapshot and saved to:
- MongoDB: user_snapshots collection

Usage:
    python3 test_single_user.py --username <instagram_username>
    
Example:
    python3 test_single_user.py --username herfirst100k
"""

import os
import sys
from pathlib import Path
from datetime import datetime
import json

# Add backend to path for database imports
project_root = Path(__file__).resolve().parent.parent.parent
backend_path = project_root / "backend"
sys.path.insert(0, str(backend_path))

# Import fetcher functions
from fetcher import fetch_and_store

def test_collect_user(username: str):
    """
    Collect data for a single Instagram user.
    
    Fetches:
    - User info (1 API call)
    - Posts (2 pages with pagination)
    - Reels (2 pages with pagination)
    
    Total: 5 API calls → 5 JSON files
    """
    print("=" * 80)
    print(f"🎯 Testing Instagram Data Collection")
    print(f"   Username: {username}")
    print(f"   Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    
    print("\n📥 Starting data collection...")
    print("   - User info: 1 file")
    print("   - Posts: 2 pages (using max_id pagination)")
    print("   - Reels: 2 pages (using max_id pagination)")
    print("   Total: 5 JSON files\n")
    
    try:
        # Fetch and store data
        # fetch_and_store() defaults:
        # - posts_pages=2, reels_pages=2
        # - posts_count=50, reels_count=50
        # - Automatically handles max_id pagination
        results = fetch_and_store(
            username=username,
            fetch_posts=True,
            fetch_reels=True,
            posts_count=50,    # Max supported by TikHub API
            reels_count=50,    # Max supported by TikHub API
            posts_pages=2,     # Fetch 2 pages of posts
            reels_pages=2      # Fetch 2 pages of reels
        )
        
        print("\n✅ Data collection complete!\n")
        
        # Display results
        print("=" * 80)
        print("📊 Collection Summary")
        print("=" * 80)
        
        # User info
        if results.get('user_info'):
            print("\n1️⃣  User Info:")
            user_data = results['user_info']
            # Try to extract user details from common paths
            user_id = None
            follower_count = None
            following_count = None
            
            # Navigate nested structure
            if 'data' in user_data and 'data' in user_data['data']:
                user_obj = user_data['data']['data'].get('user', {})
                user_id = user_obj.get('id') or user_obj.get('pk')
                follower_count = user_obj.get('follower_count')
                following_count = user_obj.get('following_count')
            
            print(f"   ✅ Fetched successfully")
            if user_id:
                print(f"   📍 User ID: {user_id}")
            if follower_count is not None:
                print(f"   👥 Followers: {follower_count:,}")
            if following_count is not None:
                print(f"   👤 Following: {following_count:,}")
        
        # Posts
        posts_list = results.get('posts', [])
        print(f"\n2️⃣  Posts:")
        if posts_list:
            print(f"   ✅ Fetched {len(posts_list)} page(s)")
            total_posts = 0
            for i, page in enumerate(posts_list, 1):
                items = page.get('data', {}).get('items', [])
                next_max_id = page.get('data', {}).get('next_max_id')
                print(f"   📄 Page {i}: {len(items)} posts" + 
                      (f" (next_max_id: {next_max_id[:20]}...)" if next_max_id else " (no more pages)"))
                total_posts += len(items)
            print(f"   📊 Total posts: {total_posts}")
        else:
            print("   ⚠️  No posts fetched")
        
        # Reels
        reels_list = results.get('reels', [])
        print(f"\n3️⃣  Reels:")
        if reels_list:
            print(f"   ✅ Fetched {len(reels_list)} page(s)")
            total_reels = 0
            for i, page in enumerate(reels_list, 1):
                items = page.get('data', {}).get('items', [])
                paging_info = page.get('data', {}).get('paging_info', {})
                next_max_id = paging_info.get('max_id')
                print(f"   📄 Page {i}: {len(items)} reels" + 
                      (f" (next_max_id: {next_max_id[:20]}...)" if next_max_id else " (no more pages)"))
                total_reels += len(items)
            print(f"   📊 Total reels: {total_reels}")
        else:
            print("   ⚠️  No reels fetched")
        
        # Snapshot
        print(f"\n4️⃣  Snapshot:")
        if results.get('snapshot_upserted'):
            print("   ✅ Created and saved to user_snapshots collection")
        else:
            error = results.get('snapshot_error', 'Unknown error')
            print(f"   ⚠️  Failed: {error}")
        
        # Local files
        print(f"\n5️⃣  Local Files:")
        output_dir = Path(f"outputs/raw/instagram/{username}")
        if output_dir.exists():
            files = list(output_dir.glob("*.json"))
            print(f"   ✅ Saved to: {output_dir}")
            print(f"   📁 Total files: {len(files)}")
            for f in sorted(files):
                size_kb = f.stat().st_size / 1024
                print(f"      - {f.name} ({size_kb:.1f} KB)")
        else:
            print("   ℹ️  No local files (stored in MongoDB only)")
        
        print("\n" + "=" * 80)
        print("🎉 Test Complete!")
        print("=" * 80)
        
        # Next steps
        print("\n📝 Next Steps:")
        print(f"   1. Check MongoDB collections:")
        print(f"      - raw_api_responses (5 documents)")
        print(f"      - user_snapshots (1 document)")
        print(f"\n   2. Run pipeline to analyze user:")
        print(f"      cd /workspaces/IG_data_Project/collectors/instagram")
        print(f"      python3 pipeline.py --user {username}")
        print(f"\n   3. Check data structure:")
        print(f"      python3 -c \"from database import UserSnapshotRepository; repo = UserSnapshotRepository(); snap = repo.get_by_user_id('{username}', 'instagram'); print('Posts:', len(snap.get('posts', [])))")
        
        return results
        
    except Exception as e:
        print(f"\n❌ Error during collection: {e}")
        import traceback
        traceback.print_exc()
        return None


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Test Instagram data collection for a single user",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    # Fetch data for herfirst100k
    python3 test_single_user.py --username herfirst100k
    
    # Fetch data for another user
    python3 test_single_user.py --username cristiano
        """
    )
    
    parser.add_argument(
        "--username",
        required=True,
        help="Instagram username to fetch"
    )
    
    args = parser.parse_args()
    
    # Run test
    results = test_collect_user(args.username)
    
    # Exit with appropriate code
    if results:
        sys.exit(0)
    else:
        sys.exit(1)
