"""
Quick migration to add engagement data (like_count, comment_count) to post_embeddings
"""
import sys
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).resolve().parent.parent.parent / 'backend'
sys.path.insert(0, str(backend_path))

from database import UserSnapshotRepository, PostEmbeddingRepository

def fix_engagement_data():
    """Copy engagement data from snapshots to post_embeddings"""
    snapshot_repo = UserSnapshotRepository()
    post_repo = PostEmbeddingRepository()
    
    # Get all Instagram post embeddings
    all_post_embeddings = list(post_repo.collection.find({'platform': 'instagram'}))
    
    print(f'Found {len(all_post_embeddings)} post embeddings to update')
    print()
    
    updated_count = 0
    skipped_count = 0
    
    # Group by user_id
    by_user = {}
    for post in all_post_embeddings:
        user_id = post.get('user_id')
        if user_id not in by_user:
            by_user[user_id] = []
        by_user[user_id].append(post)
    
    for user_id, posts in by_user.items():
        print(f'Processing {user_id}: {len(posts)} posts...')
        
        # Get snapshot
        snapshot = snapshot_repo.get_by_user_id(user_id, 'instagram')
        if not snapshot:
            print(f'  ❌ No snapshot found')
            skipped_count += len(posts)
            continue
        
        # Build lookup by post_id
        snapshot_posts = snapshot.get('posts', [])
        post_lookup = {}
        for sp in snapshot_posts:
            post_id = sp.get('id') or sp.get('pk') or sp.get('post_id')
            if post_id:
                post_lookup[str(post_id)] = sp
        
        # Update each post embedding
        user_updated = 0
        for post_emb in posts:
            post_id = str(post_emb.get('post_id', ''))
            if post_id in post_lookup:
                sp = post_lookup[post_id]
                like_count = sp.get('like_count', sp.get('liked_count', 0))
                comment_count = sp.get('comment_count', 0)
                
                # Update in database
                post_repo.collection.update_one(
                    {'_id': post_emb['_id']},
                    {'$set': {
                        'like_count': like_count,
                        'comment_count': comment_count
                    }}
                )
                user_updated += 1
        
        print(f'  ✅ Updated {user_updated}/{len(posts)} posts')
        updated_count += user_updated
        skipped_count += (len(posts) - user_updated)
    
    print()
    print('='*80)
    print(f'Migration complete!')
    print(f'  Updated: {updated_count}')
    print(f'  Skipped: {skipped_count}')
    print('='*80)

if __name__ == '__main__':
    fix_engagement_data()
