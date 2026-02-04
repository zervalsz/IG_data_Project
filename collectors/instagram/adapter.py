#!/usr/bin/env python3
"""
Adapter: raw_api_responses -> user_snapshots

This script reads your single collection (default: `raw_api_responses`),
groups records by username (or other id) and writes unified snapshot
documents to `user_snapshots` collection so the existing pipeline can
process them.

Usage examples:

# dry-run to preview 5 users
python3 adapter.py --dry-run --limit 5

# perform upserts into DB
python3 adapter.py --apply

Environment variables (from project .env):
- MONGO_URI
- DATABASE_NAME (default: instagram_data)
- RAW_COLLECTION (optional, default: raw_api_responses)
- SNAPSHOT_COLLECTION (optional, default: user_snapshots)

The adapter is resilient to a few common raw shapes. It will try to:
- extract username from common locations
- aggregate posts-like arrays from fields like `data`, `items`, `media`, `edges`, `posts`

"""

import os
import argparse
from collections import defaultdict
from datetime import datetime
from dotenv import load_dotenv
from pymongo import MongoClient
from typing import Any, Dict, List, Optional
import pprint


def load_env():
    # load env from repo root .env if exists
    root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
    env_file = os.path.join(root, '.env')
    if os.path.exists(env_file):
        load_dotenv(env_file)
    else:
        # fallback to local collectors/instagram/.env
        local = os.path.join(os.path.dirname(__file__), '.env')
        if os.path.exists(local):
            load_dotenv(local)


def mongo_client():
    uri = os.environ.get('MONGO_URI')
    if not uri:
        raise RuntimeError('MONGO_URI is not set in environment (.env)')
    return MongoClient(uri)


def extract_username(raw: Dict[str, Any]) -> Optional[str]:
    # Try common locations for username
    if not raw:
        return None
    # 1. raw.get('username')
    if isinstance(raw.get('username'), str) and raw.get('username'):
        return raw.get('username')
    # 2. raw.get('user', {}).get('username')
    user = raw.get('user')
    if isinstance(user, dict):
        for k in ('username', 'user_name', 'screen_name', 'id'):
            if k in user and isinstance(user[k], str) and user[k]:
                return user[k]
    # 3. raw.get('data') where data may be dict with 'username' or 'user'
    data = raw.get('data')
    if isinstance(data, dict):
        if 'username' in data and isinstance(data['username'], str):
            return data['username']
        if 'user' in data and isinstance(data['user'], dict):
            if 'username' in data['user']:
                return data['user']['username']
    # 4. nested keys commonly found in API responses
    for key in ('author', 'owner'):
        node = raw.get(key)
        if isinstance(node, dict) and node.get('username'):
            return node.get('username')
    # 5. try to parse username from file/source path if present
    sf = None
    for k in ('source_file', 'source_path', 'file_name', 'file'):
        v = raw.get(k)
        if isinstance(v, str) and v:
            sf = v
            break

    if sf:
        # Try patterns: (username) inside parentheses
        import re
        m = re.search(r"\(([^)]+)\)", sf)
        if m:
            return m.group(1)
        # Try prefix patterns like: prefix_username_user_info or username_posts_list
        m2 = re.search(r"(?:^|[/_\\-])([A-Za-z0-9._-]{3,50})_(?:user|user_info|posts|post|posts_list|reel|reels)", sf)
        if m2:
            return m2.group(1)
        # As fallback, pick the filename without extension and take the first token
        base = os.path.basename(sf)
        base = os.path.splitext(base)[0]
        parts = re.split(r"[_\- ]+", base)
        if parts:
            return parts[0]

    return None


def extract_posts(raw: Dict[str, Any]) -> List[Dict[str, Any]]:
    # Try to extract a list of post-like objects from common fields
    posts = []
    if not raw:
        return posts

    # If raw itself looks like a list
    if isinstance(raw, list):
        return raw

    # Candidate fields
    candidates = ['items', 'data', 'media', 'posts', 'edges', 'nodes', 'results']
    for c in candidates:
        v = raw.get(c)
        if isinstance(v, list) and v:
            # If items are dicts, assume posts
            if all(isinstance(x, dict) for x in v):
                posts.extend(v)
            else:
                # wrap primitives as caption objects
                posts.extend([{'text': str(x)} for x in v])
            return posts

    # Some APIs embed posts inside raw['data']['items'] etc.
    data = raw.get('data')
    if isinstance(data, dict):
        for c in candidates:
            v = data.get(c)
            if isinstance(v, list) and v:
                posts.extend(v)
                return posts

    # If raw has a 'caption' or 'text' field, consider it a single post
    if any(k in raw for k in ('caption', 'text', 'comment', 'message')):
        # Normalize keys
        post = {}
        for k in ('id', 'caption', 'text', 'likes', 'comments', 'hashtags', 'timestamp'):
            if k in raw:
                post[k] = raw[k]
        posts.append(post)
        return posts

    return posts


