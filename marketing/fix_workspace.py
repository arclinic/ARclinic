#!/usr/bin/env python3
"""Конвертация workspace-файлов: строки -> объекты для v1.15.11."""

import json
from pathlib import Path

p = Path.home() / "AppData" / "Roaming" / "ai.opencode.desktop"

print("=" * 60)
print("Конвертация workspace-файлов для v1.15.11")
print("=" * 60)

for f in sorted(p.glob("opencode.workspace.*.dat")):
    print(f"\n📝 {f.name}")
    
    with open(f, "r", encoding="utf-8") as fh:
        raw = json.load(fh)
    
    # Конвертируем строки в объекты
    converted = {}
    for k, v in raw.items():
        if isinstance(v, str):
            try:
                converted[k] = json.loads(v)
                print(f"   ✅ {k}: строка -> объект")
            except json.JSONDecodeError:
                converted[k] = v
                print(f"   ⚠️ {k}: не JSON, оставлено")
        else:
            converted[k] = v
            print(f"   ℹ️ {k}: уже объект")
    
    # Сохраняем
    with open(f, "w", encoding="utf-8") as fh:
        json.dump(converted, fh, indent=2, ensure_ascii=False)
    
    print(f"   ✅ Сохранён ({f.stat().st_size} bytes)")

print(f"\n✅ Готово!")
