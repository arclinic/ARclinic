"""
Конкурентный анализ SMM-активности.
Автоматический сбор метрик из Telegram (Telethon) и VK (API).
Поиск незанятых ниш и идей для контента.

Usage:
  python competitor_analyzer.py --update              # полный анализ всех конкурентов
  python competitor_analyzer.py --platform tg          # только Telegram
  python competitor_analyzer.py --platform vk          # только VK
  python competitor_analyzer.py --competitor ggmed     # один конкурент
  python competitor_analyzer.py --gaps                 # поиск незанятых ниш
  python competitor_analyzer.py --list                 # список конкурентов с соцсетями
"""

import os, sys, json, asyncio, re
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List, Tuple
from pathlib import Path
from collections import Counter, defaultdict

import requests

ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT))
from dotenv import load_dotenv
load_dotenv(ROOT / ".env")

SMM_DIR = Path(__file__).resolve().parent
REPORTS_DIR = ROOT / "reports" / "competitors"

VK_TOKEN = os.getenv("VK_ACCESS_TOKEN", "")
VK_API_VERSION = "5.199"

TELEGRAM_PHONE = os.getenv("TG_PHONE", "+79312440044")
TELEGRAM_SESSION = str(SMM_DIR / "arclinic_user_session")
TELEGRAM_API_ID = 2040
TELEGRAM_API_HASH = "b18441a1ff607e10a989891a5462e627"


