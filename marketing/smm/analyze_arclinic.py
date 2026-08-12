"""Аналитика Instagram @arclinic: топ-50, стиль, хуки, сезонность, активность."""
import json, re
from datetime import datetime
from collections import Counter, defaultdict
from pathlib import Path

RAW = Path("C:/Arclinic/marketing/smm/content_factory/output/research/instagram/2026-08-12/raw.json")
OUT = Path("C:/Arclinic/marketing/smm/content_factory/output/research/instagram/2026-08-12/analysis.md")

with open(RAW, encoding="utf-8") as f:
    posts = json.load(f)

posts = [p for p in posts if p.get("caption")]  # only posts with text
print(f"Posts with captions: {len(posts)}")

# Score: likes + comments*3
for p in posts:
    p["_score"] = (p.get("likes", 0) or 0) + (p.get("comments", 0) or 0) * 3

top50 = sorted(posts, key=lambda x: x["_score"], reverse=True)[:50]

# ====== 1. TOP-50 ======
lines = []
lines.append("# Аналитика Instagram @arclinic")
lines.append(f"**Дата анализа:** {datetime.now().strftime('%d.%m.%Y')}")
lines.append(f"**Всего постов:** {len(posts):,}")
lines.append(f"**Период:** 2017–2026")
lines.append("")

lines.append("## ТОП-50 постов по вовлечённости")
lines.append("")
lines.append("| # | Дата | Тип | Лайки | Комм. | Ссылка | Хук (начало текста) |")
lines.append("|---|------|-----|-------|-------|--------|----------------------|")
for i, p in enumerate(top50, 1):
    ts = p["timestamp"][:10]
    t = p["type"]
    l = p.get("likes", 0) or 0
    c = p.get("comments", 0) or 0
    url = p.get("url", "")
    cap = (p.get("caption") or "")[:120].replace("\n", " ").replace("|", "/")
    lines.append(f"| {i} | {ts} | {t} | {l} | {c} | {url} | {cap} |")

# ====== 2. ХУКИ ======
lines.append("")
lines.append("## Хуки (первые фразы топ-50)")
lines.append("")
for i, p in enumerate(top50, 1):
    cap = (p.get("caption") or "").strip()
    first_sentence = cap.split("\n")[0][:150]
    lines.append(f"{i}. {first_sentence}")

# ====== 3. СТИЛЬ ======
lines.append("")
lines.append("## Стиль написания")
lines.append("")

# Average caption length
lengths = [len((p.get("caption") or "")) for p in posts]
avg_len = sum(lengths) / len(lengths) if lengths else 0
lines.append(f"- **Средняя длина текста:** {avg_len:.0f} символов")
lines.append(f"- **Мин / Макс:** {min(lengths)} / {max(lengths)} символов")

# Emoji usage
all_captions = " ".join(p.get("caption", "") for p in posts)
emoji_pattern = re.compile(r'[\U0001F300-\U0001F9FF\u2600-\u27BF\u200D\uFE0F]')
emojis = emoji_pattern.findall(all_captions)
emoji_counter = Counter(emojis)
lines.append(f"- **Постов с эмодзи:** {sum(1 for p in posts if emoji_pattern.search(p.get('caption', '')))} / {len(posts)}")
lines.append(f"- **Топ-10 эмодзи:** {' '.join(e for e, _ in emoji_counter.most_common(10))}")

# Hashtag analysis
all_text = " ".join(p.get("caption", "") for p in posts)
hashtags = re.findall(r'#[\wа-яА-ЯёЁ]+', all_text, re.IGNORECASE)
ht_counter = Counter(h.lower() for h in hashtags)
lines.append(f"- **Топ-20 хештегов:**")
for ht, cnt in ht_counter.most_common(20):
    lines.append(f"  - {ht} ({cnt})")

# Sentence structure
sentences_per_post = []
words_per_sentence = []
for p in posts:
    text = p.get("caption", "")
    sents = re.split(r'[.!?]+', text)
    sents = [s.strip() for s in sents if len(s.strip()) > 5]
    if sents:
        sentences_per_post.append(len(sents))
        for s in sents:
            words_per_sentence.append(len(s.split()))

