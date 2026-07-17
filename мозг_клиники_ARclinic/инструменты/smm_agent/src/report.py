from datetime import datetime
from typing import Dict, List

PLATFORM_EMOJI = {
    "instagram": "📸",
    "tiktok": "🎵",
    "vkontakte": "📘",
    "youtube": "▶️",
    "telegram": "✈️",
}


def _delta_span(delta_val):
    """HTML-спан с цветом для дельты."""
    if delta_val > 0:
        return f'<span style="color:#22c55e">▲ +{delta_val}%</span>'
    elif delta_val < 0:
        return f'<span style="color:#ef4444">▼ {delta_val}%</span>'
    return '<span style="color:#6b7280">— 0%</span>'


def generate_html_report(
    report_date: str,
    accounts_summary: List[Dict],
    competitors_summary: List[Dict],
    top_outliers: List[Dict],
) -> str:
    """
    Генерирует HTML-отчёт для отправки по почте.
    """
    now = datetime.now().strftime("%d.%m.%Y %H:%M")

    def render_table(items: List[Dict], title: str) -> str:
        if not items:
            return ""

        rows = ""
        for item in items:
            emoji = PLATFORM_EMOJI.get(item.get("platform", ""), "")
            delta = item.get("delta", {})
            er_d = delta.get("er_delta", 0)
            eng_d = delta.get("engagement_delta", 0)

            rows += f"""
            <tr>
                <td>{emoji} {item.get('username', '')}</td>
                <td>{item.get('total_posts', 0)}</td>
                <td>{item.get('total_likes', 0):,}</td>
                <td>{item.get('total_comments', 0):,}</td>
                <td>{item.get('total_views', 0):,}</td>
                <td>{item.get('avg_engagement_score', 0):,.0f}</td>
                <td>{item.get('er_percent', 0):.2f}%</td>
                <td>{_delta_span(er_d)}</td>
                <td>{_delta_span(eng_d)}</td>
            </tr>"""

        return f"""
        <h3 style="color:#1e293b;margin-top:30px">{title}</h3>
        <table style="width:100%;border-collapse:collapse;font-size:12px;margin-top:10px">
            <thead>
                <tr style="background:#f1f5f9;text-align:left">
                    <th style="padding:8px">Аккаунт</th>
                    <th style="padding:8px">Постов</th>
                    <th style="padding:8px">Лайков</th>
                    <th style="padding:8px">Комм.</th>
                    <th style="padding:8px">Просм.</th>
                    <th style="padding:8px">Eng.Score</th>
                    <th style="padding:8px">ER%</th>
                    <th style="padding:8px">Δ ER</th>
                    <th style="padding:8px">Δ Eng</th>
                </tr>
            </thead>
            <tbody>{rows}</tbody>
        </table>"""

    def render_outliers(outliers: List[Dict]) -> str:
        if not outliers:
            return '<p style="color:#6b7280">Нет аномальных постов в этом месяце.</p>'

        cards = ""
        for i, o in enumerate(outliers[:10], 1):
            cards += f"""
            <tr>
                <td>{i}</td>
                <td>{o.get('platform', '')}</td>
                <td>{o.get('username', '')}</td>
                <td>{o.get('engagement_score', 0):,.0f}</td>
                <td>{o.get('likes', 0):,}</td>
                <td>{o.get('comments', 0):,}</td>
                <td>{o.get('views', 0):,}</td>
                <td><a href="{o.get('url', '#')}" style="color:#2563eb">ссылка</a></td>
            </tr>"""

        return f"""
        <table style="width:100%;border-collapse:collapse;font-size:12px;margin-top:10px">
            <thead>
                <tr style="background:#f1f5f9;text-align:left">
                    <th style="padding:8px">#</th>
                    <th style="padding:8px">Платф.</th>
                    <th style="padding:8px">Аккаунт</th>
                    <th style="padding:8px">Score</th>
                    <th style="padding:8px">Лайки</th>
                    <th style="padding:8px">Комм.</th>
                    <th style="padding:8px">Просм.</th>
                    <th style="padding:8px">URL</th>
                </tr>
            </thead>
            <tbody>{cards}</tbody>
        </table>"""

    accounts_table = render_table(accounts_summary, "📊 Ваши аккаунты")
    competitors_table = render_table(competitors_summary, "🔍 Конкуренты")
    outliers_section = render_outliers(top_outliers)

    html = f"""<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ARclinic — Отчёт по соцсетям</title>
</head>
<body style="margin:0;padding:0;font-family:'Segoe UI',Arial,sans-serif;background:#f8fafc;color:#0f172a">
    <div style="max-width:800px;margin:0 auto;background:#fff;border-radius:8px;overflow:hidden">

        <div style="background:#1e293b;color:#fff;padding:30px 40px">
            <h1 style="margin:0;font-size:22px">ARclinic — Отчёт по соцсетям</h1>
            <p style="margin:8px 0 0;font-size:14px;color:#94a3b8">{report_date} | Сгенерирован: {now}</p>
        </div>

        <div style="padding:20px 40px 40px">

            <div style="background:#e0f2fe;border-left:4px solid #0284c7;padding:16px 20px;border-radius:4px;margin-bottom:20px">
                <strong>📋 Сводка:</strong> проанализировано аккаунтов — <strong>{len(accounts_summary) + len(competitors_summary)}</strong>
                ({len(accounts_summary)} своих, {len(competitors_summary)} конкурентов)
            </div>

            {accounts_table}
            {competitors_table}

            <h3 style="color:#1e293b;margin-top:30px">🚀 Топ-10 аномальных постов (outliers)</h3>
            <p style="color:#64748b;font-size:13px">Посты с вовлечением >2σ выше среднего</p>
            {outliers_section}

            <div style="margin-top:40px;padding:20px;background:#f1f5f9;border-radius:4px;font-size:13px;color:#475569">
                <strong>📌 Пояснение метрик:</strong><br>
                <strong>Engagement Score</strong> — взвешенная сумма (лайки×1 + комментарии×3 + просмотры×коэф.)<br>
                <strong>ER%</strong> — (лайки + комментарии) / подписчики × 100. Если подписчики неизвестны, считается от просмотров.<br>
                <strong>Δ</strong> — изменение относительно предыдущего месяца.<br>
                <strong>Outliers</strong> — посты с engagement >2σ (стандартных отклонений) выше среднего по аккаунту.
            </div>

            <div style="margin-top:20px;border-top:1px solid #e2e8f0;padding-top:16px;font-size:12px;color:#94a3b8">
                ARclinic SMM Agent • Автоматический ежемесячный отчёт • <a href="https://www.arclinic.ru" style="color:#2563eb">arclinic.ru</a>
            </div>

        </div>
    </div>
</body>
</html>"""
    return html
