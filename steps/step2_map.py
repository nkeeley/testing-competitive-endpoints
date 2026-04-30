#!/usr/bin/env python3
"""Step 2: Map — Discover all pages on competitor docs/sites.
Firecrawl-only primitive. No competitor has a direct equivalent.
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import runners.firecrawl_runner as fc_runner
import runners.spider_runner as spider_runner
import runners.crawl4ai_runner as crawl4ai_runner
import time
from utils import timed_call, save_result, excerpt, print_step_header, print_competitor_header, print_comparison_table
from config import ALL_BASE_URLS, PRIMARY_BASE_URL

STEP = 2
TARGET_URLS = ALL_BASE_URLS


def main():
    print_step_header(STEP, "Map", "Discover all pages on competitor sites")

    fc_all = {}
    spider_all = {}
    crawl4ai_all = {}

    # --- Firecrawl ---
    for url in TARGET_URLS:
        name = url.replace("https://", "").replace("/", "_")
        print_competitor_header(f"Firecrawl → {url}")
        r = timed_call(fc_runner.map_url, url)
        fc_all[url] = r
        if r["error"]:
            print(f"  ERROR: {r['error']}")
        else:
            result = r["result"]
            urls_found = result if isinstance(result, list) else result.get("links", result)
            count = len(urls_found) if isinstance(urls_found, list) else "?"
            print(f"  Latency: {r['latency_s']}s")
            print(f"  URLs found: {count}")
            print(f"  Sample (first 10): {urls_found[:10] if isinstance(urls_found, list) else excerpt(urls_found)}")
        fp = save_result(STEP, f"firecrawl_{name}", {url: r})
        print(f"  [saved to {fp}]")
        time.sleep(2)

    # --- Spider (links endpoint) ---
    for url in TARGET_URLS:
        name = url.replace("https://", "").replace("/", "_")
        print_competitor_header(f"Spider → {url}")
        r = timed_call(spider_runner.links, url, 100)
        spider_all[url] = r
        if r["error"]:
            print(f"  ERROR: {r['error']}")
        else:
            print(f"  Latency: {r['latency_s']}s")
            print(f"  Output (first 500 chars):\n{excerpt(r['result'])}")
        fp = save_result(STEP, f"spider_{name}", {url: r})
        print(f"  [saved to {fp}]")
        time.sleep(2)

    # --- Crawl4AI (URL seeding fallback) ---
    for url in TARGET_URLS:
        name = url.replace("https://", "").replace("/", "_")
        print_competitor_header(f"Crawl4AI → {url}")
        r = timed_call(crawl4ai_runner.url_seeding, url, 100)
        crawl4ai_all[url] = r
        if r["error"]:
            print(f"  ERROR: {r['error']}")
        else:
            result = r["result"]
            urls_found = result.get("urls", []) if isinstance(result, dict) else []
            print(f"  Latency: {r['latency_s']}s")
            print(f"  URLs found: {len(urls_found)} (method: {result.get('method', '?')})")
            print(f"  Sample (first 10): {urls_found[:10]}")
        fp = save_result(STEP, f"crawl4ai_{name}", {url: r})
        print(f"  [saved to {fp}]")
        time.sleep(2)

    all_out = fc_all  # for the comparison table below

    competitors = ["Firecrawl", "Spider", "Crawl4AI", "ScrapeGraphAI", "Apify", "Exa"]

    def primary_count(d):
        r = d.get(PRIMARY_BASE_URL, {})
        if r.get("error"):
            return "ERROR"
        result = r.get("result")
        if isinstance(result, list):
            return f"{len(result)} links"
        if isinstance(result, dict):
            urls = result.get("urls") or result.get("links") or []
            if isinstance(urls, list):
                return f"{len(urls)} links"
        return "?"

    rows = [
        ("Endpoint used", {
            "Firecrawl": "/map",
            "Spider": "/v1/links",
            "Crawl4AI": "URL seeding (or fallback)",
            "ScrapeGraphAI": "N/A", "Apify": "N/A", "Exa": "N/A",
        }),
        ("Has equivalent?", {
            "Firecrawl": "Yes", "Spider": "Yes", "Crawl4AI": "Yes",
            "ScrapeGraphAI": "No", "Apify": "No", "Exa": "No",
        }),
        ("Output quality (1-5)", {"Firecrawl": "___", "Spider": "___", "Crawl4AI": "___",
                                   "ScrapeGraphAI": "N/A", "Apify": "N/A", "Exa": "N/A"}),
        (f"URLs returned ({PRIMARY_BASE_URL})", {
            "Firecrawl": primary_count(fc_all),
            "Spider": primary_count(spider_all),
            "Crawl4AI": primary_count(crawl4ai_all),
            "ScrapeGraphAI": "N/A", "Apify": "N/A", "Exa": "N/A",
        }),
        ("Cost", {"Firecrawl": "per credit", "Spider": "not reported", "Crawl4AI": "free",
                  "ScrapeGraphAI": "N/A", "Apify": "N/A", "Exa": "N/A"}),
        ("Failure behavior", {c: "N/A" for c in competitors}),
        ("Notes", {c: "" for c in competitors}),
    ]
    print_comparison_table(competitors, rows)


if __name__ == "__main__":
    main()
