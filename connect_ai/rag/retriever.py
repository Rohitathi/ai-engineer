from connect_ai.agent.retriever import RAGRetriever


def retrieve(query: str, limit: int = 5):
    retriever = RAGRetriever()
    payload = retriever.build_context(query, limit=limit)
    return [item.get("text", "") for item in payload.get("matches", [])]
