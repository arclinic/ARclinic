#!/usr/bin/env python3
"""Скрипт для добавления модели free-claude-code в конфиг OpenCode."""

import json
from pathlib import Path

CONFIG_PATH = Path.home() / "AppData" / "Roaming" / "ai.opencode.desktop" / "opencode.global.dat"

def main():
    print("=" * 60)
    print("Добавление модели free-claude-code в OpenCode")
    print("=" * 60)
    
    # Читаем конфиг
    print(f"\n📖 Чтение: {CONFIG_PATH}")
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        config = json.load(f)
    
    # Обновляем раздел model
    model_data = json.loads(config.get("model", "{}"))
    
    # Модели от free-claude-code
    fcc_models = [
        {"modelID": "claude-sonnet-4-20250514", "providerID": "free-claude-code", "visibility": "show"},
        {"modelID": "claude-opus-4-20250514", "providerID": "free-claude-code", "visibility": "show"},
        {"modelID": "claude-haiku-4-20250514", "providerID": "free-claude-code", "visibility": "show"},
        {"modelID": "claude-3-5-sonnet-20241022", "providerID": "free-claude-code", "visibility": "show"},
        {"modelID": "claude-3-5-haiku-20241022", "providerID": "free-claude-code", "visibility": "show"},
        {"modelID": "claude-3-opus-20240229", "providerID": "free-claude-code", "visibility": "show"},
        {"modelID": "claude-3-haiku-20240307", "providerID": "free-claude-code", "visibility": "show"},
    ]
    
    existing = model_data.get("user", [])
    existing_ids = {(m["modelID"], m["providerID"]) for m in existing}
    
    added = 0
    for model in fcc_models:
        if (model["modelID"], model["providerID"]) not in existing_ids:
            existing.insert(0, model)
            added += 1
            print(f"   ✅ Добавлена: {model['providerID']}/{model['modelID']}")
    
    model_data["user"] = existing
    
    # Добавляем в recent
    recent = model_data.get("recent", [])
    recent_ids = {(m["modelID"], m["providerID"]) for m in recent}
    for model in fcc_models[:3]:
        if (model["modelID"], model["providerID"]) not in recent_ids:
            recent.insert(0, {"modelID": model["modelID"], "providerID": model["providerID"]})
    
    model_data["recent"] = recent
    config["model"] = json.dumps(model_data, ensure_ascii=False)
    
    # Сохраняем
    print(f"\n💾 Сохранение конфигурации...")
    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=2, ensure_ascii=False)
    
    print(f"\n✅ Готово! Добавлено моделей: {added}")
    print(f"   📍 {CONFIG_PATH}")

if __name__ == "__main__":
    main()
