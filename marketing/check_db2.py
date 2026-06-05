import sqlite3
from pathlib import Path
import json

p = Path.home() / 'AppData' / 'Roaming' / 'ai.opencode.desktop' / 'DIPS'
conn = sqlite3.connect(str(p))
cursor = conn.cursor()

for table in ['meta', 'config', 'bounces', 'popups']:
    cursor.execute(f'SELECT * FROM "{table}"')
    rows = cursor.fetchall()
    cursor.execute(f'PRAGMA table_info("{table}")')
    cols = [c[1] for c in cursor.fetchall()]
    print(f'\n=== {table} ===')
    print(f'  Columns: {cols}')
    print(f'  Rows: {len(rows)}')
    for row in rows[:5]:
        print(f'    {row}')

conn.close()
