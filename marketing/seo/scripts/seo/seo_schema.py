#!/usr/bin/env python3
"""Extract and validate Schema.org JSON-LD and microdata from HTML."""

import json
import sys
import requests
from bs4 import BeautifulSoup

HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; SEO-Audit/1.0; +https://opencode.ai)",
}

REQUIRED_FIELDS = {
    "Organization": ["name", "url"],
    "LocalBusiness": ["name", "address"],
    "Product": ["name"],
    "Article": ["headline", "author", "datePublished"],
    "BlogPosting": ["headline", "author", "datePublished"],
    "WebSite": ["name", "url"],
    "WebPage": ["name"],
    "Person": ["name"],
    "BreadcrumbList": ["itemListElement"],
    "Event": ["name", "startDate", "location"],
    "JobPosting": ["title", "description", "datePosted", "hiringOrganization"],
    "Review": ["itemReviewed", "reviewRating"],
    "FAQPage": ["mainEntity"],
}

RECOMMENDED_FIELDS = {
    "Organization": ["logo", "sameAs", "contactPoint", "foundingDate", "founder"],
    "LocalBusiness": ["geo", "openingHours", "telephone", "image", "priceRange", "areaServed"],
    "Product": ["image", "description", "brand", "offers", "aggregateRating", "review"],
    "Article": ["image", "publisher", "dateModified"],
    "BlogPosting": ["image", "publisher", "dateModified", "articleBody"],
    "WebSite": ["potentialAction"],
    "Person": ["url", "sameAs", "jobTitle", "image"],
    "BreadcrumbList": [],
    "Event": ["description", "image", "offers", "performer", "endDate"],
    "JobPosting": ["jobLocation", "employmentType", "baseSalary", "dateValid"],
}


def fetch_page(url):
    resp = requests.get(url, headers=HEADERS, timeout=30)
    resp.raise_for_status()
    return resp.text


def extract_jsonld(html):
    soup = BeautifulSoup(html, "lxml")
    blocks = []
    for script in soup.find_all("script", type="application/ld+json"):
        try:
            data = json.loads(script.string.strip() if script.string else "{}")
            if isinstance(data, list):
                blocks.extend(data)
            else:
                blocks.append(data)
        except json.JSONDecodeError as e:
            blocks.append({"_parse_error": str(e), "_raw": (script.string or "")[:200]})
    return blocks


def extract_microdata(html):
    soup = BeautifulSoup(html, "lxml")
    items = []
    for el in soup.find_all(attrs={"itemscope": True}):
        item = {"type": el.get("itemtype", ""), "properties": []}
        for prop in el.find_all(attrs={"itemprop": True}):
            item["properties"].append({
                "name": prop["itemprop"],
                "content": prop.get("content", "") or prop.get_text(strip=True)[:200],
            })
        items.append(item)
    return items


def validate_schema_block(block):
    if "_parse_error" in block:
        return {"valid": False, "error": block["_parse_error"]}

    context = block.get("@context", "")
    schema_type = block.get("@type", "")
    issues = []
    warnings = []
    passed = []

    if not context or "schema.org" not in str(context).lower():
        issues.append("@context missing or not schema.org")
    else:
        passed.append("@context is schema.org")

    if not schema_type:
        issues.append("@type is missing")
    else:
        passed.append(f"@type: {schema_type}")

    required = REQUIRED_FIELDS.get(schema_type, [])
    recommended = RECOMMENDED_FIELDS.get(schema_type, [])

    for field in required:
        if field in block:
            passed.append(f"{field}: present")
        else:
            issues.append(f"Required field missing: {field}")

    for field in recommended:
        if field in block:
            passed.append(f"{field}: present")
        else:
            warnings.append(f"Recommended field missing: {field}")

    if "@id" in block:
        passed.append("@id for cross-referencing")

    if "image" in block or "logo" in block:
        passed.append("Image property present")

    if "sameAs" in block:
        same_as = block["sameAs"]
        if isinstance(same_as, list) and len(same_as) >= 2:
            passed.append(f"sameAs: {len(same_as)} social profiles")
        elif isinstance(same_as, list):
            warnings.append("sameAs: only 1 profile, consider adding more")

    if "url" in block:
        url = block["url"]
        if isinstance(url, str) and url.startswith("http"):
            passed.append("url: absolute")
        elif isinstance(url, str):
            warnings.append("url: should be absolute (https://)")

    score = max(0, 100 - (len(issues) * 20) - (len(warnings) * 5))
    grade = "A" if score >= 90 else "B+" if score >= 80 else "B" if score >= 70 else "C" if score >= 60 else "D" if score >= 40 else "F"

    return {
        "type": schema_type,
        "score": score,
        "grade": grade,
        "critical_issues": issues,
        "warnings": warnings,
        "passed_checks": passed,
    }


def audit_schema(url):
    if not url.startswith("http"):
        url = "https://" + url

    html = fetch_page(url)
    jsonld_blocks = extract_jsonld(html)
    microdata_items = extract_microdata(html)

    validations = [validate_schema_block(b) for b in jsonld_blocks]

    total_issues = sum(len(v.get("critical_issues", [])) for v in validations)
    total_warnings = sum(len(v.get("warnings", [])) for v in validations)
    total_passed = sum(len(v.get("passed_checks", [])) for v in validations)

    if validations:
        avg_score = sum(v.get("score", 0) for v in validations) / len(validations)
    else:
        avg_score = 0

    grade = "A" if avg_score >= 90 else "B+" if avg_score >= 80 else "B" if avg_score >= 70 else "C" if avg_score >= 60 else "D" if avg_score >= 40 else "F"

    return {
        "url": url,
        "jsonld_blocks": len(jsonld_blocks),
        "microdata_items": len(microdata_items),
        "raw_jsonld": jsonld_blocks,
        "microdata": microdata_items,
        "validations": validations,
        "summary": {
            "total_blocks": len(jsonld_blocks) + len(microdata_items),
            "critical_issues": total_issues,
            "warnings": total_warnings,
            "passed_checks": total_passed,
            "average_score": round(avg_score, 1),
            "grade": grade,
        },
    }


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python seo_schema.py <url>", file=sys.stderr)
        sys.exit(1)

    url = sys.argv[1]
    try:
        data = audit_schema(url)
        print(json.dumps(data, ensure_ascii=False, indent=2))
    except Exception as e:
        print(json.dumps({"error": str(e), "url": url}, ensure_ascii=False), file=sys.stderr)
        sys.exit(1)
