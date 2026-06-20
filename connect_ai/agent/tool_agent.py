from connect_ai.tools import message_tools, search_tools, user_tools


class ToolAgent:
    """Executes tool steps and saves outputs into memory."""

    def execute(self, steps, memory):
        results = []
        for step in steps:
            tool = step.get("tool")
            args = step.get("args", {})
            try:
                if tool == "find_nearby_users":
                    data = user_tools.find_nearby_users(**args)
                elif tool == "get_inbox":
                    data = message_tools.get_inbox(**args)
                elif tool == "get_chat":
                    data = message_tools.get_chat(**args)
                elif tool == "find_users_by_interest":
                    data = search_tools.find_users_by_interest(**args)
                elif tool == "search_posts_by_keyword":
                    data = search_tools.search_posts_by_keyword(**args)
                elif tool == "semantic_user_search":
                    data = search_tools.semantic_user_search(**args)
                elif tool == "semantic_post_search":
                    data = search_tools.semantic_post_search(**args)
                elif tool == "get_memory":
                    data = memory.get_recent(**args)
                else:
                    data = {"error": f"Unknown tool: {tool}"}
            except Exception as exc:
                data = {"error": str(exc)}

            results.append({"tool": tool, "data": data})
            memory.add("tool", str(data), meta={"tool": tool, "args": args})
        return results
