class RouterAgent:
    """Decides which specialist agents should be activated."""

    PLATFORM_KEYWORDS = (
        "nearby",
        "near me",
        "near ",
        "inbox",
        "chat",
        "messages with",
        "conversation",
        "interest",
        "interested in",
        "search posts",
        "find posts",
        "post search",
        "semantic user",
        "semantic post",
        "semantic search",
    )
    KNOWLEDGE_KEYWORDS = ("rag", "knowledge", "docs", "ask docs", "documents")
    RECOMMENDER_KEYWORDS = ("recommend", "suggest", "similar")
    MEMORY_KEYWORDS = ("memory", "history", "recent conversation")

    def route(self, user_input: str, memory=None):
        text = (user_input or "").lower().strip()
        route = {
            "use_tools": False,
            "use_rag": False,
            "use_recommender": False,
            "use_memory": True,
            "intent": "general",
        }

        if any(token in text for token in self.PLATFORM_KEYWORDS):
            route["use_tools"] = True
            route["intent"] = "platform_action"

        if any(token in text for token in self.KNOWLEDGE_KEYWORDS):
            route["use_rag"] = True
            route["intent"] = "knowledge"

        if any(token in text for token in self.RECOMMENDER_KEYWORDS):
            route["use_recommender"] = True
            route["intent"] = "recommendation"

        if any(token in text for token in self.MEMORY_KEYWORDS):
            route["use_tools"] = True
            route["intent"] = "memory"

        return route
