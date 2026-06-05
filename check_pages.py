import urllib.request, json

gh_token_path = r'C:\Users\Пользователь\AppData\Local\Temp\gh_token.txt'
with open(gh_token_path) as f:
    gh_token = f.read().strip()

req = urllib.request.Request(
    'https://api.github.com/repos/arclinic/ARclinic/pages/builds',
    headers={
        'Authorization': f'token {gh_token}',
        'Accept': 'application/vnd.github.v3+json'
    }
)
resp = urllib.request.urlopen(req, timeout=15)
data = json.loads(resp.read())

for build in data[:3]:
    status = build.get('status')
    error = build.get('error', {}).get('message', 'none')
    commit = build.get('commit')
    created = build.get('created_at')
    print(f'Status: {status}')
    print(f'Error: {error}')
    print(f'Commit: {commit}')
    print(f'Created: {created}')
    print()

req2 = urllib.request.Request(
    'https://api.github.com/repos/arclinic/ARclinic/pages',
    headers={
        'Authorization': f'token {gh_token}',
        'Accept': 'application/vnd.github.v3+json'
    }
)
resp2 = urllib.request.urlopen(req2, timeout=15)
pages = json.loads(resp2.read())
print(f'HTML URL: {pages.get("html_url")}')
print(f'Status: {pages.get("status")}')
