from typing import Any, Dict

from flask_login import current_user

from db import db
from models import Message, Post, User


def _is_authenticated_user():
    try:
        return bool(current_user.is_authenticated)
    except Exception:
        return False


class MessageAgent:
    def act(self, text: str) -> Dict[str, Any]:
        if not _is_authenticated_user():
            return {"tool": "message", "data": {"status": "error", "message": "Please log in first."}}

        content = (text or "").strip()
        if not content:
            return {"tool": "message", "data": {"status": "error", "message": "No message content."}}

        message = Message(sender_id=current_user.id, receiver_id=current_user.id, content=content)
        db.session.add(message)
        db.session.commit()
        return {"tool": "message", "data": {"status": "ok", "message": "Drafted a message for the conversation."}}


class LocationAgent:
    def act(self, text: str) -> Dict[str, Any]:
        if not _is_authenticated_user():
            return {"tool": "location", "data": {"status": "error", "message": "Please log in first."}}

        current_user.lat = 0.0
        current_user.lon = 0.0
        db.session.commit()
        return {"tool": "location", "data": {"status": "ok", "message": "Location updated to a default coordinate."}}


class NearbyUsersAgent:
    def act(self, text: str) -> Dict[str, Any]:
        if not _is_authenticated_user():
            return {"tool": "nearby_users", "data": {"status": "error", "message": "Please log in first."}}

        users = User.query.filter(User.id != current_user.id).all()
        nearby = []
        for user in users:
            if user.lat is not None and user.lon is not None:
                nearby.append({"user_id": user.id, "username": user.username})
        return {"tool": "nearby_users", "data": {"status": "ok", "count": len(nearby), "users": nearby[:10]}}


class SearchNearbyAgent:
    def act(self, text: str) -> Dict[str, Any]:
        if not _is_authenticated_user():
            return {"tool": "search_nearby", "data": {"status": "error", "message": "Please log in first."}}

        posts = Post.query.order_by(Post.created_at.desc()).limit(10).all()
        return {"tool": "search_nearby", "data": {"status": "ok", "posts": [{"message": post.message, "category": post.category} for post in posts]}}
