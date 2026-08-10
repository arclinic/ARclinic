import requests, re
urls = [
    '/services/cosmetology/injection/botulinoterapiya/',
    '/services/cosmetology/injection/konturnaya-plastika/',
    '/services/cosmetology/injection/biorevitalizatsiya/',
    '/services/health-center/ginekologiya/',
    '/services/health-center/endokrinologiya/',
    '/doctors/',
]
for url_path in urls:
    r = requests.get('https://arclinic.ru' + url_path, timeout=15)
    h1 = re.search(r'<h1[^>]*>(.*?)</h1>', r.text, re.IGNORECASE | re.DOTALL)
    title = re.search(r'<title>(.*?)</title>', r.text, re.IGNORECASE | re.DOTALL)
    if h1:
        h1_text = re.sub(r'<[^>]*>', '', h1.group(1)).strip()
        print(f'{url_path.split("/")[-2]}:')
        print(f'  Title: {title.group(1) if title else "N/A"}')
        print(f'  H1:    {h1_text}')
    else:
        print(f'{url_path.split("/")[-2]}: H1 NOT FOUND')
