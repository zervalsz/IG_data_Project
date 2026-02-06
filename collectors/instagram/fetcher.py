"""
TikHub-based fetcher for Instagram raw data.

Provides programmatic functions to:
- fetch user info by username
- fetch posts / reels by user_id
- store raw responses into `raw_api_responses` collection
- build and upsert a snapshot for a single username (using adapter.normalize_snapshot)

This makes it easy to integrate fetching into the existing pipeline (fetch -> snapshot -> analyze).
"""

import os
import time
from datetime import datetime
from typing import Any, Dict, List, Optional
from pathlib import Path
import json
import requests
try:
    from pymongo import MongoClient
except Exception:
    MongoClient = None  # pymongo may not be available in test environments

try:
    from dotenv import load_dotenv
except Exception:
    # Allow tests to run in environments without python-dotenv installed
    def load_dotenv(*args, **kwargs):
        return None


# Load .env like other modules
root = Path(__file__).resolve().parents[2]
env_file = root / '.env'
local = Path(__file__).resolve().parent / '.env'
if env_file.exists():
    load_dotenv(env_file)
elif local.exists():
    load_dotenv(local)


def _get_mongo():
    uri = os.environ.get('MONGO_URI')
    if not uri:
        raise RuntimeError('MONGO_URI is not set')
    if MongoClient is None:
        raise RuntimeError('pymongo is not installed in this environment')
    client = MongoClient(uri)
    db_name = os.environ.get('DATABASE_NAME', 'ig_raw')
    return client[db_name]


def _get_tikhub_base():
    base = os.environ.get('TIKHUB_BASE_URL', 'https://api.tikhub.io').rstrip('/')
    return base


def _get_tikhub_token():
    token = os.environ.get('TIKHUB_API_TOKEN')
    if not token:
        raise RuntimeError('TIKHUB_API_TOKEN not found in environment')
    return token


def _save_raw(db, payload: Dict[str, Any], endpoint: str, username: Optional[str] = None, user_id: Optional[str] = None, source_file: Optional[str] = None):
    raw_col_name = os.environ.get('RAW_COLLECTION', 'raw_api_responses')
    raw_col = db[raw_col_name]
    # Ensure a file_hash field to avoid duplicate-key errors on null file_hash
    import hashlib
    fh = None
    if source_file:
        fh = source_file
    else:
        # Use a deterministic hash of the payload if possible
        try:
            payload_bytes = json.dumps(payload, sort_keys=True, ensure_ascii=False).encode('utf-8')
            fh = hashlib.sha256(payload_bytes).hexdigest()[:64]
        except Exception:
            fh = f"auto:{username}:{int(time.time()*1000)}"

    doc = {
        'platform': 'instagram',
        'endpoint': endpoint,
        'username': username or (payload.get('username') if isinstance(payload, dict) else None),
        'user_id': user_id or None,
        'raw': payload,
        'source_file': source_file,
        'file_hash': fh,
        'fetched_at': datetime.utcnow()
    }
    try:
        result = raw_col.insert_one(doc)
        return result.inserted_id
    except Exception as e:
        # Handle duplicate key errors gracefully by returning existing document id when possible
        try:
            from pymongo.errors import DuplicateKeyError
            if isinstance(e, DuplicateKeyError):
                existing = raw_col.find_one({'platform': 'instagram', 'file_hash': fh})
                if existing:
                    return existing.get('_id')
        except Exception:
            pass
        raise


def _extract_user_id(payload: Dict[str, Any]) -> Optional[str]:
    """Robustly extract a numeric/string user id from a TikHub user_info payload.

    Tries common paths and then does a recursive search for keys like 'id', 'pk', 'fbid'.
    Returns the id as a string or None.
    """
    if not isinstance(payload, dict):
        return None

    def try_path(d, path):
        v = d
        for p in path:
            if isinstance(v, dict):
                v = v.get(p)
            else:
                return None
        return v

    paths = [
        ['user', 'pk'], ['user', 'id'],
        ['data', 'id'], ['data', 'user', 'id'], ['data', 'data', 'user', 'id'],
        ['data', 'data', 'id'], ['data', 'user', 'pk'], ['fbid'], ['id']
    ]
    for path in paths:
        v = try_path(payload, path)
        if v:
            return str(v)

    # fallback: recursive search
    def find_key(d):
        if isinstance(d, dict):
            for k, val in d.items():
                if k in ('id', 'pk', 'fbid') and val:
                    return str(val)
                res = find_key(val)
                if res:
                    return res
        elif isinstance(d, list):
            for el in d:
                res = find_key(el)
                if res:
                    return res
        return None

    return find_key(payload)


