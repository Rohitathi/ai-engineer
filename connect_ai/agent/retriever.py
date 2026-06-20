from typing import Dict, List

from .vector_store import VectorStore


class RAGRetriever:
    def __init__(self):
        self.store = VectorStore()

    def build_context(self, query: str, limit: int = 5) -> Dict[str, List[dict]]:
        indexed = self.store.index_all()
        matches = self.store.search(query, limit=limit)
        return {"indexed": indexed, "matches": matches}

    def answer(self, query: str, limit: int = 5) -> Dict[str, object]:
        payload = self.build_context(query, limit=limit)
        matches = payload["matches"]
        if not matches:
            return {
                "answer": "I could not find matching knowledge yet. Try creating posts or messages first, then ask again.",
                "sources": [],
                "indexed": payload["indexed"],
            }

        lines = []
        for item in matches[:limit]:
            text = (item.get("text") or "").strip().replace("\n", " ")
            if len(text) > 120:
                text = text[:117] + "..."
            lines.append(f"[{item['source_type']} #{item['source_id']}] {text}")

        answer = "Based on your Connect knowledge base, here are the closest matches: " + " | ".join(lines)
        return {"answer": answer, "sources": matches, "indexed": payload["indexed"]}
