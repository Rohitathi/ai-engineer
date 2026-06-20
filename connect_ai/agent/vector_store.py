import json
from typing import Any, Dict, List, Optional

from flask_login import current_user

from db import db
from models import KnowledgeChunk, Message, Post
from .embeddings import cosine_similarity, embed_text


class VectorStore:
    def upsert_chunk(
        self,
        *,
        source_type: str,
        source_id: int,
        text: str,
        user_id: Optional[int] = None,
        meta: Optional[Dict[str, Any]] = None,
    ) -> KnowledgeChunk:
        chunk = KnowledgeChunk.query.filter_by(source_type=source_type, source_id=source_id).first()
        embedding = embed_text(text)
        embedding_json = json.dumps(embedding)
        meta_json = json.dumps(meta or {})

        if chunk is None:
            chunk = KnowledgeChunk(
                source_type=source_type,
                source_id=source_id,
                user_id=user_id,
                text=text,
                embedding_json=embedding_json,
                meta_json=meta_json,
            )
            db.session.add(chunk)
        else:
            chunk.user_id = user_id
            chunk.text = text
            chunk.embedding_json = embedding_json
            chunk.meta_json = meta_json

        db.session.commit()
        return chunk

    def index_posts(self) -> int:
        count = 0
        for post in Post.query.all():
            text = f"{post.category or ''} {post.message or ''}".strip()
            self.upsert_chunk(
                source_type="post",
                source_id=post.id,
                user_id=post.user_id,
                text=text,
                meta={"category": post.category, "created_at": str(post.created_at)},
            )
            count += 1
        return count

    def index_messages(self, limit_per_user: int = 100) -> int:
        count = 0
        if not current_user.is_authenticated:
            return count

        messages = (
            Message.query.filter(
                (Message.sender_id == current_user.id) | (Message.receiver_id == current_user.id)
            )
            .order_by(Message.created_at.desc())
            .limit(limit_per_user)
            .all()
        )
        for message in messages:
            text = message.content or ""
            self.upsert_chunk(
                source_type="message",
                source_id=message.id,
                user_id=message.sender_id,
                text=text,
                meta={
                    "sender_id": message.sender_id,
                    "receiver_id": message.receiver_id,
                    "created_at": str(message.created_at),
                },
            )
            count += 1
        return count

    def index_all(self) -> Dict[str, int]:
        post_count = self.index_posts()
        message_count = self.index_messages()
        return {"posts": post_count, "messages": message_count, "total": post_count + message_count}

    def search(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        query_vector = embed_text(query)
        results: List[Dict[str, Any]] = []

        for chunk in KnowledgeChunk.query.order_by(KnowledgeChunk.created_at.desc()).all():
            try:
                vector = json.loads(chunk.embedding_json or "[]")
            except Exception:
                vector = []
            score = cosine_similarity(query_vector, vector)
            if score <= 0:
                continue
            try:
                meta = json.loads(chunk.meta_json or "{}")
            except Exception:
                meta = {}
            results.append(
                {
                    "chunk_id": chunk.id,
                    "source_type": chunk.source_type,
                    "source_id": chunk.source_id,
                    "user_id": chunk.user_id,
                    "text": chunk.text,
                    "score": round(float(score), 4),
                    "meta": meta,
                }
            )

        results.sort(key=lambda item: item["score"], reverse=True)
        return results[:limit]
