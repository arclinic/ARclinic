import os
import sys
import json
import traceback
from datetime import datetime, timedelta
from typing import Dict, List
from dotenv import load_dotenv

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.scraper import ApifyScraper, VKScraper, YouTubeScraper, TelegramScraper
from src.engagement import calculate_engagement, calculate_account_summary, identify_outliers, compare_periods
from src.database import MetricsDB
from src.report import generate_html_report

CONFIG_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config")


def load_json(path: str) -> Dict:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def safe_scrape(fn, name):
    try:
        return fn()
    except Exception as e:
        print(f"  [WARN] [{name}] Error: {e}")
        return []


def run():
    print("=" * 60)
    print("  ARclinic SMM Agent — Ежемесячный отчёт")
    print(f"  Старт: {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}")
    print("=" * 60)

    load_dotenv(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env"))

    accounts = load_json(os.path.join(CONFIG_DIR, "accounts.json"))
    competitors = load_json(os.path.join(CONFIG_DIR, "competitors.json"))

    max_posts = int(os.getenv("MAX_POSTS_PER_ACCOUNT", "50"))
    outlier_threshold = float(os.getenv("OUTLIER_THRESHOLD", "2.0"))
    db_path = os.getenv("DB_PATH", "./data/metrics.db")
    if not os.path.isabs(db_path):
        db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), db_path)

    db = MetricsDB(db_path)
    report_date = datetime.now().strftime("%B %Y")

    today_str = datetime.now().strftime("%Y-%m-%d")

    apify = ApifyScraper()
    vk_token = os.getenv("VK_ACCESS_TOKEN", "")
    yt_key = os.getenv("YOUTUBE_API_KEY", "")
    vk = VKScraper(vk_token) if vk_token else None
    yt = YouTubeScraper(yt_key) if yt_key else None
    tg = TelegramScraper()

    all_posts = []
    all_accounts_data = []
    all_outliers = []

    # ─── СВОИ АККАУНТЫ ───────────────────────────────

    # Instagram
    ig_accs = accounts.get("instagram", [])
    if ig_accs:
        print("\n[СВОИ] Instagram")
        usernames = [a["username"] for a in ig_accs]
        raw = safe_scrape(lambda: apify.fetch_posts("instagram", usernames, max_posts), "Instagram")
        for a in ig_accs:
            username = a["username"]
            acc_posts = [apify.normalize_instagram_post(p, username) for p in raw if p.get("ownerUsername", "") == username]
            acc_posts = calculate_engagement(acc_posts)
            summary = calculate_account_summary(acc_posts, "instagram")
            prev = db.get_previous_snapshot("own", a["username"], "instagram", username)
            prev_summary = prev or {}
            delta = compare_periods(summary, prev_summary)
            summary["username"] = username
            summary["platform"] = "instagram"
            summary["owner"] = a.get("owner", username)
            summary["delta"] = delta
            all_accounts_data.append(summary)
            outliers = identify_outliers(acc_posts, outlier_threshold)
            all_outliers.extend(outliers)
            all_posts.extend(acc_posts)
            db.save_snapshot(today_str, "own", a["username"], "instagram", username, summary)
            db.cache_posts(acc_posts)
            print(f"  [OK] {username}: {summary['total_posts']} постов, ER={summary['er_percent']}%")

    # TikTok
    tt_accs = accounts.get("tiktok", [])
    if tt_accs:
        print("\n[СВОИ] TikTok")
        usernames = [a["username"] for a in tt_accs]
        raw = safe_scrape(lambda: apify.fetch_posts("tiktok", usernames, max_posts), "TikTok")
        for a in tt_accs:
            username = a["username"]
            acc_posts = [apify.normalize_tiktok_post(p, username) for p in raw if p.get("authorMeta", {}).get("name", "") == username]
            if not acc_posts:
                acc_posts = [apify.normalize_tiktok_post(p, username) for p in raw]
            acc_posts = calculate_engagement(acc_posts)
            summary = calculate_account_summary(acc_posts, "tiktok")
            prev = db.get_previous_snapshot("own", username, "tiktok", username)
            delta = compare_periods(summary, prev or {})
            summary["username"] = f"@{username}"
            summary["platform"] = "tiktok"
            summary["delta"] = delta
            all_accounts_data.append(summary)
            outliers = identify_outliers(acc_posts, outlier_threshold)
            all_outliers.extend(outliers)
            all_posts.extend(acc_posts)
            db.save_snapshot(today_str, "own", username, "tiktok", username, summary)
            db.cache_posts(acc_posts)
            print(f"  [OK] @{username}: {summary['total_posts']} постов, ER={summary['er_percent']}%")

    # VK
    vk_accs = accounts.get("vkontakte", [])
    if vk_accs and vk:
        print("\n[СВОИ] ВКонтакте")
        for a in vk_accs:
            username = a["username"]
            acc_posts = safe_scrape(lambda: vk.fetch_posts(username, max_posts), f"VK {username}")
            acc_posts = calculate_engagement(acc_posts)
            summary = calculate_account_summary(acc_posts, "vkontakte")
            prev = db.get_previous_snapshot("own", username, "vkontakte", username)
            delta = compare_periods(summary, prev or {})
            summary["username"] = username
            summary["platform"] = "vkontakte"
            summary["delta"] = delta
            all_accounts_data.append(summary)
            all_outliers.extend(identify_outliers(acc_posts, outlier_threshold))
            all_posts.extend(acc_posts)
            db.save_snapshot(today_str, "own", username, "vkontakte", username, summary)
            db.cache_posts(acc_posts)
            print(f"  [OK] {username}: {summary['total_posts']} постов, ER={summary['er_percent']}%")
    elif vk_accs and not vk:
        print("\n[СВОИ] VK — пропущен (нет VK_ACCESS_TOKEN)")

    # YouTube
    yt_accs = accounts.get("youtube", [])
    if yt_accs and yt:
        print("\n[СВОИ] YouTube")
        for a in yt_accs:
            channel_id = a["channel_id"]
            channel_name = a.get("channel_name", channel_id)
            acc_posts = safe_scrape(lambda: yt.fetch_channel_videos(channel_id, max_posts), f"YT {channel_name}")
            acc_posts = calculate_engagement(acc_posts)
            summary = calculate_account_summary(acc_posts, "youtube")
            prev = db.get_previous_snapshot("own", channel_id, "youtube", channel_name)
            delta = compare_periods(summary, prev or {})
            summary["username"] = channel_name
            summary["platform"] = "youtube"
            summary["delta"] = delta
            all_accounts_data.append(summary)
            all_outliers.extend(identify_outliers(acc_posts, outlier_threshold))
            all_posts.extend(acc_posts)
            db.save_snapshot(today_str, "own", channel_id, "youtube", channel_name, summary)
            db.cache_posts(acc_posts)
            print(f"  [OK] {channel_name}: {summary['total_posts']} видео")
    elif yt_accs and not yt:
        print("\n[СВОИ] YouTube — пропущен (нет YOUTUBE_API_KEY)")

    # Telegram
    tg_accs = accounts.get("telegram", [])
    if tg_accs:
        print("\n[СВОИ] Telegram")
        for a in tg_accs:
            username = a["username"]
            acc_posts = safe_scrape(lambda: tg.fetch_channel_posts(username, max_posts), f"TG {username}")
            if acc_posts:
                acc_posts = calculate_engagement(acc_posts)
                summary = calculate_account_summary(acc_posts, "telegram")
                prev = db.get_previous_snapshot("own", username, "telegram", username)
                delta = compare_periods(summary, prev or {})
                summary["username"] = f"@{username}"
                summary["platform"] = "telegram"
                summary["delta"] = delta
                all_accounts_data.append(summary)
                all_outliers.extend(identify_outliers(acc_posts, outlier_threshold))
                all_posts.extend(acc_posts)
                db.save_snapshot(today_str, "own", username, "telegram", username, summary)
                print(f"  [OK] @{username}: {summary['total_posts']} постов")
            else:
                print(f"  [WARN] @{username}: 0 постов (публичный парсинг Telegram ограничен)")

    # ─── КОНКУРЕНТЫ ──────────────────────────────────
    competitors_data = []

    for comp_key, comp in competitors.items():
        print(f"\n[КОНКУРЕНТ] {comp['name']}")
        ig_handle = comp.get("instagram")
        if ig_handle:
            raw = safe_scrape(lambda: apify.fetch_posts("instagram", [ig_handle], max_posts), f"IG {comp['name']}")
            acc_posts = [apify.normalize_instagram_post(p, ig_handle) for p in raw]
            acc_posts = calculate_engagement(acc_posts)
            summary = calculate_account_summary(acc_posts, "instagram")
            prev = db.get_previous_snapshot("competitor", comp_key, "instagram", ig_handle)
            delta = compare_periods(summary, prev or {})
            summary["username"] = f"{comp['name']} (@{ig_handle})"
            summary["platform"] = "instagram"
            summary["delta"] = delta
            competitors_data.append(summary)
            all_outliers.extend(identify_outliers(acc_posts, outlier_threshold))
            all_posts.extend(acc_posts)
            db.save_snapshot(today_str, "competitor", comp_key, "instagram", ig_handle, summary)
            db.cache_posts(acc_posts)
            print(f"  [OK] IG @{ig_handle}: {summary['total_posts']} постов, ER={summary['er_percent']}%")

        tt_handle = comp.get("tiktok")
        if tt_handle:
            raw = safe_scrape(lambda: apify.fetch_posts("tiktok", [tt_handle], max_posts), f"TT {comp['name']}")
            acc_posts = [apify.normalize_tiktok_post(p, tt_handle) for p in raw]
            acc_posts = calculate_engagement(acc_posts)
            summary = calculate_account_summary(acc_posts, "tiktok")
            prev = db.get_previous_snapshot("competitor", comp_key, "tiktok", tt_handle)
            delta = compare_periods(summary, prev or {})
            summary["username"] = f"{comp['name']} (@{tt_handle})"
            summary["platform"] = "tiktok"
            summary["delta"] = delta
            competitors_data.append(summary)
            all_outliers.extend(identify_outliers(acc_posts, outlier_threshold))
            all_posts.extend(acc_posts)
            db.save_snapshot(today_str, "competitor", comp_key, "tiktok", tt_handle, summary)
            print(f"  [OK] TT @{tt_handle}: {summary['total_posts']} постов")

    # ─── ОТЧЁТ ─────────────────────────────────────────

    all_outliers.sort(key=lambda x: x.get("engagement_score", 0), reverse=True)
    top_outliers = all_outliers[:10]

    html = generate_html_report(report_date, all_accounts_data, competitors_data, top_outliers)

    output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "reports")
    os.makedirs(output_dir, exist_ok=True)
    report_file = os.path.join(output_dir, f"report_{datetime.now().strftime('%Y-%m-%d_%H%M')}.html")
    with open(report_file, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"\n[OK] Отчёт сохранён: {report_file}")

    import webbrowser
    webbrowser.open(f"file:///{report_file.replace(chr(92), '/')}")
    print("[OK] Отчёт открыт в браузере")

    print("\n" + "=" * 60)
    print(f"  Готово!")
    print(f"  Аккаунтов: своих — {len(all_accounts_data)}, конкурентов — {len(competitors_data)}")
    print(f"  Всего постов: {len(all_posts)}")
    print(f"  Outliers: {len(top_outliers)}")
    print("=" * 60)


if __name__ == "__main__":
    run()
