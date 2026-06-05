from pathlib import Path
import json

p = Path.home() / 'AppData' / 'Roaming' / 'ai.opencode.desktop'

# Читаем текущий конфиг
with open(p / 'opencode.global.dat', 'r', encoding='utf-8') as f:
    config = json.load(f)

# Парсим layout.page
lp = json.loads(config.get('layout.page', '{}'))

# Сопоставляем workspace файлы с проектами
workspace_map = {
    'opencode.workspace.C--Arclinic-.zsijlh.dat': 'C:\\Arclinic',
    'opencode.workspace.C--Arclinic.gvb6oy.dat': 'C:\\Arclinic',
    'opencode.workspace.D--------.1k7owpu.dat': 'D:\\Ксения',
    'opencode.workspace.D--TEST.1g9n7pk.dat': 'D:\\TEST',
    'opencode.workspace.QzpcQXJjbGlu.lus2f5.dat': 'C:\\Arclinic',
    'opencode.workspace.QzpcQXJjbGlu.pq2zyd.dat': 'C:\\Arclinic',
    'opencode.workspace.RDpc0JrRgdC1.1tnkkwb.dat': 'D:\\Ксения',
    'opencode.workspace.RDpcVEVTVA.1nikrew.dat': 'D:\\TEST',
}

# Собираем сессии из workspace-файлов
workspace_order = {}
workspace_name = {}
workspace_branch = {}
workspace_expanded = {}
last_project_session = {}

for fname, project_path in workspace_map.items():
    fpath = p / fname
    if not fpath.exists():
        continue
    
    with open(fpath, 'r', encoding='utf-8') as f:
        wdata = json.load(f)
    
    # Определяем имя проекта из пути
    proj_name = project_path.split('\\')[-1]
    
    # Получаем vcs
    vcs = wdata.get('workspace:vcs', {})
    if isinstance(vcs, str):
        try:
            vcs = json.loads(vcs)
        except:
            vcs = {}
    
    # Определяем ветку
    branch = None
    if isinstance(vcs, dict):
        vcs_val = vcs.get('value', {})
        if isinstance(vcs_val, dict):
            branch = vcs_val.get('branch')
    
    # Добавляем в workspaceOrder
    if proj_name not in workspace_order:
        workspace_order[proj_name] = []
    
    # Добавляем в workspaceName
    workspace_name[proj_name] = proj_name
    
    # Добавляем в workspaceBranchName
    if branch:
        workspace_branch[proj_name] = branch
    
    # Добавляем в workspaceExpanded
    workspace_expanded[proj_name] = True
    
    # Получаем model-selection (сессии)
    ms = wdata.get('workspace:model-selection', {})
    if isinstance(ms, str):
        try:
            ms = json.loads(ms)
        except:
            ms = {}
    
    if isinstance(ms, dict):
        sessions = ms.get('session', {})
        if isinstance(sessions, dict):
            for session_id, session_data in sessions.items():
                if session_id not in last_project_session:
                    last_project_session[session_id] = {}
                last_project_session[session_id]['model'] = session_data

# Обновляем layout.page
lp['workspaceOrder'] = workspace_order
lp['workspaceName'] = workspace_name
lp['workspaceBranchName'] = workspace_branch
lp['workspaceExpanded'] = workspace_expanded
lp['lastProjectSession'] = last_project_session
lp['gettingStartedDismissed'] = True

# Сохраняем обратно
config['layout.page'] = json.dumps(lp, ensure_ascii=False)

with open(p / 'opencode.global.dat', 'w', encoding='utf-8') as f:
    json.dump(config, f, indent=2, ensure_ascii=False)

print('=== Восстановлено ===')
print('workspaceOrder:', json.dumps(workspace_order, indent=2, ensure_ascii=False))
print()
print('workspaceName:', json.dumps(workspace_name, indent=2, ensure_ascii=False))
print()
print('workspaceBranchName:', json.dumps(workspace_branch, indent=2, ensure_ascii=False))
print()
print('lastProjectSession keys:', list(last_project_session.keys()))
for sid, sdata in last_project_session.items():
    print(f'  {sid}: {json.dumps(sdata, indent=4, ensure_ascii=False)}')
