from collections import Counter

from connect_ai.vector.embeddings import DIMENSION

try:
    import faiss
except Exception:  # pragma: no cover - optional dependency fallback
    faiss = None

try:
    import numpy as np
except Exception:  # pragma: no cover - optional dependency fallback
    np = None


items = []
vectors_count = 0


def _new_index():
    if faiss is None:
        return []
    return faiss.IndexFlatL2(DIMENSION)


index = _new_index()


def _vector_to_list(vector):
    if np is not None:
        return np.asarray(vector, dtype="float32").tolist()
    return [float(value) for value in vector]


def _vectors_to_lists(vectors):
    if np is not None:
        matrix = np.asarray(vectors, dtype="float32")
        if matrix.ndim == 1:
            matrix = matrix.reshape(1, -1)
        return matrix.tolist()
    if not vectors:
        return []
    if isinstance(vectors[0], (int, float)):
        return [[float(value) for value in vectors]]
    return [[float(value) for value in row] for row in vectors]


def _distance(a, b):
    return sum((x - y) ** 2 for x, y in zip(a, b))


def reset_index():
    global index, items, vectors_count
    index = _new_index()
    items = []
    vectors_count = 0


def add_item(item_id, vector, item_type="generic", payload=None):
    add_items(
        [
            {
                "item_id": item_id,
                "vector": vector,
                "item_type": item_type,
                "payload": payload or {},
            }
        ]
    )


def add_items(batch_items):
    global vectors_count
    if not batch_items:
        return

    vecs = _vectors_to_lists([item["vector"] for item in batch_items])
    metas = [
        {
            "item_id": item["item_id"],
            "item_type": item.get("item_type", "generic"),
            "payload": item.get("payload", {}),
        }
        for item in batch_items
    ]

    if faiss is not None and np is not None:
        index.add(np.asarray(vecs, dtype="float32"))
    else:
        index.extend(vecs)

    items.extend(metas)
    vectors_count += len(batch_items)


def search_index(vector, k=5, item_type=None):
    if not items:
        return []

    limit = min(max(k, 1), len(items))
    query = _vector_to_list(vector)

    if faiss is not None and np is not None:
        distances, indices = index.search(np.asarray([query], dtype="float32"), limit)
        pairs = zip(distances[0], indices[0])
    else:
        ranked = sorted(
            ((float(_distance(query, row)), idx) for idx, row in enumerate(index)),
            key=lambda item: item[0],
        )[:limit]
        pairs = ranked

    results = []
    for score, idx in pairs:
        if idx < 0 or idx >= len(items):
            continue
        item = items[idx]
        if item_type and item["item_type"] != item_type:
            continue
        results.append(
            {
                "item_id": item["item_id"],
                "item_type": item["item_type"],
                "score": float(score),
                "payload": item["payload"],
            }
        )
    return results


def stats():
    return {
        "dimension": DIMENSION,
        "total_items": len(items),
        "vectors_count": vectors_count,
        "by_type": dict(Counter(item["item_type"] for item in items)),
    }


class VectorStore:
    """Compatibility wrapper around the global FAISS store."""

    def __init__(self, dim: int = DIMENSION):
        self.dim = dim

    def reset(self):
        reset_index()

    def add(self, vectors, ids):
        batch = []
        for item_id, vector in zip(ids, _vectors_to_lists(vectors)):
            batch.append({"item_id": item_id, "vector": vector, "item_type": "generic", "payload": {}})
        add_items(batch)

    def search(self, vector, k: int = 5):
        return [item["item_id"] for item in search_index(vector, k=k)]
