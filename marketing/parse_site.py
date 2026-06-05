#!/usr/bin/env python3
"""Parse arclinic.ru to extract services and doctors info."""
import requests
from bs4 import BeautifulSoup

# Get main page
r = requests.get('https://arclinic.ru', timeout=15, headers={'User-Agent': 'Mozilla/5.0'})
soup = BeautifulSoup(r.text, 'html.parser')

print("=== ALL SERVICE PAGES ===")
urls = [
    'https://arclinic.ru/services/cosmetology/apparat/',
    'https://arclinic.ru/services/cosmetology/injection/',
    'https://arclinic.ru/services/cosmetology/estetic/',
    'https://arclinic.ru/services/cosmetology/komplex/',
    'https://arclinic.ru/services/cosmetology/konsult/',
    'https://arclinic.ru/services/cosmetology/lechenie/',
    'https://arclinic.ru/services/health-center/ginekologiya/',
    'https://arclinic.ru/services/health-center/endokrinologiya/',
    'https://arclinic.ru/services/health-center/nevrologiya/',
    'https://arclinic.ru/services/health-center/dietologiya/',
    'https://arclinic.ru/services/health-center/dermatologiya/',
]
for url in urls:
    name = url.split("/")[-2]
    print(f"\n=== {name} ===")
    try:
        r = requests.get(url, timeout=15, headers={'User-Agent': 'Mozilla/5.0'})
        soup = BeautifulSoup(r.text, 'html.parser')
        # Get all links that look like service items
        for a in soup.find_all('a'):
            txt = a.get_text(strip=True)
            if txt and len(txt) > 3 and len(txt) < 120:
                href = a.get('href', '')
                if '/services/' in href or '/doctors/' in href:
                    print(f"  {txt}")
        # Also get h2/h3/h4
        for tag in soup.find_all(['h2','h3','h4']):
            txt = tag.get_text(strip=True)
            if txt and len(txt) > 3 and len(txt) < 100:
                print(f"  [H] {txt}")
    except Exception as e:
        print(f"  Error: {e}")

print("\n\n=== DOCTORS ===")
r = requests.get('https://arclinic.ru/doctors/', timeout=15, headers={'User-Agent': 'Mozilla/5.0'})
soup = BeautifulSoup(r.text, 'html.parser')
for a in soup.find_all('a'):
    txt = a.get_text(strip=True)
    href = a.get('href', '')
    if '/doctors/' in href and href != '/doctors/':
        print(f"  {txt} -> {href}")
