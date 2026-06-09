#!/usr/bin/env python3
"""SEO page fetcher: collects HTML, meta tags, headings, links, images."""

import json
import sys
import time
from urllib.parse import urljoin, urlparse
import requests
from bs4 import BeautifulSoup

HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; SEO-Audit/1.0; +https://opencode.ai)",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9,ru;q=0.8",
}

TIMEOUT = 30


def fetch_url(url):
    start = time.time()
    resp = requests.get(url, headers=HEADERS, timeout=TIMEOUT, allow_redirects=True)
    elapsed = round(time.time() - start, 3)
    return resp, elapsed


def extract_meta(soup):
    meta = {}
    title_tag = soup.find("title")
    meta["title"] = title_tag.get_text(strip=True) if title_tag else None
    meta["title_length"] = len(meta["title"]) if meta["title"] else 0

    for tag in soup.find_all("meta"):
        name = tag.get("name", "").lower() or tag.get("property", "").lower()
        content = tag.get("content", "")
        if name:
            meta[name] = content

    desc = meta.get("description", "")
    meta["description_length"] = len(desc)
    return meta


def extract_headings(soup):
    headings = {}
    for level in range(1, 7):
        tags = soup.find_all(f"h{level}")
        headings[f"h{level}"] = {
            "count": len(tags),
            "texts": [t.get_text(strip=True)[:120] for t in tags[:20]],
        }
    return headings


def extract_links(soup, base_url):
    internal = []
    external = []
    nofollow = []
    base_domain = urlparse(base_url).netloc

    for a in soup.find_all("a", href=True):
        href = a["href"]
        if href.startswith(("#", "mailto:", "tel:", "javascript:")):
            continue
        full = urljoin(base_url, href)
        rel = a.get("rel", [])
        is_nofollow = "nofollow" in rel

        if urlparse(full).netloc == base_domain:
            internal.append(full)
        else:
            external.append(full)

        if is_nofollow:
            nofollow.append({"href": full, "anchor": a.get_text(strip=True)[:80]})

    return {
        "internal_count": len(set(internal)),
        "external_count": len(set(external)),
        "total_count": len(internal) + len(external),
        "nofollow_count": len(nofollow),
        "sample_internal": list(set(internal))[:10],
        "sample_external": list(set(external))[:5],
        "nofollow_links": nofollow[:10],
    }


def extract_images(soup):
    images = []
    missing_alt = []
    for img in soup.find_all("img"):
        src = img.get("src", "")
        alt = img.get("alt", None)
        width = img.get("width")
        height = img.get("height")
        loading = img.get("loading")

        info = {"src": src[:200], "alt": alt, "width": width, "height": height, "loading": loading}
        images.append(info)

        if alt is None or alt.strip() == "":
            missing_alt.append(src[:200])

    return {
        "total": len(images),
        "missing_alt": len(missing_alt),
        "missing_alt_samples": missing_alt[:10],
        "lazy_loading": sum(1 for i in images if i.get("loading") == "lazy"),
        "without_dimensions": sum(1 for i in images if not i.get("width") or not i.get("height")),
    }


def extract_content_stats(soup):
    for tag in soup(["script", "style", "nav", "footer", "header"]):
        tag.decompose()

    text = soup.get_text(separator=" ", strip=True)
    words = len(text.split())
    paragraphs = len(soup.find_all("p"))
    lists = len(soup.find_all(["ul", "ol"]))
    bold = len(soup.find_all(["b", "strong"]))
    italic = len(soup.find_all(["i", "em"]))

    return {
        "word_count": words,
        "char_count": len(text),
        "paragraphs": paragraphs,
        "lists": lists,
        "bold_tags": bold,
        "italic_tags": italic,
    }


def check_https(url):
    parsed = urlparse(url)
    if parsed.scheme == "https":
        return {"https": True}
    return {"https": False, "issue": "Site not using HTTPS"}


def check_robots(url):
    parsed = urlparse(url)
    robots_url = f"{parsed.scheme}://{parsed.netloc}/robots.txt"
    try:
        resp = requests.get(robots_url, headers=HEADERS, timeout=10)
        if resp.status_code == 200:
            return {
                "found": True,
                "status": resp.status_code,
                "content_preview": resp.text[:500],
            }
        return {"found": False, "status": resp.status_code}
    except Exception as e:
        return {"found": False, "error": str(e)}


def check_sitemap(url):
    parsed = urlparse(url)
    sitemap_url = f"{parsed.scheme}://{parsed.netloc}/sitemap.xml"
    try:
        resp = requests.get(sitemap_url, headers=HEADERS, timeout=10)
        if resp.status_code == 200:
            urls_found = resp.text.count("<loc>")
            return {
                "found": True,
                "status": resp.status_code,
                "url_count": urls_found,
                "content_preview": resp.text[:500],
            }
        return {"found": False, "status": resp.status_code}
    except Exception as e:
        return {"found": False, "error": str(e)}


def check_mobile(soup):
    viewport = soup.find("meta", attrs={"name": "viewport"})
    if viewport:
        content = viewport.get("content", "")
        return {"viewport_found": True, "viewport_content": content, "has_width_device": "width=device-width" in content}
    return {"viewport_found": False}


def check_canonical(soup, url):
    canonical = soup.find("link", rel="canonical")
    if canonical:
        href = canonical.get("href", "")
        return {"found": True, "href": href, "matches_url": href.rstrip("/") == url.rstrip("/")}
    return {"found": False}


def check_open_graph(soup):
    og = {}
    for tag in soup.find_all("meta", attrs={"property": True}):
        prop = tag.get("property", "")
        if prop.startswith("og:"):
            og[prop] = tag.get("content", "")
    return og


def check_twitter_card(soup):
    tw = {}
    for tag in soup.find_all("meta", attrs={"name": True}):
        name = tag.get("name", "")
        if name.startswith("twitter:"):
            tw[name] = tag.get("content", "")
    return tw


def audit_url(url):
    if not url.startswith("http"):
        url = "https://" + url

    result = {"url": url}

    resp, elapsed = fetch_url(url)
    result["http_status"] = resp.status_code
    result["response_time_ms"] = elapsed * 1000
    result["page_size_bytes"] = len(resp.content)
    result["page_size_kb"] = round(len(resp.content) / 1024, 1)
    result["encoding"] = resp.encoding
    result["final_url"] = resp.url
    result["redirects"] = len(resp.history)
    result["headers"] = dict(resp.headers)

    soup = BeautifulSoup(resp.text, "lxml")

    result["meta"] = extract_meta(soup)
    result["headings"] = extract_headings(soup)
    result["links"] = extract_links(soup, url)
    result["images"] = extract_images(soup)
    result["content"] = extract_content_stats(soup)
    result["https"] = check_https(url)
    result["robots_txt"] = check_robots(url)
    result["sitemap"] = check_sitemap(url)
    result["mobile"] = check_mobile(soup)
    result["canonical"] = check_canonical(soup, url)
    result["open_graph"] = check_open_graph(soup)
    result["twitter_card"] = check_twitter_card(soup)

    lang = soup.find("html", attrs={"lang": True})
    result["html_lang"] = lang["lang"] if lang else None

    charset = soup.find("meta", attrs={"charset": True})
    result["charset"] = charset["charset"] if charset else None

    return result


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python seo_fetch.py <url>", file=sys.stderr)
        sys.exit(1)

    url = sys.argv[1]
    try:
        data = audit_url(url)
        print(json.dumps(data, ensure_ascii=False, indent=2))
    except Exception as e:
        print(json.dumps({"error": str(e), "url": url}, ensure_ascii=False), file=sys.stderr)
        sys.exit(1)
