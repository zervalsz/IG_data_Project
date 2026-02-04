from collectors.instagram.fetcher import _find_candidate_max_id


def test_find_candidate_next_cursor_from_page_info():
    payload = {'data': {'some': {'page_info': {'end_cursor': 'c1'}}}}
    assert _find_candidate_max_id(payload) == 'c1'


def test_find_candidate_last_node_id():
    payload = {'data': {'edges': [{'node': {'id': 'first'}}, {'node': {'id': 'last'}}]}}
    assert _find_candidate_max_id(payload) == 'last'


def test_find_candidate_max_id_key():
    payload = {'wrapper': {'max_id': 'm123'}}
    assert _find_candidate_max_id(payload) == 'm123'
