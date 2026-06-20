from typing import Any, Dict

from .automation import AutomationEngine
from .recommendations import RecommendationEngine
from .retriever import RAGRetriever


class SearchAgent:
    def act(self, text: str) -> Dict[str, Any]:
        retriever = RAGRetriever()
        return {"tool": "rag_answer", "data": retriever.answer(text, limit=5)}


class RecommendationAgent:
    def act(self, text: str) -> Dict[str, Any]:
        engine = RecommendationEngine()
        return {"tool": "recommend_users", "data": engine.recommend_users(limit=5)}


class AutomationAgent:
    def act(self, text: str) -> Dict[str, Any]:
        engine = AutomationEngine()
        return {"tool": "run_automation", "data": engine.run()}


class ManagerAgent:
    def __init__(self):
        self.search_agent = SearchAgent()
        self.recommendation_agent = RecommendationAgent()
        self.automation_agent = AutomationAgent()

    def dispatch(self, text: str) -> Dict[str, Any]:
        lowered = (text or "").lower()
        if any(word in lowered for word in ("recommend", "suggest", "match")):
            return self.recommendation_agent.act(text)
        if any(word in lowered for word in ("automate", "automation", "digest", "refresh")):
            return self.automation_agent.act(text)
        return self.search_agent.act(text)
