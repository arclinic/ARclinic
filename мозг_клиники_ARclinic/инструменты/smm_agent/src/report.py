from datetime import datetime
from typing import Dict, List

PLATFORM_LABEL = {
    "instagram": "Instagram", "tiktok": "TikTok",
    "vkontakte": "VK", "youtube": "YouTube", "telegram": "Telegram",
}

def _delta(val):
    if val > 0: return f'<span style="color:#22c55e">+{val}%</span>'
    if val < 0: return f'<span style="color:#ef4444">{val}%</span>'
    return '<span style="color:#6b7280">0%</span>'

def _s(lvl=2, **kw):
    return f"style=\"margin-top:{lvl*8}px;{';'.join(f'{k}:{v}' for k,v in kw.items())}\""

def _box(color, title, body):
    return f'<div style="background:{color};border-left:4px solid #0284c7;padding:16px 20px;border-radius:4px;margin-top:16px"><strong>{title}</strong><br>{body}</div>'

def generate_report_v2(
    report_date: str, period_label: str,
    accounts: List[Dict], competitors: List[Dict],
    outliers: List[Dict],
    timing_data: Dict = None, hashtag_data: Dict = None,
    video_data: Dict = None, content_plan: List[Dict] = None,
    tg_strategy: Dict = None, male_data: Dict = None,
    target_data: Dict = None, reviews_data: List[Dict] = None,
) -> str:
    now = datetime.now().strftime("%d.%m.%Y %H:%M")

    # --- ER table ---
    def er_table(items, title):
        if not items: return ""
        rows = "".join(f"""<tr>
            <td style="padding:6px">{PLATFORM_LABEL.get(item.get('platform',''),'')} {item.get('username','')}</td>
            <td style="padding:6px;text-align:right">{item.get('total_posts',0)}</td>
            <td style="padding:6px;text-align:right">{item.get('total_likes',0):,}</td>
            <td style="padding:6px;text-align:right">{item.get('total_comments',0):,}</td>
            <td style="padding:6px;text-align:right">{item.get('total_views',0):,}</td>
            <td style="padding:6px;text-align:right">{item.get('avg_eng_score',item.get('avg_engagement_score',0)):,.0f}</td>
            <td style="padding:6px;text-align:right;font-weight:bold">{item.get('er_percent',0):.2f}%</td>
            <td style="padding:6px;text-align:right">{_delta(item.get('delta',{}).get('er_delta',0))}</td>
        </tr>""" for item in items)
        tbl = f"<thead><tr style='background:#f1f5f9'><th style='padding:6px;text-align:left'>Account</th><th style='padding:6px'>Posts</th><th style='padding:6px'>Likes</th><th style='padding:6px'>Comm</th><th style='padding:6px'>Views</th><th style='padding:6px'>Score</th><th style='padding:6px'>ER%</th><th style='padding:6px'>Chg</th></tr></thead><tbody>{rows}</tbody>"
        return f"<h3 {_s(3,color='#1e293b')}>{title}</h3><table style='width:100%;border-collapse:collapse;font-size:12px;'>{tbl}</table>"

    # --- Outliers ---
    def outliers_table(items):
        if not items: return "<p style='color:#6b7280'>No outlier posts this period.</p>"
        rows = "".join(f"""<tr>
            <td style="padding:6px">{i}</td>
            <td style="padding:6px">{item.get('platform','')}</td>
            <td style="padding:6px">{item.get('username','')}</td>
            <td style="padding:6px;text-align:right">{item.get('engagement_score',0):,.0f}</td>
            <td style="padding:6px;text-align:right">{item.get('likes',0):,}</td>
            <td style="padding:6px;text-align:right">{item.get('comments',0):,}</td>
            <td style="padding:6px;text-align:right">{item.get('views',0):,}</td>
            <td style="padding:6px"><a href="{item.get('url','#')}" style="color:#2563eb">link</a></td>
        </tr>""" for i, item in enumerate(items[:10], 1))
        tbl = f"<thead><tr style='background:#f1f5f9'><th style='padding:6px'>#</th><th style='padding:6px'>Plat</th><th style='padding:6px'>Account</th><th style='padding:6px'>Score</th><th style='padding:6px'>Likes</th><th style='padding:6px'>Comm</th><th style='padding:6px'>Views</th><th style='padding:6px'>URL</th></tr></thead><tbody>{rows}</tbody>"
        return f"<h3 {_s(3,color='#1e293b')}>Top-10 Outlier Posts</h3><table style='width:100%;border-collapse:collapse;font-size:12px;'>{tbl}</table>"

    # --- Timing ---
    def timing_section(td):
        if not td: return ""
        days = " > ".join(f"{d['день']} ({d['средний_engagement']})" for d in td.get("лучшие_дни", [])[:3])
        hours = ", ".join(f"{d['час']}" for d in td.get("лучшие_часы", [])[:3])
        rec = f"Best: {td.get('рекомендация_день','?')} at {td.get('рекомендация_время','?')}"
        return f"""<div {_s(3)}>
            <h3 {_s(0,color='#1e293b')}>Best Posting Times</h3>
            <p style="font-size:13px;color:#475569">{rec} | Days: {days} | Hours: {hours}</p>
        </div>"""

    # --- Hashtags ---
    def hashtag_section(hd):
        if not hd: return ""
        top = ", ".join(f"#{h['тег']}" for h in hd.get("топ_хэштегов", [])[:10])
        missing = hd.get("хэштеги_конкурентов_которые_мы_не_используем", [])
        missing_str = "" if not missing else "<br><strong>Competitor hashtags we miss:</strong><br>" + ", ".join(f"#{m['тег']}({m['используется_конкурентами']})" for m in missing[:8])
        return f"""<div {_s(3)}>
            <h3 {_s(0,color='#1e293b')}>Top Hashtags</h3>
            <p style="font-size:13px;color:#475569">{top}</p>
            <p style="font-size:13px;color:#ef4444">{missing_str}</p>
        </div>"""

    # --- Content plan ---
    def content_plan_section(plan):
        if not plan: return ""
        rows = "".join(f"""<tr>
            <td style="padding:6px">{p['дата']} ({p['день_недели']})</td>
            <td style="padding:6px">{p['тип']}</td>
            <td style="padding:6px">{p['хук']}</td>
            <td style="padding:6px">{p['врач']}</td>
            <td style="padding:6px">{p['длительность']}</td>
        </tr>""" for p in plan[:20])
        tbl = f"<thead><tr style='background:#f1f5f9'><th style='padding:6px'>Date</th><th style='padding:6px'>Type</th><th style='padding:6px'>Hook</th><th style='padding:6px'>Doctor</th><th style='padding:6px'>Dur</th></tr></thead><tbody>{rows}</tbody>"
        return f"<h3 {_s(3,color='#1e293b')}>Content Plan (4 weeks, generated)</h3><table style='width:100%;border-collapse:collapse;font-size:12px;'>{tbl}</table>"

    # --- Video analysis ---
    def video_section(vd):
        if not vd: return ""
        recs = "<br>".join(f"- {r}" for r in vd.get("recommendations", [])[:5])
        plat = vd.get("platform_breakdown", {}).get("instagram", {})
        stats = f"Videos: {vd.get('total_videos',0)} | Avg views: {plat.get('средние_просмотры',0):,} | ER: {plat.get('engagement_rate',0)}%"
        return f"""<div {_s(3)}>
            <h3 {_s(0,color='#1e293b')}>Reels Video Analysis</h3>
            <p style="font-size:13px;color:#475569">{stats}</p>
            <p style="font-size:13px"><strong>Recommendations:</strong><br>{recs}</p>
        </div>"""

    # --- Recommendations ---
    def reco_section(td, vd, hd, md, tard):
        items = []
        if td:
            items.append(f"Publish on <strong>{td.get('рекомендация_день','Wed')} at {td.get('рекомендация_время','12:00')}</strong> for best engagement")
        if vd and vd.get("recommendations"):
            items.extend(vd["recommendations"][:3])
        if hd and hd.get("рекомендуемые_хэштеги"):
            items.append(f"Use hashtags: {' '.join('#'+t for t in hd['рекомендуемые_хэштеги'][:5])}")
        if md:
            items.append(f"Male segment: {md.get('доля','?')} of competitor content. Gap opportunity for ARclinic")
        if tard and tard.get("рекомендации"):
            items.extend(tard["рекомендации"][:2])
        return "".join(f"<li style='margin-bottom:6px;font-size:13px'>{r}</li>" for r in items)

    # --- Reviews ---
    def reviews_section(rd):
        if not rd: return ""
        rows = "".join(f"""<tr>
            <td style="padding:6px">{r.get('источник','?')}</td>
            <td style="padding:6px;text-align:right">{r.get('рейтинг',0)}</td>
            <td style="padding:6px;text-align:right">{r.get('отзывов',0)}</td>
            <td style="padding:6px">{r.get('статус','?')}</td>
        </tr>""" for r in rd)
        tbl = f"<thead><tr style='background:#f1f5f9'><th style='padding:6px'>Source</th><th style='padding:6px'>Rating</th><th style='padding:6px'>Reviews</th><th style='padding:6px'>Status</th></tr></thead><tbody>{rows}</tbody>"
        return f"<h3 {_s(3,color='#1e293b')}>Reviews Monitoring</h3><table style='width:100%;border-collapse:collapse;font-size:12px;'>{tbl}</table>"

    # Build
    acct_t = er_table(accounts, "Your Accounts")
    comp_t = er_table(competitors, "Competitors")
    out_t = outliers_table(outliers)
    tim_s = timing_section(timing_data)
    hash_s = hashtag_section(hashtag_data)
    vid_s = video_section(video_data)
    plan_s = content_plan_section(content_plan)
    rev_s = reviews_section(reviews_data)
    reco_items = reco_section(timing_data, video_data, hashtag_data, male_data, target_data)

    html = f"""<!DOCTYPE html><html lang="ru"><head><meta charset="UTF-8">
<title>ARclinic SMM Report {period_label}</title></head>
<body style="margin:0;padding:0;font-family:Segoe UI,Arial,sans-serif;background:#f8fafc;color:#0f172a">
<div style="max-width:900px;margin:0 auto;background:#fff;border-radius:8px;overflow:hidden">

<div style="background:#1e293b;color:#fff;padding:30px 40px">
    <h1 style="margin:0;font-size:22px">ARclinic - SMM Report</h1>
    <p style="margin:8px 0 0;font-size:14px;color:#94a3b8">{report_date} | {period_label} | Generated: {now}</p>
</div>

<div style="padding:20px 40px 40px">

<div style="background:#dbeafe;border-left:4px solid #2563eb;padding:14px 20px;border-radius:4px">
    <strong>Summary:</strong> {len(accounts)} own accounts, {len(competitors)} competitors analyzed.
</div>

{acct_t}
{comp_t}

<div style="background:#f0fdf4;border-left:4px solid #16a34a;padding:16px 20px;border-radius:4px;margin-top:20px">
    <strong>Actionable Recommendations</strong>
    <ol style="margin:8px 0 0 16px;padding:0">{reco_items}</ol>
</div>

{out_t}
{tim_s}
{hash_s}
{vid_s}
{plan_s}
{rev_s}

<div style="margin-top:40px;padding:16px 20px;background:#f1f5f9;border-radius:4px;font-size:12px;color:#475569">
    <strong>Metrics explained:</strong> Engagement Score = likes*1 + comments*3 + views*0.02 | ER% = (likes+comments)/views*100 | Chg = change vs previous period | Outliers = posts >2 sigma above mean
</div>
<div style="margin-top:16px;border-top:1px solid #e2e8f0;padding-top:12px;font-size:11px;color:#94a3b8">
    ARclinic SMM Agent v2 | Biweekly report | <a href="https://www.arclinic.ru" style="color:#2563eb">arclinic.ru</a>
</div>

</div></div></body></html>"""
    return html
