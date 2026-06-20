from flask_login import current_user

from connect_ai.indexing.index_builder import index_users
from connect_ai.vector.embeddings import embed_text
from connect_ai.vector.faiss_store import search_index, stats
from models import Post


def _current_user_interest_text():
    posts = Post.query.filter_by(user_id=current_user.id).order_by(Post.created_at.desc()).all()
    return " ".join(f"{post.category or ''} {post.message or ''}".strip() for post in posts).strip()


def recommend_users(top_k=5):
    if not current_user.is_authenticated:
        return []

    interests = _current_user_interest_text()
    if not interests.strip():
        return []

    if not stats()["by_type"].get("user"):
        index_users()

    results = search_index(embed_text(interests), k=top_k + 3, item_type="user")
    filtered = []
    for item in results:
        if item.get("item_id") == current_user.id:
            continue
        filtered.append(item)
        if len(filtered) >= top_k:
            break
    return filtered
