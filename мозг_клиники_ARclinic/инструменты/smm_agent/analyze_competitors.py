import sqlite3, json, os, sys, re
from collections import Counter
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from src.engagement import calculate_engagement

def clean_text(text):
    return re.sub(r'[^\x00-\x7F\u0400-\u04FF\s]', '', text or '')[:120].replace("\n", " ").strip()

DB = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "metrics.db")
print(f"DB: {DB}, exists: {os.path.exists(DB)}")

TOPIC_KEYWORDS = {
    "ботокс/ботулинотерапия": ["ботокс", "ботулинотерапия", "ботулотоксин", "мимические морщины", "ботулин", "диспорт", "релатокс", "botox", "botulinum"],
    "филлеры/контурная пластика": ["филлер", "контурная пластика", "губы", "скулы", "juvederm", "belotero", "restylane", "объем", "углы", "носогубные", "filler", "lip"],
    "аппаратная косметология": ["smas", "ультразвук", "rf-лифтинг", "игольчатый", "микроигольчатый", "morpheus", "ultraformer", "virtue", "термаж", "thermage", "аппарат", "лазер"],
    "уход/чистка/пилинг": ["чистка", "пилинг", "уход", "маска", "биоревитализация", "мезотерапия", "jalupro", "ial", "profhilo", "профайло", "collagen", "коллаген"],
    "до/после": ["до после", "результат", "трансформация", "преображение", "до/после", "результаты", "эффект", "разница"],
    "образование/советы": ["почему", "как", "совет", "ошибк", "правда", "миф", "разбор", "что будет", "нужно знать", "важно", "секрет", "лайфхак"],
    "личное/врач": ["я", "мой", "доктор", "врач", "прием", "пациент", "консультация", "клиника", "команда"],
    "акции/цены": ["скидка", "акция", "подарок", "цена", "стоимость", "спецпредложение", "выгодно", "рассрочка"],
    "осложнения/лечение": ["осложнение", "исправление", "ошибка", "неудачн", "переделать", "спасение"],
    "мужчины": ["мужчин", "мужской", "мужская", "для него", "брутальный"],
}

def classify_topic(caption):
    cap = (caption or "").lower()
    found_topics = []
    for topic, keywords in TOPIC_KEYWORDS.items():
        for kw in keywords:
            if kw.lower() in cap:
                found_topics.append(topic)
                break
    return found_topics if found_topics else ["прочее"]

def classify_format(post):
    post_type = post.get("type", "").lower()
    is_video = post.get("is_video", False)
    views = post.get("views", 0)
    if views > 0 or is_video or "video" in post_type:
        return "Reels/Video"
    elif "sidecar" in post_type or "carousel" in post_type:
        return "Carousel"
    else:
        return "Image"

with sqlite3.connect(DB) as conn:
    rows = conn.execute("SELECT data_json FROM posts_cache WHERE platform='instagram'").fetchall()

all_posts = [json.loads(r[0]) for r in rows]
all_posts = calculate_engagement(all_posts)

# Group by owner
our_handles = {"arclinic", "reznik_anna_v"}

# Read competitor handles from config
config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config", "competitors.json")
with open(config_path, "r", encoding="utf-8") as f:
    comp_config = json.load(f)
comp_handles = set()
comp_names = {}
for key, val in comp_config.items():
    if val.get("instagram"):
        comp_handles.add(val["instagram"])
        comp_names[val["instagram"]] = val["name"]

accounts = {}
for p in all_posts:
    u = p.get("username", "")
    if u not in accounts:
        accounts[u] = []
    accounts[u].append(p)

print("\n" + "=" * 80)
print("  АНАЛИЗ КОНКУРЕНТОВ: ТОП-ПОСТЫ, ФОРМАТЫ, ТЕМЫ")
print(f"  Дата: {datetime.now().strftime('%d.%m.%Y')}")
print("=" * 80)

# --- OUR PERFORMANCE ---
print("\n### НАШИ АККАУНТЫ\n")
for handle in ["arclinic", "reznik_anna_v"]:
    if handle not in accounts:
        continue
    posts = accounts[handle]
    posts.sort(key=lambda p: p.get("engagement_score", 0), reverse=True)
    formats = Counter(classify_format(p) for p in posts)
    topics_flat = []
    for p in posts[:5]:
        topics_flat.extend(classify_topic(p.get("caption", "")))

    print(f"--- @{handle} ({len(posts)} постов) ---")
    print(f"  Среднее: likes={sum(p['likes'] for p in posts)//len(posts)}, comments={sum(p['comments'] for p in posts)//len(posts)}")
    print(f"  Форматы: {dict(formats)}")
    if topics_flat:
        print(f"  Темы топ-5: {dict(Counter(topics_flat).most_common(5))}")
    print(f"  Топ-3 поста:")
    for p in posts[:3]:
        cap = (p.get("caption", "") or "")[:120].replace("\n", " ")
        fmt = classify_format(p)
        print(f"    [{p['engagement_score']:.0f}] {fmt} | L:{p['likes']} C:{p['comments']} V:{p['views']}")
        print(f"    {cap}")
        print()
    print()

