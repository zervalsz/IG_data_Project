#!/usr/bin/env python3
"""
Extract follower counts from raw_api_responses and update user_profiles
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'backend'))

from database.connection import get_database

def extract_follower_count(raw_data):
    """Extract follower count from user_info raw response"""
    try:
        # Path: raw.data.data.user.edge_followed_by.count
        user = raw_data.get('data', {}).get('data', {}).get('user', {})
        followers = user.get('edge_followed_by', {}).get('count', 0)
        following = user.get('edge_follow', {}).get('count', 0)
        return followers, following
    except Exception as e:
        print(f"  Error extracting follower count: {e}")
        return 0, 0

def main():
    db = get_database()
    
    print(f"\n{'='*60}")
    print(f"🔧 Updating Follower Counts from user_info Endpoints")
    print(f"{'='*60}\n")
    
    # Get all user_info responses
    user_info_responses = list(db.raw_api_responses.find({'endpoint': 'user_info'}))
    
    print(f"Found {len(user_info_responses)} user_info responses\n")
    
    updated = 0
    not_found = 0
    
    for resp in user_info_responses:
        username = resp.get('username')
        if not username:
            continue
        
        # Extract follower count from raw data
        raw = resp.get('raw', {})
        followers, following = extract_follower_count(raw)
        
        if followers > 0:
            print(f"{username}: {followers:,} followers, {following:,} following")
            
            # Update user_profile
            result = db.user_profiles.update_one(
                {'user_id': username},
                {'$set': {
                    'profile_data.follower_count': followers,
                    'profile_data.following_count': following
                }}
            )
            
            if result.modified_count > 0:
                updated += 1
                print(f"  ✅ Updated profile")
            else:
                print(f"  ⚠️  Profile not found or already had this value")
                not_found += 1
        else:
            print(f"{username}: No follower data found")
            not_found += 1
    
    print(f"\n{'='*60}")
    print(f"📊 Summary: {updated} updated, {not_found} not found/skipped")
    print(f"{'='*60}\n")
    
    # Verify
    print("Verifying updates...")
    profiles_with_followers = db.user_profiles.count_documents({'profile_data.follower_count': {'$exists': True, '$gt': 0}})
    print(f"Profiles with follower counts: {profiles_with_followers}/{db.user_profiles.count_documents({})}")
    
    # Show sample
    print("\nSample profiles:")
    for profile in db.user_profiles.find({}, {'user_id': 1, 'profile_data.follower_count': 1}).limit(5):
        user_id = profile.get('user_id')
        followers = profile.get('profile_data', {}).get('follower_count', 'MISSING')
        print(f"  {user_id}: {followers:,} followers" if isinstance(followers, int) else f"  {user_id}: {followers}")

if __name__ == '__main__':
    main()
