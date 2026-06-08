#!/usr/bin/env python3
"""
Скил для анализа карточки медицинской клиники на Яндекс Картах.
Собирает: рейтинг, отзывы, категории, часы работы, фото, конкурентов,
а также даёт рекомендации по улучшению позиций.
"""

import json
import re
import sys
import time
from datetime import datetime, timedelta
from typing import Optional
from urllib.parse import urlparse, parse_qs

import requests
from bs4 import BeautifulSoup


class YandexMapsAnalyzer:
    """
    Анализатор карточки организации на Яндекс Картах.
    Использует requests + BeautifulSoup для парсинга статики
    и Playwright для динамических элементов.
    """

    BASE_URL = "https://yandex.com/maps"

    def __init__(self, org_url: str, use_playwright: bool = True):
        self.org_url = org_url
        self.org_id = self._extract_org_id(org_url)
        self.use_playwright = use_playwright
        self.data = {
            "url": org_url,
            "org_id": self.org_id,
            "analyzed_at": datetime.now().isoformat(),
            "basic_info": {},
            "ratings": {},
            "reviews": [],
            "competitors": [],
            "photos_count": 0,
            "services": [],
            "features": [],
            "working_hours": {},
            "seo_analysis": {},
            "recommendations": [],
        }

    def _extract_org_id(self, url: str) -> Optional[str]:
        """Извлекает ID организации из URL Яндекс Карт."""
        # Пример: https://yandex.com/maps/org/arclinic/29776995657/
        match = re.search(r'/org/[^/]+/(\d+)', url)
        if match:
            return match.group(1)
        # Попробуем из query параметров
        parsed = urlparse(url)
        params = parse_qs(parsed.query)
        if 'oid' in params:
            return params['oid'][0]
        return None

    def fetch_with_requests(self) -> str:
        """Загружает страницу через requests."""
        headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/125.0.0.0 Safari/537.36"
            ),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "ru-RU,ru;q=0.9,en;q=0.8",
        }
        resp = requests.get(self.org_url, headers=headers, timeout=30)
        resp.raise_for_status()
        return resp.text

    def fetch_with_playwright(self) -> str:
        """Загружает страницу через Playwright (для динамического контента)."""
        from playwright.sync_api import sync_playwright

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context(
                user_agent=(
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/125.0.0.0 Safari/537.36"
                ),
                locale="ru-RU",
            )
            page = context.new_page()
            page.goto(self.org_url, wait_until="networkidle", timeout=60000)
            # Ждём загрузки основных элементов
            time.sleep(3)
            # Скроллим для подгрузки контента
            page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            time.sleep(2)
            page.evaluate("window.scrollTo(0, 0)")
            time.sleep(1)

            html = page.content()
            browser.close()
            return html

    def parse_basic_info(self, soup: BeautifulSoup):
        """Парсит основную информацию об организации."""
        # Название
        title_tag = soup.find("h1")
        if title_tag:
            self.data["basic_info"]["name"] = title_tag.get_text(strip=True)

        # Адрес
        address_patterns = [
            r'Адрес[:\s]*([^\n]+)',
            r'"address"[:\s]*"([^"]+)"',
        ]
        for pattern in address_patterns:
            match = re.search(pattern, str(soup))
            if match:
                self.data["basic_info"]["address"] = match.group(1).strip()
                break

        # Категория / тип организации
        category_tags = soup.find_all("a", href=re.compile(r"/maps/category/"))
        if category_tags:
            self.data["basic_info"]["categories"] = [
                t.get_text(strip=True) for t in category_tags
            ]

        # Телефон
        phone_patterns = [
            r'\+7[\d\s\-\(\)]{10,}',
            r'8[\d\s\-\(\)]{10,}',
        ]
        phones = set()
        for pattern in phone_patterns:
            for match in re.finditer(pattern, str(soup)):
                phones.add(match.group().strip())
        if phones:
            self.data["basic_info"]["phones"] = list(phones)

        # Сайт
        site_match = re.search(r'(https?://(?:www\.)?arclinic[^\s"\'<]+)', str(soup))
        if site_match:
            self.data["basic_info"]["website"] = site_match.group(1)

    def parse_ratings(self, soup: BeautifulSoup):
        """Парсит рейтинг и количество оценок."""
        # Рейтинг (ищем числа с плавающей точкой рядом со звёздами)
        rating_patterns = [
            r'рейтинг[:\s]*([\d.]+)',
            r'rating[":\s]*([\d.]+)',
            r'"rating"[:\s]*([\d.]+)',
            r'([\d.]+)\s*/\s*5',
        ]
        for pattern in rating_patterns:
            match = re.search(pattern, str(soup), re.IGNORECASE)
            if match:
                try:
                    self.data["ratings"]["rating"] = float(match.group(1))
                    break
                except ValueError:
                    continue

        # Количество оценок
        votes_patterns = [
            r'(\d+)\s*(?:оцен|оценк|голос|отзыв)',
            r'(?:оцен|оценк|голос|отзыв)[^\d]*(\d+)',
            r'"votes"[:\s]*(\d+)',
        ]
        for pattern in votes_patterns:
            match = re.search(pattern, str(soup), re.IGNORECASE)
            if match:
                self.data["ratings"]["votes"] = int(match.group(1))
                break

    def parse_reviews(self, soup: BeautifulSoup):
        """Парсит отзывы (первые несколько)."""
        # Ищем блоки с отзывами
        review_blocks = soup.find_all("div", class_=re.compile(r"review|comment|feedback", re.I))
        if not review_blocks:
            # Пробуем найти через data-атрибуты
            review_blocks = soup.find_all("div", attrs={"data-review-id": True})

        for block in review_blocks[:10]:
            try:
                author = block.find(["span", "div", "a"], class_=re.compile(r"author|name|user", re.I))
                text = block.find(["p", "div", "span"], class_=re.compile(r"text|content|message", re.I))
                rating = block.find(["span", "div"], class_=re.compile(r"rating|star", re.I))
                date = block.find(["span", "time"], class_=re.compile(r"date|time", re.I))

                review = {
                    "author": author.get_text(strip=True) if author else None,
                    "text": text.get_text(strip=True)[:500] if text else None,
                    "rating": rating.get_text(strip=True) if rating else None,
                    "date": date.get_text(strip=True) if date else None,
                }
                if review["text"] or review["rating"]:
                    self.data["reviews"].append(review)
            except Exception:
                continue

    def parse_working_hours(self, soup: BeautifulSoup):
        """Парсит часы работы."""
        hours_patterns = [
            r'(пн|вт|ср|чт|пт|сб|вс|ежедневно|будни|выходные)[^.]*\d{1,2}[:]\d{2}',
            r'часы работы[:\s]*([^\n]+)',
            r'"working_hours"[:\s]*({[^}]+})',
        ]
        hours_found = []
        for pattern in hours_patterns:
            for match in re.finditer(pattern, str(soup), re.IGNORECASE):
                hours_found.append(match.group().strip())
        if hours_found:
            self.data["working_hours"]["raw"] = hours_found

    def parse_photos_count(self, soup: BeautifulSoup):
        """Парсит количество фото."""
        photo_patterns = [
            r'(\d+)\s*(?:фото|фотографий|photo|photos)',
            r'"photos_count"[:\s]*(\d+)',
        ]
        for pattern in photo_patterns:
            match = re.search(pattern, str(soup), re.IGNORECASE)
            if match:
                self.data["photos_count"] = int(match.group(1))
                break

    def parse_services(self, soup: BeautifulSoup):
        """Парсит услуги/категории услуг."""
        service_blocks = soup.find_all(["div", "span", "a"], class_=re.compile(r"service|rubric|category|tag", re.I))
        services = []
        for block in service_blocks:
            text = block.get_text(strip=True)
            if text and len(text) < 100:
                services.append(text)
        if services:
            self.data["services"] = list(set(services))

    def parse_features(self, soup: BeautifulSoup):
        """Парсит особенности (парковка, оплата картой и т.д.)."""
        feature_patterns = [
            r'парковк[а-я]*',
            r'оплат[а-я]*\s*карт[а-я]*',
            r'Wi[-\s]*Fi',
            r'доступн[а-я]*\s*среда',
            r'дет[ияей]*',
            r'сво[яё]*\s*парковк[а-я]*',
        ]
        features = set()
        for pattern in feature_patterns:
            for match in re.finditer(pattern, str(soup), re.IGNORECASE):
                features.add(match.group().strip())
        if features:
            self.data["features"] = list(features)

    def parse_seo_analysis(self, soup: BeautifulSoup):
        """Анализирует SEO-элементы карточки."""
        seo = {}

        # Title
        title_tag = soup.find("title")
        seo["title"] = title_tag.get_text(strip=True) if title_tag else None

        # Meta description
        meta_desc = soup.find("meta", attrs={"name": "description"})
        seo["meta_description"] = meta_desc.get("content", "").strip() if meta_desc else None

        # Meta keywords
        meta_keys = soup.find("meta", attrs={"name": "keywords"})
        seo["meta_keywords"] = meta_keys.get("content", "").strip() if meta_keys else None

        # H1
        h1 = soup.find("h1")
        seo["h1"] = h1.get_text(strip=True) if h1 else None

        # Canonical
        canonical = soup.find("link", rel="canonical")
        seo["canonical"] = canonical.get("href") if canonical else None

        # JSON-LD (структурированные данные)
        jsonld_scripts = soup.find_all("script", type="application/ld+json")
        seo["jsonld_count"] = len(jsonld_scripts)
        seo["jsonld"] = []
        for script in jsonld_scripts[:3]:
            try:
                seo["jsonld"].append(json.loads(script.string))
            except (json.JSONDecodeError, TypeError):
                seo["jsonld"].append({"raw": script.string[:200] if script.string else None})

        self.data["seo_analysis"] = seo

    def generate_recommendations(self):
        """Генерирует рекомендации на основе собранных данных."""
        recs = []
        data = self.data

        # 1. Рейтинг
        rating = data["ratings"].get("rating", 0)
        votes = data["ratings"].get("votes", 0)
        if rating < 4.5:
            recs.append({
                "priority": "HIGH",
                "category": "Рейтинг",
                "action": f"Повысить рейтинг с {rating} до 4.5+. "
                          f"Активно просить пациентов оставлять отзывы.",
                "impact": "Высокий — рейтинг влияет на позиции в выдаче",
            })
        if votes < 100:
            recs.append({
                "priority": "HIGH",
                "category": "Количество отзывов",
                "action": f"Увеличить количество отзывов (сейчас {votes}). "
                          f"Цель: минимум 200-300 отзывов для конкурентного преимущества.",
                "impact": "Высокий — больше отзывов = выше доверие и позиции",
            })

        # 2. Фото
        if data["photos_count"] < 50:
            recs.append({
                "priority": "MEDIUM",
                "category": "Фотографии",
                "action": f"Добавить больше фото (сейчас {data['photos_count']}). "
                          f"Рекомендуется 50+ качественных фото: интерьер, оборудование, команда.",
                "impact": "Средний — визуальный контент повышает конверсию",
            })

        # 3. Услуги
        if not data["services"]:
            recs.append({
                "priority": "HIGH",
                "category": "Услуги",
                "action": "Заполнить полный список услуг в карточке. "
                          "Это ключевой фактор ранжирования по запросам услуг.",
                "impact": "Высокий —直接影响 поиск по услугам",
            })

        # 4. SEO
        seo = data.get("seo_analysis", {})
        if not seo.get("meta_description"):
            recs.append({
                "priority": "MEDIUM",
                "category": "SEO",
                "action": "Добавить meta-description в карточку организации.",
                "impact": "Средний — влияет на CTR в поиске",
            })
        if seo.get("jsonld_count", 0) == 0:
            recs.append({
                "priority": "MEDIUM",
                "category": "Структурированные данные",
                "action": "Добавить JSON-LD разметку для медицинской организации.",
                "impact": "Средний — улучшает понимание карточки поисковиками",
            })

        # 5. Часы работы
        if not data.get("working_hours"):
            recs.append({
                "priority": "HIGH",
                "category": "Часы работы",
                "action": "Заполнить актуальные часы работы. "
                          "Указать часы приёма по каждому специалисту.",
                "impact": "Высокий — влияет на показ в поиске 'открыто сейчас'",
            })

        # 6. Ответы на отзывы
        recs.append({
            "priority": "HIGH",
            "category": "Работа с отзывами",
            "action": "Отвечать на ВСЕ отзывы (положительные — благодарить, "
                      "отрицательные — предлагать решение). "
                      "Это улучшает поведенческие факторы.",
            "impact": "Высокий — влияет на ранжирование",
        })

        # 7. Ключевые слова
        recs.append({
            "priority": "MEDIUM",
            "category": "Ключевые слова",
            "action": "Оптимизировать описание организации под ключевые запросы: "
                      "'медицинская клиника', 'платная клиника', "
                      "'[район] клиника', 'врачи [специальности]'.",
            "impact": "Средний — улучшает релевантность поиска",
        })

        # 8. Акции и новости
        recs.append({
            "priority": "LOW",
            "category": "Контент",
            "action": "Добавлять акции и новости в карточку. "
                      "Яндекс любит активные организации.",
            "impact": "Низкий, но даёт дополнительный трафик",
        })

        self.data["recommendations"] = recs

    def analyze(self) -> dict:
        """Запускает полный анализ карточки."""
        print(f"🔍 Анализирую карточку: {self.org_url}")
        print(f"   ID организации: {self.org_id}")

        # Загружаем страницу
        print("   Загружаю страницу...")
        try:
            if self.use_playwright:
                html = self.fetch_with_playwright()
            else:
                html = self.fetch_with_requests()
        except Exception as e:
            print(f"   ❌ Ошибка загрузки: {e}")
            # Пробуем альтернативный метод
            print("   ⚠️ Пробую загрузить через requests...")
            try:
                html = self.fetch_with_requests()
            except Exception as e2:
                print(f"   ❌ Ошибка загрузки через requests: {e2}")
                self.data["error"] = str(e2)
                return self.data

        soup = BeautifulSoup(html, "html.parser")

        print("   Парсю данные...")
        self.parse_basic_info(soup)
        self.parse_ratings(soup)
        self.parse_reviews(soup)
        self.parse_working_hours(soup)
        self.parse_photos_count(soup)
        self.parse_services(soup)
        self.parse_features(soup)
        self.parse_seo_analysis(soup)

        print("   Генерирую рекомендации...")
        self.generate_recommendations()

        print("   ✅ Анализ завершён!")
        return self.data

    def print_report(self):
        """Выводит отчёт в консоль."""
        d = self.data

        print("\n" + "=" * 70)
        print(f"📊 ОТЧЁТ ПО КАРТОЧКЕ ЯНДЕКС КАРТЫ")
        print("=" * 70)

        # Основная информация
        print(f"\n🏥 ОСНОВНАЯ ИНФОРМАЦИЯ:")
        bi = d.get("basic_info", {})
        print(f"   Название: {bi.get('name', 'N/A')}")
        print(f"   Адрес: {bi.get('address', 'N/A')}")
        print(f"   Сайт: {bi.get('website', 'N/A')}")
        print(f"   Телефоны: {', '.join(bi.get('phones', ['N/A']))}")
        print(f"   Категории: {', '.join(bi.get('categories', ['N/A']))}")

        # Рейтинг
        print(f"\n⭐ РЕЙТИНГ:")
        rt = d.get("ratings", {})
        print(f"   Рейтинг: {rt.get('rating', 'N/A')} / 5")
        print(f"   Количество оценок: {rt.get('votes', 'N/A')}")

        # Отзывы
        print(f"\n💬 ОТЗЫВЫ (последние {len(d.get('reviews', []))}):")
        for i, rev in enumerate(d.get("reviews", [])[:5], 1):
            print(f"   {i}. {rev.get('author', 'Аноним')}: "
                  f"\"{rev.get('text', '')[:100]}...\" "
                  f"[{rev.get('rating', '?')}⭐]")

        # Фото
        print(f"\n📸 ФОТО: {d.get('photos_count', 'N/A')}")

        # Услуги
        if d.get("services"):
            print(f"\n🩺 УСЛУГИ ({len(d['services'])}):")
            for s in d["services"][:10]:
                print(f"   • {s}")

        # Часы работы
        if d.get("working_hours"):
            print(f"\n🕐 ЧАСЫ РАБОТЫ:")
            for h in d["working_hours"].get("raw", []):
                print(f"   {h}")

        # SEO
        print(f"\n🔍 SEO-АНАЛИЗ:")
        seo = d.get("seo_analysis", {})
        print(f"   Title: {seo.get('title', 'N/A')[:80]}...")
        print(f"   Meta Description: {str(seo.get('meta_description', 'N/A'))[:80]}...")
        print(f"   JSON-LD блоков: {seo.get('jsonld_count', 0)}")

        # Рекомендации
        print(f"\n🎯 РЕКОМЕНДАЦИИ:")
        for i, rec in enumerate(d.get("recommendations", []), 1):
            priority_icon = {"HIGH": "🔴", "MEDIUM": "🟡", "LOW": "🟢"}
            print(f"\n   {priority_icon.get(rec['priority'], '⚪')} [{rec['priority']}] {rec['category']}")
            print(f"   📌 {rec['action']}")
            print(f"   💡 Влияние: {rec['impact']}")

        print("\n" + "=" * 70)
        print(f"📅 Анализ выполнен: {d.get('analyzed_at', 'N/A')}")
        print("=" * 70 + "\n")


def main():
    """Точка входа."""
    url = "https://yandex.com/maps/org/arclinic/29776995657/?ll=30.329154%2C59.913727&z=16"

    print("🚀 Запуск анализа карточки Яндекс Карт")
    print(f"   URL: {url}")
    print()

    analyzer = YandexMapsAnalyzer(url, use_playwright=True)
    result = analyzer.analyze()
    analyzer.print_report()

    # Сохраняем результат в JSON
    output_file = f"yandex/report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2, default=str)
    print(f"📁 Отчёт сохранён: {output_file}")

    return result


if __name__ == "__main__":
    main()
