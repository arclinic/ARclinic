from pathlib import Path
import json

p = Path.home() / 'AppData' / 'Roaming' / 'ai.opencode.desktop'

with open(p / 'opencode.global.dat', 'r', encoding='utf-8') as f:
    config = json.load(f)

# Проверяем server
server = config.get('server', {})
print('=== SERVER ===')
print('  projects:', json.dumps(server.get('projects', {}), indent=2, ensure_ascii=False)[:500])

# Проверяем model
model = config.get('model', {})
print()
print('=== MODEL ===')
print('  user count:', len(model.get('user', [])))
for u in model.get('user', []):
    pid = u.get('providerID', '?')
    mid = u.get('modelID', '?')
    print(f'    - {pid}/{mid}')

# Проверяем layout.page
lp = config.get('layout.page', {})
print()
print('=== LAYOUT.PAGE ===')
print('  workspaceOrder:', json.dumps(lp.get('workspaceOrder', {}), indent=2, ensure_ascii=False)[:300])
print('  lastProjectSession keys:', list(lp.get('lastProjectSession', {}).keys())[:5])
