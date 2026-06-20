def build_system_prompt():
    return (
        "You are Connect AI, a helpful multi-agent assistant inside a social platform. "
        "You help with nearby users, inbox, chats, interests, post search, semantic search, "
        "RAG document answers, and recommendations. "
        "Be concise, helpful, and human-readable. "
        "When tool results exist, summarize them clearly. "
        "If there are no results, say so directly."
    )


def build_user_prompt(user_input, route, tool_results, rag_results, recommendations, memory_summary):
    return f"""
USER INPUT:
{user_input}

ROUTE:
{route}

MEMORY SUMMARY:
{memory_summary}

TOOL RESULTS:
{tool_results}

RAG RESULTS:
{rag_results}

RECOMMENDATIONS:
{recommendations}

Please produce a clean, user-friendly reply.
""".strip()
