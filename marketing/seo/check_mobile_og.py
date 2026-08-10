import requests, re

pages = {
    'Homepage': 'https://arclinic.ru/',
    'Doctors': 'https://arclinic.ru/doctors/',
    'Services': 'https://arclinic.ru/services/',
    'About': 'https://arclinic.ru/about/',
    'Blog': 'https://arclinic.ru/blog/',
    'Prices': 'https://arclinic.ru/prices/',
    'Contacts': 'https://arclinic.ru/contacts/',
    'Ginekol': 'https://arclinic.ru/services/health-center/ginekologiya/',
    'Botox': 'https://arclinic.ru/services/cosmetology/injection/botulinoterapiya/',
    'Doctor': 'https://arclinic.ru/doctors/drozdova-anna-andreevna/',
}

for name, url in pages.items():
    r = requests.get(url, timeout=15)
    c = r.text
    og_title = re.search(r'<meta\s+property=["\']og:title["\']\s+content=["\'](.*?)["\']', c, re.IGNORECASE)
    og_desc = re.search(r'<meta\s+property=["\']og:description["\']\s+content=["\'](.*?)["\']', c, re.IGNORECASE)
    og_image = re.search(r'<meta\s+property=["\']og:image["\']\s+content=["\'](.*?)["\']', c, re.IGNORECASE)
    og_url = re.search(r'<meta\s+property=["\']og:url["\']\s+content=["\'](.*?)["\']', c, re.IGNORECASE)
    twitter_card = re.search(r'<meta\s+name=["\']twitter:card["\']\s+content=["\'](.*?)["\']', c, re.IGNORECASE)
    twitter_title = re.search(r'<meta\s+name=["\']twitter:title["\']\s+content=["\'](.*?)["\']', c, re.IGNORECASE)
    viewport = re.search(r'<meta\s+name=["\']viewport["\']\s+content=["\'](.*?)["\']', c, re.IGNORECASE)
    ga4 = re.search(r'G-[A-Z0-9]+', c)
    
    mobile = 'width=device-width' in c and 'initial-scale=1.0' in c
    
    print(f'{name}:')
    print(f'  og:title: {"YES" if og_title else "NO"}  og:desc: {"YES" if og_desc else "NO"}')
    print(f'  og:image: {"YES" if og_image else "NO"}  og:url: {"YES" if og_url else "NO"}')
    print(f'  twitter:card: {"YES" if twitter_card else "NO"}  twitter:title: {"YES" if twitter_title else "NO"}')
    print(f'  viewport mobile: {"YES" if mobile else "NO"}  GA4: {"YES" if ga4 else "NO"}')
    
    # Check for canonical
    canonical = re.search(r'<link\s+rel=["\']canonical["\']\s+href=["\'](.*?)["\']', c, re.IGNORECASE)
    print(f'  canonical: {canonical.group(1) if canonical else "NO"}')
    print()
