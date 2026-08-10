import os
import sys
import json
import traceback
import webbrowser
from datetime import datetime, timedelta
from typing import Dict, List
from dotenv import load_dotenv

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.scraper import ApifyScraper, VKScraper, YouTubeScraper, TelegramScraper
from src.engagement import calculate_engagement, calculate_account_summary, identify_outliers, compare_periods
from src.database import MetricsDB
from src.hashtag_timing import analyze_timing, analyze_hashtags
from src.video_analyzer import analyze_video_posts, generate_video_recommendations
from src.content_planner import generate_content_plan, generate_tg_strategy
from src.segment_analyzer import analyze_male_segment, generate_target_recommendations
from src.reviews_monitor import collect_all_reviews
from src.report import generate_report_v2
from src.emailer import send_email_report

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
    print("  ARclinic SMM Agent v2 — Biweekly Report")
    print(f"  Start: {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}")
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
    period_label = datetime.now().strftime("%d.%m") + " - " + (datetime.now() + timedelta(days=14)).strftime("%d.%m.%Y")

    apify = ApifyScraper()
    vk_token = os.getenv("VK_ACCESS_TOKEN", "")
    yt_key = os.getenv("YOUTUBE_API_KEY", "")
    vk = VKScraper(vk_token) if vk_token else None
    yt = YouTubeScraper(yt_key) if yt_key else None
    tg = TelegramScraper()

    all_posts = []
    all_accounts_data = []
    all_outliers = []

    # ─── СВОИ ──────────────────────────────────────────

    ig_accs = accounts.get("instagram", [])
    if ig_accs:
        print("\n[OWN] Instagram")
        usernames = [a["username"] for a in ig_accs]
        raw = safe_scrape(lambda: apify.fetch_posts("instagram", usernames, max_posts), "Instagram")
        for a in ig_accs:
            username = a["username"]
            acc_posts = [apify.normalize_instagram_post(p, username) for p in raw if p.get("ownerUsername", "") == username]
            acc_posts = calculate_engagement(acc_posts)
            summary = calculate_account_summary(acc_posts, "instagram")
            prev = db.get_previous_snapshot("own", a["username"], "instagram", username)
            delta = compare_periods(summary, prev or {})
            summary["username"] = username
            summary["platform"] = "instagram"
            summary["owner"] = a.get("owner", username)
            summary["delta"] = delta
            all_accounts_data.append(summary)
            all_outliers.extend(identify_outliers(acc_posts, outlier_threshold))
            all_posts.extend(acc_posts)
            db.save_snapshot(today_str, "own", a["username"], "instagram", username, summary)
            db.cache_posts(acc_posts)
            print(f"  [OK] {username}: {summary['total_posts']} posts, ER={summary['er_percent']}%")

    tt_accs = accounts.get("tiktok", [])
    if tt_accs:
        print("\n[OWN] TikTok")
        usernames = [a["username"] for a in tt_accs]
        raw = safe_scrape(lambda: apify.fetch_posts("tiktok", usernames, max_posts), "TikTok")
        for a in tt_accs:
            username = a["username"]
            acc_posts = [apify.normalize_tiktok_post(p, username) for p in raw]
            acc_posts = calculate_engagement(acc_posts)
            summary = calculate_account_summary(acc_posts, "tiktok")
            prev = db.get_previous_snapshot("own", username, "tiktok", username)
            delta = compare_periods(summary, prev or {})
            summary["username"] = f"@{username}"
            summary["platform"] = "tiktok"
            summary["delta"] = delta
            all_accounts_data.append(summary)
            all_outliers.extend(identify_outliers(acc_posts, outlier_threshold))
            all_posts.extend(acc_posts)
            db.save_snapshot(today_str, "own", username, "tiktok", username, summary)
            db.cache_posts(acc_posts)
            print(f"  [OK] @{username}: {summary['total_posts']} posts")

    if vk_accs := accounts.get("vkontakte", []):
        if vk:
            print("\n[OWN] VK")
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
                all_posts.extend(acc_posts)
                db.save_snapshot(today_str, "own", username, "vkontakte", username, summary)
                print(f"  [OK] {username}: {summary['total_posts']} posts")
        else:
            print("\n[OWN] VK — skipped (no VK_ACCESS_TOKEN)")

    if yt_accs := accounts.get("youtube", []):
        if yt:
            print("\n[OWN] YouTube")
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
                all_posts.extend(acc_posts)
                db.save_snapshot(today_str, "own", channel_id, "youtube", channel_name, summary)
                print(f"  [OK] {channel_name}: {summary['total_posts']} videos")
        else:
            print("\n[OWN] YouTube — skipped (no YOUTUBE_API_KEY)")

    # Telegram
    tg_accs = accounts.get("telegram", [])
    if tg_accs:
        print("\n[OWN] Telegram")
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
                all_posts.extend(acc_posts)
                db.save_snapshot(today_str, "own", username, "telegram", username, summary)
                print(f"  [OK] @{username}: {summary['total_posts']} posts")
            else:
                print(f"  [WARN] @{username}: 0 posts (TG public parsing limited)")

    # ─── КОНКУРЕНТЫ ──────────────────────────────────
    competitors_data = []

    for comp_key, comp in competitors.items():
        print(f"\n[COMPETITOR] {comp['name']}")
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
            print(f"  [OK] IG @{ig_handle}: {summary['total_posts']} posts, ER={summary['er_percent']}%")

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
            print(f"  [OK] TT @{tt_handle}: {summary['total_posts']} posts")

    # ─── АНАЛИТИКА ────────────────────────────────────

    all_outliers.sort(key=lambda x: x.get("engagement_score", 0), reverse=True)
    top_outliers = all_outliers[:10]

    print("\n[ANALYTICS] Running extended analysis...")

    timing_data = analyze_timing(all_posts) if all_posts else None
    hashtag_data = analyze_hashtags(all_posts) if all_posts else None
    video_analysis = analyze_video_posts(all_posts) if all_posts else None
    if video_analysis:
        video_analysis["recommendations"] = generate_video_recommendations(video_analysis)
    content_plan = generate_content_plan({}, datetime.now().month)
    tg_strategy = generate_tg_strategy()
    male_data = analyze_male_segment(all_posts) if all_posts else None
    target_data = generate_target_recommendations(all_posts) if all_posts else None
    reviews_data = collect_all_reviews()

    # ─── ОТЧЁТ ────────────────────────────────────────

    html = generate_report_v2(
        report_date=report_date,
        period_label=period_label,
        accounts=all_accounts_data,
        competitors=competitors_data,
        outliers=top_outliers,
        timing_data=timing_data,
        hashtag_data=hashtag_data,
        video_data=video_analysis,
        content_plan=content_plan,
        tg_strategy=tg_strategy,
        male_data=male_data,
        target_data=target_data,
        reviews_data=reviews_data,
    )

    output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "reports")
    os.makedirs(output_dir, exist_ok=True)
    report_file = os.path.join(output_dir, f"report_{datetime.now().strftime('%Y-%m-%d_%H%M')}.html")
    with open(report_file, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"\n[OK] Report saved: {report_file}")

    webbrowser.open(f"file:///{report_file.replace(chr(92), '/')}")
    print("[OK] Report opened in browser")

    # Email
    smtp_password = os.getenv("SMTP_PASSWORD", "")
    to_email = os.getenv("REPORT_TO", "arclinic.adwords@gmail.com")
    subject = f"ARclinic — SMM Report {period_label}"

    if smtp_password and not smtp_password.startswith("your_"):
        success = send_email_report(html, subject, to_email)
        print(f"[EMAIL] {'Sent' if success else 'Failed'} to {to_email}")
    else:
        print(f"[EMAIL] Skipped — SMTP_PASSWORD not configured in .env")

    print("\n" + "=" * 60)
    print(f"  Done! Own: {len(all_accounts_data)}, Competitors: {len(competitors_data)}")
    print(f"  Total posts: {len(all_posts)} | Outliers: {len(top_outliers)}")
    print("=" * 60)


if __name__ == "__main__":
    run()
