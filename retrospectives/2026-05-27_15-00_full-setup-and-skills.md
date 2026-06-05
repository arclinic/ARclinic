# Ретроспектива: 2026-05-27

## Что сделано
- Установлены скиллы: bulletproof (внешний репо), skill-creator, frontend-design, pdf (+ 8 скриптов), pptx (+ 60+ файлов) — все в `~/.claude/skills/`
- Создан daily-report skill (`~/.claude/skills/daily-report/SKILL.md`)
- Создан `.opencode/opencode.json` — конфиг OpenCode (MCP Playwright, permissions, skills paths)
- Установлен Playwright MCP (@playwright/mcp)
- Скачаны браузеры Playwright (chromium, headless shell, ffmpeg)
- Решена проблема ExecutionPolicy: вместо npx/pnpm используем npx.cmd/npm.cmd
- Создан `.env` с B24_TOKEN (токен: ti9ujbt1f9z0bq6c)
- Chrome extension Claude — страница открыта, кнопка «Установить» недоступна (нет Google-аккаунта)
- Скриншот headless Chrome сделан (`google-search-result.png`)

## Что не получилось
- Автоустановка Claude Chrome extension — кнопка disabled без входа в Google-аккаунт
- Daily-report через skill-creator — прервался, создан вручную

## Выучено
- Установка extension через Playwright требует авторизованного Google-аккаунта в Chrome
- npx.cmd обходит PowerShell ExecutionPolicy
- Bitrix24 REST API работает (проверено profile.json)

## Feedback для ai-clone/feedback/
- (нет новых правил)

## Статус задач
- Playwright MCP: готов
- opencode.json: готов
- .env с B24_TOKEN: готов
- Daily-report skill: готов
- Chrome extension: отменено
