import os, sys
from datetime import datetime, timedelta, timezone
from collections import defaultdict

from client_segmentation_transition import load_deals, parse_dt, is_lose, segment

sys.path.insert(0, r"C:\Arclinic")
from shared.bitrix24 import call

MSK = timezone(timedelta(hours=3))

print("Загружаем сделки (с автосвежестью кэша)...")
deals = load_deals()

clean = [d for d in deals if not is_lose(d.get("STAGE_ID", ""))]

contact_dates = defaultdict(list)
for d in clean:
    cid = d.get("CONTACT_ID")
    if not cid or cid == "0":
        continue
    dt = parse_dt(d.get("BEGINDATE") or d.get("DATE_CREATE", ""))
    if dt:
        contact_dates[cid].append(dt)

snap_prev = datetime(2026, 5, 31, 23, 59, 59, tzinfo=MSK)
snap_curr = datetime(2026, 6, 30, 23, 59, 59, tzinfo=MSK)
win_prev_start = snap_prev - timedelta(days=365)
win_curr_start = snap_curr - timedelta(days=365)

reactivated = []
for cid, dates in contact_dates.items():
    seg_prev = segment(dates, win_prev_start, snap_prev)
    seg_curr = segment(dates, win_curr_start, snap_curr)
    if seg_prev == "lost" and seg_curr == "dev":
        count_curr = sum(1 for dt in dates if win_curr_start < dt <= snap_curr)
        curr_new = sum(1 for dt in dates if snap_prev < dt <= snap_curr)
        last_before = max((dt for dt in dates if dt <= snap_prev), default=None)
        reactivated.append((cid, count_curr, curr_new, last_before))

reactivated.sort(key=lambda x: -x[1])

print(f"Загружаем имена для {len(reactivated)} клиентов...")
names = {}
for i, (cid, _, _, _) in enumerate(reactivated):
    try:
        r = call("crm.contact.get", {"id": cid})
        res = r.get("result", {})
        if res:
            name = f"{res.get('NAME', '')} {res.get('LAST_NAME', '')}".strip()
            names[cid] = name or f"ID:{cid}"
        else:
            names[cid] = f"ID:{cid}"
    except Exception:
        names[cid] = f"ID:{cid}"
    print(f"  {i + 1}/{len(reactivated)}", end="\r")
print()

OUTPUT = os.path.join(os.path.dirname(__file__), "lost_to_dev_june.txt")
BASE_URL = "https://arclinic.bitrix24.ru/crm/contact/details"

with open(OUTPUT, "w", encoding="utf-8") as f:
    f.write("N  | Пациент                                    | Сделок июнь | Новых в июне | Посл. до июня | Карточка\n")
    f.write("-" * 130 + "\n")
    for idx, (cid, cnt_m, new_m, last_d) in enumerate(reactivated, 1):
        nm = names.get(cid, f"ID:{cid}")
        ld_str = last_d.strftime("%d.%m.%Y") if last_d else "-"
        url = f"{BASE_URL}/{cid}/"
        f.write(f"{idx:2} | {nm:<44} | {cnt_m:>10} | {new_m:>10} | {ld_str:>12} | {url}\n")
        print(f"{idx:2} | {nm:<44} | {cnt_m:>10} | {new_m:>10} | {ld_str:>12} | {url}")
    f.write(f"\nВсего: {len(reactivated)} пациентов\n")

print(f"\nСохранено: {OUTPUT}")
print(f"Найдено: {len(reactivated)} пациентов")
