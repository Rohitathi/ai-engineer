import math
import re
from typing import List

_DIMENSIONS = 64
_TOKEN_RE = re.compile(r"[a-zA-Z0-9_']+")


def tokenize(text: str) -> List[str]:
    return [t.lower() for t in _TOKEN_RE.findall(text or "")]


def embed_text(text: str, dimensions: int = _DIMENSIONS) -> List[float]:
    """Small local embedding function.

    This avoids external dependencies so the demo app can run locally.
    It is not as strong as OpenAI embeddings, but it is good enough to power
    semantic search and recommendations in a learning project.
    """
    vector = [0.0] * dimensions
    tokens = tokenize(text)
    if not tokens:
        return vector

    for token in tokens:
        idx = hash(token) % dimensions
        vector[idx] += 1.0

    norm = math.sqrt(sum(v * v for v in vector)) or 1.0
    return [round(v / norm, 6) for v in vector]


def cosine_similarity(a: List[float], b: List[float]) -> float:
    if not a or not b or len(a) != len(b):
        return 0.0
    return sum(x * y for x, y in zip(a, b))
