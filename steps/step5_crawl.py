#!/usr/bin/env python3
"""Step 5: Crawl — Crawl each competitor's docs site (limit 20 pages), return markdown.
Competitors: Firecrawl, Spider, Crawl4AI, Apify.
"""
import sys
import os
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import runners.firecrawl_runner as fc_runner
import runners.spider_runner as spider_runner
import runners.crawl4ai_runner as crawl4ai_runner
import runners.apify_runner as apify_runner
import runners.scrapegraphai_runner as sgai_runner
from utils import timed_call, save_result, excerpt, credits_used, print_step_header, print_competitor_header, print_comparison_table
from config import PRIMARY_DOCS_URL

STEP = 5
TARGET_URL = PRIMARY_DOCS_URL
CRAWL_LIMIT = 20


def page_count(result):
    if result is None:
        return 0
    if isinstance(result, list):
        return len(result)
    if isinstance(result, dict):
        pages = result.get("data") or result.get("pages") or result.get("results") or []
        if isinstance(pages, list):
            return len(pages)
    return "?"


def sample_markdown(result):
    if result is None:
        return None
    if isinstance(result, list) and result:
        item = result[0]
        if isinstance(item, dict):
            return item.get("markdown") or item.get("content") or str(item)
        return str(item)
    if isinstance(result, dict):
        pages = result.get("data") or result.get("pages") or []
        if pages and isinstance(pages, list):
            item = pages[0]
            return item.get("markdown") or item.get("content") if isinstance(item, dict) else str(item)
    return str(result)