class CompetitorAnalyzer:
    """Анализатор SMM-активности конкурентов."""

    def __init__(self):
        self.data_path = SMM_DIR / "competitors_data.json"
        self._load_data()

    def _load_data(self):
        with open(self.data_path, "r", encoding="utf-8") as f:
            raw = json.load(f)
        self.theme_keywords = raw["theme_keywords"]
        self.competitors = raw["competitors"]

    # ── Telegram ────────────────────────────────────────────

    async def _analyze_telegram_channel(
        self, username: str, limit: int = 100, client=None
    ) -> Optional[dict]:
        """Анализирует Telegram-канал через Telethon.

        client: существующий клиент (для массового анализа).
        Если не передан — создаётся и закрывается внутри метода.
        """
        from telethon import TelegramClient, functions, types

        owns_client = client is None
        try:
            if owns_client:
                client = TelegramClient(TELEGRAM_SESSION, TELEGRAM_API_ID, TELEGRAM_API_HASH)
                await client.start(phone=TELEGRAM_PHONE)

            entity = await client.get_entity(username)
            participants = 0
            is_channel = isinstance(entity, (types.Channel, types.Chat))
            if is_channel:
                full = await client(functions.channels.GetFullChannelRequest(entity))
                participants = full.full_chat.participants_count or 0

            posts = []
            async for msg in client.iter_messages(entity, limit=limit):
                if is_channel and not msg.post:
                    continue
                caption = getattr(msg, "caption", None)
                text = (msg.text or caption or "").strip()

                posts.append({
                    "id": msg.id,
                    "date": msg.date.strftime("%Y-%m-%d %H:%M"),
                    "weekday": msg.date.strftime("%A"),
                    "hour": msg.date.hour,
                    "views": msg.views or 0,
                    "forwards": msg.forwards or 0,
                    "reactions": self._count_reactions(msg),
                    "has_photo": bool(msg.photo),
                    "has_video": bool(msg.video),
                    "has_document": bool(msg.document),
                    "text_length": len(text),
                    "text": text,
                    "has_link": "http" in text,
                    "has_hashtag": "#" in text,
                })

            if not posts:
                return None

            return self._compute_metrics(
                posts=posts,
                platform="telegram",
                channel_name=getattr(entity, "title", getattr(entity, "first_name", username)),
                channel_username=username,
                subscribers=participants,
            )

        except Exception as e:
            print(f"  [TG] Ошибка @{username}: {e}")
            return None
        finally:
            if owns_client and client is not None:
                try:
                    await client.disconnect()
                except Exception:
                    pass

    @staticmethod
    def _count_reactions(msg) -> int:
        if not msg.reactions:
            return 0
        return sum(rc.count for rc in msg.reactions.results)

    # ── VK ──────────────────────────────────────────────────

    def _analyze_vk_community(
        self, domain: str, limit: int = 100
    ) -> Optional[dict]:
        """Анализирует VK-сообщество через API."""
        try:
            info = self._vk_api("groups.getById", group_id=domain)
            if not info or "response" not in info:
                print(f"  [VK] Сообщество не найдено: {domain}")
                return None

            groups = info["response"].get("groups", [])
            if not groups:
                print(f"  [VK] Сообщество не найдено: {domain}")
                return None
            group = groups[0]
            group_name = group.get("name", domain)
            members_count = 0

            try:
                members = self._vk_api("groups.getMembers", group_id=group["id"])
                if members and "response" in members:
                    members_count = members["response"].get("count", 0)
            except Exception:
                pass

            offset = 0
            all_posts = []
            while len(all_posts) < limit:
                wall = self._vk_api("wall.get", owner_id=f"-{group['id']}",
                                    count=min(100, limit - len(all_posts)),
                                    offset=offset)
                if not wall or "response" not in wall:
                    break
                items = wall["response"].get("items", [])
                if not items:
                    break
                for item in items:
                    text = item.get("text", "").strip()
                    all_posts.append({
                        "id": item["id"],
                        "date": datetime.fromtimestamp(item["date"]).strftime("%Y-%m-%d %H:%M"),
                        "weekday": datetime.fromtimestamp(item["date"]).strftime("%A"),
                        "hour": datetime.fromtimestamp(item["date"]).hour,
                        "likes": item.get("likes", {}).get("count", 0),
                        "reposts": item.get("reposts", {}).get("count", 0),
                        "comments": item.get("comments", {}).get("count", 0),
                        "views": item.get("views", {}).get("count", 0),
                        "has_photo": self._vk_has_attachment(item, "photo"),
                        "has_video": self._vk_has_attachment(item, "video"),
                        "text_length": len(text),
                        "text": text,
                        "has_link": "http" in text or "vk.cc" in text,
                        "has_hashtag": "#" in text,
                        "is_pinned": item.get("is_pinned", 0),
                    })
                offset += 100
                if offset >= wall["response"].get("count", 0):
                    break

            unpinned = [p for p in all_posts if not p.get("is_pinned")]
            if not unpinned:
                unpinned = all_posts
            unpinned = unpinned[:limit]

            if not unpinned:
                return None

            return self._compute_metrics(
                posts=unpinned,
                platform="vk",
                channel_name=group_name,
                channel_username=domain,
                subscribers=members_count,
            )

        except Exception as e:
            print(f"  [VK] Ошибка {domain}: {e}")
            return None

    @staticmethod
    def _vk_has_attachment(item: dict, att_type: str) -> bool:
        for att in item.get("attachments", []):
            if att.get("type") == att_type:
                return True
        return False

    def _vk_api(self, method: str, **params) -> dict:
        params.setdefault("v", VK_API_VERSION)
        params.setdefault("access_token", VK_TOKEN)
        url = f"https://api.vk.com/method/{method}"
        resp = requests.get(url, params=params, timeout=15)
        return resp.json()

    # ── Общие метрики ───────────────────────────────────────

    def _compute_metrics(
        self, posts: List[dict], platform: str,
        channel_name: str, channel_username: str, subscribers: int
    ) -> dict:
        total = len(posts)
        if platform == "telegram":
            eng_values = [p["views"] for p in posts]
            fwd_values = [p["forwards"] for p in posts]
            react_values = [p["reactions"] for p in posts]
        else:
            eng_values = [p["views"] + p["likes"] * 2 + p["comments"] * 3 for p in posts]
            fwd_values = [p["reposts"] for p in posts]
            react_values = [p["likes"] for p in posts]

        sorted_eng = sorted(eng_values)
        dates = sorted(p["date"] for p in posts)

        if total >= 2:
            intervals = []
            for i in range(1, len(dates)):
                d1 = datetime.strptime(dates[i - 1], "%Y-%m-%d %H:%M")
                d2 = datetime.strptime(dates[i], "%Y-%m-%d %H:%M")
                intervals.append((d2 - d1).total_seconds() / 3600)
            avg_interval_hrs = sum(intervals) / len(intervals)
            total_span_days = (
                datetime.strptime(dates[-1], "%Y-%m-%d %H:%M")
                - datetime.strptime(dates[0], "%Y-%m-%d %H:%M")
            ).total_seconds() / 86400
            posts_per_week = total / (total_span_days / 7) if total_span_days > 0 else 0
        else:
            avg_interval_hrs = 0
            posts_per_week = total

        er_pct = round((sum(eng_values) / total / subscribers * 100), 2) if total and subscribers else 0

        weekday_stats = defaultdict(lambda: {"count": 0, "total_eng": 0})
        for p in posts:
            wd = p["weekday"]
            eng = p["views"] if platform == "telegram" else (p["views"] + p["likes"] * 2 + p["comments"] * 3)
            weekday_stats[wd]["count"] += 1
            weekday_stats[wd]["total_eng"] += eng
        for wd in weekday_stats:
            weekday_stats[wd]["avg_eng"] = (
                weekday_stats[wd]["total_eng"] // weekday_stats[wd]["count"]
                if weekday_stats[wd]["count"] else 0
            )

        formats = {
            "text_only": sum(1 for p in posts if not p["has_photo"] and not p["has_video"]),
            "with_photo": sum(1 for p in posts if p["has_photo"]),
            "with_video": sum(1 for p in posts if p["has_video"]),
        }
        dominant_format = max(formats, key=formats.get) if total else "text_only"

        themes = self._extract_themes([p["text"] for p in posts])

        all_text = " ".join(p["text"] for p in posts).lower()
        tone_signals = {
            "promo": sum(1 for w in ["скидк", "акци", "%", "выгод", "спецпредлож"] if w in all_text),
            "educational": sum(1 for w in ["почему", "как работает", "разбираем", "важно знать", "исследовани"] if w in all_text),
            "lifestyle": sum(1 for w in ["закулисье", "команда", "врач", "истори", "утро", "день"] if w in all_text),
            "case": sum(1 for w in ["результат", "до/после", "кейс", "пациент", "история пациент"] if w in all_text),
        }
        dominant_tone = max(tone_signals, key=tone_signals.get) if any(tone_signals.values()) else "mixed"

        return {
            "channel_name": channel_name,
            "channel_username": channel_username,
            "platform": platform,
            "subscribers": subscribers,
            "period_from": dates[0] if dates else None,
            "period_to": dates[-1] if dates else None,
            "summary": {
                "total_posts": total,
                "posts_per_week": round(posts_per_week, 1),
                "avg_interval_hours": round(avg_interval_hrs, 1),
                "avg_views": sum(eng_values) // total if total else 0,
                "median_views": sorted_eng[total // 2] if total else 0,
                "max_views": max(eng_values) if eng_values else 0,
                "avg_forwards": sum(fwd_values) // total if total else 0,
                "avg_reactions": sum(react_values) // total if total else 0,
                "er_pct": er_pct,
            },
            "weekday_stats": dict(weekday_stats),
            "formats": formats,
            "dominant_format": dominant_format,
            "themes": themes,
            "tone": tone_signals,
            "dominant_tone": dominant_tone,
            "top_posts": sorted(posts, key=lambda p: (
                p["views"] if platform == "telegram"
                else (p["views"] + p["likes"] * 2 + p["comments"] * 3)
            ), reverse=True)[:3],
            "raw_posts": posts,
        }

    def _extract_themes(self, texts: List[str]) -> Dict[str, int]:
        combined = " ".join(texts).lower()
        result = {}
        for theme, keywords in self.theme_keywords.items():
            count = sum(1 for kw in keywords if kw in combined)
            if count > 0:
                result[theme] = count
        return dict(sorted(result.items(), key=lambda x: x[1], reverse=True))

    # ── Сбор данных ─────────────────────────────────────────

    def _competitors_with_telegram(self) -> List[Tuple[str, dict]]:
        return [
            (key, comp) for key, comp in self.competitors.items()
            if comp.get("telegram")
        ]

    def _competitors_with_vk(self) -> List[Tuple[str, dict]]:
        return [
            (key, comp) for key, comp in self.competitors.items()
            if comp.get("vk")
        ]

    def list_competitors(self) -> str:
        """Выводит список конкурентов и их соцсетей."""
        lines = [
            f"{'─' * 80}",
            f"{'Клиника':<30} {'Группа':<18} {'TG':<25} {'VK':<25}",
            f"{'─' * 80}",
        ]
        for key, comp in self.competitors.items():
            tg = comp.get("telegram", "") or "—"
            vk = comp.get("vk", "") or "—"
            group = comp.get("group_name", "")[:17]
            lines.append(f"{comp['name']:<30} {group:<18} {tg:<25} {vk:<25}")
        lines.append(f"{'─' * 80}")
        lines.append(f"Всего конкурентов: {len(self.competitors)}")
        lines.append(f"С Telegram: {len(self._competitors_with_telegram())}")
        lines.append(f"С VK: {len(self._competitors_with_vk())}")
        return "\n".join(lines)

    async def analyze_all_telegram(self, limit: int = 100) -> Dict[str, dict]:
        """Анализирует всех конкурентов в Telegram (одно подключение на всех)."""
        from telethon import TelegramClient

        results = {}
        tg_competitors = self._competitors_with_telegram()
        if not tg_competitors:
            print("Нет конкурентов с Telegram-каналами.")
            return results

        print(f"\n{'='*60}")
        print(f"  Анализ Telegram: {len(tg_competitors)} конкурентов")
        print(f"{'='*60}")

        client = TelegramClient(TELEGRAM_SESSION, TELEGRAM_API_ID, TELEGRAM_API_HASH)
        try:
            await client.start(phone=TELEGRAM_PHONE)
            print(f"Подключено: {await client.get_me()}")

            for key, comp in tg_competitors:
                username = comp["telegram"]
                print(f"\n► {comp['name']} (@{username})")
                result = await self._analyze_telegram_channel(username, limit, client=client)
                if result:
                    results[key] = result
                    s = result["summary"]
                    print(f"  Подписчики: {result['subscribers']}  |  Постов: {s['total_posts']}")
                    print(f"  ER: {s['er_pct']}%  |  Постов/нед: {s['posts_per_week']}  |  Формат: {result['dominant_format']}")
                else:
                    print(f"  ⚠ Не удалось собрать данные")
        finally:
            try:
                await client.disconnect()
            except Exception:
                pass
        return results

    def analyze_all_vk(self, limit: int = 100) -> Dict[str, dict]:
        """Анализирует всех конкурентов в VK."""
        results = {}
        vk_competitors = self._competitors_with_vk()
        if not vk_competitors:
            print("Нет конкурентов с VK-сообществами.")
            return results

        print(f"\n{'='*60}")
        print(f"  Анализ VK: {len(vk_competitors)} конкурентов")
        print(f"{'='*60}")

        for key, comp in vk_competitors:
            domain = comp["vk"]
            print(f"\n► {comp['name']} (vk.com/{domain})")
            result = self._analyze_vk_community(domain, limit)
            if result:
                results[key] = result
                s = result["summary"]
                print(f"  Подписчики: {result['subscribers']}  |  Постов: {s['total_posts']}")
                print(f"  ER: {s['er_pct']}%  |  Постов/нед: {s['posts_per_week']}  |  Формат: {result['dominant_format']}")
            else:
                print(f"  ⚠ Не удалось собрать данные")
        return results

    # ── Отчёты ──────────────────────────────────────────────

    def _save_raw(self, results: Dict[str, dict], platform: str):
        date_str = datetime.now().strftime("%Y%m%d_%H%M")
        os.makedirs(REPORTS_DIR, exist_ok=True)
        path = REPORTS_DIR / f"raw_{platform}_{date_str}.json"
        serializable = {}
        for key, data in results.items():
            d = dict(data)
            d.pop("raw_posts", None)
            d.pop("top_posts", None)
            serializable[key] = d
        with open(path, "w", encoding="utf-8") as f:
            json.dump(serializable, f, indent=2, ensure_ascii=False)
        return path

    def _load_previous(self, platform: str) -> Optional[Dict[str, dict]]:
        """Загружает предыдущий отчёт для сравнения."""
        if not REPORTS_DIR.exists():
            return None
        files = sorted(REPORTS_DIR.glob(f"raw_{platform}_*.json"), reverse=True)
        if not files:
            return None
        with open(files[0], "r", encoding="utf-8") as f:
            return json.load(f)

    def generate_report(self, results: Dict[str, dict], platform: str) -> str:
        """Генерирует Markdown-отчёт."""
        date_str = datetime.now().strftime("%Y-%m-%d %H:%M")
        prev = self._load_previous(platform)

        lines = [
            f"# Конкурентный анализ SMM — {platform.upper()}",
            f"**Дата:** {date_str}",
            f"**Платформа:** {platform}",
            f"**Конкурентов с данными:** {len(results)}",
            "",
        ]

        if not results:
            lines.append("⚠ Нет данных для отчёта. Добавьте ссылки на соцсети в competitors_data.json.")
            return "\n".join(lines)

        # Сводная таблица
        lines.extend([
            "## Сводка",
            "",
            "| Клиника | Подписчики | Постов/нед | ER% | Доминантный формат | Доминантный тон | Топ-темы |",
            "|---------|-----------|------------|-----|--------------------|-----------------|----------|",
        ])
        for key, m in results.items():
            comp = self.competitors.get(key, {})
            name = comp.get("name", key)
            s = m["summary"]
            themes_top = ", ".join(list(m["themes"].keys())[:3])
            prev_er = ""
            if prev and key in prev and "summary" in prev[key]:
                old_er = prev[key]["summary"].get("er_pct", 0)
                if old_er and s["er_pct"]:
                    delta = s["er_pct"] - old_er
                    prev_er = f" {'↑' if delta > 0 else '↓'}{abs(delta):.1f}пп"

            lines.append(
                f"| {name} | {m['subscribers']} | {s['posts_per_week']} | "
                f"{s['er_pct']}{prev_er} | {m['dominant_format']} | "
                f"{m['dominant_tone']} | {themes_top or '—'} |"
            )

        # Детально по каждому конкуренту
        lines.extend(["", "## Детальный анализ", ""])
        for key, m in results.items():
            comp = self.competitors.get(key, {})
            name = comp.get("name", key)
            s = m["summary"]
            lines.extend([
                f"### {name}",
                f"- **Канал:** {m['channel_name']} ({'@' if platform == 'tg' else 'vk.com/'}{m['channel_username']})",
                f"- **Подписчики:** {m['subscribers']}",
                f"- **Период:** {m['period_from']} → {m['period_to']}",
                f"- **Постов:** {s['total_posts']} | Постов/нед: {s['posts_per_week']} | Интервал: {s['avg_interval_hours']}ч",
                f"- **Просмотры:** ср. {s['avg_views']} | мед. {s['median_views']} | макс. {s['max_views']}",
                f"- **Вовлечённость:** ER {s['er_pct']}% | репостов/пост {s['avg_forwards']} | реакций/пост {s['avg_reactions']}",
                f"- **Форматы:** текст {m['formats']['text_only']} | фото {m['formats']['with_photo']} | видео {m['formats']['with_video']}",
                f"- **Тональность:** {m.get('dominant_tone', '—')}",
                f"- **Темы:** {', '.join(f'{t}({c})' for t, c in m['themes'].items()) or '—'}",
                "",
            ])

        # Сравнение с предыдущим периодом
        if prev:
            lines.extend(["## Изменения vs предыдущий период", ""])
            changes_found = False
            for key, m in results.items():
                if key not in prev or "summary" not in prev[key]:
                    continue
                old = prev[key]["summary"]
                new = m["summary"]
                deltas = []
                if old.get("posts_per_week") and new["posts_per_week"]:
                    d = new["posts_per_week"] - old["posts_per_week"]
                    if abs(d) > 0.5:
                        deltas.append(f"постов/нед {d:+.1f}")
                if old.get("er_pct") and new["er_pct"]:
                    d = round(new["er_pct"] - old["er_pct"], 1)
                    if abs(d) > 0.05:
                        deltas.append(f"ER {d:+.1f}пп")
                if deltas:
                    changes_found = True
                    name = self.competitors.get(key, {}).get("name", key)
                    lines.append(f"- **{name}:** {', '.join(deltas)}")
            if not changes_found:
                lines.append("- Значимых изменений нет")

        # Незанятые ниши
        lines.extend(["", "## Незанятые ниши (темы, которые не покрывают конкуренты)", ""])
        all_covered = set()
        for m in results.values():
            all_covered.update(m["themes"].keys())
        all_themes = set(self.theme_keywords.keys())
        gaps = all_themes - all_covered
        if gaps:
            for g in sorted(gaps):
                lines.append(f"- **{g.replace('_', ' ')}** — нет ни у одного конкурента")
        else:
            lines.append("- Все ключевые темы покрываются конкурентами")

        # Рекомендации
        lines.extend([
            "",
            "## Рекомендации для ARclinic",
            "",
            "### Что перенять",
        ])
        top_format = Counter(m["dominant_format"] for m in results.values()).most_common(2)
        lines.extend(f"- Конкуренты чаще всего постят в формате: **{f[0]}** (у {f[1]} из {len(results)})" for f in top_format)

        top_tones = Counter(m["dominant_tone"] for m in results.values()).most_common(2)
        lines.extend(f"- Доминирующая тональность: **{t[0]}** (у {t[1]} из {len(results)})" for t in top_tones)

        high_er = sorted(results.items(), key=lambda x: x[1]["summary"].get("er_pct", 0), reverse=True)
        if high_er:
            best = high_er[0]
            name = self.competitors.get(best[0], {}).get("name", best[0])
            lines.append(f"- Лучший ER: **{name}** ({best[1]['summary']['er_pct']}%) — изучить их контент")

        lines.extend([
            "",
            "### Что делать ARclinic",
            f"- Занять ниши: {', '.join(sorted(gaps)).replace('_', ' ') if gaps else 'искать смежные темы'}",
            "- Усилить форматы, которых нет у конкурентов (видео-рубрики, карусели с инфографикой)",
            "- Делать акцент на уникальные УТП: геронтология, лечение осложнений, ботокс от невролога",
        ])

        return "\n".join(lines)

    def find_gaps(self) -> List[str]:
        """Возвращает список незанятых конкурентами тем."""
        brain_path = ROOT / "мозг_клиники_ARclinic" / "бизнес" / "конкуренты" / "анализ-конкурентов.md"
        gaps = []
        if brain_path.exists():
            text = brain_path.read_text(encoding="utf-8")
            for line in text.split("\n"):
                s = line.strip()
                if not s.startswith("- "):
                    continue
                lower = s.lower()
                if any(kw in lower for kw in [
                    "прямых конкурентов нет", "аналогов нет",
                    "аналогов в спб нет", "нет учёного",
                    "нет лечения", "нет персонального",
                    "нет городского", "практически отсутствует",
                    "вне конкуренции", "ни у одного конкурента нет",
                    "не заявляет", "нет прямых конкурентов",
                ]):
                    gap = re.sub(r'[^\w\s\-.,;:!?()«»"\'а-яА-ЯёЁa-zA-Z]', '', s.strip("- "))
                    if gap and len(gap) > 15:
                        gaps.append(gap)

        defaults = [
            "Лечение осложнений после других клиник",
            "Preventive-медицина и чекапы с геронтологом",
            "ЗГТ и менопауза — экспертный контент",
            "Кабинет акне — комплексный подход",
            "Личный бренд основателя (Анна Резник)",
            "Видео-рубрика «День из жизни врача»",
            "Ботокс от невролога по медицинским показаниям",
            "Мужская косметология + урология в одном враче",
            "Коллаборации с врачами других специальностей",
            "Образовательные Reels с инфографикой",
        ]
        for d in defaults:
            if d not in gaps:
                gaps.append(d)
        return gaps


# ── CLI ─────────────────────────────────────────────────────

if __name__ == "__main__":
    import io
    if sys.stdout.encoding != "utf-8":
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

    import argparse
    parser = argparse.ArgumentParser(description="Конкурентный анализ SMM ARclinic")
    parser.add_argument("--update", action="store_true", help="Полный анализ (TG + VK)")
    parser.add_argument("--platform", default="", choices=["tg", "vk"],
                        help="Платформа для анализа (tg или vk)")
    parser.add_argument("--competitor", default="", help="Ключ одного конкурента")
    parser.add_argument("--limit", type=int, default=100, help="Лимит постов (по умолчанию 100)")
    parser.add_argument("--gaps", action="store_true", help="Показать незанятые ниши")
    parser.add_argument("--list", action="store_true", help="Список конкурентов и соцсетей")
    parser.add_argument("--save", action="store_true", help="Сохранить отчёт в файл")

    args = parser.parse_args()
    analyzer = CompetitorAnalyzer()

    if args.list:
        print(analyzer.list_competitors())

    elif args.gaps:
        for g in analyzer.find_gaps():
            print(f"- {g}")

    elif args.competitor:
        comp = analyzer.competitors.get(args.competitor)
        if not comp:
            print(f"Конкурент '{args.competitor}' не найден. Доступные ключи: {', '.join(analyzer.competitors)}")
            sys.exit(1)

        results = {}
        if comp.get("telegram"):
            print(f"Анализ Telegram: @{comp['telegram']}")
            result = asyncio.run(analyzer._analyze_telegram_channel(comp["telegram"], args.limit))
            if result:
                results[f"{args.competitor}_tg"] = result
        if comp.get("vk"):
            print(f"Анализ VK: vk.com/{comp['vk']}")
            result = analyzer._analyze_vk_community(comp["vk"], args.limit)
            if result:
                results[f"{args.competitor}_vk"] = result

        if results:
            print(json.dumps(
                {k: {kk: vv for kk, vv in v.items() if kk != "raw_posts"}
                 for k, v in results.items()},
                indent=2, ensure_ascii=False
            ))

    elif args.update or args.platform:
        platforms = [args.platform] if args.platform else ["tg", "vk"]
        all_results = {}

        for plat in platforms:
            if plat == "tg":
                results = asyncio.run(analyzer.analyze_all_telegram(args.limit))
            else:
                results = analyzer.analyze_all_vk(args.limit)

            if results:
                raw_path = analyzer._save_raw(results, plat)
                print(f"\nСырые данные сохранены: {raw_path}")

                report = analyzer.generate_report(results, plat)
                print(f"\n{report}")

                if args.save:
                    report_path = REPORTS_DIR / f"report_{plat}_{datetime.now().strftime('%Y%m%d_%H%M')}.md"
                    os.makedirs(REPORTS_DIR, exist_ok=True)
                    with open(report_path, "w", encoding="utf-8") as f:
                        f.write(report)
                    print(f"\nОтчёт сохранён: {report_path}")

                all_results[plat] = results

    else:
        parser.print_help()
