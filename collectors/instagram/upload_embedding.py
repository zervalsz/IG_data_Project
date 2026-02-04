"""Upload local user embedding JSON files into MongoDB collection `user_embedding`.

Usage:
    python upload_embedding.py --file outputs/embeddings/nabela_profile_embedding.json

The script expects MONGO_URI (and optional DATABASE_NAME) to be available via environment variables
or in one of the repository .env files (project root or backend/.env). It will upsert a document keyed
by (platform, user_id) into the `user_embedding` collection.
"""
import os
import json
import argparse
from datetime import datetime

# Import get_database which will read MONGO_URI from env/.env
from backend.database.connection import get_database


def load_json_file(path: str):
    with open(path, 'r', encoding='utf-8') as fh:
        return json.load(fh)


def upsert_embedding(doc: dict, collection_name: str = 'user_embedding'):
    db = get_database()
    col = db[collection_name]

    # Normalize doc fields
    platform = doc.get('platform', 'instagram')
    user_id = doc.get('user_id') or doc.get('username')
    if not user_id:
        raise RuntimeError('user_id/username not found in document')

    payload = {
        'platform': platform,
        'user_id': user_id,
        'username': doc.get('username'),
        'embedding': doc.get('profile_data', {}).get('user_style_embedding') or doc.get('profile_data', {}).get('user_style_embedding'),
        'model': doc.get('model'),
        'dimension': doc.get('dimension') or (len(doc.get('profile_data', {}).get('user_style_embedding', [])) if doc.get('profile_data') else None),
        'profile_data': doc.get('profile_data'),
        'created_at': doc.get('created_at') or datetime.utcnow(),
        'updated_at': datetime.utcnow()
    }

    # Upsert by platform + user_id
    res = col.update_one({'platform': platform, 'user_id': user_id}, {'$set': payload}, upsert=True)
    if res.upserted_id:
        print(f"Inserted new embedding doc with _id={res.upserted_id}")
    else:
        print(f"Updated embedding for {platform}/{user_id}")


def main():
    parser = argparse.ArgumentParser(description='Upload local user embedding JSON to MongoDB')
    parser.add_argument('--file', '-f', required=True, help='Path to local embedding JSON file')
    parser.add_argument('--collection', '-c', default='user_embedding', help='MongoDB collection name to upsert into')
    args = parser.parse_args()

    # Quick env check
    if not os.environ.get('MONGO_URI'):
        raise RuntimeError('MONGO_URI environment variable is not set. Please set it or add a .env file with MONGO_URI.')

    payload = load_json_file(args.file)

    upsert_embedding(payload, collection_name=args.collection)


if __name__ == '__main__':
    main()
