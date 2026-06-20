from flask_login import current_user

from connect_ai.indexing.index_builder import index_posts, index_users
from connect_ai.vector.embeddings import embed_text
from connect_ai.vector.faiss_store import search_index, stats
from models import Post, User


def _user_profile_text(user):
    posts = Post.query.filter_by(user_id=user.id).order_by(Post.created_at.desc()).all()
    return " ".join(f"{post.category or ''} {post.message or ''}".strip() for post in posts).strip()


def _ensure_index(item_type=None):
    snapshot = stats()
    if snapshot["total_items"] == 0:
        index_users()
        index_posts()
        return
    if item_type == "user" and not snapshot["by_type"].get("user"):
        index_users()
    if item_type == "post" and not snapshot["by_type"].get("post"):
        index_posts()


def find_users_by_interest(interest):
    interest = (interest or "").strip().lower()
    if not interest:
        return []

    results = []
    for user in User.query.all():
        if current_user.is_authenticated and user.id == current_user.id:
            continue
        profile_text = _user_profile_text(user)
        if interest not in profile_text.lower():
            continue
        results.append({"id": user.id, "name": getattr(user, "username", ""), "interest": profile_text[:200]})
    return results


def search_posts_by_keyword(query):
    query = (query or "").strip().lower()
    if not query:
        return []

    posts = Post.query.filter(Post.message.ilike(f"%{query}%") | Post.category.ilike(f"%{query}%")).all()
    return [
        {
            "post_id": post.id,
            "user_id": post.user_id,
            "content": post.message,
            "category": post.category,
        }
        for post in posts
    ]


def semantic_user_search(query, top_k=5):
    query = (query or "").strip()
    if not query:
        return []

    _ensure_index(item_type="user")
    vector = embed_text(query)
    return search_index(vector, k=top_k, item_type="user")


def semantic_post_search(query, top_k=5):
    query = (query or "").strip()
    if not query:
        return []

    _ensure_index(item_type="post")
    vector = embed_text(query)
    return search_index(vector, k=top_k, item_type="post")
