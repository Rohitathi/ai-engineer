import re


class PlannerAgent:
    """Converts user input into one or more tool steps."""

    def _extract_number(self, text: str, default: int):
        nums = re.findall(r"\d+", text)
        if nums:
            try:
                return int(nums[0])
            except Exception:
                return default
        return default

    def _extract_after_keyword(self, text: str, keyword: str):
        idx = text.find(keyword)
        if idx == -1:
            return ""
        return text[idx + len(keyword) :].strip()

    def plan(self, user_input, memory=None, route=None):
        text = (user_input or "").lower().strip()
        steps = []

        if "nearby" in text or "near me" in text or "near " in text:
            steps.append(
                {"tool": "find_nearby_users", "args": {"radius_km": self._extract_number(text, 10), "limit": 20}}
            )

        if "inbox" in text:
            steps.append({"tool": "get_inbox", "args": {"limit": 20}})

        if "chat" in text or "messages with" in text or "conversation" in text:
            nums = re.findall(r"user\s*(\d+)", text)
            steps.append({"tool": "get_chat", "args": {"user_id": int(nums[0]) if nums else None, "limit": 50}})

        if "interest" in text or "interested in" in text or "users interested in" in text:
            interest = text
            if "users interested in" in text:
                interest = self._extract_after_keyword(text, "users interested in")
            elif "interested in" in text:
                interest = self._extract_after_keyword(text, "interested in")
            else:
                interest = self._extract_after_keyword(text, "interest")
            steps.append({"tool": "find_users_by_interest", "args": {"interest": interest.strip()}})

        if "search posts" in text or "find posts" in text or "post search" in text:
            query = text
            if "search posts" in text:
                query = self._extract_after_keyword(text, "search posts")
            elif "find posts" in text:
                query = self._extract_after_keyword(text, "find posts")
            else:
                query = self._extract_after_keyword(text, "post search")
            steps.append({"tool": "search_posts_by_keyword", "args": {"query": query.strip()}})

        if "semantic user" in text or "semantic search user" in text or "semantic users" in text:
            query = text
            if "semantic search user" in text:
                query = self._extract_after_keyword(text, "semantic search user")
            elif "semantic users" in text:
                query = self._extract_after_keyword(text, "semantic users")
            else:
                query = self._extract_after_keyword(text, "semantic user")
            steps.append({"tool": "semantic_user_search", "args": {"query": query.strip(), "top_k": 5}})

        if "semantic post" in text or "semantic search" in text:
            query = text
            if "semantic post" in text:
                query = self._extract_after_keyword(text, "semantic post")
            else:
                query = self._extract_after_keyword(text, "semantic search")
            steps.append({"tool": "semantic_post_search", "args": {"query": query.strip(), "top_k": 5}})

        if "memory" in text or "history" in text:
            steps.append({"tool": "get_memory", "args": {"limit": 10}})

        return steps
