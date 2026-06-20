from connect_ai.vector.embeddings import embed_text
from connect_ai.vector.faiss_store import search_index


def rag_search(query, top_k=5):
    query = (query or "").strip()
    if not query:
        return []

    vector = embed_text(query)
    return search_index(vector, k=top_k, item_type="doc")
