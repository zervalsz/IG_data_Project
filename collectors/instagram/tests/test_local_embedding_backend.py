def test_sentence_transformers_wrapper_smoke():
    try:
        import sentence_transformers  # quick availability check
    except Exception:
        import pytest
        pytest.skip("sentence-transformers not available in this environment")

    from collectors.instagram.embedding_backend import SentenceTransformersWrapper
    w = SentenceTransformersWrapper('all-MiniLM-L6-v2')
    # encode a short text
    emb = w.encode("hello world")
    assert hasattr(emb, 'tolist')
    assert len(emb.tolist()) > 0