if sentences_per_post:
    lines.append(f"- **Предложений в посте (в среднем):** {sum(sentences_per_post)/len(sentences_per_post):.1f}")
if words_per_sentence:
    lines.append(f"- **Слов в предложении (в среднем):** {sum(words_per_sentence)/len(words_per_sentence):.1f}")

# ====== 4. АКТИВНОСТЬ ПО МЕСЯЦАМ ======
lines.append("")
lines.append("## Активность по месяцам")
lines.append("")
lines.append("| Месяц | Постов | Лайков | Комм. |")
lines.append("|-------|--------|--------|-------|")

monthly = defaultdict(lambda: {"posts": 0, "likes": 0, "comments": 0})
for p in posts:
    ts = p["timestamp"][:7]
    monthly[ts]["posts"] += 1
    monthly[ts]["likes"] += p.get("likes", 0) or 0
    monthly[ts]["comments"] += p.get("comments", 0) or 0

for month in sorted(monthly.keys()):
    m = monthly[month]
    lines.append(f"| {month} | {m['posts']} | {m['likes']:,} | {m['comments']} |")

# ====== 5. АКТИВНОСТЬ ПО ГОДАМ ======
lines.append("")
lines.append("## Активность по годам")
lines.append("")
lines.append("| Год | Постов | Лайков | Комм. | Ср.лайков/пост |")
lines.append("|-----|--------|--------|-------|----------------|")

yearly = defaultdict(lambda: {"posts": 0, "likes": 0, "comments": 0})
for p in posts:
    yr = p["timestamp"][:4]
    yearly[yr]["posts"] += 1
    yearly[yr]["likes"] += p.get("likes", 0) or 0
    yearly[yr]["comments"] += p.get("comments", 0) or 0

for year in sorted(yearly.keys()):
    y = yearly[year]
    avg_likes = y["likes"] / y["posts"] if y["posts"] else 0
    lines.append(f"| {year} | {y['posts']} | {y['likes']:,} | {y['comments']} | {avg_likes:.1f} |")

# ====== 6. СЕЗОННОСТЬ ======
lines.append("")
lines.append("## Сезонность (по месяцам, все годы)")
lines.append("")
lines.append("| Месяц | Постов | Ср.лайков |")
lines.append("|-------|--------|-----------|")

season = defaultdict(lambda: {"posts": 0, "likes": 0})
month_names = ["", "Янв", "Фев", "Мар", "Апр", "Май", "Июн", "Июл", "Авг", "Сен", "Окт", "Ноя", "Дек"]
for p in posts:
    m = int(p["timestamp"][5:7])
    season[m]["posts"] += 1
    season[m]["likes"] += p.get("likes", 0) or 0

for m in range(1, 13):
    s = season[m]
    avg = s["likes"] / s["posts"] if s["posts"] else 0
    lines.append(f"| {month_names[m]} | {s['posts']} | {avg:.1f} |")

# ====== 7. ТИПЫ КОНТЕНТА ======
lines.append("")
lines.append("## Типы контента")
lines.append("")
type_counter = Counter(p.get("type", "?") for p in posts)
for t, cnt in type_counter.most_common():
    lines.append(f"- **{t}:** {cnt}")

# ====== 8. ТОП-50 ПОЛНЫЕ ТЕКСТЫ ======
lines.append("")
lines.append("## Полные тексты ТОП-50 постов")
lines.append("")
for i, p in enumerate(top50, 1):
    lines.append(f"### {i}. {p['timestamp'][:10]} | 👍{p.get('likes',0)} 💬{p.get('comments',0)} | {p.get('url','')}")
    lines.append("")
    lines.append(p.get("caption", "")[:2000])
    lines.append("")
    lines.append("---")
    lines.append("")

with open(OUT, "w", encoding="utf-8") as f:
    f.write("\n".join(lines))

print(f"Saved: {OUT}")
print(f"Lines: {len(lines)}")
