from . import tools


def execute(steps, memory, user_id=None):
    results = []

    for step in steps:
        tool = step.get("tool")
        args = step.get("args", {})

        if tool == "find_nearby_users":
            data = tools.find_nearby_users(**args)
        elif tool == "get_inbox":
            data = tools.get_inbox(**args)
        elif tool == "get_chat":
            data = tools.get_chat(**args)
        elif tool == "send_message":
            data = tools.send_message(**args)
        elif tool == "find_users_by_interest":
            data = tools.find_users_by_interest(**args)
        elif tool == "build_knowledge_index":
            data = tools.build_knowledge_index(**args)
        elif tool == "semantic_search":
            data = tools.semantic_search(**args)
        elif tool == "recommend_users":
            data = tools.recommend_users(**args)
        elif tool == "rag_answer":
            data = tools.rag_answer(**args)
        elif tool == "run_automation":
            data = tools.run_automation(**args)
        else:
            data = {"error": "Unknown tool"}

        results.append({"tool": tool, "data": data})
        if user_id is not None:
            memory.add("tool", str(data), meta={"user_id": user_id, "tool": tool})

    return results
