class MemoryAgent:
    """Summarizes recent memory for better GenAI responses."""

    def summarize(self, memory, limit=8):
        logs = memory.get_recent(limit)
        if not logs:
            return "No recent memory."

        lines = []
        for item in logs:
            role = item.get("role", "unknown")
            content = str(item.get("content", ""))
            if len(content) > 200:
                content = content[:200] + "..."
            lines.append(f"{role}: {content}")
        return "\n".join(lines)
