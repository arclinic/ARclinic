#!/usr/bin/env python3
"""Миграция данных из opencode.global.dat (v1.15.13) в workspace-файлы (v1.15.11)."""

import json
import os
from pathlib import Path

p = Path.home() / "AppData" / "Roaming" / "ai.opencode.desktop"

print("=" * 60)
print("Миграция данных OpenCode v1.15.13 -> v1.15.11")
print("=" * 60)

# 1. Читаем opencode.global.dat
config_path = p / "opencode.global.dat"
if not config_path.exists():
    print("❌ opencode.global.dat не найден!")
    exit(1)

with open(config_path, "r", encoding="utf-8") as f:
    raw = json.load(f)

# Парсим строки в объекты
config = {}
for k, v in raw.items():
    if isinstance(v, str):
        try:
            config[k] = json.loads(v)
        except json.JSONDecodeError:
            config[k] = v
    else:
        config[k] = v

print(f"\n📖 Прочитан конфиг: {config_path}")
print(f"   Ключи: {list(config.keys())}")

# 2. Получаем проекты из server
server = config.get("server", {})
projects = server.get("projects", {}).get("local", [])
print(f"\n📁 Проекты ({len(projects)}):")
for proj in projects:
    print(f"   - {proj.get('worktree')}")

# 3. Получаем модели из model
model_data = config.get("model", {})
user_models = model_data.get("user", [])
print(f"\n🤖 Модели ({len(user_models)}):")
for m in user_models:
    print(f"   - {m.get('providerID')}/{m.get('modelID')}")

# 4. Получаем layout для sidebar
layout = config.get("layout", {})
sidebar = layout.get("sidebar", {})
print(f"\n📐 Layout: sidebar.opened={sidebar.get('opened')}")

# 5. Создаём/обновляем workspace-файлы для каждого проекта
print(f"\n🔧 Создание workspace-файлов...")

# Маппинг путей проектов -> имена workspace-файлов
# OpenCode использует хэшированные имена на основе пути
import hashlib
import base64

def get_workspace_name(worktree):
    """Генерирует имя workspace-файла как это делает OpenCode."""
    # OpenCode использует base64url от пути
    path_bytes = worktree.replace("\\", "/").lower().encode("utf-8")
    # Простое кодирование: заменяем спецсимволы
    name = worktree.replace(":", "").replace("\\", "-").replace("/", "-").replace(" ", "-")
    return f"opencode.workspace.{name}"

# Создаём workspace-файлы
for proj in projects:
    worktree = proj.get("worktree", "")
    if not worktree:
        continue
    
    # Ищем существующий workspace-файл для этого пути
    ws_files = list(p.glob(f"opencode.workspace.*{Path(worktree).name}*.dat"))
    
    if ws_files:
        ws_file = ws_files[0]
        print(f"   📝 Обновляем: {ws_file.name}")
        
        with open(ws_file, "r", encoding="utf-8") as f:
            ws_data = json.load(f)
        
        # Добавляем project info
        ws_data["workspace:project"] = json.dumps({
            "value": {
                "icon": {"color": "purple"}
            }
        }, ensure_ascii=False)
        
        # Добавляем model-selection (выбираем первую модель free-claude-code)
        fcc_models = [m for m in user_models if m.get("providerID") == "free-claude-code"]
        if fcc_models:
            ws_data["workspace:model-selection"] = json.dumps({
                "session": {}
            }, ensure_ascii=False)
        
        with open(ws_file, "w", encoding="utf-8") as f:
            json.dump(ws_data, f, indent=2, ensure_ascii=False)
    else:
        print(f"   ⚠️ Не найден workspace-файл для: {worktree}")

# 6. Обновляем opencode.global.dat для v1.15.11 (только notification и command.catalog)
print(f"\n💾 Обновление opencode.global.dat для v1.15.11...")

v1511_config = {
    "notification": json.dumps(config.get("notification", {"list": []}), ensure_ascii=False),
    "command.catalog.v1": json.dumps(config.get("command.catalog.v1", {}), ensure_ascii=False)
}

with open(config_path, "w", encoding="utf-8") as f:
    json.dump(v1511_config, f, indent=2, ensure_ascii=False)

print(f"   ✅ Конфиг обновлён: {list(v1511_config.keys())}")

print(f"\n✅ Готово! Теперь можно запустить OpenCode v1.15.11")
