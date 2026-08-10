import requests
from typing import Dict, List
from datetime import datetime


def fetch_prodoctors_reviews(clinic_name: str = "ARclinic") -> Dict:
    reviews = []
    rating = 0
    total = 0

    try:
        url = f"https://prodoctorov.ru/spb/lpu/arclinic/"
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
        resp = requests.get(url, headers=headers, timeout=15)

        if resp.status_code == 200:
            text = resp.text
            import re
            rating_match = re.search(r'ratingValue["\s:]+(\d+\.?\d*)', text)
            if rating_match:
                rating = float(rating_match.group(1))
            count_match = re.search(r'reviewCount["\s:]+(\d+)', text)
            if count_match:
                total = int(count_match.group(1))
    except Exception as e:
        return {"источник": "ПроДокторов", "статус": f"ошибка: {str(e)[:80]}", "отзывов": 0, "рейтинг": 0}

    return {
        "источник": "ПроДокторов",
        "статус": "OK" if rating > 0 else "не удалось извлечь",
        "отзывов": total,
        "рейтинг": rating,
    }


def fetch_2gis_reviews(clinic_name: str = "ARclinic") -> Dict:
    return {
        "источник": "2GIS",
        "статус": "требуется API-ключ или ручная проверка",
        "отзывов": 0,
        "рейтинг": 0,
    }


def fetch_google_reviews(clinic_name: str = "ARclinic") -> Dict:
    return {
        "источник": "Google Maps",
        "статус": "требуется Google Places API ключ",
        "отзывов": 0,
        "рейтинг": 0,
    }


def collect_all_reviews() -> List[Dict]:
    results = []
    results.append(fetch_prodoctors_reviews())
    results.append(fetch_2gis_reviews())
    results.append(fetch_google_reviews())
    return results
