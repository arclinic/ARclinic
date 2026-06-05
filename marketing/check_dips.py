#!/usr/bin/env python3
"""Проверка SQLite базы данных OpenCode."""

import sqlite3
from pathlib import Path

db_path = Path.home() / "AppData" / "Roaming" / "ai.opencode.desktop" / "DIPS"

print(f"📂 База данных: {db_path}")
print(f"   Размер: {db_path.stat().st_size} байт")
print()

conn = sqlite3.connect(str(db_path))
cursor = conn.cursor()

# Получаем список таблиц
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = [t[0] for t in cursor.fetchall()]
print(f"📋 Таблицы ({len(tables)}): {tables}")
print()

for table in tables:
    try:
        cursor.execute(f'SELECT * FROM "{table}" LIMIT 5')
        rows = cursor.fetchall()
        cols = [d[0] for d in cursor.description]
        print(f"📄 Таблица: {table}")
        print(f"   Колонки: {cols}")
        for row in rows:
            # Показываем содержимое, обрезая длинные строки
            display_row = tuple(str(c)[:200] if isinstance(c, str) else c for c in row)
            print(f"   {display_row}")
        print()
    except Exception as e:
        print(f"   ❌ Ошибка: {e}")

conn.close()
