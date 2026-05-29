import urllib.request, json

token_path = r'C:\Users\Пользователь\AppData\Local\Temp\gh_token.txt'
with open(token_path) as f:
    token = f.read().strip()

req = urllib.request.Request(
    'https://api.github.com/repos/arclinic/ARclinic/pages/builds?per_page=1',
    headers={
        'Authorization': f'token {token}',
        'Accept': 'application/vnd.github.v3+json'
    }
)

try:
    resp = urllib.request.urlopen(req, timeout=15)
    data = json.loads(resp.read())
    for build in data:
        print('Status:', build.get('status'))
        print('Error:', build.get('error', {}).get('message', 'none'))
        print('Commit:', str(build.get('commit', ''))[:8])
except Exception as e:
    print('API Error:', e)

print('---')
req2 = urllib.request.Request(
    'https://api.github.com/repos/arclinic/ARclinic/pages',
    headers={
        'Authorization': f'token {token}',
        'Accept': 'application/vnd.github.v3+json'
    }
)
try:
    resp2 = urllib.request.urlopen(req2, timeout=15)
    data2 = json.loads(resp2.read())
    print('Pages status:', data2.get('status'))
    print('URL:', data2.get('html_url'))
except Exception as e:
    print('Pages API Error:', e)
