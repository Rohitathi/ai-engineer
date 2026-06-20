from flask_login import current_user

from connect_ai.indexing.index_builder import index_posts
from connect_ai.vector.embeddings import embed_text
from connect_ai.vector.faiss_store import search_index, stats
from models import Post


def _current_user_interest_text():
    posts = Post.query.filter_by(user_id=current_user.id).order_by(Post.created_at.desc()).all()
    return " ".join(f"{post.category or ''} {post.message or ''}".strip() for post in posts).strip()


def recommend_posts(top_k=5):
    if not current_user.is_authenticated:
        return []

    interests = _current_user_interest_text()
    if not interests.strip():
        return []

    if not stats()["by_type"].get("post"):
        index_posts()

    vector = embed_text(interests)
    return search_index(vector, k=top_k, item_type="post")
