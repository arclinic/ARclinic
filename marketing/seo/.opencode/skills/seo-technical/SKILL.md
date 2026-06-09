---
name: seo-technical
description: "Технический SEO-аудит страницы: Core Web Vitals, HTTPS, mobile, sitemap, robots.txt, canonical, структура URL, скорость. Запускай когда нужна техническая проверка сайта."
---

# SEO Technical Audit Sub-Skill

## Когда запускать

Когда пользователь хочет:
- Проверить техническую сторону сайта
- Узнать о Core Web Vitals
- Проверить мобильность, HTTPS, sitemap, robots.txt
- Найти битые ссылки и редиректы

## Инструменты

Запусти Python-скрипты:

```bash
python scripts/seo/seo_fetch.py <url>
python scripts/seo/seo_pagespeed.py <url> mobile
```

## Checklist (что проверять)

### 1. Core Web Vitals (из PageSpeed Insights)

| Metric | Target | Status |
|--------|--------|--------|
| LCP < 2.5s | Largest Contentful Paint | Good/NI/Poor |
| INP/TBT < 200ms | Interaction/Total Blocking | Good/NI/Poor |
| CLS < 0.1 | Layout Shift | Good/NI/Poor |

Если PageSpeed API недоступен — отметь что метрики не получены.

### 2. HTTPS
- Все страницы на HTTPS?
- Нет mixed-content?
- Все ссылки на https://?

### 3. Mobile
- `<meta name="viewport">` с `width=device-width`?
- Responsive design?

### 4. Crawlability
- `robots.txt` существует?
- `sitemap.xml` существует?
- Canonical-тег корректный?

### 5. URL structure
- Чистые URL без параметров?
- Логическая иерархия?

### 6. Links
- Внутренние ссылки связывают контент?
- Нет битых внешних ссылок?
- `nofollow` только там где нужно?

### 7. Images
- У всех картинок есть `alt`?
- Lazy loading для below-fold?
- Указаны width/height?

### 8. Performance
- Размер страницы < 2MB?
- Время ответа < 600ms?
- Есть gzip/brotli (header `content-encoding`)?

## Scoring

```
base_score = 100
- LCP > 2.5s: -15
- CLS > 0.1: -15
- TBT > 200ms: -15
- Нет HTTPS: -20
- Нет viewport: -10
- Нет robots.txt: -5
- Нет sitemap: -5
- Нет canonical: -5
- missing_alt > 30%: -5
- page_size > 2MB: -5
- response_time > 1s: -10
```

## Output Format

Верни JSON:
```json
{
  "score": 0-100,
  "grade": "A/B+/B/C/D/F",
  "findings": [
    {"severity": "critical|warning|info", "check": "имя", "issue": "...", "fix": "...", "indicator": "..."}
  ],
  "metrics": {
    "lcp_ms": null,
    "cls": null,
    "tbt_ms": null,
    "response_time_ms": 432,
    "page_size_kb": 150,
    "has_https": true,
    "has_viewport": true,
    "has_robots": true,
    "has_sitemap": true,
    "has_canonical": true
  }
}
```

## Example Findings

```json
[
  {"severity": "critical", "check": "https", "issue": "Сайт не использует HTTPS", "fix": "Получить SSL-сертификат (Let's Encrypt бесплатно)", "indicator": "Browser console warning"},
  {"severity": "warning", "check": "images_alt", "issue": "15 из 42 картинок без alt-атрибутов", "fix": "Добавить описательный alt для каждой картинки", "indicator": "Доступность для скринридеров"},
  {"severity": "info", "check": "sitemap", "issue": "sitemap.xml не найден", "fix": "Сгенерировать sitemap с основными URL", "indicator": "Поисковики смогут обнаружить все страницы"}
]
```
