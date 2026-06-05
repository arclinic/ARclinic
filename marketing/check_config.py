from pathlib import Path
import json

p = Path.home() / 'AppData' / 'Roaming' / 'ai.opencode.desktop'

with open(p / 'opencode.global.dat', 'r', encoding='utf-8') as f:
    d = json.load(f)

# Проверяем server (проекты)
server = json.loads(d.get('server', '{}'))
print('=== SERVER (проекты) ===')
print('  projects:', len(server.get('projects', [])))
for pr in server.get('projects', []):
    print('    -', pr.get('name', '?'))

# Проверяем model
model = json.loads(d.get('model', '{}'))
print()
print('=== MODEL ===')
print('  user:', model.get('user', 'N/A'))
print('  recent:', model.get('recent', []))
print('  variant:', model.get('variant', 'N/A'))

# Проверяем layout.page (сессии)
lp = json.loads(d.get('layout.page', '{}'))
print()
print('=== LAYOUT.PAGE (сессии) ===')
print('  workspaceOrder:', lp.get('workspaceOrder', []))
print('  workspaceName:', lp.get('workspaceName', {}))
