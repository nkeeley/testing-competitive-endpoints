#!/usr/bin/env python3
"""Step 3: Scrape (Markdown) — Extract pricing page content as clean markdown.
Competitors: Firecrawl, Spider, Crawl4AI, ScrapeGraphAI (via smartscraper), Apify.
"""
import sys
import os
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import runners.firecrawl_runner as fc_runner
import runners.spider_runner as spider_runner
import runners.crawl4ai_runner as crawl4ai_runner
import runners.scrapegraphai_runner as sgai_runner
import runners.apify_runner as apify_runner
from utils import timed_call, save_result, excerpt, credits_used, print_step_header, print_competitor_header, print_comparison_table
from config import PRIMARY_PRICING_URL

STEP = 3
TARGET_URL = PRIMARY_PRICING_URL


def extract_markdown(result):
    if result is None:
        return None
    if isinstance(result, str):
        return result
    if isinstance(result, dict):
        return result.get("markdown") or result.get("content") or result.get("text")
    if isinstance(result, list) and result:
        item = result[0]
        if isinstance(item, dict):
            return item.get("markdown") or item.get("content") or item.get("text")
    return str(result)


def main():
    print_step_header(STEP, "Scrape (Markdown)", TARGET_URL)

    data = {}

    # --- Firecrawl ---
    print_competitor_header("Firecrawl")
    r = timed_call(fc_runner.scrape_markdown, TARGET_URL)
    data["firecrawl"] = r
    if r["error"]:
        print(f"  ERROR: {r['error']}")
    else:
        md = extract_markdown(r["result"])
        cost = credits_used(r["result"])
        print(f"  Latency: {r['latency_s']}s")
        print(f"  Credits used: {cost}")
        print(f"  Output (first 500 chars):\n{excerpt(md)}")
    fp = save_result(STEP, "firecrawl", r)
    print(f"  [saved to {fp}]")
    time.sleep(2)

    # --- Spider ---
    print_competitor_header("Spider")
    r = timed_call(spider_runner.scrape_markdown, TARGET_URL)
    data["spider"] = r
    if r["error"]:
        print(f"  ERROR: {r['error']}")
    else:
        md = extract_markdown(r["result"])
        print(f"  Latency: {r['latency_s']}s")
        print(f"  Cost: not reported in response")
        print(f"  Output (first 500 chars):\n{excerpt(md)}")
    fp = save_result(STEP, "spider", r)
    print(f"  [saved to {fp}]")
    time.sleep(2)

    # --- Crawl4AI ---
    print_competitor_header("Crawl4AI")
    r = timed_call(crawl4ai_runner.scrape_markdown, TARGET_URL)
    data["crawl4ai"] = r
    if r["error"]:
        print(f"  ERROR: {r['error']}")
    else:
        md = extract_markdown(r["result"])
        print(f"  Latency: {r['latency_s']}s")
        print(f"  Cost: free (self-hosted)")
        print(f"  Output (first 500 chars):\n{excerpt(md)}")
    fp = save_result(STEP, "crawl4ai", r)
    print(f"  [saved to {fp}]")
    time.sleep(2)

    # --- ScrapeGraphAI ---
    print_competitor_header("ScrapeGraphAI")
    prompt = "Extract all text content from this pricing page as markdown"
    r = timed_call(sgai_runner.smartscraper, TARGET_URL, prompt)
    data["scrapegraphai"] = r
    if r["error"]:
        print(f"  ERROR: {r['error']}")
    else:
        print(f"  Latency: {r['latency_s']}s")
        print(f"  Cost: not reported in response")
        print(f"  Output (first 500 chars):\n{excerpt(r['result'])}")
    fp = save_result(STEP, "scrapegraphai", r)
    print(f"  [saved to {fp}]")
    time.sleep(2)

    # --- Apify ---
    print_competitor_header("Apify")
    r = timed_call(apify_runner.scrape_url, TARGET_URL)
    data["apify"] = r
    if r["error"]:
        print(f"  ERROR: {r['error']}")
    else:
        md = extract_markdown(r["result"])
        print(f"  Latency: {r['latency_s']}s")
        print(f"  Cost: not reported in response")
        print(f"  Output (first 500 chars):\n{excerpt(md)}")
    fp = save_result(STEP, "apify", r)
    print(f"  [saved to {fp}]")

    # --- Exa (partial — no dedicated scrape, only contents via search) ---
    print_competitor_header("Exa")
    print("  No direct scrape equivalent — Exa returns page contents only via search.")
    print("  N/A for standalone scrape.")

    competitors = ["Firecrawl", "Spider", "Crawl4AI", "ScrapeGraphAI", "Apify", "Exa"]
    def lat(key):
        r = data.get(key, {})
        return f"{r['latency_s']}s" if r and not r.get("error") else ("ERROR" if r.get("error") else "N/A")

    rows = [
        ("Endpoint used", {
            "Firecrawl": "/scrape",
            "Spider": "scrape_url()",
            "Crawl4AI": "AsyncWebCrawler",
            "ScrapeGraphAI": "smartscraper",
            "Apify": "website-content-crawler",
            "Exa": "N/A",
        }),
        ("Has equivalent?", {
            "Firecrawl": "Yes", "Spider": "Yes", "Crawl4AI": "Yes",
            "ScrapeGraphAI": "Yes (schema-first)", "Apify": "Yes (via actor)", "Exa": "No",
        }),
        ("Output quality (1-5)", {c: "___" if c != "Exa" else "N/A" for c in competitors}),
        ("Latency", {
            "Firecrawl": lat("firecrawl"),
            "Spider": lat("spider"),
            "Crawl4AI": lat("crawl4ai"),
            "ScrapeGraphAI": lat("scrapegraphai"),
            "Apify": lat("apify"),
            "Exa": "N/A",
        }),
        ("Cost", {
            "Firecrawl": str(credits_used(data.get("firecrawl", {}).get("result"))) + " credit(s)",
            "Spider": "not reported",
            "Crawl4AI": "free",
            "ScrapeGraphAI": "not reported",
            "Apify": "not reported",
            "Exa": "N/A",
        }),
        ("Cost matched docs?", {
            "Firecrawl": "yes", "Spider": "N/A", "Crawl4AI": "N/A",
            "ScrapeGraphAI": "N/A", "Apify": "N/A", "Exa": "N/A",
        }),
        ("Failure behavior", {c: "N/A" for c in competitors}),
        ("Notes", {c: "" for c in competitors}),
    ]
    print_comparison_table(competitors, rows)


if __name__ == "__main__":
    main()
