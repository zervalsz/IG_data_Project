"""Lightweight local embedding backend using sentence-transformers.

Provides a small wrapper with an encode(...) method compatible with the
existing `FlagModel`-like usage in the analyzer (returns a numpy array).
"""
from typing import Any, Iterable, List, Optional

class SentenceTransformersWrapper:
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        try:
            from sentence_transformers import SentenceTransformer
        except Exception as e:
            raise RuntimeError("sentence-transformers is not installed or failed to import: %s" % e)
        self.model = SentenceTransformer(model_name)

    def encode(self, texts: Any, **kwargs) -> "list":
        """Encode a string or list of strings and return a numpy array-like object.

        The analyzer expects an object that has .tolist() — numpy arrays satisfy that.
        """
        emb = self.model.encode(texts, convert_to_numpy=True, **kwargs)
        return emb
