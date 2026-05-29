# Ретроспектива: 2026-05-29 SEO-фиксы + Q3 Phase 1-2

## Какая задача была поставлена
1. Починить OG-теги (AddHeadString с http://, robots.txt, og:description)
2. OG image 1200×630
3. Q3 продвижение: начать Phase 1 (аудит) и Phase 2 (контент)

## Как я решал
1. **SEO-фиксы:** параллельная работа: чтение header.php через Bitrix code editor, замена AddHeadString через cloneNode+FormData на 6 страницах, исправление robots.txt
2. **OG image:** создал HTML/CSS дизайн, сделал screenshot через Playwright (1200×630), загрузил через Bitrix file upload, обновил og:image в header.php
3. **Q3 Phase 1:** прочитал все business/ файлы, проверил сайт (blog, Telegram, /dlya-muzhchin/), составил аудит в плане
4. **Q3 Phase 2:** создал UTM-document, 30 scenarios, Telegram content plan, Yandex.Direct prep, men landing prototype, reviews collection system

## Решил ли
да, все задачи выполнены

## Эффективно ли решение, что можно было лучше
- **OG image:** получился минималистичный, но без логотипа клиники (нет доступа к брендбуку). Можно улучшить, когда будет брендбук.
- **Bitrix24 API:** токен не работает (INVALID_CREDENTIALS). Нужно создать новый вебхук в Bitrix24.
- **Phase 2** подготовлена как контент, но не развёрнута на сайтах/в кабинетах — это требует ручного доступа.
- **CloneNode+FormData** для сохранения в Bitrix — работает надёжно. Метод отточен.

## Как было и как стало
- OG-теги: были с http:// и AddHeadString (3 строки на каждой странице) → единый источник в header.php, https://
- robots.txt: указывал на sitemap.xml с localhost → sitemap_index.xml
- Meta description: хардкод → динамический с fallback
- OG image: favicon (96×96) → 1200×630 дизайнерский
- UTM: не было → структура и стандарт
- 30 сценариев: не было → готовый файл
- Telegram контент-план: не было → 4 недели
- Marketing: не было системного аудита → полная картина Phase 1

## Что записать в ai-clone/feedback/
- OG image можно создавать через Playwright screenshot HTML/CSS, если нет доступа к image-gen инструментам
- Bitrix24 REST API может выдавать INVALID_CREDENTIALS — проверять токен через простой GET-запрос без параметров
- При upload файлов в Bitrix: сначала нужно открыть диалог выбора файла (щелчок по input), потом setInputFiles