def _extract_next_cursor(d: Dict[str, Any]) -> Optional[str]:
    """Extract pagination cursor from a TikHub paged response.

    Looks for common keys: 'next_max_id', 'max_id', 'next_cursor', 'cursor', 'end_cursor',
    and falls back to searching nested structures (including 'page_info').
    Returns the cursor string or None.
    """
    if not isinstance(d, dict):
        return None
    # top-level
    for k in ('next_max_id', 'max_id', 'next_cursor', 'cursor', 'end_cursor'):
        if d.get(k):
            return d.get(k)
    # nested common spots
    if d.get('data') and isinstance(d.get('data'), dict):
        dd = d.get('data')
        for k in ('next_max_id', 'max_id', 'next_cursor', 'cursor', 'end_cursor'):
            if dd.get(k):
                return dd.get(k)
        # page_info
        pi = dd.get('page_info') or {}
        if isinstance(pi, dict):
            if pi.get('end_cursor'):
                return pi.get('end_cursor')
            if pi.get('has_next_page') and pi.get('end_cursor'):
                return pi.get('end_cursor')
    # fallback: recursive search for keys
    def find_key(x):
        if isinstance(x, dict):
            for kk, vv in x.items():
                if kk in ('next_max_id', 'max_id', 'next_cursor', 'cursor', 'end_cursor') and vv:
                    return vv
                res = find_key(vv)
                if res:
                    return res
        elif isinstance(x, list):
            for el in x:
                res = find_key(el)
                if res:
                    return res
        return None
    return find_key(d)


# Module-level helper: write a local copy of fetched payloads
def _write_local(payload, username, endpoint, page_num):
    try:
        from pathlib import Path
        from datetime import datetime
        def safe_slug(s: str) -> str:
            import re
            s = (s or "").strip().lower()
            s = re.sub(r"\s+", "_", s)
            s = re.sub(r"[^a-z0-9_]+", "", s)
            return s[:80] or "account"

        outdir = Path("outputs/raw/instagram") / safe_slug(username or f"user_{payload.get('user_id', '')}")
        outdir.mkdir(parents=True, exist_ok=True)
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        fname = f"{safe_slug(username or f'user_{payload.get('user_id','') }')}_{endpoint}_page{page_num}_{ts}.json"
        outpath = outdir / fname
        outpath.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
        return str(outpath)
    except Exception:
        return None


# Module-level helper: candidate max id/cursor extraction
def _find_candidate_max_id(data):
    """Find a candidate max_id/cursor even when there's no explicit next cursor.

    Strategy:
    1. Use _extract_next_cursor
    2. Look for page_info.end_cursor anywhere
    3. Look for common edge lists (edges, items) and pick the last node's id/pk/shortcode
    4. Fallback: recursive look for 'max_id' keys
    """
    # 1
    nx = _extract_next_cursor(data)
    if nx:
        return nx

    # 2 - page_info end_cursor
    def find_page_info_end_cursor(x):
        if isinstance(x, dict):
            if 'page_info' in x and isinstance(x['page_info'], dict):
                pi = x['page_info']
                if pi.get('end_cursor'):
                    return pi.get('end_cursor')
            for v in x.values():
                res = find_page_info_end_cursor(v)
                if res:
                    return res
        elif isinstance(x, list):
            for el in x:
                res = find_page_info_end_cursor(el)
                if res:
                    return res
        return None

    pi_end = find_page_info_end_cursor(data)
    if pi_end:
        return pi_end

    # 3 - look for edges/items and take last node id or shortcode
    def find_last_node_id(x):
        if isinstance(x, dict):
            for k, v in x.items():
                if k in ('edges', 'items') and isinstance(v, list) and v:
                    last = v[-1]
                    if isinstance(last, dict):
                        node = last.get('node') if 'node' in last else last
                        for key in ('id', 'pk', 'shortcode', 'cursor'):
                            if isinstance(node, dict) and node.get(key):
                                return node.get(key)
                res = find_last_node_id(v)
                if res:
                    return res
        elif isinstance(x, list):
            for el in reversed(x):
                res = find_last_node_id(el)
                if res:
                    return res
        return None

    last_id = find_last_node_id(data)
    if last_id:
        return last_id

    # 4 - direct search for 'max_id' keys
    def find_key(d):
        if isinstance(d, dict):
            for k, v in d.items():
                if k in ('max_id', 'next_max_id') and v:
                    return v
                res = find_key(v)
                if res:
                    return res
        elif isinstance(d, list):
            for el in d:
                res = find_key(el)
                if res:
                    return res
        return None

    return find_key(data)