def main():
    print_step_header(STEP, "Crawl", f"{TARGET_URL} (limit {CRAWL_LIMIT} pages)")

    data = {}

    # --- Firecrawl ---
    print_competitor_header("Firecrawl")
    print("  (this may take 30-60s for 20 pages)")
    r = timed_call(fc_runner.crawl, TARGET_URL, CRAWL_LIMIT)
    data["firecrawl"] = r
    if r["error"]:
        print(f"  ERROR: {r['error']}")
    else:
        cost = credits_used(r["result"])
        count = page_count(r["result"])
        print(f"  Latency: {r['latency_s']}s")
        print(f"  Credits used: {cost}")
        print(f"  Pages returned: {count}")
        print(f"  Sample (first 500 chars of page 1):\n{excerpt(sample_markdown(r['result']))}")
    fp = save_result(STEP, "firecrawl", r)
    print(f"  [saved to {fp}]")
    time.sleep(2)

    # --- Spider ---
    print_competitor_header("Spider")
    print("  (this may take 30-60s for 20 pages)")
    r = timed_call(spider_runner.crawl, TARGET_URL, CRAWL_LIMIT)
    data["spider"] = r
    if r["error"]:
        print(f"  ERROR: {r['error']}")
    else:
        count = page_count(r["result"])
        print(f"  Latency: {r['latency_s']}s")
        print(f"  Cost: not reported in response")
        print(f"  Pages returned: {count}")
        print(f"  Sample (first 500 chars of page 1):\n{excerpt(sample_markdown(r['result']))}")
    fp = save_result(STEP, "spider", r)
    print(f"  [saved to {fp}]")
    time.sleep(2)

    # --- Crawl4AI ---
    print_competitor_header("Crawl4AI")
    print("  (this may take several minutes — runs sequentially)")
    r = timed_call(crawl4ai_runner.crawl, TARGET_URL, CRAWL_LIMIT)
    data["crawl4ai"] = r
    if r["error"]:
        print(f"  ERROR: {r['error']}")
    else:
        count = page_count(r["result"])
        print(f"  Latency: {r['latency_s']}s")
        print(f"  Cost: free (self-hosted)")
        print(f"  Pages returned: {count}")
        print(f"  Sample (first 500 chars of page 1):\n{excerpt(sample_markdown(r['result']))}")
    fp = save_result(STEP, "crawl4ai", r)
    print(f"  [saved to {fp}]")
    time.sleep(2)

    # --- Apify ---
    print_competitor_header("Apify")
    print("  (this may take 60-120s)")
    r = timed_call(apify_runner.crawl, TARGET_URL, CRAWL_LIMIT)
    data["apify"] = r
    if r["error"]:
        print(f"  ERROR: {r['error']}")
    else:
        count = page_count(r["result"])
        print(f"  Latency: {r['latency_s']}s")
        print(f"  Cost: not reported in response")
        print(f"  Pages returned: {count}")
        print(f"  Sample (first 500 chars of page 1):\n{excerpt(sample_markdown(r['result']))}")
    fp = save_result(STEP, "apify", r)
    print(f"  [saved to {fp}]")
    time.sleep(2)

    # --- ScrapeGraphAI (smartcrawler) ---
    print_competitor_header("ScrapeGraphAI")
    r = timed_call(sgai_runner.crawl, TARGET_URL, "Extract all docs page content as markdown", CRAWL_LIMIT)
    data["scrapegraphai"] = r
    if r["error"]:
        print(f"  ERROR: {r['error']}")
    else:
        count = page_count(r["result"])
        print(f"  Latency: {r['latency_s']}s")
        print(f"  Cost: not reported in response")
        print(f"  Pages returned: {count}")
        print(f"  Sample (first 500 chars of page 1):\n{excerpt(sample_markdown(r['result']))}")
    fp = save_result(STEP, "scrapegraphai", r)
    print(f"  [saved to {fp}]")

    # --- No-equivalent competitors ---
    for name, note in [
        ("Exa", "No crawl primitive"),
    ]:
        print_competitor_header(name)
        print(f"  {note} — N/A")

    competitors = ["Firecrawl", "Spider", "Crawl4AI", "ScrapeGraphAI", "Apify", "Exa"]
    def lat(key):
        r = data.get(key, {})
        return f"{r['latency_s']}s" if r and not r.get("error") else ("ERROR" if r.get("error") else "N/A")
    def pages(key):
        r = data.get(key, {})
        return str(page_count(r.get("result"))) if r and not r.get("error") else ("ERROR" if r.get("error") else "N/A")

    rows = [
        ("Endpoint used", {
            "Firecrawl": "/crawl",
            "Spider": "crawl_url()",
            "Crawl4AI": "AsyncWebCrawler (sequential)",
            "ScrapeGraphAI": "/smartcrawler",
            "Apify": "website-content-crawler",
            "Exa": "N/A",
        }),
        ("Has equivalent?", {
            "Firecrawl": "Yes", "Spider": "Yes", "Crawl4AI": "Yes (manual link-follow)",
            "ScrapeGraphAI": "Yes", "Apify": "Yes (via actor)", "Exa": "No",
        }),
        ("Output quality (1-5)", {
            "Firecrawl": "___", "Spider": "___", "Crawl4AI": "___",
            "ScrapeGraphAI": "___", "Apify": "___", "Exa": "N/A",
        }),
        ("Latency", {
            "Firecrawl": lat("firecrawl"), "Spider": lat("spider"),
            "Crawl4AI": lat("crawl4ai"), "ScrapeGraphAI": lat("scrapegraphai"),
            "Apify": lat("apify"), "Exa": "N/A",
        }),
        ("Pages returned", {
            "Firecrawl": pages("firecrawl"), "Spider": pages("spider"),
            "Crawl4AI": pages("crawl4ai"), "ScrapeGraphAI": pages("scrapegraphai"),
            "Apify": pages("apify"), "Exa": "N/A",
        }),
        ("Cost", {
            "Firecrawl": str(credits_used(data.get("firecrawl", {}).get("result"))) + " credit(s)",
            "Spider": "not reported", "Crawl4AI": "free",
            "ScrapeGraphAI": "not reported", "Apify": "not reported", "Exa": "N/A",
        }),
        ("Failure behavior", {c: "N/A" for c in competitors}),
        ("Notes", {c: "" for c in competitors}),
    ]
    print_comparison_table(competitors, rows)


if __name__ == "__main__":
    main()
