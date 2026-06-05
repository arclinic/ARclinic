import sys, json, subprocess

result = subprocess.run(
    ['curl.exe', '-s', 'https://api.github.com/repos/anomalyco/opencode/releases/latest'],
    capture_output=True, text=True
)
d = json.loads(result.stdout)
print('Tag:', d.get('tag_name'))
print()
for a in d.get('assets', []):
    name = a.get('name', '')
    url = a.get('browser_download_url', '')
    size = a.get('size', 0)
    print(f'  {name} ({size} bytes)')
    print(f'    {url}')
