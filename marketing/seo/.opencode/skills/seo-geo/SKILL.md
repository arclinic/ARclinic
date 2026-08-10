---
name: seo-geo
description: "AI-Search оптимизация (GEO/Generative Engine Optimization): цитируемость пассажей, question-answer структура, готовность к AI Overviews, entity presence. Запускай для оптимизации под нейросети и AI-поиск."
---

# SEO GEO Audit Sub-Skill

## Когда запускать

Когда пользователь хочет:
- Оптимизировать сайт под AI-поиск (AI Overviews, ChatGPT, Perplexity)
- Проверить "цитируемость" контента
- Улучшить passage для AI-ответов

## Key Principles

From [Google AI Optimization Guide (2026)](https://developers.google.com/search/docs/fundamentals/ai-optimization-guide):
- **AEO и GEO — это обычный SEO переименованный.** AI Overviews используют те же ranking systems.
- **LLMs.txt — не lever для цитирования** (нет доказательств что LLMs его читают приоритетнее).
- **Content chunking не обязателен.** Современные LLM понимают длинный контекст.
- **Переписывать под "AI-ключевые" не нужно** — модели понимают синонимы.

## Checklist

### 1. Passage Citability (цитируемость пассажей)

**Идеальный цитируемый passage:**
- 134-167 слов (optimal для AI extraction)
- Self-contained: можно вырвать из контекста и понять
- Starts with direct answer на вопрос
- Contains specific facts, numbers, examples
- Ends with attribution or source

**Проверка:**
- Разбит ли контент на self-contained блоки?
- Есть ли прямые ответы в первых предложениях абзацев?
- Длина ключевых пассажей в оптимальном диапазоне?

### 2. Question-Answer Structure

**Ищи признаки:**
- H2/H3 в форме вопросов (Как?, Что?, Почему?, Когда?)
- Следующий абзац даёт прямой ответ
- Есть FAQ-секция (даже без FAQ schema)
- Используются определения и списки

**Шаблон идеального passage:**
```
H2: Что такое X?
[134-167 слов self-contained answer с фактами]
```

### 3. Structured Data Coverage

Есть ли schema для:
- Основные сущности (Organization, Product, Person)
- FAQ/HowTo (если релевантно)
- DefinitionList / QAPage

### 4. Content Patterns to Avoid

❌ **Anti-patterns:**
- Clickbait заголовки без содержания
- Стена текста (>500 слов без подзаголовков)
- "Как многие знают..." без конкретики
- Повторяющиеся вводные фразы
- Ответы размазанные по странице

✅ **Хорошие практики:**
- Прямые ответы в начале секций
- Короткие абзацы по одной теме
- Конкретные примеры и цифры
- Списки с actionable items

### 5. Entity Presence

Проверь есть ли сущности в:
- **Wikipedia/Wikidata**: упоминается ли бренд/продукт?
- **Reddit**: есть ли обсуждения?
- **YouTube**: есть ли видео?
- **LinkedIn**: есть ли страница компании?

(Это не проверяется автоматически — отметь в отчёте как manual check)

### 6. Attribution & Trust Signals

- Dates: дата публикации и обновления
- Sources: ссылки на внешние источники
- Author byline: автор с credentials
- Contact info: видна на странице

## Scoring

```
base_score = 100

# Question-answer structure
- Нет Q&A блоков: -15
- Заголовки не-вопросительные: -10
- H2/H3 без прямых ответов: -10

# Passage citability
- Средняя длина < 100 слов: -10
- Средний passage > 300 слов (нет self-contained): -10  
- Нет direct answers в первом предложении: -10
- Нет списков (ul/ol) для перечислений: -5

# Content patterns
- Стена текста (>500 without breaks): -15
- Clickbait: -10
- Filler > 40%: -10

# Schema for entities
- Нет Organization schema: -10
- Нет Product/Article schema (если применимо): -5

# Attribution
- Нет даты: -5
- Нет автора: -5  
- Нет sources/references: -5
```

## Output Format

```json
{
  "score": 0-100,
  "grade": "A/B+/B/C/D/F",
  "question_answer_blocks": 0,
  "citation_ready_passages": 0,
  "total_passages_analyzed": 0,
  "qa_score": "weak/medium/strong",
  "citability_score": "weak/medium/strong",
  "entity_presence": {
    "wikipidea_mentions": "manual_check",
    "reddit_discussions": "manual_check",
    "youtube": "manual_check"
  },
  "findings": [
    {"severity": "critical|warning|info", "category": "qa|citability|schema|pattern", "issue": "...", "fix": "...", "example_fix": "..."}
  ],
  "ai_citation_potential": "low/medium/high",
  "top_optimization_opportunities": ["...", "..."]
}
```

## Example Findings

```json
[
  {"severity": "critical", "category": "qa", "issue": "Нет ни одного H2/H3 в форме вопроса", "fix": "Конвертировать ключевые секции в QA-формат: 'Что такое SEO?' → [direct answer]", "example_fix": "H2: Что такое Schema.org? → 'Schema.org — это словарь структурированных данных, созданный Google, Bing, Yahoo и Yandex...' (134-167 слов)"},
  {"severity": "warning", "category": "citability", "issue": "Средняя длина пассажа 312 слов — слишком много для AI extraction", "fix": "Разбить длинные абзацы на self-contained блоки по 134-167 слов каждый", "indicator": "Частота попадания в AI Overviews"},
  {"severity": "info", "category": "schema", "issue": "Добавить Organization schema для brand entity recognition", "fix": "См. seo-schema skill — авто-генерация JSON-LD", "indicator": "Brand mention frequency в LLM ответах"}
]
```

## How to Optimize for AI Overviews

**Step 1:** Convert key sections to Q&A format
**Step 2:** Make passages 134-167 words and self-contained  
**Step 3:** Add structured data (Organization, Product, FAQ)
**Step 4:** Ensure dates, author byline, sources
**Step 5:** Remove filler and generic statements
**Step 6:** Add specific examples, numbers, data
