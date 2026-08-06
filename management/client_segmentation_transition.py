"""
Переходы между сегментами за май 2026.
Первичные — 0 сделок в окне И 0 сделок до окна (новый клиент).
Потерянные — 0 сделок в окне, но были сделки ДО окна.
Развитие — 1-5 сделок в окне.
Постоянные — >5 сделок в окне.
"""

import json, os, sys
from datetime import datetime, timedelta, timezone
from collections import defaultdict

sys.path.insert(0, r"C:\Arclinic")
from shared.bitrix24 import call

MSK = timezone(timedelta(hours=3))
CACHE = os.path.join(os.path.dirname(__file__), "client_segmentation_cache.json")
start_date = datetime(2020, 1, 1, tzinfo=MSK)


def parse_dt(ds):
    if not ds:
        return None
    try:
        return datetime.fromisoformat(ds.replace("Z", "+00:00"))
    except Exception:
        try:
            return datetime.strptime(ds[:10], "%Y-%m-%d").replace(tzinfo=MSK)
        except Exception:
            return None


def is_won(stage_id):
    """Только завершённые приёмы (C1:WON) учитываются в сегментации."""
    return (stage_id or "").upper() == "C1:WON"

def is_excluded(stage_id):
    return not is_won(stage_id)


def fetch_all_deals():
    print("  (API-запросы ~5 минут)")
    all_deals = []
    offset = 0
    page = 0
    while True:
        result = call("crm.deal.list", {
            "filter": {">=DATE_CREATE": start_date.strftime("%Y-%m-%dT%H:%M:%S+03:00")},
            "select": ["ID", "CONTACT_ID", "BEGINDATE", "UF_CRM_1738231866", "STAGE_ID"],
            "order": {"ID": "DESC"},
            "start": offset,
        })
        batch = result.get("result", [])
        if not batch:
            break
        total = result.get("total", 0)
        page += 1
        if page % 50 == 0 or len(all_deals) + len(batch) >= total:
            print(f"    Страница {page}: {len(all_deals) + len(batch)}/{total} сделок" + " " * 10, end="\r")
        all_deals.extend(batch)
        nxt = result.get("next")
        if nxt is None or nxt <= offset:
            break
        offset = nxt
    print()
    return all_deals


def load_deals(force=False):
    if os.path.exists(CACHE) and not force:
        cache_mtime = datetime.fromtimestamp(os.path.getmtime(CACHE), tz=MSK)
        if cache_mtime.date() == datetime.now(MSK).date():
            print(f"Загружаем сделки из кэша (сегодня, {cache_mtime.strftime('%H:%M')})...")
            with open(CACHE, "r", encoding="utf-8") as f:
                return json.load(f)
        else:
            print(f"Кэш устарел ({cache_mtime.strftime('%d.%m.%Y')}), перевыгружаем из Bitrix24...")

    deals = fetch_all_deals()
    with open(CACHE, "w", encoding="utf-8") as f:
        json.dump(deals, f, ensure_ascii=False)
    print(f"Сохранено в кэш: {len(deals)} сделок")
    return deals


def segment(dates, window_start, snapshot):
    """Определяет сегмент: primary / lost / dev / reg"""
    count = sum(1 for dt in dates if window_start < dt <= snapshot)
    if count == 0:
        has_history = any(dt <= window_start for dt in dates)
        return "lost" if has_history else "primary"
    elif count <= 5:
        return "dev"
    else:
        return "reg"


