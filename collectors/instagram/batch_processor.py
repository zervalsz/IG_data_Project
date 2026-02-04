#!/usr/bin/env python3
"""
Batch Profile Generator for Instagram Users

This script processes all Instagram users from raw data and generates profiles,
skipping users that already have profiles generated.

Usage:
    # Generate profiles for all users without existing profiles
    python3 batch_processor.py
    
    # Generate profiles for all users (skip existing)
    python3 batch_processor.py --all
    
    # Force regenerate profiles even if they exist
    python3 batch_processor.py --force-all
    
    # Regenerate specific user(s)
    python3 batch_processor.py --force user1 user2
"""

import os
import sys
import argparse
from pathlib import Path
from pymongo import MongoClient
from dotenv import load_dotenv

# Load environment
project_root = Path(__file__).resolve().parent.parent.parent
env_file = project_root / '.env'
if env_file.exists():
    load_dotenv(env_file)
else:
    local_env = Path(__file__).resolve().parent / '.env'
    if local_env.exists():
        load_dotenv(local_env)

# Import pipeline
sys.path.insert(0, str(Path(__file__).parent))
from pipeline import process_instagram_user


def get_users_with_raw_data(db):
    """Get all unique users from raw_api_responses"""
    users = db.raw_api_responses.distinct("username")
    return [u for u in users if u]  # Filter None/empty


def get_users_with_profiles(db):
    """Get all users that already have profiles"""
    profiles = db.user_profiles.find({}, {"user_id": 1})
    return set(p.get("user_id") for p in profiles if p.get("user_id"))


def get_mongo_db():
    """Get MongoDB connection"""
    mongo_uri = os.environ.get('MONGO_URI')
    if not mongo_uri:
        raise RuntimeError('MONGO_URI is not set in environment (.env)')
    database_name = os.environ.get('DATABASE_NAME', 'ig_raw')
    client = MongoClient(mongo_uri, serverSelectionTimeoutMS=10000)
    return client[database_name], client


def main():
    parser = argparse.ArgumentParser(
        description='Generate profiles for Instagram users',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 batch_processor.py              # Process only new users
  python3 batch_processor.py --all        # Process all users (skip existing)
  python3 batch_processor.py --force-all  # Regenerate all profiles
  python3 batch_processor.py --force user1 user2  # Regenerate specific users
        """
    )
    parser.add_argument('--all', action='store_true',
                       help='Process all users (skip those with existing profiles)')
    parser.add_argument('--force-all', action='store_true',
                       help='Regenerate profiles for all users')
    parser.add_argument('--force', nargs='*', metavar='USER',
                       help='Regenerate profiles for specific users (if no users specified with --force, regenerates all)')
    
    args = parser.parse_args()
    
    # Connect to DB
    try:
        db, client = get_mongo_db()
        client.admin.command('ping')
    except Exception as e:
        print(f"❌ MongoDB connection failed: {e}")
        return False
    
    # Get users
    raw_users = get_users_with_raw_data(db)
    profile_users = get_users_with_profiles(db)
    
    print("=" * 80)
    print("📊 BATCH PROFILE GENERATOR")
    print("=" * 80)
    print(f"\n📥 Users with raw data: {len(raw_users)}")
    print(f"✅ Users with profiles: {len(profile_users)}")
    print(f"⏳ Users needing profiles: {len(raw_users) - len(profile_users)}")
    
    # Determine which users to process
    if args.force_all:
        users_to_process = raw_users
        print(f"\n🔄 Mode: Force regenerate ALL users")
    elif args.force is not None:
        if args.force:  # If users specified with --force
            users_to_process = args.force
            print(f"\n🔄 Mode: Force regenerate specific users")
        else:  # --force without user list
            users_to_process = raw_users
            print(f"\n🔄 Mode: Force regenerate ALL users")
    elif args.all:
        users_to_process = raw_users
        print(f"\n📋 Mode: Process all users (skip existing)")
    else:
        # Default: only process users without profiles
        users_to_process = [u for u in raw_users if u not in profile_users]
        print(f"\n📋 Mode: Process only new users")
    
    # Filter out users not in raw data
    users_to_process = [u for u in users_to_process if u in raw_users]
    
    if not users_to_process:
        print("\n✅ All users already have profiles!")
        return True
    
    print(f"\n🎯 Will process {len(users_to_process)} user(s):")
    for user in sorted(users_to_process):
        status = "🔄 Regenerate" if user in profile_users else "✨ New"
        print(f"   {status}: {user}")
    
    # Process users
    print("\n" + "=" * 80)
    print("🚀 STARTING PROCESSING")
    print("=" * 80)
    
    successful = []
    failed = []
    
    for i, user_id in enumerate(sorted(users_to_process), 1):
        print(f"\n[{i}/{len(users_to_process)}] Processing: {user_id}")
        print("-" * 60)
        
        try:
            success = process_instagram_user(user_id)
            if success:
                successful.append(user_id)
            else:
                failed.append(user_id)
        except Exception as e:
            print(f"❌ Exception processing {user_id}: {e}")
            failed.append(user_id)
    
    # Summary
    print("\n" + "=" * 80)
    print("📈 PROCESSING SUMMARY")
    print("=" * 80)
    print(f"\n✅ Successful: {len(successful)}")
    for user in successful:
        print(f"   ✓ {user}")
    
    if failed:
        print(f"\n❌ Failed: {len(failed)}")
        for user in failed:
            print(f"   ✗ {user}")
    
    print(f"\n{'='*80}")
    if failed:
        print(f"⚠️  {len(failed)} user(s) failed to process")
        return False
    else:
        print(f"✅ All users processed successfully!")
        return True


if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
