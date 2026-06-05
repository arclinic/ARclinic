import sqlite3
from pathlib import Path

p = Path.home() / 'AppData' / 'Roaming' / 'ai.opencode.desktop' / 'DIPS'
conn = sqlite3.connect(str(p))
cursor = conn.cursor()

# Получаем список таблиц
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = cursor.fetchall()
print('Tables:', [t[0] for t in tables])

for table in tables:
    name = table[0]
    cursor.execute(f'SELECT * FROM "{name}" LIMIT 3')
    rows = cursor.fetchall()
    cursor.execute(f'PRAGMA table_info("{name}")')
    cols = [c[1] for c in cursor.fetchall()]
    print(f'\n=== {name} ===')
    print(f'  Columns: {cols}')
    print(f'  Rows: {len(rows)}')
    for row in rows:
        print(f'    {row}')

conn.close()
