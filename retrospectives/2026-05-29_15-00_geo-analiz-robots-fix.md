# Ретроспектива: 2026-05-29 15:00

## Какая задача была поставлена
GEO-анализ ARclinic (AI Visibility — ChatGPT, Perplexity, AI Overviews) + технические исправления.

## Как я её решал
1. Загрузил скилл seo-geo
2. Проверил robots.txt (GPTBot/ClaudeBot/PerplexityBot заблокированы), llms.txt (отсутствует)
3. Проверил главную страницу (schema, og-теги, meta description, заголовки)
4. Проверил блог-статью (структура, автор, дата, схема)
5. Написал GEO-ANALYSIS.md с полным аудитом по 5 критериям (итог: 38/100)
6. Исправил robots.txt (3 изменения) через Bitrix admin — с дублями и перезаписями

## Решил ли
да (GEO анализ готов, robots.txt исправлен)

## Эффективно ли решение, что можно было лучше
- GEO-анализ получился полным и структурированным — можно сразу действовать по топ-5 быстрых изменений
- robots.txt фиксился с 4 попыток — код сработал, но из-за race condition (дважды добавилась AI-секция)
- Лучше: после каждого save делать verify сразу, а не ждать
- Битрексовый редактор без `full_src=Y` использует CodeMirror — пришлось разбираться с видимостью textarea
- fetch-based save через FormData сработал, cloneNode подход не нужен — достаточно FormData + POST

## Как было и как стало
**robots.txt:**
- Было: `User-agent: *` первым правилом (GPTBot/OAI-SearchBot/ClaudeBot/PerplexityBot заблокированы), `Disallow: *utm*= ` блокировал UTM-страницы, `Sitemap: sitemap.xml`
- Стало: AI-краулеры разрешены в начале файла, `Disallow: *utm*= ` удалён, `Sitemap: sitemap_index.xml`

**GEO:**
- Не было анализа AI Visibility
- Стало: документ GEO-ANALYSIS.md с 5 критериями, скорингом 38/100, топ-10 рекомендаций

## Что записать в ai-clone/feedback/
- robots.txt для Bitrix: не использовать cloneNode для формы — FormData напрямую с `fd.set('filesrc', value)` + fetch работает без перезагрузки
- Save через input click в Битриксе НЕ срабатывает для CodeMirror-редактора — код отправляется, но файл не сохраняется. Нужно FormData + fetch.
- После каждого save сразу проверять response через отдельный запрос (curl/Invoke-WebRequest)
