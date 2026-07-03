import os
from datetime import datetime, timedelta, timezone
from collections import defaultdict

from client_segmentation_transition import load_deals, parse_dt, is_lose, segment

MSK = timezone(timedelta(hours=3))

print("Загружаем сделки (с автосвежестью кэша)...")
deals = load_deals()

clean = [d for d in deals if not is_lose(d.get("STAGE_ID", ""))]

contact_dates = defaultdict(list)
no_contact = 0
for d in clean:
    cid = d.get("CONTACT_ID")
    if not cid or cid == "0":
        no_contact += 1
        continue
    dt = parse_dt(d.get("BEGINDATE") or d.get("DATE_CREATE", ""))
    if dt:
        contact_dates[cid].append(dt)

snap_prev = datetime(2026, 5, 31, 23, 59, 59, tzinfo=MSK)
snap_curr = datetime(2026, 6, 30, 23, 59, 59, tzinfo=MSK)
win_prev_start = snap_prev - timedelta(days=365)
win_curr_start = snap_curr - timedelta(days=365)

transition = defaultdict(lambda: defaultdict(int))
for cid, dates in contact_dates.items():
    seg_prev = segment(dates, win_prev_start, snap_prev)
    seg_curr = segment(dates, win_curr_start, snap_curr)
    transition[seg_prev][seg_curr] += 1

primary_to_dev = transition["primary"]["dev"]
primary_to_reg = transition["primary"]["reg"]
primary_to_lost = transition["primary"]["lost"]
lost_to_dev = transition["lost"]["dev"]
lost_to_reg = transition["lost"]["reg"]
dev_to_reg = transition["dev"]["reg"]
dev_to_lost = transition["dev"]["lost"]
dev_to_primary = transition["dev"]["primary"]
reg_to_lost = transition["reg"]["lost"]
reg_to_dev = transition["reg"]["dev"]

print("=== Переходы между сегментами за июнь 2026 ===")
print("(без проваленных сделок LOSE)")
print()

print("--- Новые клиенты (первичные -> активные) ---")
print(f"Первичные -> развитие:                             {primary_to_dev} чел.")
print(f"Первичные -> постоянные:                           {primary_to_reg} чел.")
print(f"Первичные -> потерянные (уже ушли):                {primary_to_lost} чел.")
print()

print("--- Реактивация (потерянные -> активные) ---")
print(f"Потерянные -> развитие:                            {lost_to_dev} чел.")
print(f"Потерянные -> постоянные:                          {lost_to_reg} чел.")
print()

print("--- Рост (развитие -> постоянные) ---")
print(f"Развитие -> постоянные:                            {dev_to_reg} чел.")
print()

print("--- Отток (активные -> потерянные) ---")
print(f"Развитие -> потерянные:                            {dev_to_lost} чел.")
print(f"Постоянные -> потерянные:                          {reg_to_lost} чел.")
print()

print("--- Снижение ---")
print(f"Постоянные -> развитие:                            {reg_to_dev} чел.")
print(f"Развитие -> первичные (обнулились):                {dev_to_primary} чел.")
print()

print("=== Баланс ===")
outflow = dev_to_lost + reg_to_lost + primary_to_lost
inflow = lost_to_dev + lost_to_reg
new_active = primary_to_dev + primary_to_reg
print(f"Ушло в потерянные (активные + первичные):          {outflow} чел.")
print(f"Вернулось из потерянных в активные:                {inflow} чел.")
print(f"Новых клиентов в активе (первичные -> dev/reg):    {new_active} чел.")
print(f"Чистый отток в потерянные:                         {outflow - inflow} чел.")
