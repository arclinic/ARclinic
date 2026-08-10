---
name: seo-content
description: "Анализ контента и E-E-A-T: качество текста, заголовки H1-H6, мета-теги title/description, структура, экспертиза автора. Запускай когда нужен контент-аудит."
---

# SEO Content Audit Sub-Skill

## Когда запускать

Когда пользователь хочет проверить:
- Качество контента страницы
- Структуру заголовков H1-H6
- Мета-теги title и description
- E-E-A-T сигналы (опыт, экспертиза, авторитетность, доверие)
- Читаемость и полезность текста

## Инструменты

```bash
python scripts/seo/seo_fetch.py <url>
```

## Checklist

### 1. Title Tag
- **Длина**: 50-60 символов (идеал), 30-70 (допустимо)
- **Содержимое**: основной ключ + бренд
- **Уникальность**: не дублирует H1

### 2. Meta Description
- **Длина**: 120-160 символов (идеал), 80-200 (допустимо)
- **CTA**: призыв к действию
- **Ключевые слова**: естественно вписаны

### 3. H1 Tag
- **Присутствие**: ровно один H1 на странице
- **Ключ** в заголовке
- **Не дублирует** title полностью

### 4. Heading Hierarchy
- H1 → H2 → H3, без пропусков
- Логическая структура
- Ключевые темы в H2

### 5. Content Quality
- **Минимум слов**: 300+ для обычных страниц, 1000+ для статей
- **Параграфы**: короткие (3-5 предложений)
- **Списки**: ul/ol для перечислений
- **Болд/курсив**: выделение ключевых фраз
- **Без воды**: нет filler-предложений

### 6. E-E-A-T Signals

| Signal | Что искать |
|--------|-----------|
| **Experience** | Case studies, "я попробовал", реальные фото, личный опыт |
| **Expertise** | Автор указан с credentials, глубина анализа, терминология |
| **Authoritativeness** | Внешние ссылки на авторитетные источники, упоминания в других местах |
| **Trustworthiness** | Contact page, о компании, дата публикации/обновления, HTTPS |

### 7. Filler Detection
Ищи признаки "воды":
- Повторяющиеся фразы без новой информации
- Обобщения без конкретики ("многие люди считают что...")
- Длинные вводные без сути
- Списки ради списков (без actionable content)

### 8. AI Content Patterns
Признаки AI-generated текста:
- Чрезмерно формальный тон
- Повторяющаяся структура (параграф → буллеты → параграф)
- Одинаковая длина абзацев
- Generic statements без specifics
- Отсутствие реальных примеров

## Scoring

```
base_score = 100

# Title
- Нет title: -20
- Title < 30 chars: -5
- Title > 70 chars: -3

# Description  
- Нет description: -15
- Description < 80 chars: -5
- Description > 200 chars: -3

# H1
- Нет H1: -10
- Больше одного H1: -5

# Content length
- < 300 слов: -15
- 300-500: -5
- 500-800: -2

# Structure
- Параграфы > 5 предложений (avg): -5
- Нет списков: -3
- Heading hierarchy нарушена: -8

# E-E-A-T
- Нет автора/credentials: -5
- Нет даты публикации: -5
- Нет внешних authoritative ссылок: -3
- Нет contact page: -3

# AI patterns (soft)
- Filler > 30%: -10
- AI-паттерны обнаружены: -5 (info only)
```

## Output Format

```json
{
  "score": 0-100,
  "grade": "A/B+/B/C/D/F",
  "title": {"text": "...", "length": 0, "issues": []},
  "description": {"text": "...", "length": 0, "issues": []},
  "h1": {"text": "...", "count": 1, "issues": []},
  "headings_structure": {"h1": 1, "h2": 5, "h3": 12, "issues": []},
  "content": {
    "word_count": 1500,
    "readability": "good",
    "paragraphs": 20,
    "lists": 5,
    "bolt_italic_usage": "good"
  },
  "e_e_a_t": {
    "experience": "weak/medium/strong",
    "expertise": "weak/medium/strong",
    "authoritativeness": "weak/medium/strong",
    "trustworthiness": "weak/medium/strong",
    "issues": []
  },
  "ai_patterns": {
    "detected": false,
    "signals": []
  },
  "findings": [
    {"severity": "critical|warning|info", "category": "title|description|content|e-eat", "issue": "...", "fix": "..."}
  ]
}
```

## Example Findings

```json
[
  {"severity": "warning", "category": "title", "issue": "Title слишком длинный (87 символов)", "fix": "Сократить до 50-60 символов, оставить ключ + бренд", "indicator": "CTR в поисковой выдаче"},
  {"severity": "critical", "category": "e-eat", "issue": "Нет информации об авторе или credentials", "fix": "Добавить блок об авторе с опытом и ссылками", "indicator": "Google Quality Rater Guidelines §4.6"},
  {"severity": "info", "category": "content", "issue": "Обнаружены AI-паттерны: повторяющаяся структура абзацев", "fix": "Добавить конкретные примеры, личные наблюдения, уникальные данные", "indicator": "User engagement metrics"}
]
```
