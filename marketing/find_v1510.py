import subprocess, json

# Получаем все релизы
result = subprocess.run(
    ['curl.exe', '-s', 'https://api.github.com/repos/anomalyco/opencode/releases?per_page=100'],
    capture_output=True, text=True
)
print(f'Status: {result.returncode}')
print(f'Output length: {len(result.stdout)}')
print(f'Stderr: {result.stderr[:200]}')

try:
    releases = json.loads(result.stdout)
    print(f'Releases count: {len(releases)}')
    for rel in releases[:5]:
        print(f'  {rel.get("tag_name")}')
except Exception as e:
    print(f'Error: {e}')
    print(result.stdout[:500])
