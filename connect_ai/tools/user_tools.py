import math

from flask_login import current_user

from models import Post, User


def haversine(lat1, lon1, lat2, lon2):
    radius = 6371.0
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (
        math.sin(dlat / 2) ** 2
        + math.cos(math.radians(lat1))
        * math.cos(math.radians(lat2))
        * math.sin(dlon / 2) ** 2
    )
    return radius * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))


def _user_interest_text(user):
    posts = Post.query.filter_by(user_id=user.id).order_by(Post.created_at.desc()).limit(5).all()
    return " | ".join(f"{post.category or ''} {post.message or ''}".strip() for post in posts if post.message).strip()


def find_nearby_users(radius_km=10, limit=20):
    if getattr(current_user, "lat", None) is None or getattr(current_user, "lon", None) is None:
        return [{"error": "Current user location is missing."}]

    results = []
    for user in User.query.all():
        if user.id == current_user.id:
            continue
        if getattr(user, "lat", None) is None or getattr(user, "lon", None) is None:
            continue

        distance = haversine(current_user.lat, current_user.lon, user.lat, user.lon)
        if distance <= radius_km:
            results.append(
                {
                    "id": user.id,
                    "name": getattr(user, "username", ""),
                    "distance_km": round(distance, 2),
                    "interests": _user_interest_text(user),
                }
            )

    results.sort(key=lambda item: item["distance_km"])
    return results[:limit]
