from connect_ai.genai.prompt_builder import build_system_prompt, build_user_prompt


class ResponseBuilder:
    """Builds the final response using an LLM if available, otherwise structured fallback."""

    def __init__(self, llm_client):
        self.llm = llm_client

    def _fallback(self, tool_results, rag_results, recommendations):
        parts = []
        if tool_results:
            parts.append("Tool Results:")
            for result in tool_results:
                parts.append(f"- {result.get('tool')}: {result.get('data')}")
        if rag_results:
            parts.append("")
            parts.append("Knowledge Results:")
            for item in rag_results:
                parts.append(f"- {item}")
        if recommendations:
            parts.append("")
            parts.append("Recommendations:")
            parts.append(str(recommendations))
        return "\n".join(parts) if parts else "I could not find anything useful."

    def build(self, user_input, route, tool_results, rag_results, recommendations, memory_summary):
        messages = [
            {"role": "system", "content": build_system_prompt()},
            {
                "role": "user",
                "content": build_user_prompt(
                    user_input=user_input,
                    route=route,
                    tool_results=tool_results,
                    rag_results=rag_results,
                    recommendations=recommendations,
                    memory_summary=memory_summary,
                ),
            },
        ]
        reply = self.llm.chat(messages, temperature=0.2)
        return reply or self._fallback(tool_results, rag_results, recommendations)
