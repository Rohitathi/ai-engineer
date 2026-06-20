from typing import List, Dict, Any

from flask_login import current_user

from db import db
from models import Message, Post, User
from .automation import AutomationEngine
from .recommendations import RecommendationEngine
from .retriever import RAGRetriever
from .vector_store import VectorStore
from connect_ai.vector.embeddings import embed_texts, embed_text
from connect_ai.vector.faiss_store import VectorStore as UserVectorStore


from .geo import haversine_km


user_vector_store = UserVectorStore()


def _haversine_km(lat1, lon1, lat2, lon2) -> float:
    return haversine_km(lat1, lon1, lat2, lon2)



def find_nearby_users(radius_km: float = 10.0, limit: int = 20) -> List[Dict[str, Any]]:
    if current_user.lat is None or current_user.lon is None:
        return [{"error": "Your lat/lon is missing. Save location first."}]

    me_lat = float(current_user.lat)
    me_lon = float(current_user.lon)
    users = User.query.filter(User.id != current_user.id).all()

    out = []
    for user in users:
        if user.lat is None or user.lon is None:
            continue
        distance = _haversine_km(me_lat, me_lon, float(user.lat), float(user.lon))
        if distance <= radius_km:
            out.append({"id": user.id, "username": user.username, "distance_km": round(distance, 2)})

    out.sort(key=lambda item: item["distance_km"])
    return out[:limit]


def send_message(receiver_id: int, content: str) -> str:
    msg = Message(sender_id=current_user.id, receiver_id=receiver_id, content=content)
    db.session.add(msg)
    db.session.commit()
    return "Message sent."


def get_chat(other_user_id: int, limit: int = 50) -> List[Dict[str, Any]]:
    chat = (
        Message.query.filter(
            ((Message.sender_id == current_user.id) & (Message.receiver_id == other_user_id))
            | ((Message.sender_id == other_user_id) & (Message.receiver_id == current_user.id))
        )
        .order_by(Message.created_at.asc())
        .all()
    )
    chat = chat[-limit:]
    return [
        {
            "sender_id": item.sender_id,
            "receiver_id": item.receiver_id,
            "content": item.content,
            "created_at": str(item.created_at),
        }
        for item in chat
    ]


def get_inbox(limit: int = 30) -> List[Dict[str, Any]]:
    msgs = (
        Message.query.filter((Message.sender_id == current_user.id) | (Message.receiver_id == current_user.id))
        .order_by(Message.created_at.desc())
        .limit(limit)
        .all()
    )
    return [
        {
            "id": item.id,
            "sender_id": item.sender_id,
            "receiver_id": item.receiver_id,
            "content": item.content[:150],
        }
        for item in msgs
    ]


def find_users_by_interest(keyword: str, radius_km: float = 10.0):
    if current_user.lat is None or current_user.lon is None:
        return [{"error": "Location missing."}]

    me_lat = float(current_user.lat)
    me_lon = float(current_user.lon)
    candidate_users = []

    for user in User.query.filter(User.id != current_user.id).all():
        if user.lat is None or user.lon is None:
            continue
        distance = _haversine_km(me_lat, me_lon, float(user.lat), float(user.lon))
        if distance > radius_km:
            continue

        posts = Post.query.filter_by(user_id=user.id).order_by(Post.created_at.desc()).all()
        profile_text = " ".join(
            f"{post.category or ''} {post.message or ''}".strip() for post in posts
        ).strip()
        if not profile_text:
            continue

        candidate_users.append(
            {
                "id": user.id,
                "username": user.username,
                "distance_km": round(distance, 2),
                "profile_text": profile_text,
            }
        )

    if not candidate_users:
        return []

    user_vector_store.reset()
    user_vector_store.add(
        embed_texts([user["profile_text"] for user in candidate_users]),
        [user["id"] for user in candidate_users],
    )

    ranked_ids = user_vector_store.search(embed_text(keyword), k=min(20, len(candidate_users)))
    users_by_id = {user["id"]: user for user in candidate_users}
    return [
        {
            "id": users_by_id[user_id]["id"],
            "username": users_by_id[user_id]["username"],
            "distance_km": users_by_id[user_id]["distance_km"],
            "interest": keyword,
        }
        for user_id in ranked_ids
        if user_id in users_by_id
    ]


def build_knowledge_index() -> Dict[str, int]:
    store = VectorStore()
    return store.index_all()


def semantic_search(query: str, limit: int = 5) -> List[Dict[str, Any]]:
    store = VectorStore()
    store.index_all()
    return store.search(query, limit=limit)


def recommend_users(limit: int = 5) -> List[Dict[str, Any]]:
    engine = RecommendationEngine()
    return engine.recommend_users(limit=limit)


def rag_answer(query: str, limit: int = 5) -> Dict[str, Any]:
    retriever = RAGRetriever()
    return retriever.answer(query, limit=limit)


def run_automation() -> Dict[str, Any]:
    engine = AutomationEngine()
    return engine.run()
