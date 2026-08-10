from typing import List, Dict
from collections import Counter
from datetime import datetime
import re


def analyze_video_posts(posts: List[Dict]) -> Dict:
    video_posts = [p for p in posts if p.get("views", 0) > 0 or p.get("is_video", False)]

    if not video_posts:
        return {"total_videos": 0, "insights": "Нет видео-постов для анализа"}

    lengths = []
    hooks = []
    has_text = 0
    has_face = 0
    total_views = 0
    total_likes = 0

    for p in video_posts:
        caption = (p.get("caption", "") or "").lower()
        views = p.get("views", 0)
        likes = p.get("likes", 0)

        total_views += views
        total_likes += likes

        caption_len = len(caption)
        if caption_len > 200:
            has_text += 1

        if any(w in caption for w in ["#врач", "#доктор", "прием", "консультация", "лицо", "себе", "показываю"]):
            has_face += 1

        lines = [l.strip() for l in caption.split("\n") if l.strip()]
        if lines:
            first_line = lines[0]
            if len(first_line) < 120:
                hooks.append(first_line[:80])
            lengths.append(len(caption))

    n = len(video_posts)

    platform_insights = {}
    platforms = set(p.get("platform", "") for p in video_posts)
    for plat in platforms:
        plat_posts = [p for p in video_posts if p.get("platform") == plat]
        if not plat_posts:
            continue
        avg_views = sum(p.get("views", 0) for p in plat_posts) // len(plat_posts)
        avg_likes = sum(p.get("likes", 0) for p in plat_posts) // len(plat_posts)
        engagement_ratio = round(avg_likes / avg_views * 100, 2) if avg_views > 0 else 0
        platform_insights[plat] = {
            "видео_всего": len(plat_posts),
            "средние_просмотры": avg_views,
            "средние_лайки": avg_likes,
            "engagement_rate": engagement_ratio,
        }

    top_hooks = Counter(hooks).most_common(5)

    return {
        "total_videos": n,
        "platform_breakdown": platform_insights,
        "avg_caption_length": sum(lengths) // n if lengths else 0,
        "format_insights": {
            "has_text_overlay_pct": round(has_text / n * 100) if n else 0,
            "has_face_pct": round(has_face / n * 100) if n else 0,
            "recommendation": "",
        },
        "top_hooks": [{"текст": h[0], "частота": h[1]} for h in top_hooks],
        "recommendations": [],
    }


def generate_video_recommendations(analysis: Dict, platform: str = "instagram") -> List[str]:
    recs = []

    has_face = analysis.get("format_insights", {}).get("has_face_pct", 0)
    if has_face < 50:
        recs.append(f"[HIGH] Только {has_face}% Reels содержат лицо врача. Увеличить до 80%+ — личный бренд строится на лицах.")

    plat = analysis.get("platform_breakdown", {}).get(platform, {})
    er = plat.get("engagement_rate", 0)
    if er > 0 and er < 5:
        recs.append(f"[MED] ER видео = {er}%. Добавить субтитры и текст на экране для удержания внимания.")
    elif er > 10:
        recs.append(f"[OK] ER видео = {er}% — отличный показатель. Масштабировать формат.")

    top_hooks = analysis.get("top_hooks", [])
    if top_hooks:
        recs.append(f"[TIP] Популярные хуки: {', '.join(h['текст'][:40] for h in top_hooks[:3])}")

    recs.append("[TIP] Оптимальная длина Reels: 15-25 сек (до/после), 30-45 сек (образовательные). Длиннее 60 сек — просадка.")
    recs.append("[TIP] Первые 3 секунды решают всё: крупный план, движение, вопрос.")

    return recs
