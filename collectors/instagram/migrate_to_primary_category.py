#!/usr/bin/env python3
"""
Migration script: Update post_embeddings to use only primary_category
Changes from: categories = ["Category1", "Category2"]
To: categories = ["PrimaryCategory"]
"""

import os
from pymongo import MongoClient
from collections import Counter

def main():
    # Connect to MongoDB
    client = MongoClient(os.getenv('MONGODB_URI'))
    db = client['ig_raw']
    
    print("\n" + "="*70)
    print("Migration: Update posts to use only primary_category")
    print("="*70)
    
    # Get all user profiles with their primary categories
    profiles = list(db.user_profiles.find({}, {
        'user_id': 1,
        'profile_data.primary_category': 1,
        'profile_data.categories': 1
    }))
    
    user_primary_map = {}
    for p in profiles:
        user_id = p['user_id']
        profile_data = p.get('profile_data', {})
        primary = profile_data.get('primary_category')
        
        # Fallback to first category if no primary_category
        if not primary:
            cats = profile_data.get('categories', [])
            primary = cats[0] if cats else 'Lifestyle'
        
        user_primary_map[user_id] = primary
    
    print(f"\nFound {len(user_primary_map)} users with primary categories:")
    for user_id, primary in sorted(user_primary_map.items()):
        print(f"  {user_id}: {primary}")
    
    # Update all post_embeddings
    print("\n" + "-"*70)
    print("Updating post_embeddings...")
    print("-"*70)
    
    updated_count = 0
    skipped_count = 0
    category_dist = Counter()
    
    for user_id, primary_category in user_primary_map.items():
        # Update all posts for this user
        result = db.post_embeddings.update_many(
            {'user_id': user_id},
            {'$set': {'categories': [primary_category]}}
        )
        
        updated = result.modified_count
        updated_count += updated
        category_dist[primary_category] += updated
        
        if updated > 0:
            print(f"  {user_id}: {updated} posts → {primary_category}")
        else:
            skipped_count += 1
    
    print("\n" + "="*70)
    print("Migration Complete!")
    print("="*70)
    print(f"\nTotal posts updated: {updated_count}")
    print(f"Users with no posts: {skipped_count}")
    
    print("\n" + "-"*70)
    print("Post distribution by category:")
    print("-"*70)
    for cat, count in sorted(category_dist.items(), key=lambda x: -x[1]):
        print(f"  {cat}: {count} posts")
    
    # Verify
    print("\n" + "-"*70)
    print("Verification - Sample posts:")
    print("-"*70)
    sample_posts = db.post_embeddings.aggregate([
        {'$sample': {'size': 5}},
        {'$project': {'user_id': 1, 'categories': 1, 'caption': 1}}
    ])
    
    for post in sample_posts:
        caption = post.get('caption', '')[:50]
        print(f"  {post['user_id']}: {post['categories']} - \"{caption}...\"")
    
    print("\n✅ Migration successful!")

if __name__ == '__main__':
    main()
