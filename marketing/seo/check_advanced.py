#!/usr/bin/env python3
"""Check rel next/prev, nofollow, and pagination on blog."""
import requests, re

# Blog pagination check
r = requests.get('https://arclinic.ru/blog/', timeout=15)
c = r.text
print('=== Blog ===')
for rel in ['next', 'prev']:
    match = re.search(rf'<link\s+rel=["\']{rel}["\']\s+href=["\'](.*?)["\']', c, re.IGNORECASE)
    print(f'  rel={rel}: {match.group(1) if match else "NOT FOUND"}')

# Check external links for nofollow
from urllib.parse import urlparse
links = re.findall(r'<a\s+[^>]*href=["\'](https?://[^"\']+)["\'][^>]*>', c, re.IGNORECASE)
external = [l for l in links if 'arclinic.ru' not in l and 'arclinic' not in l]
nofollow_links = re.findall(r'<a\s+[^>]*rel=["\']([^"\']*nofollow[^"\']*)["\'][^>]*href=["\'](https?://[^"\']+)["\']', c, re.IGNORECASE)
print(f'  External links on homepage: {len(external)}')
print(f'  External links with nofollow: {len(nofollow_links)}')

# Check Marquiz scripts count on random page
marquiz_count = c.count('script.marquiz.ru')
print(f'  Marquiz script refs: {marquiz_count}')

# Check meta description content (is it unique?)
meta_og_desc = re.search(r'<meta\s+property=["\']og:description["\']\s+content=["\'](.*?)["\']', c, re.IGNORECASE)
meta_name_desc = re.search(r'<meta\s+name=["\']description["\']\s+content=["\'](.*?)["\']', c, re.IGNORECASE)
print(f'  meta description: {"YES" if meta_name_desc else "NO"}')
if meta_og_desc:
    print(f'  og:description: {meta_og_desc.group(1)[:60]}...')
if meta_name_desc:
    print(f'  meta description: {meta_name_desc.group(1)[:60]}...')

# Check H1 on a few random service pages for uniqueness
for url_path in ['/services/cosmetology/injection/botulinoterapiya/',
                  '/services/cosmetology/injection/konturnaya-plastika/',
                  '/services/cosmetology/injection/biorevitalizatsiya/']:
    r2 = requests.get('https://arclinic.ru' + url_path, timeout=15)
    c2 = r2.text
    h1 = re.search(r'<h1[^>]*>(.*?)</h1>', c2, re.IGNORECASE | re.DOTALL)
    if h1:
        h1_text = re.sub(r'<[^>]*>', '', h1.group(1)).strip()
        print(f'\n  {url_path.split("/")[-2]}: H1 = "{h1_text}"')
