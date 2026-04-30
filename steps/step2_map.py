#!/usr/bin/env python3
"""Step 2: Map — Discover all pages on competitor docs/sites.
Tests Firecrawl /map, Spider /v1/links, Crawl4AI URL seeding.
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

# Crawl4AI hangs on JS-heavy / anti-bot pages (apify.com confirmed twice).
# Even with asyncio.wait_for(timeout=60) wrapping the runner, the underlying
# headless-browser process can hang during cleanup. Skip these explicitly so
# the rest of the run completes — the hang itself is a real finding (see
# reflections), not a bug to hide.
CRAWL4AI_SKIP_URLS = {"https://apify.com"}


def extract_url_list(result):
    """Pull a flat list of URL strings from any /map-style result.
    Handles Firecrawl's MapData Pydantic model, plain dict, plain list."""
    if result is None:
        return []
    if isinstance(result, list):
        return [item if isinstance(item, str) else (item.get("url") if isinstance(item, dict) else getattr(item, "url", str(item))) for item in result]
    # Try attribute access (Pydantic), then dict, then model_dump fallback
    links = getattr(result, "links", None)
    if links is None and isinstance(result, dict):
        links = result.get("links") or result.get("urls")
    if links is None and hasattr(result, "model_dump"):
        d = result.model_dump()
        links = d.get("links") or d.get("urls")
    if not isinstance(links, list):
        return []
    out = []
    for item in links:
        if isinstance(item, str):
            out.append(item)
        elif isinstance(item, dict):
            url = item.get("url") or item.get("href")
            if url:
                out.append(url)
        else:
            url = getattr(item, "url", None) or getattr(item, "href", None)
            if url:
                out.append(url)
    return out


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
            urls_found = extract_url_list(result)
            print(f"  Latency: {r['latency_s']}s")
            print(f"  URLs found: {len(urls_found)}")
            print(f"  Sample (first 10): {urls_found[:10]}")
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
            urls_found = extract_url_list(r["result"])
            print(f"  Latency: {r['latency_s']}s")
            print(f"  URLs found: {len(urls_found)}")
            if urls_found:
                print(f"  Sample (first 10): {urls_found[:10]}")
            else:
                print(f"  Output (first 500 chars):\n{excerpt(r['result'])}")
        fp = save_result(STEP, f"spider_{name}", {url: r})
        print(f"  [saved to {fp}]")
        time.sleep(2)

    # --- Crawl4AI (URL seeding fallback) ---
    for url in TARGET_URLS:
        name = url.replace("https://", "").replace("/", "_")
        print_competitor_header(f"Crawl4AI → {url}")
        if url in CRAWL4AI_SKIP_URLS:
            print(f"  SKIPPED — Crawl4AI hangs on this URL (JS-heavy / anti-bot).")
            print(f"  Documented as a finding, not hidden. See step 2 reflections.")
            crawl4ai_all[url] = {"result": None, "latency_s": 0, "error": "skipped: known hang"}
            continue
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
        urls = extract_url_list(r.get("result"))
        return f"{len(urls)} links"

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
