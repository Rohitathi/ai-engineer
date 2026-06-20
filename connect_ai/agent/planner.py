import re


STOPWORDS = {
    "find",
    "show",
    "people",
    "person",
    "users",
    "user",
    "friends",
    "matches",
    "near",
    "nearby",
    "me",
    "and",
    "suggest",
    "who",
    "i",
    "should",
    "message",
    "for",
    "to",
    "my",
    "with",
    "the",
    "a",
    "an",
}


def _extract_interest_keyword(text: str) -> str | None:
    lowered = (text or "").lower().strip()
    if not lowered:
        return None

    phrase_patterns = (
        r"interested in ([a-z0-9\s-]+?)(?: near| and|$)",
        r"about ([a-z0-9\s-]+?)(?: near| and|$)",
        r"for ([a-z0-9\s-]+?)(?: people| users| friends| near| and|$)",
        r"find ([a-z0-9\s-]+?)(?: people| users| friends| near| and|$)",
    )
    for pattern in phrase_patterns:
        match = re.search(pattern, lowered)
        if match:
            keyword = match.group(1).strip(" -")
            if keyword:
                return keyword

    tokens = re.findall(r"[a-z0-9]+", lowered)
    candidates = [token for token in tokens if token not in STOPWORDS]
    return candidates[0] if candidates else None


def plan(text, user_ctx=None):
    lowered = (text or "").lower().strip()
    steps = []

    if not lowered:
        return steps

    keyword = _extract_interest_keyword(text)
    wants_nearby = any(word in lowered for word in ("near", "nearby"))
    wants_recommendation = any(
        phrase in lowered
        for phrase in ("recommend", "suggest users", "best matches", "match me", "suggest who", "who should i message")
    )

    if "inbox" in lowered:
        steps.append({"tool": "get_inbox", "args": {}})
        return steps

    if wants_nearby and keyword:
        steps.append({"tool": "find_users_by_interest", "args": {"keyword": keyword, "radius_km": 10}})
        if wants_recommendation:
            steps.append({"tool": "recommend_users", "args": {"limit": 5}})
        return steps

    if wants_nearby:
        steps.append({"tool": "find_nearby_users", "args": {"radius_km": 10}})
        if wants_recommendation:
            steps.append({"tool": "recommend_users", "args": {"limit": 5}})
        return steps

    if keyword:
        steps.append({"tool": "find_users_by_interest", "args": {"keyword": keyword, "radius_km": 10}})
        if wants_recommendation:
            steps.append({"tool": "recommend_users", "args": {"limit": 5}})
        return steps

    if any(word in lowered for word in ("vector", "embedding", "index knowledge", "build index")):
        steps.append({"tool": "build_knowledge_index", "args": {}})
        return steps

    if wants_recommendation:
        steps.append({"tool": "recommend_users", "args": {"limit": 5}})
        return steps

    if any(word in lowered for word in ("rag", "knowledge", "what do we know", "search semantically", "semantic")):
        steps.append({"tool": "rag_answer", "args": {"query": text, "limit": 5}})
        return steps

    if any(word in lowered for word in ("automate", "automation", "run digest", "run workflow")):
        steps.append({"tool": "run_automation", "args": {}})
        return steps

    return steps
