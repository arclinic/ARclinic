from collections import Counter
from typing import List, Dict
from datetime import datetime
import re


def extract_hashtags(caption: str) -> List[str]:
    if not caption:
        return []
    return re.findall(r'#[\wа-яё]+', caption.lower())


def analyze_timing(posts: List[Dict]) -> Dict:
    if not posts:
        return {"best_day": None, "best_hour": None}

    day_counts = Counter()
    hour_counts = Counter()
    day_engagement = Counter()
    hour_engagement = Counter()

    for p in posts:
        ts_str = p.get("timestamp", "")
        if not ts_str:
            continue
        try:
            ts = datetime.fromisoformat(ts_str.replace("Z", "+00:00"))
        except (ValueError, TypeError):
            try:
                ts = datetime.strptime(ts_str[:19], "%Y-%m-%dT%H:%M:%S")
            except (ValueError, TypeError):
                continue

        day_name = ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс"][ts.weekday()]
        hour = ts.hour
        eng = p.get("engagement_score", 0)

        day_counts[day_name] += 1
        hour_counts[hour] += 1
        day_engagement[day_name] += eng
        hour_engagement[hour] += eng

    day_avg = {}
    for d in day_counts:
        day_avg[d] = round(day_engagement[d] / day_counts[d], 1)

    hour_avg = {}
    for h in hour_counts:
        hour_avg[h] = round(hour_engagement[h] / hour_counts[h], 1)

    best_days = sorted(day_avg.items(), key=lambda x: x[1], reverse=True)[:3]
    best_hours = sorted(hour_avg.items(), key=lambda x: x[1], reverse=True)[:5]

    return {
        "лучшие_дни": [{"день": d, "средний_engagement": v} for d, v in best_days],
        "лучшие_часы": [{"час": f"{h}:00", "средний_engagement": v} for h, v in best_hours],
        "рекомендация_день": best_days[0][0] if best_days else "Ср",
        "рекомендация_время": f"{best_hours[0][0]}:00" if best_hours else "12:00",
        "антирекомендация_день": sorted(day_avg.items(), key=lambda x: x[1])[0][0] if day_avg else None,
    }


def analyze_hashtags(posts: List[Dict], top_n: int = 20) -> Dict:
    all_hashtags = Counter()
    hashtag_engagement = {}
    total_hashtags = 0

    for p in posts:
        caption = p.get("caption", "") or ""
        tags = extract_hashtags(caption)
        total_hashtags += len(tags)
        for tag in tags:
            all_hashtags[tag] += 1
            if tag not in hashtag_engagement:
                hashtag_engagement[tag] = {"count": 0, "total_engagement": 0}
            hashtag_engagement[tag]["count"] += 1
            hashtag_engagement[tag]["total_engagement"] += p.get("engagement_score", 0)

    top_hashtags = all_hashtags.most_common(top_n)

    engagement_hashtags = []
    for tag, data in hashtag_engagement.items():
        if data["count"] >= 3:
            avg = round(data["total_engagement"] / data["count"], 1)
            engagement_hashtags.append({"тег": tag, "использований": data["count"], "средний_engagement": avg})

    engagement_hashtags.sort(key=lambda x: x["средний_engagement"], reverse=True)

    our_posts = [p for p in posts if p.get("username") in ("arclinic", "reznik_anna_v")]
    comp_posts = [p for p in posts if p.get("username") not in ("arclinic", "reznik_anna_v")]

    our_tags = Counter()
    for p in our_posts:
        for tag in extract_hashtags(p.get("caption", "") or ""):
            our_tags[tag] += 1

    comp_tags = Counter()
    for p in comp_posts:
        for tag in extract_hashtags(p.get("caption", "") or ""):
            comp_tags[tag] += 1

    tags_only_competitors = set(comp_tags.keys()) - set(our_tags.keys())
    missing_tags = [
        {"тег": t, "используется_конкурентами": comp_tags[t]}
        for t in sorted(tags_only_competitors, key=lambda t: comp_tags[t], reverse=True)[:15]
    ]

    return {
        "топ_хэштегов": [{"тег": h[0], "использований": h[1]} for h in top_hashtags],
        "хэштеги_с_высоким_engagement": engagement_hashtags[:10],
        "хэштеги_конкурентов_которые_мы_не_используем": missing_tags,
        "рекомендуемые_хэштеги": [h["тег"] for h in engagement_hashtags[:10]],
    }
