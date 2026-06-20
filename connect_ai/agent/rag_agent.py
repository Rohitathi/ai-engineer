from connect_ai.rag.rag_engine import rag_search


class RAGAgent:
    """Specialist retrieval agent for knowledge and document queries."""

    def run(self, user_input: str, memory=None):
        query = (user_input or "").strip()
        if not query:
            return []

        results = rag_search(query=query, top_k=5)
        if memory is not None:
            memory.add("rag", str(results), meta={"query": query})
        return results
