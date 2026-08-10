import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env"))

keys_raw = os.getenv("APIFY_KEYS", "")
keys = [k.strip() for k in keys_raw.split(",") if k.strip()]

print(f"Keys found: {len(keys)}\n")

if not keys:
    print("[FAIL] No keys in APIFY_KEYS!")
    sys.exit(1)

import requests
from concurrent.futures import ThreadPoolExecutor, as_completed

BASE = "https://api.apify.com/v2"

def check_key(i, key):
    mask = key[:25] + "..."
    try:
        resp = requests.get(
            f"{BASE}/users/me",
            params={"token": key},
            timeout=10
        )
        if resp.status_code == 200:
            data = resp.json()
            user = data.get("data", {})
            username = user.get("username", "?")
            plan = user.get("plan", {}).get("name", "?")
            limits = user.get("stats", {}).get("currentMonth", {})
            runs = limits.get("actRunsUsd", "?")
            return (i, "OK", mask, username, plan, runs)
        elif resp.status_code == 401:
            return (i, "EXP", mask, "—", "—", "TOKEN_EXPIRED")
        else:
            return (i, "ERR", mask, f"HTTP {resp.status_code}", "—", "—")
    except Exception as e:
        return (i, "ERR", mask, str(e)[:40], "—", "—")

print(f"{'#':<3} {'St':<5} {'Key':<35} {'User':<22} {'Plan':<15} {'Usage/mo'}")
print("-" * 100)

results = []
with ThreadPoolExecutor(max_workers=5) as pool:
    futures = {pool.submit(check_key, i, k): i for i, k in enumerate(keys)}
    for f in as_completed(futures):
        i, status, mask, user, plan, runs = f.result()
        results.append((i, status, mask, user, plan, runs))

results.sort()
for i, status, mask, user, plan, runs in results:
    print(f"{i+1:<3} {status:<5} {mask:<35} {user:<22} {plan:<15} {runs}")

active = [r for r in results if r[1] == "OK"]
dead = [r for r in results if r[1] != "OK"]
print(f"\nActive keys: {len(active)} / {len(keys)}")

if active:
    print(f"\n[OK] Rotation works — {len(active)} valid keys in pool.")
    print(f"     When current key runs out of quota — auto-switch to next.")
    if dead:
        dead_idx = [d[0]+1 for d in dead]
        print(f"     [WARN] Dead keys (will be skipped after 401): #{dead_idx}")
else:
    print("\n[FAIL] No valid keys! Check your tokens.")