# --- COMPETITOR PERFORMANCE ---
print("### КОНКУРЕНТЫ\n")
leaderboard = []
for handle in comp_handles:
    if handle not in accounts:
        continue
    posts = accounts[handle]
    posts.sort(key=lambda p: p.get("engagement_score", 0), reverse=True)
    avg_likes = sum(p['likes'] for p in posts) // len(posts) if posts else 0
    avg_comments = sum(p['comments'] for p in posts) // len(posts) if posts else 0
    avg_views = sum(p['views'] for p in posts) // len(posts) if posts else 0
    er = round((avg_likes + avg_comments) / avg_views * 100, 2) if avg_views > 0 else 0
    formats = Counter(classify_format(p) for p in posts)

    leaderboard.append((handle, er, avg_likes, avg_comments, len(posts), formats))

    topics_flat = []
    for p in posts[:5]:
        topics_flat.extend(classify_topic(p.get("caption", "")))

    print(f"--- @{handle} ({len(posts)} постов, ER={er}%) ---")
    print(f"  Среднее: likes={avg_likes}, comments={avg_comments}, views={avg_views}")
    print(f"  Форматы: {dict(formats)}")
    if topics_flat:
        tc = Counter(topics_flat).most_common(5)
        print(f"  Темы топ-5: {dict(tc)}")
    print(f"  Топ-3 поста:")
    for p in posts[:3]:
        cap = (p.get("caption", "") or "")[:120].replace("\n", " ")
        fmt = classify_format(p)
        url = p.get("url", "")
        print(f"    [{p['engagement_score']:.0f}] {fmt} | L:{p['likes']} C:{p['comments']} V:{p['views']}")
        print(f"    {cap}")
        print(f"    {url}")
        print()
    print()

# --- COMPARATIVE SUMMARY ---
print("=" * 80)
print("  ИТОГОВОЕ СРАВНЕНИЕ")
print("=" * 80)

our_avg_er = 0
n_our = 0
for h in our_handles:
    if h in accounts:
        posts = accounts[h]
        al = sum(p['likes'] for p in posts) // len(posts) if posts else 0
        ac = sum(p['comments'] for p in posts) // len(posts) if posts else 0
        av = sum(p['views'] for p in posts) // len(posts) if posts else 0
        er = round((al + ac) / av * 100, 2) if av > 0 else 0
        our_avg_er += er
        n_our += 1

our_er = round(our_avg_er / n_our, 2) if n_our else 0

leaderboard.sort(key=lambda x: x[1], reverse=True)

print(f"\n{'Аккаунт':<25} {'ER%':>7} {'Likes':>8} {'Comm':>6} {'Posts':>6} {'Форматы'}")
print("-" * 80)

for handle, er, likes, comm, cnt, fmts in leaderboard:
    fmt_str = "/".join(f"{v}{k[0]}" for k, v in fmts.most_common(3))
    marker = " <-- ЛИДЕР" if er == max(l[1] for l in leaderboard) else ""
    print(f"{handle:<25} {er:>6.2f}% {likes:>7}  {comm:>5}  {cnt:>5}  {fmt_str}{marker}")

print(f"\nНаш средний ER: {our_er}%")
print(f"Лучший конкурент: {leaderboard[0][0]} ({leaderboard[0][1]}%)")

# Recommendations
print(f"\n### РЕКОМЕНДАЦИИ\n")
top_comp = leaderboard[0]
if top_comp[1] > our_er:
    print(f"1. {top_comp[0]} имеет ER {top_comp[1]}% против нашего {our_er}%.")
    print(f"   Основной формат: {dict(top_comp[5])}")

# Find Reels-heavy competitors
reels_kings = [(h, er, fmts) for h, er, _, _, _, fmts in leaderboard if fmts.get("Reels/Video", 0) > 5]
if reels_kings:
    print(f"\n2. Конкуренты активно используют Reels: {', '.join(r[0] for r in reels_kings)}")
    print(f"   Твоим: @arclinic — посмотреть, стоит ли усилить Reels-формат")
