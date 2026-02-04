import pytest
from collectors.instagram.fetcher import _extract_user_id, _extract_next_cursor


def test_extract_user_id_simple():
    payload = {'id': '12345'}
    assert _extract_user_id(payload) == '12345'


def test_extract_user_id_nested():
    payload = {'data': {'data': {'user': {'id': 67890}}}}
    assert _extract_user_id(payload) == '67890'


def test_extract_user_id_none():
    assert _extract_user_id(None) is None


def test_extract_next_cursor_top_level():
    payload = {'next_max_id': 'abc123'}
    assert _extract_next_cursor(payload) == 'abc123'


def test_extract_next_cursor_page_info():
    payload = {'data': {'page_info': {'end_cursor': 'cursor789', 'has_next_page': True}}}
    assert _extract_next_cursor(payload) == 'cursor789'


def test_extract_next_cursor_nested_list():
    payload = {'something': [{'more': {'next_cursor': 'x'}}]}
    assert _extract_next_cursor(payload) == 'x'
