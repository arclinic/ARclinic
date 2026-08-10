from typing import Dict, List
from collections import Counter
import re


def detect_male_content(posts: List[Dict]) -> List[Dict]:
    male_keywords = [
        "мужчин", "мужской", "мужская", "мужчину", "мужчины",
        "для него", "брутальный", "мужское", "мужских",
        "андропауза", "тестостерон", "уролог", "половой член",
        "муж", "парень", "сын",
    ]

    male_posts = []
    for p in posts:
        caption = (p.get("caption", "") or "").lower()
        if any(kw.lower() in caption for kw in male_keywords):
            male_posts.append(p)

    return male_posts


def analyze_male_segment(posts: List[Dict]) -> Dict:
    male = detect_male_content(posts)

    if not male:
        return {
            "найдено_постов": 0,
            "доля": "0%",
            "рекомендация": "Конкуренты почти не делают контент для мужчин — это голубой океан для ARclinic",
        }

    total = len(posts)
    male_n = len(male)
    avg_engagement_male = round(sum(p.get("engagement_score", 0) for p in male) / male_n, 1) if male_n else 0
    avg_engagement_all = round(sum(p.get("engagement_score", 0) for p in posts) / total, 1) if total else 0

    male_accounts = Counter(p.get("username", "") for p in male)

    topics = []
    for p in male:
        cap = (p.get("caption", "") or "").lower()
        if "уролог" in cap or "тестостерон" in cap or "андропауза" in cap:
            topics.append("гормоны/андропауза")
        elif "ботокс" in cap or "ботулин" in cap:
            topics.append("ботокс для мужчин")
        elif "филлер" in cap or "контур" in cap or "половой член" in cap:
            topics.append("контурная пластика/коррекция")
        elif "уход" in cap or "чистка" in cap or "пилинг" in cap:
            topics.append("уходовые процедуры")
        else:
            topics.append("прочее")

    topic_counts = dict(Counter(topics).most_common(5))

    return {
        "найдено_постов": male_n,
        "доля": f"{round(male_n / total * 100, 1)}%",
        "средний_engagement_мужские_посты": avg_engagement_male,
        "средний_engagement_все_посты": avg_engagement_all,
        "аккаунты_с_мужским_контентом": dict(male_accounts.most_common(5)),
        "темы_мужского_контента": topic_counts,
        "рекомендация": "",
        "рекомендуемые_темы_для_arclinic": [
            "Мужская косметология: ботокс для мужчин (зоны: лоб, межбровье)",
            "Коррекция полового члена филлерами (Труфанов)",
            "Андропауза: тестостерон и ЗГТ (Плотникова)",
            "Уходовые процедуры «Выглядеть отдохнувшим»",
            "Аппаратная косметология для мужчин: SMAS, RF-лифтинг",
        ],
    }


def generate_target_recommendations(posts: List[Dict]) -> Dict:
    video_posts = [p for p in posts if p.get("views", 0) > 1000]

    if not video_posts:
        return {"рекомендация": "Недостаточно данных по охватам видео"}

    video_posts.sort(key=lambda p: p.get("views", 0), reverse=True)
    top = video_posts[:10]

    topics_for_ads = Counter()
    for p in top:
        cap = (p.get("caption", "") or "").lower()
        if any(w in cap for w in ["до после", "результат", "преображение"]):
            topics_for_ads["до/после"] += 1
        elif any(w in cap for w in ["почему", "как", "что такое"]):
            topics_for_ads["образовательное"] += 1
        elif any(w in cap for w in ["себе", "показываю", "моё", "личное"]):
            topics_for_ads["личное/врач"] += 1
        else:
            topics_for_ads["прочее"] += 1

    avg_views_top = sum(p.get("views", 0) for p in top) // len(top)
    avg_engagement_top = round(sum(p.get("engagement_score", 0) for p in top) / len(top), 1)

    return {
        "топ_видео_для_рекламы": len(top),
        "средние_просмотры_топ": avg_views_top,
        "средний_engagement_топ": avg_engagement_top,
        "форматы_для_таргета": dict(topics_for_ads.most_common()),
        "рекомендации": [
            f"Пускать в таргет Reels с охватом > {avg_views_top} просмотров",
            "Формат до/после — самый конверсионный для рекламы",
            "Образовательные Reels — для холодной аудитории (узнавание бренда)",
            "Личные Reels — для тёплой аудитории (узнавание врача)",
            "Добавлять CTA в конец: 'Запись в директ' или ссылка на сайт",
        ],
    }