def _http_get(url, headers=None, params=None, timeout=60, max_retries=3):
    """Perform GET with simple retry/backoff for transient errors.

    Retries on network errors, 429 and 5xx responses. Returns the `requests.Response`.
    """
    import time as _time
    from requests.exceptions import RequestException

    last_resp = None
    backoff = 1
    for attempt in range(1, max_retries + 1):
        try:
            r = requests.get(url, headers=headers, params=params, timeout=timeout)
            last_resp = r
            # Retry on rate limit or server errors
            if r.status_code == 429 or (500 <= r.status_code < 600):
                if attempt == max_retries:
                    return r
                _time.sleep(backoff)
                backoff *= 2
                continue
            # For client errors like 422, return the response so caller can handle
            return r
        except RequestException as e:
            last_exc = e
            if attempt == max_retries:
                raise
            _time.sleep(backoff)
            backoff *= 2
    # If we exit loop unexpectedly, raise the last exception or return last response
    if last_resp is not None:
        return last_resp
    raise RuntimeError('HTTP GET failed after retries')


def fetch_user_info(username: str, save: bool = True) -> Dict[str, Any]: 
    """Fetch user info from TikHub by username. Returns the JSON payload.

    If `save` is True, the raw payload will be inserted into `raw_api_responses`.
    """
    token = _get_tikhub_token()
    base = _get_tikhub_base()
    url = f"{base}/api/v1/instagram/v1/fetch_user_info_by_username"

    headers = {"Authorization": f"Bearer {token}"}
    params = {"username": username}

    r = requests.get(url, headers=headers, params=params, timeout=60)
    r.raise_for_status()
    data = r.json()

    if save:
        db = _get_mongo()
        # store raw with a source_file hint
        sf = f"tikhub_user_info_{username}_{int(time.time())}.json"
        _save_raw(db, data, endpoint='user_info', username=username, user_id=None, source_file=sf)
    return data


def fetch_user_posts(user_id: str, username: Optional[str] = None, count: int = 50, save: bool = True, max_id: Optional[str] = None, page_num: int = 1) -> Dict[str, Any]:
    """Fetch user's posts from TikHub.

    - The TikHub API enforces a `count` <= 50. If the caller supplies a larger
      value we cap it to 50 and warn to avoid 422 errors.
    - Always write a local copy (via `_write_local`) to ensure reproducibility
      even if DB insert fails.
    - max_id: Pagination cursor from previous response's next_max_id field
    - page_num: Page number for local file naming (default 1)
    """
    token = _get_tikhub_token()
    base = _get_tikhub_base()
    url = f"{base}/api/v1/instagram/v1/fetch_user_posts"

    # Cap count to TikHub limits
    if count > 50:
        try:
            import warnings
            warnings.warn("TikHub API `count` limited to 50; capping the request to 50.")
        except Exception:
            pass
        count = 50

    headers = {"Authorization": f"Bearer {token}"}
    params = {"user_id": user_id, "count": count}
    
    # Add pagination cursor if provided
    if max_id:
        params["max_id"] = max_id

    # Use retrying GET helper
    r = _http_get(url, headers=headers, params=params, timeout=60)

    try:
        r.raise_for_status()
    except Exception as e:
        # Persist error payload for triage
        try:
            db = _get_mongo()
            err_doc = {'error': str(e), 'status': r.status_code, 'body': r.text, 'params': params}
            _save_raw(db, err_doc, endpoint='posts_list_error', username=username, user_id=user_id, source_file=None)
        except Exception:
            pass
        msg = f"TikHub fetch_user_posts failed: {e} - status={r.status_code} - body={r.text}"
        raise RuntimeError(msg)

    data = r.json()

    # Always write a local copy for reproducibility
    try:
        _write_local(data, username or str(user_id), 'posts_list', page_num)
    except Exception:
        pass

    if save:
        db = _get_mongo()
        sf = f"tikhub_user_{username or user_id}_posts_{int(time.time())}.json"
        _save_raw(db, data, endpoint='posts_list', username=username, user_id=user_id, source_file=sf)
    return data


