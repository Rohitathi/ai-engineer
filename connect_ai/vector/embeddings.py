import math
import re
from functools import lru_cache

try:
    import numpy as np
except Exception:  # pragma: no cover - optional dependency fallback
    np = None


DIMENSION = 384
_TOKEN_RE = re.compile(r"[a-zA-Z0-9_']+")


@lru_cache(maxsize=1)
def get_model():
    from sentence_transformers import SentenceTransformer

    return SentenceTransformer("all-MiniLM-L6-v2")


def _as_vector(values):
    if np is not None:
        return np.asarray(values, dtype="float32")
    return [float(value) for value in values]


def _fallback_embed(text):
    vector = [0.0] * DIMENSION
    tokens = [token.lower() for token in _TOKEN_RE.findall(text or "")]
    if not tokens:
        return _as_vector(vector)

    for token in tokens:
        vector[hash(token) % DIMENSION] += 1.0

    norm = math.sqrt(sum(value * value for value in vector)) or 1.0
    return _as_vector([value / norm for value in vector])


def embed_text(text):
    text = (text or "").strip()
    if not text:
        return _as_vector([0.0] * DIMENSION)

    try:
        embedding = get_model().encode(text, normalize_embeddings=True)
        return _as_vector(embedding)
    except Exception:
        return _fallback_embed(text)


def embed_texts(texts):
    texts = texts or []
    if not texts:
        return []

    try:
        embeddings = get_model().encode(texts, normalize_embeddings=True)
        if np is not None:
            return np.asarray(embeddings, dtype="float32")
        return [[float(value) for value in row] for row in embeddings]
    except Exception:
        return [_fallback_embed(text) for text in texts]
