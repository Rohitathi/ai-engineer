from connect_ai.agent.memory import Memory
from connect_ai.agent.memory_agent import MemoryAgent
from connect_ai.agent.planner_agent import PlannerAgent
from connect_ai.agent.rag_agent import RAGAgent
from connect_ai.agent.recommender_agent import RecommenderAgent
from connect_ai.agent.router_agent import RouterAgent
from connect_ai.agent.tool_agent import ToolAgent
from connect_ai.genai.llm_client import LLMClient
from connect_ai.genai.response_builder import ResponseBuilder
from connect_ai.tools.message_tools import get_chat


class ConnectAgent:
    """Multi-agent controller."""

    def __init__(self):
        self.memory = Memory()
        self.router_agent = RouterAgent()
        self.planner_agent = PlannerAgent()
        self.tool_agent = ToolAgent()
        self.rag_agent = RAGAgent()
        self.recommender_agent = RecommenderAgent()
        self.memory_agent = MemoryAgent()
        self.llm = LLMClient()
        self.response_builder = ResponseBuilder(self.llm)

    def should_handle(self, user_input: str) -> bool:
        route = self.router_agent.route(user_input, self.memory)
        return any(
            [
                route.get("use_tools"),
                route.get("use_rag"),
                route.get("use_recommender"),
                route.get("intent") == "memory",
            ]
        )

    def run(self, user_input: str):
        user_input = (user_input or "").strip()
        if not user_input:
            return {"reply": "Please type something.", "route": {}, "steps": [], "results": []}

        self.memory.add("user", user_input)
        route = self.router_agent.route(user_input, self.memory)
        steps = self.planner_agent.plan(user_input, self.memory, route)
        tool_results = self.tool_agent.execute(steps, self.memory) if route.get("use_tools") else []

        rag_results = []
        if route.get("use_rag"):
            rag_results = self.rag_agent.run(user_input, self.memory)

        recommendations = {}
        if route.get("use_recommender"):
            recommendations = self.recommender_agent.run(user_input, self.memory)

        memory_summary = self.memory_agent.summarize(self.memory)
        reply = self.response_builder.build(
            user_input=user_input,
            route=route,
            tool_results=tool_results,
            rag_results=rag_results,
            recommendations=recommendations,
            memory_summary=memory_summary,
        )

        self.memory.add("assistant", reply, meta={"route": route})
        return {
            "reply": reply,
            "route": route,
            "steps": steps,
            "results": tool_results,
            "rag_results": rag_results,
            "recommendations": recommendations,
            "memory": self.memory.get_recent(10),
        }

    def suggest_reply(self, user_id: int) -> str:
        chat = get_chat(user_id=user_id, limit=10)
        if not chat:
            return "Hey, how are you?"

        last_message = chat[-1]
        if last_message.get("sender") == user_id:
            content = (last_message.get("content") or "").strip()
            if "?" in content:
                return "Yes, that works for me."
            if any(word in content.lower() for word in ("hello", "hi", "hey")):
                return "Hey, good to hear from you."
            return "Sounds good. I am interested to hear more."
        return "Let me know what you think."
