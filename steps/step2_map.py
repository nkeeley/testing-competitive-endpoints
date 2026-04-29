#!/usr/bin/env python3
"""Step 2: Map — Discover all pages on competitor docs/sites.
Firecrawl-only primitive. No competitor has a direct equivalent.
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import runners.firecrawl_runner as fc_runner
from utils import timed_call, save_result, excerpt, print_step_header, print_competitor_header, print_comparison_table

STEP = 2
TARGET_URLS = [
    "https://spider.cloud",
    "https://crawl4ai.com",
    "https://scrapegraphai.com",
    "https://apify.com",
    "https://exa.ai",
]


def main():
    print_step_header(STEP, "Map", "Discover all pages on competitor sites")

    all_out = {}
    for url in TARGET_URLS:
        name = url.replace("https://", "").replace("/", "_")
        print_competitor_header(f"Firecrawl → {url}")
        r = timed_call(fc_runner.map_url, url)
        all_out[url] = r
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

    # No-equivalent note
    print("\n" + "=" * 60)
    print("NOTE: /map has no equivalent in Spider, Crawl4AI, ScrapeGraphAI, Apify, or Exa.")
    print("Closest alternatives: sitemap.xml parsing, or crawling with link extraction.")

    competitors = ["Firecrawl", "Spider", "Crawl4AI", "ScrapeGraphAI", "Apify", "Exa"]
    rows = [
        ("Endpoint used", {
            "Firecrawl": "/map",
            "Spider": "N/A", "Crawl4AI": "N/A",
            "ScrapeGraphAI": "N/A", "Apify": "N/A", "Exa": "N/A",
        }),
        ("Has equivalent?", {
            "Firecrawl": "Yes", "Spider": "No", "Crawl4AI": "No",
            "ScrapeGraphAI": "No", "Apify": "No", "Exa": "No",
        }),
        ("Output quality (1-5)", {"Firecrawl": "___", **{c: "N/A" for c in competitors[1:]}}),
        ("URLs returned (spider.cloud)", {
            "Firecrawl": str(len(all_out.get("https://spider.cloud", {}).get("result", []) or [])) + " links",
            **{c: "N/A" for c in competitors[1:]},
        }),
        ("Cost", {"Firecrawl": "per credit", **{c: "N/A" for c in competitors[1:]}}),
        ("Failure behavior", {c: "N/A" for c in competitors}),
        ("Notes", {c: "" for c in competitors}),
    ]
    print_comparison_table(competitors, rows)


if __name__ == "__main__":
    main()