def fetch_user_reels(user_id: str, username: Optional[str] = None, count: int = 50, save: bool = True, max_id: Optional[str] = None, page_num: int = 1) -> Dict[str, Any]:
    """Fetch user's reels from TikHub.

    Cap `count` to 50 to comply with TikHub API limits and provide clearer
    error messages on failure.
    - max_id: Pagination cursor from previous response's paging_info.max_id field
    - page_num: Page number for local file naming (default 1)
    """
    token = _get_tikhub_token()
    base = _get_tikhub_base()
    url = f"{base}/api/v1/instagram/v1/fetch_user_reels"

    if count > 50:
        try:
            import warnings
            warnings.warn("TikHub API `count` limited to 50; capping the request to 50.")
        except Exception:
            pass
        count = 50

    headers = {"Authorization": f"Bearer {token}"}
    params = {"user_id": user_id, "count": count}
    
    # Add pagination cursor if provided
    if max_id:
        params["max_id"] = max_id

    # Use retrying GET helper
    r = _http_get(url, headers=headers, params=params, timeout=60)

    try:
        r.raise_for_status()
    except Exception as e:
        try:
            db = _get_mongo()
            err_doc = {'error': str(e), 'status': r.status_code, 'body': r.text, 'params': params}
            _save_raw(db, err_doc, endpoint='reels_list_error', username=username, user_id=user_id, source_file=None)
        except Exception:
            pass
        msg = f"TikHub fetch_user_reels failed: {e} - status={r.status_code} - body={r.text}"
        raise RuntimeError(msg)

    data = r.json()

    try:
        _write_local(data, username or str(user_id), 'reels_list', page_num)
    except Exception:
        pass

    if save:
        db = _get_mongo()
        sf = f"tikhub_user_{username or user_id}_reels_{int(time.time())}.json"
        _save_raw(db, data, endpoint='reels_list', username=username, user_id=user_id, source_file=sf)
    return data


def fetch_and_store(username: str, fetch_posts: bool = True, fetch_reels: bool = True, posts_count: int = 50, reels_count: int = 50) -> Dict[str, Any]:
    """Fetch user info + posts/reels and store raw responses into DB.

    Returns a dict with keys: user_info, posts, reels and inserted raw ids.
    """
    db = _get_mongo()
    results = {'user_info': None, 'posts': None, 'reels': None, 'inserted_ids': []}

    user_info = fetch_user_info(username, save=True)
    results['user_info'] = user_info
    # Try to extract user_id from the user_info payload using a robust helper
    user_id = _extract_user_id(user_info)

    # If user_id not found, leave as None; posts/reels API needs user_id - caller can pass one instead
    if fetch_posts and user_id:
        posts = fetch_user_posts(user_id, username=username, count=posts_count, save=True)
        results['posts'] = posts
    if fetch_reels and user_id:
        reels = fetch_user_reels(user_id, username=username, count=reels_count, save=True)
        results['reels'] = reels

    # Upsert snapshot for this username using adapter.normalize_snapshot
    try:
        # Import adapter in a flexible way so fetcher works when executed as a script
        try:
            from .adapter import normalize_snapshot  # package context
        except Exception:
            try:
                from adapter import normalize_snapshot  # script context (collectors/instagram)
            except Exception:
                from collectors.instagram.adapter import normalize_snapshot  # absolute package

        raw_col = db[os.environ.get('RAW_COLLECTION', 'raw_api_responses')]
        # Find all raw docs for this username
        docs = list(raw_col.find({'platform': 'instagram', 'username': username}))
        if not docs:
            # Try a more lenient match: look for username in source_file
            docs = list(raw_col.find({'platform': 'instagram', 'source_file': {'$regex': username}}))

        if docs:
            # Call normalize_snapshot with docs formatted like adapter expects
            records = docs
            snap = normalize_snapshot(username, records)
            snapshot_col = db[os.environ.get('SNAPSHOT_COLLECTION', 'user_snapshots')]
            filter_q = {'platform': 'instagram', 'user_id': username}
            snapshot_col.update_one(filter_q, {'$set': snap}, upsert=True)
            results['snapshot_upserted'] = True
        else:
            results['snapshot_upserted'] = False
    except Exception as e:
        results['snapshot_upserted'] = False
        results['snapshot_error'] = str(e)

    return results


