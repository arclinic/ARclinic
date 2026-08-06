import os, sys
from datetime import datetime, timedelta, timezone
from collections import defaultdict

from client_segmentation_transition import load_deals, parse_dt, is_excluded, segment

sys.path.insert(0, r"C:\Arclinic")
from shared.bitrix24 import call

MSK = timezone(timedelta(hours=3))

print("Загружаем сделки (с автосвежестью кэша)...")
deals = load_deals()

clean = [d for d in deals if not is_excluded(d.get("STAGE_ID", ""))]

contact_dates = defaultdict(list)
for d in clean:
    cid = d.get("CONTACT_ID")
    if not cid or cid == "0":
        continue
    dt = parse_dt(d.get("UF_CRM_1738231866") or d.get("BEGINDATE") or d.get("DATE_CREATE", ""))
    if dt:
        contact_dates[cid].append(dt)

snap_prev = datetime(2026, 5, 31, 23, 59, 59, tzinfo=MSK)
snap_curr = datetime(2026, 6, 30, 23, 59, 59, tzinfo=MSK)
win_prev_start = snap_prev - timedelta(days=365)
win_curr_start = snap_curr - timedelta(days=365)

new_clients = []
for cid, dates in contact_dates.items():
    seg_prev = segment(dates, win_prev_start, snap_prev)
    seg_curr = segment(dates, win_curr_start, snap_curr)
    if seg_prev == "primary" and seg_curr in ("dev", "reg"):
        count_curr = sum(1 for dt in dates if win_curr_start < dt <= snap_curr)
        first_visit = min((dt for dt in dates if dt > snap_prev), default=None)
        new_clients.append((cid, count_curr, seg_curr, first_visit))

print(f"Загружаем имена для {len(new_clients)} клиентов...")
names = {}
for i, (cid, _, _, _) in enumerate(new_clients):
    try:
        r = call("crm.contact.get", {"id": cid})
        res = r.get("result", {})
        if res:
            last = (res.get("LAST_NAME") or "").strip()
            first = (res.get("NAME") or "").strip()
            full = f"{first} {last}".strip()
            names[cid] = (last, first, full or f"ID:{cid}")
        else:
            names[cid] = ("", "", f"ID:{cid}")
    except Exception:
        names[cid] = ("", "", f"ID:{cid}")
    print(f"  {i + 1}/{len(new_clients)}", end="\r")
print()

def sort_key(item):
    cid = item[0]
    last, first, _ = names.get(cid, ("", "", ""))
    return (last.upper() if last else "zzz", first.upper() if first else "")

new_clients.sort(key=sort_key)

OUTPUT = os.path.join(os.path.dirname(__file__), "primary_to_dev_june_sorted.txt")
with open(OUTPUT, "w", encoding="utf-8") as out:
    out.write(f"{'N':>3} | {'Пациент':<42} | Сд | Сегмент | Первый визит | Карточка\n")
    out.write("-" * 120 + "\n")
    for idx, (cid, cnt, seg, first_d) in enumerate(new_clients, 1):
        nm = names.get(cid, ("", "", f"ID:{cid}"))[2]
        fd_str = first_d.strftime("%d.%m.%Y") if first_d else "-"
        seg_label = "Пост." if seg == "reg" else "Разв."
        url = f"https://arclinic.bitrix24.ru/crm/contact/details/{cid}/"
        line = f"{idx:>3} | {nm:<42} | {cnt:>3} | {seg_label:<7} | {fd_str:>12} | {url}\n"
        out.write(line)
        print(line.rstrip())
    out.write(f"\nВсего: {len(new_clients)} новых клиентов\n")

print(f"\nСохранено: {OUTPUT}")
print(f"Всего: {len(new_clients)} новых клиентов")
