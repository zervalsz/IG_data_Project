import json
import os
from pathlib import Path

from collectors.instagram import fetcher


def test_store_local_first_uploads_after_collect(monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)

    # stub fetch_user_info
    monkeypatch.setattr(fetcher, 'fetch_user_info', lambda username, save=True: {'user': {'id': 'U1', 'username': username}})

    # fake http_get to return two posts pages and one reels page
    posts_responses = [
        {'data': {'items': [{'id': 'p1'}], 'next_cursor': 'c1'}},
        {'data': {'items': [{'id': 'p2'}], 'next_cursor': None}}
    ]
    reels_responses = [
        {'data': {'items': [{'id': 'r1'}], 'next_cursor': None}}
    ]

    calls = {'n': 0, 'type': None}

    def fake_http_get(url, headers=None, params=None, timeout=None):
        if 'fetch_user_posts' in url:
            ret = posts_responses[calls['n']]
            calls['n'] += 1
            return type('R', (), {'status_code': 200, 'text': json.dumps(ret), 'json': lambda: ret, 'raise_for_status': lambda: None})
        else:
            return type('R', (), {'status_code': 200, 'text': json.dumps(reels_responses[0]), 'json': lambda: reels_responses[0], 'raise_for_status': lambda: None})

    monkeypatch.setattr(fetcher, '_http_get', fake_http_get)

    # make _write_local actually write files
    def real_write_local(payload, username, endpoint, page):
        outdir = Path('outputs/raw/instagram') / username
        outdir.mkdir(parents=True, exist_ok=True)
        p = outdir / f"{username}_{endpoint}_page{page}.json"
        p.write_text(json.dumps(payload))
        return str(p)

    monkeypatch.setattr(fetcher, '_write_local', real_write_local)

    saved = []
    def fake_save_raw(db, payload, endpoint, username=None, user_id=None, source_file=None):
        saved.append((endpoint, source_file))
        return f"id_{len(saved)}"

    monkeypatch.setattr(fetcher, '_save_raw', fake_save_raw)
    monkeypatch.setattr(fetcher, '_get_mongo', lambda: object())

    res = fetcher.fetch_and_store_paged('testuser', post_pages=5, reel_pages=2, count=1, store_local_first=True, local_file_limit=5)

    # Local files should be collected
    assert res['local_files'], 'Expected local files to be collected'
    # After upload step fake_save_raw should have been called equal to number of local files
    assert len(saved) == len(res['local_files'])
