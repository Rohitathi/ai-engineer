from typing import Dict, List

from flask_login import current_user

from db import db
from models import AgentMemory, AIAutomationTask
from .recommendations import RecommendationEngine


class AutomationEngine:
    def ensure_defaults(self) -> int:
        if not current_user.is_authenticated:
            return 0

        defaults = [
            ("daily_recommendations", "Generate fresh user recommendations"),
            ("knowledge_refresh", "Refresh vector knowledge index"),
        ]
        created = 0
        for task_type, title in defaults:
            exists = AIAutomationTask.query.filter_by(user_id=current_user.id, task_type=task_type).first()
            if exists is None:
                db.session.add(
                    AIAutomationTask(
                        user_id=current_user.id,
                        task_type=task_type,
                        title=title,
                        is_enabled=True,
                    )
                )
                created += 1
        if created:
            db.session.commit()
        return created

    def run(self) -> Dict[str, object]:
        if not current_user.is_authenticated:
            return {"error": "Please log in first."}

        self.ensure_defaults()
        tasks = AIAutomationTask.query.filter_by(user_id=current_user.id, is_enabled=True).all()
        outputs: List[str] = []
        recommender = RecommendationEngine()

        for task in tasks:
            if task.task_type == "daily_recommendations":
                recs = recommender.recommend_users(limit=3)
                if recs:
                    usernames = ", ".join(item["username"] for item in recs)
                    message = f"Automation suggested these users for you: {usernames}."
                else:
                    message = "Automation could not find user recommendations yet."
                outputs.append(message)
                db.session.add(AgentMemory(user_id=current_user.id, role="automation", content=message))
            elif task.task_type == "knowledge_refresh":
                message = "Automation marked the knowledge base for refresh on the next RAG query."
                outputs.append(message)
                db.session.add(AgentMemory(user_id=current_user.id, role="automation", content=message))

            task.last_run_at = db.func.now()

        db.session.commit()
        return {"status": "ok", "ran": len(tasks), "outputs": outputs}
