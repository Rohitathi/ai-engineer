from connect_ai.indexing.doc_indexer import index_documents
from connect_ai.vector.embeddings import embed_text
from connect_ai.vector.faiss_store import add_items
from models import Post, User


def index_users():
    batch = []
    for user in User.query.all():
        posts = Post.query.filter_by(user_id=user.id).order_by(Post.created_at.desc()).all()
        text = " ".join(
            [getattr(user, "username", "")] + [f"{post.category or ''} {post.message or ''}".strip() for post in posts]
        ).strip()
        if not text:
            continue
        batch.append(
            {
                "item_id": user.id,
                "vector": embed_text(text),
                "item_type": "user",
                "payload": {"id": user.id, "name": getattr(user, "username", ""), "profile_text": text[:500]},
            }
        )

    add_items(batch)
    return {"indexed_users": len(batch)}


def index_posts():
    batch = []
    for post in Post.query.all():
        text = f"{post.category or ''} {post.message or ''}".strip()
        if not text:
            continue
        batch.append(
            {
                "item_id": post.id,
                "vector": embed_text(text),
                "item_type": "post",
                "payload": {
                    "post_id": post.id,
                    "user_id": post.user_id,
                    "content": post.message,
                    "category": post.category,
                },
            }
        )

    add_items(batch)
    return {"indexed_posts": len(batch)}


def index_all(documents=None):
    summary = {}
    summary.update(index_users())
    summary.update(index_posts())
    if documents:
        summary.update(index_documents(documents))
    return summary