def fetch_and_store_paged(username: str, post_pages: int = 2, reel_pages: int = 2, count: int = 12, upsert_snapshot: bool = True, store_local_first: bool = False, local_file_limit: Optional[int] = None, upload_after_local: bool = True) -> Dict[str, Any]:
    """Fetch user info, then fetch multiple pages of posts and reels and store raw responses.

    - `post_pages` and `reel_pages` control how many pages to fetch (each page uses `count` items)
    - If `store_local_first` is True, all payloads are written to local files first and DB inserts are performed in bulk afterwards.
    - `local_file_limit` optionally caps how many local files will be stored before stopping (useful for your "5 file" requirement).
    - `upload_after_local` controls whether to upload collected local files to DB after fetching.

    Returns a dict summarizing fetched pages, local paths, and inserted IDs.
    """
    db = _get_mongo() if not store_local_first else None
    results = {'user_info': None, 'posts_pages': [], 'reels_pages': [], 'inserted_ids': [], 'local_files': []}

    # If storing locally first, fetch user_info without saving to DB, write local file
    if store_local_first:
        user_info = fetch_user_info(username, save=False)
        saved = _write_local(user_info, username, 'user_info', 0)
        results['user_info'] = user_info
        if saved:
            results['local_files'].append({'endpoint': 'user_info', 'local_path': saved, 'user_id': None})
    else:
        user_info = fetch_user_info(username, save=True)
        results['user_info'] = user_info

    # extract user_id using helper
    user_id = _extract_user_id(user_info)

    def _extract_next_cursor(d):
        # Try common places for a pagination cursor / next id
        if not isinstance(d, dict):
            return None
        # top-level
        for k in ('next_max_id', 'max_id', 'next_cursor', 'cursor', 'end_cursor'):
            if d.get(k):
                return d.get(k)
        # nested common spots
        if d.get('data') and isinstance(d.get('data'), dict):
            dd = d.get('data')
            for k in ('next_max_id', 'max_id', 'next_cursor', 'cursor', 'end_cursor'):
                if dd.get(k):
                    return dd.get(k)
            # page_info
            pi = dd.get('page_info') or {}
            if isinstance(pi, dict):
                if pi.get('end_cursor'):
                    return pi.get('end_cursor')
                if pi.get('has_next_page') and pi.get('end_cursor'):
                    return pi.get('end_cursor')
        # fallback: recursive search for keys
        def find_key(x):
            if isinstance(x, dict):
                for kk, vv in x.items():
                    if kk in ('next_max_id', 'max_id', 'next_cursor', 'cursor', 'end_cursor') and vv:
                        return vv
                    res = find_key(vv)
                    if res:
                        return res
            elif isinstance(x, list):
                for el in x:
                    res = find_key(el)
                    if res:
                        return res
            return None
        return find_key(d)

    # Fetch paged posts
    max_id = None
    seen_cursors = set()
    for p in range(post_pages):
        # Respect local_file_limit: stop if we've already written enough local files
        if local_file_limit and len(results['local_files']) >= local_file_limit:
            print(f"[fetcher] reached local_file_limit={local_file_limit} before posts page {p+1}; stopping posts pagination")
            break
        params = {'user_id': user_id, 'count': count}
        if max_id:
            params['max_id'] = max_id
        try:
            token = _get_tikhub_token()
            base = _get_tikhub_base()
            url = f"{base}/api/v1/instagram/v1/fetch_user_posts"
            headers = {"Authorization": f"Bearer {token}"}
            r = _http_get(url, headers=headers, params=params, timeout=60)
            try:
                r.raise_for_status()
            except Exception as e:
                # Save error doc
                try:
                    err_doc = {'error': str(e), 'status': r.status_code, 'body': r.text, 'params': params}
                    if not store_local_first:
                        _save_raw(db, err_doc, endpoint='posts_list_error', username=username, user_id=user_id, source_file=None)
                    else:
                        # store locally as a file so we persist the error
                        pth = _write_local(err_doc, username or str(user_id), 'posts_list_error', p+1)
                        if pth:
                            results['local_files'].append({'endpoint': 'posts_list_error', 'local_path': pth, 'user_id': user_id})
                except Exception:
                    pass
                raise

            data = r.json()
            # write a local copy
            saved_path = _write_local(data, username, 'posts_list', p+1)
            # If we're storing locally first, don't push to DB until later
            if store_local_first:
                results['local_files'].append({'endpoint': 'posts_list', 'local_path': saved_path, 'user_id': user_id, 'page': p+1})
                results['posts_pages'].append({'page': p+1, 'next_cursor': _extract_next_cursor(data) or _find_candidate_max_id(data), 'local_path': saved_path})
            else:
                sf = f"tikhub_user_{username}_posts_page{p+1}_{int(time.time())}.json"
                inserted_id = _save_raw(db, data, endpoint='posts_list', username=username, user_id=user_id, source_file=sf)
                results['posts_pages'].append({'page': p+1, 'inserted_id': inserted_id, 'next_cursor': _extract_next_cursor(data) or _find_candidate_max_id(data), 'local_path': saved_path})
            # Extract next cursor or find candidate
            next_cursor = _extract_next_cursor(data) or _find_candidate_max_id(data)
            # Stop if cursor is repeated
            if next_cursor and next_cursor in seen_cursors:
                results['posts_pages'][-1]['note'] = 'repeated_cursor_stopped'
                print(f"[fetcher] posts: next cursor repeated after page {p+1}; stopping pagination")
                break
            if next_cursor:
                seen_cursors.add(next_cursor)
            if not next_cursor:
                print(f"[fetcher] posts: no next cursor after page {p+1}; stopping pagination")
                break
            # set max_id for next request
            max_id = next_cursor
        except Exception as e:
            # Save error doc for this page
            try:
                if not store_local_first:
                    _save_raw(db, {'error': str(e), 'params': params}, endpoint='posts_list_error', username=username, user_id=user_id, source_file=None)
                else:
                    pth = _write_local({'error': str(e), 'params': params}, username or str(user_id), 'posts_list_error', p+1)
                    if pth:
                        results['local_files'].append({'endpoint': 'posts_list_error', 'local_path': pth, 'user_id': user_id})
            except Exception:
                pass
            results['posts_pages'].append({'page': p+1, 'error': str(e)})
            break

    # Fetch paged reels
    max_id = None
    seen_cursors = set()
    for p in range(reel_pages):
        # Respect local_file_limit
        if local_file_limit and len(results['local_files']) >= local_file_limit:
            print(f"[fetcher] reached local_file_limit={local_file_limit} before reels page {p+1}; stopping reels pagination")
            break
        params = {'user_id': user_id, 'count': count}
        if max_id:
            params['max_id'] = max_id
        try:
            token = _get_tikhub_token()
            base = _get_tikhub_base()
            url = f"{base}/api/v1/instagram/v1/fetch_user_reels"
            headers = {"Authorization": f"Bearer {token}"}
            r = _http_get(url, headers=headers, params=params, timeout=60)
            try:
                r.raise_for_status()
            except Exception as e:
                try:
                    if not store_local_first:
                        _save_raw(db, {'error': str(e), 'status': r.status_code, 'body': r.text, 'params': params}, endpoint='reels_list_error', username=username, user_id=user_id, source_file=None)
                    else:
                        pth = _write_local({'error': str(e), 'status': r.status_code, 'body': r.text, 'params': params}, username or str(user_id), 'reels_list_error', p+1)
                        if pth:
                            results['local_files'].append({'endpoint': 'reels_list_error', 'local_path': pth, 'user_id': user_id})
                except Exception:
                    pass
                raise

            data = r.json()
            saved_path = _write_local(data, username, 'reels_list', p+1)
            if store_local_first:
                results['local_files'].append({'endpoint': 'reels_list', 'local_path': saved_path, 'user_id': user_id, 'page': p+1})
                results['reels_pages'].append({'page': p+1, 'next_cursor': _extract_next_cursor(data) or _find_candidate_max_id(data), 'local_path': saved_path})
            else:
                sf = f"tikhub_user_{username}_reels_page{p+1}_{int(time.time())}.json"
                inserted_id = _save_raw(db, data, endpoint='reels_list', username=username, user_id=user_id, source_file=sf)
                results['reels_pages'].append({'page': p+1, 'inserted_id': inserted_id, 'next_cursor': _extract_next_cursor(data) or _find_candidate_max_id(data), 'local_path': saved_path})
            next_cursor = _extract_next_cursor(data) or _find_candidate_max_id(data)
            if next_cursor and next_cursor in seen_cursors:
                results['reels_pages'][-1]['note'] = 'repeated_cursor_stopped'
                print(f"[fetcher] reels: next cursor repeated after page {p+1}; stopping pagination")
                break
            if next_cursor:
                seen_cursors.add(next_cursor)
            if not next_cursor:
                print(f"[fetcher] reels: no next cursor after page {p+1}; stopping pagination")
                break
            max_id = next_cursor
        except Exception as e:
            try:
                if not store_local_first:
                    _save_raw(db, {'error': str(e), 'params': params}, endpoint='reels_list_error', username=username, user_id=user_id, source_file=None)
                else:
                    pth = _write_local({'error': str(e), 'params': params}, username or str(user_id), 'reels_list_error', p+1)
                    if pth:
                        results['local_files'].append({'endpoint': 'reels_list_error', 'local_path': pth, 'user_id': user_id})
            except Exception:
                pass
            results['reels_pages'].append({'page': p+1, 'error': str(e)})
            break

    # If storing locally first, upload the local files now (if requested)
    if store_local_first and upload_after_local:
        # Ensure we have a DB handle
        db = _get_mongo()
        inserted = []
        for lf in results['local_files']:
            try:
                p = lf.get('local_path')
                endpoint = lf.get('endpoint') or 'unknown'
                with open(p, 'r', encoding='utf-8') as fh:
                    payload = json.load(fh)
                sf = os.path.basename(p)
                iid = _save_raw(db, payload, endpoint=endpoint, username=username, user_id=lf.get('user_id'), source_file=sf)
                inserted.append(iid)
            except Exception as e:
                # Log and continue
                try:
                    _save_raw(db, {'upload_error': str(e), 'file': p}, endpoint=f"{endpoint}_upload_error", username=username, user_id=lf.get('user_id'), source_file=None)
                except Exception:
                    pass
        results['inserted_ids'] = inserted

    # Optionally upsert snapshot
    if upsert_snapshot:
        try:
            try:
                from .adapter import normalize_snapshot
            except Exception:
                try:
                    from adapter import normalize_snapshot
                except Exception:
                    from collectors.instagram.adapter import normalize_snapshot
            raw_col = db[os.environ.get('RAW_COLLECTION', 'raw_api_responses')]
            docs = list(raw_col.find({'platform': 'instagram', 'username': username}))
            if not docs:
                docs = list(raw_col.find({'platform': 'instagram', 'source_file': {'$regex': username}}))
            if docs:
                snap = normalize_snapshot(username, docs)
                snapshot_col = db[os.environ.get('SNAPSHOT_COLLECTION', 'user_snapshots')]
                filter_q = {'platform': 'instagram', 'user_id': username}
                snapshot_col.update_one(filter_q, {'$set': snap}, upsert=True)
                results['snapshot_upserted'] = True
            else:
                results['snapshot_upserted'] = False
        except Exception as e:
            results['snapshot_upserted'] = False
            results['snapshot_error'] = str(e)

    return results


if __name__ == '__main__':
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument('--username', required=True)
    ap.add_argument('--no-posts', action='store_true', help='Do not fetch posts')
    ap.add_argument('--no-reels', action='store_true', help='Do not fetch reels')
    args = ap.parse_args()

    out = fetch_and_store(args.username, fetch_posts=not args.no_posts, fetch_reels=not args.no_reels)
    print('Done:', out)
