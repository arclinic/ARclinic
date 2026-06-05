#!/usr/bin/env python3
"""Восстановление сессий и моделей для OpenCode v1.15.11 - правильная версия."""

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
for proj in projects:
    print(f"   - {proj.get('worktree')}")

print(f"🤖 Моделей: {len(user_models)}")

# 3. Читаем все workspace-файлы и определяем их маппинг
workspace_files = {}
for f in sorted(p.glob("opencode.workspace.*.dat")):
    with open(f, "r", encoding="utf-8") as fh:
        try:
            data = json.load(fh)
            workspace_files[f.name] = data
        except:
            print(f"   ⚠️ Не удалось прочитать {f.name}")

print(f"\n🔍 Найдено workspace-файлов: {len(workspace_files)}")

# 4. Для каждого проекта находим соответствующий workspace-файл
# OpenCode использует хэш от пути проекта для имени файла
# Но мы можем определить по содержимому

# Модели free-claude-code
fcc_models = [m for m in user_models if m.get("providerID") == "free-claude-code"]
print(f"\n🤖 Модели free-claude-code: {len(fcc_models)}")
for m in fcc_models:
    print(f"   - {m['modelID']}")

# Создаём сессии для free-claude-code моделей
# Каждая модель будет отдельной сессией
import uuid

def make_session_id():
    return "ses_" + uuid.uuid4().hex[:26]

# 5. Обновляем workspace-файлы
print(f"\n🔧 Обновление workspace-файлов...")

for ws_name, ws_data in workspace_files.items():
    print(f"\n   📝 {ws_name}")
    
    # Добавляем project info если нет
    if "workspace:project" not in ws_data:
        ws_data["workspace:project"] = json.dumps({
            "value": {"icon": {"color": "purple"}}
        }, ensure_ascii=False)
        print(f"      ✅ Добавлен workspace:project")
    
    # Добавляем vcs если нет
    if "workspace:vcs" not in ws_data:
        ws_data["workspace:vcs"] = json.dumps({
            "value": {"branch": None, "default_branch": None}
        }, ensure_ascii=False)
        print(f"      ✅ Добавлен workspace:vcs")
    
    # Добавляем model-selection с free-claude-code моделями
    if fcc_models and "workspace:model-selection" not in ws_data:
        sessions = {}
        for m in fcc_models:
            sid = make_session_id()
            sessions[sid] = {
                "agent": "build",
                "model": {
                    "providerID": "free-claude-code",
                    "modelID": m["modelID"]
                }
            }
        ws_data["workspace:model-selection"] = json.dumps({
            "session": sessions
        }, ensure_ascii=False)
        print(f"      ✅ Добавлен workspace:model-selection с {len(fcc_models)} моделями")
    
    # Добавляем prompt и comments если нет
    if "workspace:prompt" not in ws_data:
        ws_data["workspace:prompt"] = json.dumps({
            "prompt": [{"type": "text", "content": "", "start": 0, "end": 0}],
            "context": {"items": []},
            "cursor": 0
        }, ensure_ascii=False)
        print(f"      ✅ Добавлен workspace:prompt")
    
    if "workspace:comments" not in ws_data:
        ws_data["workspace:comments"] = json.dumps({"comments": {}}, ensure_ascii=False)
        print(f"      ✅ Добавлен workspace:comments")
    
    # Сохраняем
    with open(p / ws_name, "w", encoding="utf-8") as f:
        json.dump(ws_data, f, indent=2, ensure_ascii=False)

# 6. Обновляем opencode.global.dat для v1.15.11
print(f"\n💾 Обновление opencode.global.dat...")

v1511_config = {
    "notification": json.dumps(config.get("notification", {"list": []}), ensure_ascii=False),
    "command.catalog.v1": json.dumps(config.get("command.catalog.v1", {}), ensure_ascii=False)
}

with open(config_path, "w", encoding="utf-8") as f:
    json.dump(v1511_config, f, indent=2, ensure_ascii=False)

print(f"   ✅ Конфиг обновлён для v1.15.11")

print(f"\n✅ Готово! Запустите OpenCode v1.15.11")
