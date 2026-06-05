"""
SEO Meta Analysis Tool
Analyzes meta tags, titles, descriptions of web pages.
"""

import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse


def analyze_page(url: str) -> dict:
    """Fetch and analyze meta tags of a given URL."""
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
    except requests.RequestException as e:
        return {"error": str(e), "url": url}

    soup = BeautifulSoup(response.text, "html.parser")
    result = {
        "url": url,
        "title": soup.title.string.strip() if soup.title else None,
        "meta_description": None,
        "meta_keywords": None,
        "h1_count": 0,
        "h1_tags": [],
        "img_without_alt": 0,
        "status_code": response.status_code,
    }

    # Meta description
    meta_desc = soup.find("meta", attrs={"name": "description"})
    if meta_desc and meta_desc.get("content"):
        result["meta_description"] = meta_desc["content"].strip()

    # Meta keywords
    meta_kw = soup.find("meta", attrs={"name": "keywords"})
    if meta_kw and meta_kw.get("content"):
        result["meta_keywords"] = meta_kw["content"].strip()

    # H1 tags
    h1_tags = soup.find_all("h1")
    result["h1_count"] = len(h1_tags)
    result["h1_tags"] = [h.get_text(strip=True) for h in h1_tags]

    # Images without alt
    images = soup.find_all("img")
    result["img_without_alt"] = sum(1 for img in images if not img.get("alt"))

    return result


def print_report(data: dict):
    """Print a formatted SEO report."""
    if "error" in data:
        print(f"[ERROR] {data['url']}: {data['error']}")
        return

    print(f"\n{'='*60}")
    print(f"SEO Report for: {data['url']}")
    print(f"{'='*60}")
    print(f"Status Code:     {data['status_code']}")
    print(f"Title:           {data['title'] or 'MISSING!'}")
    print(f"Meta Description: {data['meta_description'] or 'MISSING!'}")
    print(f"Meta Keywords:   {data['meta_keywords'] or 'Not set'}")
    print(f"H1 Tags:         {data['h1_count']} found")
    for h1 in data["h1_tags"]:
        print(f"                 - {h1}")
    print(f"Images w/o alt:  {data['img_without_alt']}")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python analyze_meta.py <url>")
        sys.exit(1)

    url = sys.argv[1]
    report = analyze_page(url)
    print_report(report)
