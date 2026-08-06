import os
from datetime import datetime, timedelta, timezone
from collections import defaultdict

from client_segmentation_transition import load_deals, parse_dt, is_excluded

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

# Календарные месяцы
snap_prev = datetime(2026, 6, 30, 23, 59, 59, tzinfo=MSK)
snap_curr = datetime(2026, 7, 31, 23, 59, 59, tzinfo=MSK)
month_prev_start = snap_prev.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
month_curr_start = snap_curr.replace(day=1, hour=0, minute=0, second=0, microsecond=0)




transition = defaultdict(lambda: defaultdict(int))
for cid, dates in contact_dates.items():
    dates_sorted = sorted(dates)
    cnt_prev = sum(1 for d in dates_sorted if month_prev_start <= d <= snap_prev)
    cnt_curr = sum(1 for d in dates_sorted if month_curr_start <= d <= snap_curr)

    # Сегмент за предыдущий месяц
    if cnt_prev > 0:
        seg_prev = "dev" if cnt_prev <= 5 else "reg"
    else:
        past_prev = [d for d in dates_sorted if d < month_prev_start]
        if not past_prev:
            seg_prev = "primary"
        else:
            last_before = max(past_prev)
            first_in_curr = min((d for d in dates_sorted if d >= month_curr_start), default=None)
            if first_in_curr:
                gap = (first_in_curr - last_before).days
            else:
                gap = (snap_curr - last_before).days
            seg_prev = "lost" if gap > 365 else "dev"

    # Сегмент за текущий месяц
    if cnt_curr > 0:
        seg_curr = "dev" if cnt_curr <= 5 else "reg"
    else:
        past_curr = [d for d in dates_sorted if d < month_curr_start]
        if not past_curr:
            seg_curr = "primary"
        else:
            last_before = max(past_curr)
            gap = (snap_curr - last_before).days
            seg_curr = "lost" if gap > 365 else "dev"

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

print("=== Переходы между сегментами за июль 2026 ===")
print("(только C1:WON, календарный месяц)")
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
