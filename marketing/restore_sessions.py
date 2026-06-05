#!/usr/bin/env python3
"""Восстановление сессий и моделей для OpenCode v1.15.11."""

import json
import os
from pathlib import Path

p = Path.home() / "AppData" / "Roaming" / "ai.opencode.desktop"

print("=" * 60)
print("Восстановление сессий и моделей для OpenCode v1.15.11")
print("=" * 60)

# 1. Читаем opencode.global.dat
config_path = p / "opencode.global.dat"
with open(config_path, "r", encoding="utf-8") as f:
    raw = json.load(f)

# Парсим строки в объекты
config = {}
for k, v in raw.items():
    if isinstance(v, str):
        try:
            config[k] = json.loads(v)
        except:
            config[k] = v
    else:
        config[k] = v

print(f"\n📖 Конфиг прочитан, ключи: {list(config.keys())}")

# 2. Получаем данные
server = config.get("server", {})
projects = server.get("projects", {}).get("local", [])
model_data = config.get("model", {})
user_models = model_data.get("user", [])
layout = config.get("layout", {})

print(f"📁 Проектов: {len(projects)}")
print(f"🤖 Моделей: {len(user_models)}")

# 3. Маппинг workspace-файлов к проектам
# Определяем какой workspace-файл к какому проекту относится
workspace_files = {}
for f in p.glob("opencode.workspace.*.dat"):
    name = f.stem.replace("opencode.workspace.", "")
    workspace_files[name] = f

print(f"\n🔍 Найдено workspace-файлов: {len(workspace_files)}")
for name, f in workspace_files.items():
    print(f"   {name} -> {f.name}")

# 4. Обновляем каждый workspace-файл с проектами и моделями
print(f"\n🔧 Обновление workspace-файлов...")

# Маппинг: имя workspace -> путь проекта
# Из предыдущего анализа:
ws_project_map = {
    "C--Arclinic-": "C:\\Arclinic",
    "C--Arclinic.gvb6oy": "C:\\Arclinic\\marketing",
    "D--------": "D:\\",
    "D--TEST": "D:\\TEST",
    "QzpcQXJjbGlu.lus2f5": "C:\\Arclinic",
    "QzpcQXJjbGlu.pq2zyd": "C:\\Arclinic",
    "RDpc0JrRgdC1": "D:\\Ксения",
    "RDpcVEVTVA": "D:\\TEST",
}

# Модели free-claude-code
fcc_models = [m for m in user_models if m.get("providerID") == "free-claude-code"]
print(f"\n🤖 Модели free-claude-code: {len(fcc_models)}")
for m in fcc_models:
    print(f"   - {m['modelID']}")

# Сессии из layout
session_tabs = layout.get("sessionTabs", {})
session_view = layout.get("sessionView", {})

for ws_name, ws_path in ws_project_map.items():
    ws_file = workspace_files.get(ws_name)
    if not ws_file:
        print(f"   ⚠️ Не найден workspace-файл для {ws_name}")
        continue
    
    print(f"\n   📝 {ws_file.name} ({ws_path})")
    
    with open(ws_file, "r", encoding="utf-8") as f:
        ws_data = json.load(f)
    
    # Добавляем project info если нет
    if "workspace:project" not in ws_data:
        ws_data["workspace:project"] = json.dumps({
            "value": {"icon": {"color": "purple"}}
        }, ensure_ascii=False)
    
    # Добавляем vcs если нет
    if "workspace:vcs" not in ws_data:
        ws_data["workspace:vcs"] = json.dumps({
            "value": {"branch": None, "default_branch": None}
        }, ensure_ascii=False)
    
    # Добавляем model-selection с free-claude-code моделями
    if fcc_models:
        # Берём первую модель free-claude-code
        model = fcc_models[0]
        ws_data["workspace:model-selection"] = json.dumps({
            "session": {}
        }, ensure_ascii=False)
    
    # Добавляем prompt и comments если нет
    if "workspace:prompt" not in ws_data:
        ws_data["workspace:prompt"] = json.dumps({
            "prompt": [{"type": "text", "content": "", "start": 0, "end": 0}],
            "context": {"items": []},
            "cursor": 0
        }, ensure_ascii=False)
    
    if "workspace:comments" not in ws_data:
        ws_data["workspace:comments"] = json.dumps({"comments": {}}, ensure_ascii=False)
    
    with open(ws_file, "w", encoding="utf-8") as f:
        json.dump(ws_data, f, indent=2, ensure_ascii=False)
    
    print(f"      ✅ Обновлён")

# 5. Обновляем opencode.global.dat для v1.15.11 (только то, что он понимает)
print(f"\n💾 Обновление opencode.global.dat...")

v1511_config = {
    "notification": json.dumps(config.get("notification", {"list": []}), ensure_ascii=False),
    "command.catalog.v1": json.dumps(config.get("command.catalog.v1", {}), ensure_ascii=False)
}

with open(config_path, "w", encoding="utf-8") as f:
    json.dump(v1511_config, f, indent=2, ensure_ascii=False)

print(f"   ✅ Конфиг обновлён для v1.15.11")

print(f"\n✅ Готово! Запустите OpenCode v1.15.11")
