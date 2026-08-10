#!/usr/bin/env python3
"""Google PageSpeed Insights API fetcher (free, no API key for basic usage)."""

import json
import sys
import requests

PSI_URL = "https://www.googleapis.com/pagespeedonline/v5/runPagespeed"
TIMEOUT = 120


def run_pagespeed(url, strategy="mobile"):
    params = {
        "url": url,
        "strategy": strategy,
        "category": "performance",
    }

    resp = requests.get(PSI_URL, params=params, timeout=TIMEOUT)
    if resp.status_code != 200:
        return {"error": f"API returned {resp.status_code}", "detail": resp.text[:500]}

    data = resp.json()
    lighthouse = data.get("lighthouseResult", {})

    audits = lighthouse.get("audits", {})
    categories = lighthouse.get("categories", {})

    perf_score = categories.get("performance", {}).get("score", None)
    perf_score = perf_score * 100 if perf_score is not None else None

    metrics = {}
    metric_keys = [
        "first-contentful-paint",
        "largest-contentful-paint",
        "total-blocking-time",
        "cumulative-layout-shift",
        "interactive",
        "first-meaningful-paint",
        "speed-index",
        "server-response-time",
    ]

    for key in metric_keys:
        audit = audits.get(key, {})
        metrics[key] = {
            "display_value": audit.get("displayValue", ""),
            "numeric_value": audit.get("numericValue", None),
            "score": audit.get("score", None),
        }

    opportunities = []
    for key, audit in audits.items():
        details = audit.get("details", {})
        if details.get("type") == "opportunity" and audit.get("score") is not None and audit["score"] < 0.5:
            opportunities.append({
                "id": key,
                "title": audit.get("title", ""),
                "description": audit.get("description", "")[:200],
                "savings_ms": details.get("overallSavingsMs", 0),
                "display_value": audit.get("displayValue", ""),
            })

    diagnostics = []
    for key, audit in audits.items():
        details = audit.get("details", {})
        if details.get("type") == "table" and audit.get("score") is not None and audit["score"] < 0.5:
            diagnostics.append({
                "id": key,
                "title": audit.get("title", ""),
                "display_value": audit.get("displayValue", ""),
            })

    return {
        "strategy": strategy,
        "performance_score": perf_score,
        "metrics": metrics,
        "opportunities": sorted(opportunities, key=lambda x: x.get("savings_ms", 0), reverse=True)[:10],
        "diagnostics": diagnostics[:10],
        "final_url": data.get("loadingExperience", {}).get("final_url", url),
    }


def run_both(url):
    return {
        "url": url,
        "mobile": run_pagespeed(url, "mobile"),
        "desktop": run_pagespeed(url, "desktop"),
    }


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python seo_pagespeed.py <url>", file=sys.stderr)
        sys.exit(1)

    url = sys.argv[1]
    if not url.startswith("http"):
        url = "https://" + url

    strategy = sys.argv[2] if len(sys.argv) > 2 else "both"

    try:
        if strategy == "both":
            data = run_both(url)
        else:
            data = run_pagespeed(url, strategy)
        print(json.dumps(data, ensure_ascii=False, indent=2))
    except Exception as e:
        print(json.dumps({"error": str(e), "url": url}, ensure_ascii=False), file=sys.stderr)
        sys.exit(1)
