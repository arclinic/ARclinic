---
name: seo-schema
description: "Schema.org разметка: детекция JSON-LD и microdata, валидация типов (Organization, Product, Article и др.), генерация отсутствующей разметки. Запускай для проверки структурных данных."
---

# SEO Schema Audit Sub-Skill

## Когда запускать

- Пользователь хочет проверить Schema.org разметку
- Нужно добавить JSON-LD на сайт
- Валидация существующей разметки

## Инструменты

```bash
python scripts/seo/seo_schema.py <url>
```

## Supported Schema Types

| Тип | Назначение | Required Fields |
|-----|-----------|-----------------|
| Organization | Компания/бренд | name, url |
| LocalBusiness | Локальный бизнес | name, address |
| Product | Товар | name |
| Article/BlogPosting | Статья | headline, author, datePublished |
| WebSite | Весь сайт | name, url |
| Person | Человек | name |
| BreadcrumbList | Хлебные крошки | itemListElement |
| Event | Событие | name, startDate, location |
| JobPosting | Вакансия | title, description, datePosted |
| Review | Отзыв | itemReviewed, reviewRating |

Reference: `.opencode/skills/seo-schema/references/active-types.md`

## Validation Rules

### JSON-LD формат
1. `@context` должен быть `https://schema.org`
2. `@type` — известный активный тип
3. Все required fields присутствуют
4. URL свойства — абсолютные (https://...)
5. Даты в ISO 8601 формате
6. Изображения с width/height

### Deprecated типы (не рекомендуются с 2024-2026)
- **FAQ**: только для гос/медицинских сайтов с Aug 2023
- **HowTo**: rich results удалены Sep 2023
- **SpecialAnnouncement**: deprecated July 2025

## Schema Generation

Если разметка отсутствует — предложи JSON-LD. Шаблон:

### Organization
```json
{
  "@context": "https://schema.org",
  "@type": "Organization",
  "name": "{company_name}",
  "url": "{website_url}",
  "logo": {
    "@type": "ImageObject",
    "url": "{logo_url}",
    "width": 300,
    "height": 60
  },
  "sameAs": [
    "{social_url_1}",
    "{social_url_2}"
  ],
  "contactPoint": {
    "@type": "ContactPoint",
    "email": "{email}",
    "contactType": "customer service"
  },
  "foundingDate": "{YYYY-MM-DD}",
  "description": "{description}"
}
```

### LocalBusiness
```json
{
  "@context": "https://schema.org",
  "@type": "LocalBusiness",
  "name": "{business_name}",
  "address": {
    "@type": "PostalAddress",
    "streetAddress": "{street}",
    "addressLocality": "{city}",
    "addressRegion": "{region}",
    "postalCode": "{zip}",
    "addressCountry": "{country_code}"
  },
  "geo": {
    "@type": "GeoCoordinates",
    "latitude": 0.0,
    "longitude": 0.0
  },
  "telephone": "{phone}",
  "openingHours": "Mo-Fr 09:00-18:00",
  "priceRange": "$$-$$$",
  "image": "{image_url}",
  "url": "{website_url}"
}
```

## Scoring

```
base_score = 100

# Presence
- Нет JSON-LD вообще: -30
- Нет microdata: -5 (info)

# Per block
- Parse error: -20 per block
- Missing required field: -15 per field
- Missing recommended field: -3 per field
- Relative URL: -5 per URL
- No @id for cross-referencing: -2

# Type-specific
- Organization без logo: -10
- LocalBusiness без geo: -15
- Product без offers: -10
- Article без author: -10
- Нет social profiles (sameAs < 2): -5
```

## Output Format

```json
{
  "score": 0-100,
  "grade": "A/B+/B/C/D/F",
  "jsonld_blocks": 2,
  "microdata_items": 0,
  "types_found": ["Organization", "WebSite"],
  "validations": [
    {
      "type": "Organization",
      "score": 85,
      "issues": ["Missing sameAs"],
      "warnings": ["foundingDate without full ISO format"]
    }
  ],
  "generated_schemas": [
    {"type": "LocalBusiness", "json": "..."}
  ],
  "findings": [
    {"severity": "critical", "issue": "LocalBusiness schema отсутствует", "fix": "...", "suggestion": "..."}
  ]
}
```

## Example

```
Schema Markup Report
====================

URL: https://example.com
JSON-LD Blocks: 2 (Organization, WebSite)
Overall Grade: B+ (82/100)

Organization (75/100)
├── ✓ name, url, logo
├── ✗ CRITICAL: Missing sameAs (no social profiles)
└── ⚠ foundingDate: year-only, prefer ISO 8601

WebSite (90/100)
├── ✓ name, url
├── ✓ potentialAction (SearchAction)
└── ⚠ Consider adding publisher

Missing schemas recommended:
- BreadcrumbList (для навигации)
- LocalBusiness (если есть физический адрес)
```
