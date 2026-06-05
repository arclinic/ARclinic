#!/usr/bin/env python3
"""Восстановление конфига OpenCode из бэкапа."""

import json
from pathlib import Path

p = Path.home() / "AppData" / "Roaming" / "ai.opencode.desktop"
bak = p / "opencode.global.dat.bak2"

if bak.exists():
    with open(bak, "r", encoding="utf-8") as f:
        d = json.load(f)
    
    with open(p / "opencode.global.dat", "w", encoding="utf-8") as f:
        json.dump(d, f, indent=2, ensure_ascii=False)
    
    size = (p / "opencode.global.dat").stat().st_size
    print(f"✅ Конфиг восстановлен из {bak.name}")
    print(f"   Размер: {size} bytes")
    print(f"   Ключи: {list(d.keys())}")
else:
    print("❌ Бэкап не найден!")
