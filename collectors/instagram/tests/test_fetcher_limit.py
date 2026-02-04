import types
from collectors.instagram.fetcher import fetch_user_posts


class DummyResponse:
    def __init__(self, status_code=200, text='{}'):
        self.status_code = status_code
        self.text = text

    def raise_for_status(self):
        if self.status_code >= 400:
            raise Exception(f"HTTP {self.status_code}")

    def json(self):
        return {}


def test_fetch_user_posts_caps_count(monkeypatch):
    called = {}

    def fake_get(url, headers=None, params=None, timeout=None):
        called['url'] = url
        called['params'] = params
        return DummyResponse()

    monkeypatch.setattr('requests.get', fake_get)
    monkeypatch.setenv('TIKHUB_API_TOKEN', 'dummy')

    # Call with a large count that would exceed TikHub limits
    fetch_user_posts('12345', username='u', count=200, save=False)

    assert called['params']['count'] == 50, "fetch_user_posts should cap count to 50"
