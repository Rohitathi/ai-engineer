from connect_ai.vector.embeddings import embed_text
from connect_ai.vector.faiss_store import add_items


def index_documents(docs):
    batch = []
    for doc in docs:
        text = (doc.get("text") or "").strip()
        if not text:
            continue
        batch.append(
            {
                "item_id": doc.get("id"),
                "vector": embed_text(text),
                "item_type": "doc",
                "payload": {"title": doc.get("title", ""), "text": text[:1000]},
            }
        )

    add_items(batch)
    return {"indexed_docs": len(batch)}
