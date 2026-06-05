"""
SEO-анализатор для сайта arclinic.ru
Использует "второй мозг" для контекстных рекомендаций.
"""

import sys
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin
from brain_reader import get_clinic_info, get_identity_info, get_tone_info


def analyze_site_structure(base_url: str) -> dict:
    """Анализирует структуру сайта: заголовки, мета-теги, ссылки."""
    try:
        response = requests.get(base_url, timeout=15)
        response.raise_for_status()
    except requests.RequestException as e:
        return {"error": str(e)}

    soup = BeautifulSoup(response.text, "html.parser")
    
    result = {
        "url": base_url,
        "status": response.status_code,
        "title": soup.title.string.strip() if soup.title else None,
        "meta_description": None,
        "h1_count": 0,
        "h1_tags": [],
        "h2_count": 0,
        "internal_links": 0,
        "external_links": 0,
        "images_no_alt": 0,
        "has_canonical": False,
        "has_og_tags": False,
        "load_time_ms": response.elapsed.total_seconds() * 1000,
    }

    # Meta description
    meta_desc = soup.find("meta", attrs={"name": "description"})
    if meta_desc and meta_desc.get("content"):
        result["meta_description"] = meta_desc["content"].strip()

    # H1
    h1s = soup.find_all("h1")
    result["h1_count"] = len(h1s)
    result["h1_tags"] = [h.get_text(strip=True) for h in h1s]

    # H2
    h2s = soup.find_all("h2")
    result["h2_count"] = len(h2s)

    # Links
    base_domain = urlparse(base_url).netloc
    for a in soup.find_all("a", href=True):
        href = a["href"]
        if href.startswith("http"):
            if base_domain in href:
                result["internal_links"] += 1
            else:
                result["external_links"] += 1
        elif href.startswith("/") or href.startswith("#"):
            result["internal_links"] += 1

    # Images without alt
    for img in soup.find_all("img"):
        if not img.get("alt"):
            result["images_no_alt"] += 1

    # Canonical
    canonical = soup.find("link", rel="canonical")
    result["has_canonical"] = canonical is not None

    # OG tags
    og_tags = soup.find_all("meta", property=lambda x: x and x.startswith("og:"))
    result["has_og_tags"] = len(og_tags) > 0

    return result


def generate_seo_recommendations(analysis: dict) -> list:
    """Генерирует SEO-рекомендации на основе анализа."""
    recommendations = []

    if analysis.get("error"):
        return [f"❌ Ошибка: {analysis['error']}"]

    # Title
    title = analysis.get("title", "")
    if not title:
        recommendations.append("🔴 Отсутствует title — критично для SEO")
    elif len(title) < 30:
        recommendations.append(f"🟡 Title слишком короткий ({len(title)} символов). Рекомендуется 50-60 символов")
    elif len(title) > 70:
        recommendations.append(f"🟡 Title слишком длинный ({len(title)} символов). Рекомендуется 50-60 символов")
    else:
        recommendations.append(f"✅ Title в норме ({len(title)} символов)")

    # Meta description
    meta_desc = analysis.get("meta_description", "")
    if not meta_desc:
        recommendations.append("🔴 Отсутствует meta description")
    elif len(meta_desc) < 100:
        recommendations.append(f"🟡 Meta description короткий ({len(meta_desc)} символов). Рекомендуется 150-160")
    else:
        recommendations.append(f"✅ Meta description в норме ({len(meta_desc)} символов)")

    # H1
    h1_count = analysis.get("h1_count", 0)
    if h1_count == 0:
        recommendations.append("🔴 Нет H1 тега — критично для SEO")
    elif h1_count > 1:
        recommendations.append(f"🟡 Больше одного H1 ({h1_count}). Рекомендуется один H1 на страницу")
    else:
        recommendations.append(f"✅ Один H1: «{analysis['h1_tags'][0][:60]}...»" if analysis['h1_tags'] else "")

    # Images
    if analysis.get("images_no_alt", 0) > 0:
        recommendations.append(f"🟡 {analysis['images_no_alt']} изображений без alt-текста")
    else:
        recommendations.append("✅ Все изображения имеют alt-текст")

    # Canonical
    if not analysis.get("has_canonical"):
        recommendations.append("🟡 Нет canonical URL — рекомендуется добавить")
    else:
        recommendations.append("✅ Canonical URL присутствует")

    # OG tags
    if not analysis.get("has_og_tags"):
        recommendations.append("🟡 Нет Open Graph тегов — важно для соцсетей")
    else:
        recommendations.append("✅ Open Graph теги присутствуют")

    # Load time
    load_time = analysis.get("load_time_ms", 0)
    if load_time > 3000:
        recommendations.append(f"🔴 Медленная загрузка ({load_time:.0f}мс). Рекомендуется < 2000мс")
    elif load_time > 2000:
        recommendations.append(f"🟡 Время загрузки ({load_time:.0f}мс). Рекомендуется < 2000мс")
    else:
        recommendations.append(f"✅ Хорошая скорость загрузки ({load_time:.0f}мс)")

    return recommendations


def print_full_report(analysis: dict, recommendations: list):
    """Выводит полный SEO-отчёт."""
    print("\n" + "=" * 70)
    print(f"🔍 SEO АНАЛИЗ: {analysis.get('url', 'N/A')}")
    print("=" * 70)

    if "error" in analysis:
        print(f"\n❌ Ошибка: {analysis['error']}")
        return

    print(f"\n📊 Базовые метрики:")
    print(f"   Статус:        {analysis.get('status', 'N/A')}")
    print(f"   Время загрузки: {analysis.get('load_time_ms', 0):.0f} мс")
    print(f"   Внутренних ссылок: {analysis.get('internal_links', 0)}")
    print(f"   Внешних ссылок:    {analysis.get('external_links', 0)}")

    print(f"\n🏷 Мета-теги:")
    print(f"   Title:       {analysis.get('title', '❌ Отсутствует')}")
    print(f"   Description: {analysis.get('meta_description', '❌ Отсутствует')[:80]}...")
    print(f"   Canonical:   {'✅' if analysis.get('has_canonical') else '❌'} ")
    print(f"   OG теги:     {'✅' if analysis.get('has_og_tags') else '❌'} ")

    print(f"\n📑 Структура:")
    print(f"   H1: {analysis.get('h1_count', 0)} — {analysis.get('h1_tags', [])}")
    print(f"   H2: {analysis.get('h2_count', 0)}")
    print(f"   Изображения без alt: {analysis.get('images_no_alt', 0)}")

    print(f"\n💡 РЕКОМЕНДАЦИИ:")
    for i, rec in enumerate(recommendations, 1):
        print(f"   {i}. {rec}")

    print("=" * 70)


if __name__ == "__main__":
    url = sys.argv[1] if len(sys.argv) > 1 else "https://www.arclinic.ru"
    
    print(f"\n📖 Загружаю контекст из второго мозга...")
    clinic = get_clinic_info()
    print(f"   Клиника: ARclinic — {clinic.get('услуги', '')[:50]}...")
    
    print(f"\n🔍 Анализирую сайт: {url}")
    analysis = analyze_site_structure(url)
    recommendations = generate_seo_recommendations(analysis)
    print_full_report(analysis, recommendations)
