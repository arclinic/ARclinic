---
name: seo
description: "SEO-аудит сайта: технический SEO, контент/E-E-A-T, Schema.org, AI-search (GEO). Запускай когда пользователь хочет провести SEO-аудит, проверить сайт, оптимизировать под поисковики или нейросети. Команды: seo audit, seo page, seo schema, seo geo, seo technical, seo content."
---

# SEO Audit Skill

## Trigger

Запускай этот скилл когда пользователь говорит:
- "SEO-аудит", "seo audit", "аудит сайта", "проверь SEO"
- "оптимизируй сайт", "проверь Schema разметку", "GEO-анализ"
- "Core Web Vitals", "скорость сайта", "SEO-отчёт"

## Commands

```
seo audit <url>   — полный аудит сайта (параллельно запускает 4 sub-agents)
seo page <url>    — глубокий анализ конкретной страницы
seo schema <url>  — Schema.org детекция и валидация
seo geo <url>     — анализ готовности к AI-поиску (AI Overviews / GEO)
seo technical <url> — технический SEO аудит
seo content <url> — анализ контента и E-E-A-T
```

## Architecture

Главный skill — **orchestrator**. Для `seo audit` запусти 4 sub-agents параллельно (через task делегирование):

### Параллельный запуск (для `seo audit <url>`):

**ОДНОВРЕМЕННО** запусти 4 sub-agents:

1. **Agent `seo-technical`** — запускает скрипты и возвращает технический аудит
2. **Agent `seo-content`** — запускает скрипты и возвращает контент-аудит
3. **Agent `seo-schema`** — запускает скрипты и возвращает schema-аудит
4. **Agent `seo-geo`** — запускает скрипты и возвращает GEO-аудит

**ВАЖНО**: 
- Вызови ВСЕ 4 sub-agents в одном сообщении (параллельно)!
- Каждый агент возвращает JSON с score, grade и findings
- Объедини результаты в один отчёт

### Скрипты

Все Python-скрипты в `scripts/seo/` относительно корня проекта:
- `seo_fetch.py <url>` — HTML парсинг, мета-теги, ссылки, robots.txt, sitemap
- `seo_schema.py <url>` — Schema.org JSON-LD extraction и validation
- `seo_pagespeed.py <url> mobile` — Google PageSpeed Insights CWV

### Для одиночных команд (`seo page`, `seo schema` и т.д.):

Запусти **один** соответствующий sub-agent.

## Scoring

Каждый sub-agent возвращает оценку 0-100. Финальная оценка:

```python
final_score = int(tech * 0.30 + content * 0.30 + schema * 0.20 + geo * 0.20)
```

Оценки → Grade:
- 90-100 → A (отлично)
- 80-89 → B+ (хорошо)
- 70-79 → B (средне)
- 60-69 → C (есть проблемы)
- 40-59 → D (много проблем)
- 0-39 → F (критично)

## Report Format

Собери данные от sub-agents в один отчёт:

```markdown
# SEO-аудит: {url}
**Дата:** {date}
**Общая оценка:** {grade} ({score}/100)

## Summary
| Категория | Оценка | Grade |
|-----------|--------|-------|
| Технический SEO | {score}/100 | {grade} |
| Контент/E-E-A-T | {score}/100 | {grade} |
| Schema.org | {score}/100 | {grade} |
| AI-Search (GEO) | {score}/100 | {grade} |

## Critical Issues
- [{приоритет}] описание проблемы + как исправить
- ...

## Recommendations (приоритизированы по влиянию)
1. ...

## Technical Details
### Core Web Vitals
- LCP: ...
- CLS: ...
- TBT: ...

### Meta & Social
- Title: ...
- Description: ...
- OG: ...

### Schema
- Blocks: ...
- Issues: ...

### Content
- Words: ...
- Headings: ...
- E-E-A-T signals: ...

### AI-Readiness
- Question-answer blocks: ...
- Passage citability: ...
```

## Output

1. **Выведи отчёт в консоль** (markdown)
2. **Сохрани файл** `SEO-REPORT-{domain}-{date}.md` в корень проекта

## Script Locations

Все скрипты в `scripts/seo/`:
- `seo_fetch.py` — сбор HTML, мета-тегов, ссылок, картинок
- `seo_schema.py` — JSON-LD и microdata извлечение
- `seo_pagespeed.py` — Google PageSpeed Insights API

## Error Handling

Если скрипт падает — выведи ошибку и предложи альтернативу (webfetch).
Если API лимит (PageSpeed 429) — пропусти этот раздел, отметь в отчёте.
