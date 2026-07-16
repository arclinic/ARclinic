# Content Factory - SMM Agent Usage Guide

## Быстрый старт

### 1. Установка зависимостей

```bash
pip install -r requirements.txt
```

### 2. Настройка API ключей (автоматическая)

Просто запустите любой скрипт — агент сам запросит ключи:

```bash
python setup.py              # явный запуск мастера настройки
python research.py --platform x --setup  # только настройка
python planner.py --setup    # только настройка
```

Или ключи будут запрошены автоматически при первом запуске:

```bash
python research.py --platform x      # запросит ключи если их нет
python planner.py --with-ai          # запросит ключи если их нет
```

Мастер настройки:
- Покажет описание каждого ключа и ссылку где его получить
- Скроет ввод при наборе секретных ключей
- Предложит выбор модели (DeepSeek или Qwen)
- Сохранит ключи в файл `.env` (не попадает в git)
- Запомнит ключи — повторно спрашивать не будет

**Требуемые ключи:**
- **Apify** (скрапинг соцсетей): https://console.apify.com/account/integrations
- **TubeLab** (YouTube аналитика): https://tubelab.net/settings/api
- **Gemini** (анализ видео): https://aistudio.google.com/apikey
- **AI модель** (DeepSeek V4 Pro через Promptra): регистрация на promptra.ru, ключ в `AI_API_KEY`

Чтобы изменить настройки позже — просто запустите `python setup.py` снова.

### 3. База знаний (встроена)

`knowledge_base.md` уже включён в проект — это синхронизированная копия папки «мозг» и проекта «Аватары» из Anna_business_26.

**Содержит:**
- Личность Анны Резник (биография, ценности, научная деятельность: 25+ публикаций, 10+ лет конгрессов)
- Голос и тон (характеристики, любимые обороты, запреты, режим "эксперт" на конгрессах)
- ARclinic (позиционирование, услуги, 15 врачей с прозвищами и характеристиками)
- Аудитория (75 аватаров, 14 сегментов: премиум, мужские, корпоративные, средний/низкий доход)
- Возражения по сегментам с реальными историями пациентов
- JTBD (Jobs to Be Done) для каждого сегмента
- Когнитивные искажения и путь клиента (5 стадий LXM)
- Принципы контента (главные правила, форматы, отбор тем)
- Принципы бизнеса и экономика (метрики, сезонность)

**Агент использует эту базу при генерации всех контент-идей и стратегий.** Работает на любом устройстве — папки «мозг» и «avatars» не нужны.

При обновлении информации в Anna_business_26 — синхронизируйте knowledge_base.md.

**Агент использует эту базу при генерации всех контент-идей и стратегий.** Работает на любом устройстве — папка «мозг» не нужна.

При обновлении информации в Anna_business_26/мозг/ — синхронизируйте knowledge_base.md.

### 4. Настройка аккаунтов для мониторинга

Отредактируйте `config/accounts.json` - добавьте конкурентов и benchmark-аккаунты для отслеживания.

### 5. Запуск исследования

```bash
# Исследование одной платформы
python research.py --platform x
python research.py --platform instagram
python research.py --platform youtube
python research.py --platform tiktok

# Полный контент-план по всем платформам
python planner.py

# Полный контент-план с AI-генерацией идей (DeepSeek V4 Pro через Promptra)
python planner.py --with-ai --model deepseek
```

AI будет генерировать идеи строго в голосе Анны, с учётом всех запретов и принципов из knowledge_base.md.

## Структура результатов

```
output/
├── research/
│   ├── x/2026-06-11/
│   │   ├── raw.json          # Сырые данные API
│   │   ├── outliers.json      # Вирусные посты
│   │   ├── video-analysis.json # AI-анализ видео
│   │   └── report.md          # Отчет для чтения
│   ├── instagram/...
│   ├── youtube/...
│   └── tiktok/...
└── content-plans/
    └── 2026-06-11/
        ├── content-ideas.md      # Идеи контента от AI
        ├── x-playbook.md         # Стратегия для X
        ├── instagram-playbook.md # Стратегия для Instagram
        ├── youtube-playbook.md   # Стратегия для YouTube
        └── tiktok-playbook.md    # Стратегия для TikTok
```

## Формулы вовлеченности

### X/Twitter
```
engagement = bookmarks×4 + replies×3 + retweets×2 + quotes×2 + likes×1
```

### Instagram
```
engagement = likes + comments×3 + views×0.1
```

### TikTok
```
engagement = likes + comments×3 + shares×2 + saves×2 + views×0.05
```

### YouTube
```
score = zScore × recency_boost (5% daily decay)
```

### Определение выбросов
```
outlier = score > mean + (2.0 × std_dev)
```

## Отличия от оригинала

| | Оригинальный head-of-content | Content Factory |
|---|---|---|
| **Модель** | Claude (проприетарная) | DeepSeek V4 Pro (через Promptra) |
| **Платформа** | Claude Desktop + Cowork | CLI (любая ОС) |
| **Формат скиллов** | `.skill` (бинарный, Claude-only) | Python-скрипты |
| **Стоимость** | Claude Max Plan ($200/мес) | API-ключи по тарифам |
| **Расширяемость** | Ограничена Claude ecosystem | Открытый Python код |
| **База знаний** | Нет | knowledge_base.md (бренд, голос, аудитория) |

## Примечания

- Скрапинг X через Apify требует платной подписки (~$0.10-$0.50 за запуск)
- Бесплатный лимит Gemini: 60 запросов/мин (достаточно для анализа)
- TubeLab бесплатен для базового использования, Pro от ~$29/мес
