#!/usr/bin/env python3
"""Конвертация конфига OpenCode из формата v1.15.13 в v1.15.12."""

import json
from pathlib import Path

p = Path.home() / "AppData" / "Roaming" / "ai.opencode.desktop"
config_path = p / "opencode.global.dat"

print("=" * 60)
print("Конвертация конфига OpenCode v1.15.13 -> v1.15.12")
print("=" * 60)

# Читаем текущий конфиг
with open(config_path, "r", encoding="utf-8") as f:
    d = json.load(f)

print(f"\n📖 Прочитан конфиг: {config_path}")
print(f"   Ключи: {list(d.keys())}")

# Конвертируем строки в объекты
converted = {}
for k, v in d.items():
    if isinstance(v, str):
        try:
            converted[k] = json.loads(v)
            print(f"   ✅ {k}: строка -> объект")
        except json.JSONDecodeError:
            converted[k] = v
            print(f"   ⚠️ {k}: не удалось распарсить, оставлено как строка")
    else:
        converted[k] = v
        print(f"   ℹ️ {k}: оставлено как есть ({type(v).__name__})")

# Сохраняем бэкап
bak_path = config_path.with_suffix(".dat.bak3")
with open(bak_path, "w", encoding="utf-8") as f:
    json.dump(d, f, indent=2, ensure_ascii=False)
print(f"\n💾 Бэкап сохранён: {bak_path.name}")

# Сохраняем конвертированный конфиг
with open(config_path, "w", encoding="utf-8") as f:
    json.dump(converted, f, indent=2, ensure_ascii=False)
print(f"💾 Конвертированный конфиг сохранён")

# Проверяем
size = config_path.stat().st_size
print(f"\n✅ Готово! Размер: {size} bytes")
print(f"   Ключи: {list(converted.keys())}")