if __name__ == "__main__":
    print("Загружаем сделки...")
    all_deals = load_deals()

    print(f"Всего сделок в кэше: {len(all_deals)}")

    excluded_count = sum(1 for d in all_deals if is_excluded(d.get("STAGE_ID", "")))
    clean = [d for d in all_deals if not is_excluded(d.get("STAGE_ID", ""))]
    print(f"Исключено не-WON сделок: {excluded_count}")
    print(f"Осталось сделок: {len(clean)}")

    print("Группируем сделки по контактам...")
    contact_dates = defaultdict(list)
    no_contact = 0
    for d in clean:
        cid = d.get("CONTACT_ID")
        if not cid or cid == "0":
            no_contact += 1
            continue
        dt = parse_dt(d.get("UF_CRM_1738231866") or d.get("BEGINDATE") or d.get("DATE_CREATE", ""))
        if dt:
            contact_dates[cid].append(dt)

    print(f"Сделок без CONTACT_ID: {no_contact}")
    print(f"Уникальных клиентов:    {len(contact_dates)}")

    snap_apr = datetime(2026, 4, 30, 23, 59, 59, tzinfo=MSK)
    snap_may = datetime(2026, 5, 31, 23, 59, 59, tzinfo=MSK)
    win_apr_start = snap_apr - timedelta(days=365)
    win_may_start = snap_may - timedelta(days=365)

    print("Считаем переходы...")
    transition = defaultdict(lambda: defaultdict(int))

    for cid, dates in contact_dates.items():
        seg_apr = segment(dates, win_apr_start, snap_apr)
        seg_may = segment(dates, win_may_start, snap_may)
        transition[seg_apr][seg_may] += 1

    total = sum(sum(v.values()) for v in transition.values())

    labels = {
        "primary": "Первичные",
        "lost": "Потерянные",
        "dev": "Развитие",
        "reg": "Постоянные",
    }
    abbr = {"primary": "Перв.", "lost": "Пот.", "dev": "Разв.", "reg": "Пост."}
    order = ["primary", "lost", "dev", "reg"]

    print(f"\n=== Матрица переходов: апрель -> май 2026 ===")
    print(f"(окно апрель: {win_apr_start.strftime('%d.%m.%Y')} - {snap_apr.strftime('%d.%m.%Y')})")
    print(f"(окно май:    {win_may_start.strftime('%d.%m.%Y')} - {snap_may.strftime('%d.%m.%Y')})")
    print()

    from_col = "Из \\ В"
    exit_col = "Ушло"
    header = f"{from_col:<14}" + "".join(f"{abbr[to]:>8}" for to in order) + f"{exit_col:>8}"
    print(header)
    print("-" * (14 + 8 * 4 + 8))
    for fr in order:
        row = transition[fr]
        from_total = sum(row[to] for to in order)
        cells = "".join(f"{row.get(to, 0):>8}" for to in order)
        stayed = row.get(fr, 0)
        left = from_total - stayed
        print(f"{labels[fr]:<14}{cells}{left:>8}")

    print()
    print("=== Ключевые переходы ===")
    print(f"Из потерянных в развитие:      {transition['lost']['dev']:>5} чел.")
    print(f"Из потерянных в постоянные:     {transition['lost']['reg']:>5} чел.")
    print(f"Из первичных в развитие:        {transition['primary']['dev']:>5} чел. (новые клиенты)")
    print(f"Из первичных в постоянные:      {transition['primary']['reg']:>5} чел. (новые клиенты)")
    print(f"Из развития в постоянные:       {transition['dev']['reg']:>5} чел.")
    print()
    print(f"Из развития в потерянные:       {transition['dev']['lost']:>5} чел.")
    print(f"Из постоянных в потерянные:     {transition['reg']['lost']:>5} чел.")
    print(f"Из постоянных в развитие:       {transition['reg']['dev']:>5} чел.")

    print()
    print("=== Итоги по месяцам ===")
    april_total = sum(sum(transition[seg].values()) for seg in order)
    may_total = sum(sum(transition[fr].get(seg, 0) for seg in order) for fr in order)
    print(f"{'Сегмент':<14} {'Апрель':>8} {'Май':>8} {'Изм.':>8}")
    print("-" * 38)
    for seg in order:
        apr = sum(transition[seg].values())
        may = sum(transition[fr].get(seg, 0) for fr in order)
        delta = may - apr
        sign = "+" if delta > 0 else ""
        print(f"{labels[seg]:<14} {apr:>8} {may:>8} {sign}{delta:>7}")
    print("-" * 38)
    print(f"{'Всего':<14} {april_total:>8} {may_total:>8} {may_total - april_total:>+8}")
