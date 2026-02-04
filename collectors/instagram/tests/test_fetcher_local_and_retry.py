import os
from pathlib import Path
import json
import types
import requests

from collectors.instagram import fetcher


class DummyResponse:
    def __init__(self, json_obj=None, status_code=200, text=None):
        self._json = json_obj or {}
        self.status_code = status_code
        self.text = text or json.dumps(self._json)

    def raise_for_status(self):
        if self.status_code >= 400:
            raise requests.exceptions.HTTPError(f"HTTP {self.status_code}")

    def json(self):
        return self._json


def test_fetch_user_posts_writes_local(monkeypatch, tmp_path):
    # Run inside tmp dir so outputs are isolated
    monkeypatch.chdir(tmp_path)

    def fake_get(url, headers=None, params=None, timeout=None):
        return DummyResponse({'data': {'items': [{'id': '1'}], 'next_cursor': None}})

    monkeypatch.setenv('TIKHUB_API_TOKEN', 'dummy')
    monkeypatch.setattr('requests.get', fake_get)

    res = fetcher.fetch_user_posts('12345', username='testuser', count=1, save=False)

    outdir = Path('outputs/raw/instagram/testuser')
    assert outdir.exists(), 'Local output directory should be created'
    files = list(outdir.glob('testuser_posts_list_page*'))
    assert files, 'A local posts file should be written'


def test_http_get_retry(monkeypatch):
    calls = {'n': 0}

    def flaky_get(url, headers=None, params=None, timeout=None):
        calls['n'] += 1
        if calls['n'] < 3:
            raise requests.exceptions.ConnectionError('temporary')
        return DummyResponse({'ok': True})

    monkeypatch.setattr('requests.get', flaky_get)

    r = fetcher._http_get('http://example.local', headers={}, params={})
    assert r.json().get('ok') is True


def test_paged_fetch_stops_on_repeated_cursor(monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)

    call_count = {'n': 0}

    def fake_http_get(url, headers=None, params=None, timeout=None):
        call_count['n'] += 1
        # Return same next_cursor for first two calls
        return DummyResponse({'data': {'items': [{'id': str(call_count['n'])}], 'next_cursor': 'REPEAT'}})

    monkeypatch.setattr(fetcher, '_http_get', fake_http_get)

    # monkeypatch save_raw to avoid DB dependency and avoid needing a real DB
    monkeypatch.setattr(fetcher, '_save_raw', lambda db, payload, endpoint, username=None, user_id=None, source_file=None: 'fakeid')
    # harmless _get_mongo stub so function can run
    monkeypatch.setattr(fetcher, '_get_mongo', lambda: object())
    monkeypatch.setenv('TIKHUB_API_TOKEN', 'dummy')
    # Avoid real user_info network call
    monkeypatch.setattr(fetcher, 'fetch_user_info', lambda username, save=True: {'user': {'id': 'uid123', 'username': username}})

    res = fetcher.fetch_and_store_paged('testuser', post_pages=5, reel_pages=0, count=1)
    # Should have stopped due to repeated cursor on the second page
    assert len(res['posts_pages']) >= 1
    # The second page, if present, should have 'note' == 'repeated_cursor_stopped' or only 1 page
    if len(res['posts_pages']) >= 2:
        assert 'note' in res['posts_pages'][1] and res['posts_pages'][1]['note'] == 'repeated_cursor_stopped'
