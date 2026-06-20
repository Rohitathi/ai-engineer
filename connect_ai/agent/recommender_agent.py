from connect_ai.recommender.recommend_posts import recommend_posts
from connect_ai.recommender.recommend_users import recommend_users


class RecommenderAgent:
    """Suggests relevant users and posts."""

    def run(self, user_input: str, memory=None):
        results = {"users": recommend_users(top_k=5), "posts": recommend_posts(top_k=5)}
        if memory is not None:
            memory.add("recommender", str(results), meta={"query": user_input})
        return results
