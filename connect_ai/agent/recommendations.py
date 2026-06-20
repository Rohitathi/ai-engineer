from typing import Any, Dict, List

from flask_login import current_user

from models import Post, User
from .embeddings import cosine_similarity, embed_text, tokenize
from .geo import haversine_km


class RecommendationEngine:
    def recommend_users(self, limit: int = 5) -> List[Dict[str, Any]]:
        if not current_user.is_authenticated:
            return []

        my_posts = Post.query.filter_by(user_id=current_user.id).all()
        my_profile_text = " ".join(
            f"{post.category or ''} {post.message or ''}".strip() for post in my_posts
        ).strip() or current_user.username
        my_vector = embed_text(my_profile_text)
        my_tokens = set(tokenize(my_profile_text))

        out: List[Dict[str, Any]] = []
        for user in User.query.filter(User.id != current_user.id).all():
            their_posts = Post.query.filter_by(user_id=user.id).all()
            their_text = " ".join(
                f"{post.category or ''} {post.message or ''}".strip() for post in their_posts
            ).strip() or user.username
            their_vector = embed_text(their_text)
            similarity = cosine_similarity(my_vector, their_vector)
            overlap = len(my_tokens.intersection(set(tokenize(their_text))))
            distance_score = 0.0
            distance_km = None
            if (
                current_user.lat is not None
                and current_user.lon is not None
                and user.lat is not None
                and user.lon is not None
            ):
                distance_km = haversine_km(
                    float(current_user.lat), float(current_user.lon), float(user.lat), float(user.lon)
                )
                distance_score = max(0.0, 1.0 - min(distance_km, 50.0) / 50.0)

            final_score = round((similarity * 0.6) + (min(overlap, 5) * 0.08) + (distance_score * 0.2), 4)
            out.append(
                {
                    "user_id": user.id,
                    "username": user.username,
                    "score": final_score,
                    "similarity": round(similarity, 4),
                    "shared_terms": sorted(list(my_tokens.intersection(set(tokenize(their_text)))))[:8],
                    "distance_km": round(distance_km, 2) if distance_km is not None else None,
                }
            )

        out.sort(key=lambda item: item["score"], reverse=True)
        return out[:limit]