def normalize_snapshot(username: str, records: List[Dict[str, Any]]) -> Dict[str, Any]:
    # Build a snapshot with user_info and posts
    user_info = {}
    posts = []

    for rec in records:
        endpoint = rec.get('endpoint') or rec.get('type') or ''
        raw = rec.get('raw') or {}
        # If this record looks like user info
        if 'user' in raw or endpoint.lower().startswith('user') or endpoint == 'user_info':
            # Merge available top-level user fields
            # prefer raw['user'] if present
            if isinstance(raw.get('user'), dict):
                user_info.update(raw.get('user'))
            # some raw responses include top-level info
            for k in ('username', 'bio', 'followers', 'following', 'posts_count', 'profile_pic'):
                if k in raw and raw[k]:
                    user_info.setdefault(k, raw[k])
            # some services include in raw['data']
            if isinstance(raw.get('data'), dict):
                for k in ('username', 'bio'):
                    if k in raw['data']:
                        user_info.setdefault(k, raw['data'][k])
        # If it looks like posts
        extracted = extract_posts(raw)
        if extracted:
            posts.extend(extracted)

    # fallback: minimal user_info
    if not user_info:
        user_info = {'username': username}

    snapshot = {
        'platform': 'instagram',
        'user_id': username,
        'user_info': user_info,
        'posts': posts,
        'total_posts': len(posts),
        'created_at': datetime.utcnow(),
        'source_count': len(records)
    }
    return snapshot


def run_adapter(apply: bool = False, dry_run: bool = False, limit: Optional[int] = None, raw_collection_name: str = 'raw_api_responses'):
    load_env()
    client = mongo_client()
    db_name = os.environ.get('DATABASE_NAME', 'instagram_data')
    db = client[db_name]
    raw_col = db[raw_collection_name]
    snapshot_col_name = os.environ.get('SNAPSHOT_COLLECTION', 'user_snapshots')
    snapshot_col = db[snapshot_col_name]

    # Query only instagram platform by default
    cursor = raw_col.find({'platform': 'instagram'})
    if limit:
        cursor = cursor.limit(limit)

    groups = defaultdict(list)
    total = 0
    for doc in cursor:
        total += 1
        raw = doc.get('raw') or {}
        username = extract_username(raw) or doc.get('username') or raw.get('username') or doc.get('file_hash')
        if not username:
            # try to infer from source_file name
            sf = raw.get('source_file') or doc.get('source_file') or doc.get('file_name')
            if isinstance(sf, str):
                # crude attempt: split by underscores
                parts = sf.split('_')
                if parts:
                    username = parts[0]
        if not username:
            username = f"unknown_{doc.get('_id')}"
        groups[username].append(doc)

    print(f"Found {len(groups)} grouped users from {total} raw documents")

    # Build snapshots
    snapshots = {}
    for username, records in groups.items():
        snapshots[username] = normalize_snapshot(username, records)

    if dry_run:
        print("DRY RUN: Showing up to 5 snapshots:\n")
        pp = pprint.PrettyPrinter(depth=2)
        shown = 0
        for username, snap in snapshots.items():
            print(f"--- {username} ---")
            pp.pprint({k: snap[k] for k in ('user_id', 'total_posts', 'source_count')})
            shown += 1
            if shown >= 5:
                break
        return

    # Apply upsert to snapshot collection
    if apply:
        print(f"Applying {len(snapshots)} upserts to collection '{snapshot_col_name}' in DB '{db_name}'")
        for username, snap in snapshots.items():
            filter_q = {'platform': 'instagram', 'user_id': username}
            update = {'$set': snap}
            snapshot_col.update_one(filter_q, update, upsert=True)
        print("✅ Upsert complete")
    else:
        print("No apply flag given. Run with --apply to write snapshots into DB")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Adapter: raw_api_responses -> user_snapshots')
    parser.add_argument('--apply', action='store_true', help='Write snapshots into MongoDB (upsert)')
    parser.add_argument('--dry-run', action='store_true', help='Preview snapshots without writing')
    parser.add_argument('--limit', type=int, help='Limit number of raw docs to process')
    parser.add_argument('--raw-collection', type=str, default='raw_api_responses', help='Raw collection name')
    args = parser.parse_args()

    run_adapter(apply=args.apply, dry_run=args.dry_run, limit=args.limit, raw_collection_name=args.raw_collection)
