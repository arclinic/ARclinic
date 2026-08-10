import numpy as np
from typing import List, Dict


def calculate_engagement(posts: List[Dict]) -> List[Dict]:
    """
    Вычисляет engagement score и ER% для каждого поста.
    Формулы взвешены по платформам.
    """
    for post in posts:
        platform = post.get("platform", "")

        if platform == "instagram":
            post["engagement_raw"] = (
                post.get("likes", 0)
                + post.get("comments", 0) * 3
                + post.get("views", 0) * 0.02
            )
            post["er_type"] = "likes+comments"

        elif platform == "tiktok":
            post["engagement_raw"] = (
                post.get("likes", 0)
                + post.get("comments", 0) * 3
                + post.get("shares", 0) * 2
                + post.get("views", 0) * 0.01
            )
            post["er_type"] = "likes+comments+shares"

        elif platform == "vkontakte":
            post["engagement_raw"] = (
                post.get("likes", 0)
                + post.get("comments", 0) * 3
                + post.get("reposts", 0) * 2
                + post.get("views", 0) * 0.005
            )
            post["er_type"] = "likes+comments+reposts"

        elif platform == "youtube":
            post["engagement_raw"] = (
                post.get("likes", 0)
                + post.get("comments", 0) * 3
                + post.get("views", 0) * 0.005
            )
            post["er_type"] = "likes+comments"

        elif platform == "telegram":
            post["engagement_raw"] = (
                post.get("views", 0) * 0.01
                + post.get("reactions", 0) * 1
                + post.get("comments", 0) * 3
                + post.get("forwards", 0) * 2
            )
            post["er_type"] = "views+reactions"

        else:
            post["engagement_raw"] = post.get("likes", 0) + post.get("comments", 0)
            post["er_type"] = "likes+comments"

        post["engagement_score"] = round(post.get("engagement_raw", 0), 1)

    return posts


def calculate_account_summary(posts: List[Dict], platform: str, follower_count: int = 0) -> Dict:
    """
    Агрегирует метрики по аккаунту за период.
    Возвращает словарь с суммарными и средними метриками.
    """
    if not posts:
        return {
            "total_posts": 0,
            "total_likes": 0,
            "total_comments": 0,
            "total_views": 0,
            "avg_likes": 0,
            "avg_comments": 0,
            "avg_views": 0,
            "avg_engagement_score": 0,
            "total_engagement": 0,
            "er_percent": 0,
            "top_posts": [],
        }

    total_likes = sum(p.get("likes", 0) for p in posts)
    total_comments = sum(p.get("comments", 0) for p in posts)
    total_views = sum(p.get("views", 0) for p in posts)
    total_engagement = sum(p.get("engagement_score", 0) for p in posts)
    n = len(posts)

    avg_likes = round(total_likes / n, 1)
    avg_comments = round(total_comments / n, 1)
    avg_views = round(total_views / n, 1)
    avg_engagement = round(total_engagement / n, 1)

    er_percent = 0
    if follower_count > 0:
        er_percent = round((avg_likes + avg_comments) / follower_count * 100, 2)
    elif avg_views > 0:
        er_percent = round((total_likes + total_comments) / total_views * 100, 2)

    sorted_posts = sorted(posts, key=lambda p: p.get("engagement_score", 0), reverse=True)
    top_posts = sorted_posts[:10]

    return {
        "total_posts": n,
        "total_likes": total_likes,
        "total_comments": total_comments,
        "total_views": total_views,
        "avg_likes": avg_likes,
        "avg_comments": avg_comments,
        "avg_views": avg_views,
        "avg_engagement_score": avg_engagement,
        "total_engagement": total_engagement,
        "er_percent": er_percent,
        "top_posts": top_posts,
    }


def identify_outliers(posts: List[Dict], threshold: float = 2.0) -> List[Dict]:
    if not posts or len(posts) < 3:
        return []

    scores = [p.get("engagement_score", 0) for p in posts]
    mean = np.mean(scores)
    std = np.std(scores)

    if std == 0:
        return []

    cutoff = mean + threshold * std
    outliers = [p for p in posts if p.get("engagement_score", 0) > cutoff]
    outliers.sort(key=lambda x: x.get("engagement_score", 0), reverse=True)

    return outliers[:10]


def compare_periods(current: Dict, previous: Dict) -> Dict:
    """Сравнивает метрики текущего и предыдущего периодов."""

    def delta(cur, prev):
        if prev == 0:
            return 100 if cur > 0 else 0
        return round((cur - prev) / prev * 100, 1)

    return {
        "posts_delta": delta(current.get("total_posts", 0), previous.get("total_posts", 0)),
        "likes_delta": delta(current.get("total_likes", 0), previous.get("total_likes", 0)),
        "comments_delta": delta(current.get("total_comments", 0), previous.get("total_comments", 0)),
        "views_delta": delta(current.get("total_views", 0), previous.get("total_views", 0)),
        "engagement_delta": delta(
            current.get("avg_engagement_score", 0), previous.get("avg_engagement_score", 0)
        ),
        "er_delta": delta(current.get("er_percent", 0), previous.get("er_percent", 0)),
    }
