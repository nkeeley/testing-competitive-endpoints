#!/usr/bin/env python3
"""Step 7: Interact — Handle a pricing page requiring browser interaction.
Target: https://apify.com/pricing (monthly/annual pricing toggle).
Firecrawl-only primitive. Two-step: scrape first to get scrape_id, then /interact.
"""
import sys
import os
import json

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import runners.firecrawl_runner as fc_runner
import runners.spider_runner as spider_runner
import runners.crawl4ai_runner as crawl4ai_runner
from utils import timed_call, save_result, excerpt, print_step_header, print_competitor_header, print_comparison_table
from config import INTERACT_TARGET_URL

STEP = 7
INTERACT_PROMPT = "Click the annual pricing toggle and extract all plan names and prices for both monthly and annual billing."

# JS code to click the annual toggle on Apify pricing page (used by Crawl4AI and Spider)
TOGGLE_JS = [
    "const btns = Array.from(document.querySelectorAll('button, a, label, span, div')); "
    "const t = btns.find(el => /annual/i.test(el.textContent || '')); "
    "if (t) t.click();"
]
WAIT_FOR_SELECTOR = "css:body"


def main():
    print_step_header(STEP, "Interact", INTERACT_TARGET_URL)

    print_competitor_header("Firecrawl")
    print(f"  Target: {INTERACT_TARGET_URL}")
    print(f"  Prompt: {INTERACT_PROMPT}")

    # Step 1: scrape to get scrape_id
    print("\n  [Step 7a] Scraping page to get scrape_id...")
    scrape_r = timed_call(fc_runner.scrape_for_interact, INTERACT_TARGET_URL)

    scrape_id = None
    if scrape_r["error"]:
        print(f"  Scrape ERROR: {scrape_r['error']}")
    else:
        result = scrape_r["result"]
        scrape_id = (
            result.get("id")
            or result.get("scrape_id")
            or result.get("scrapeId")
        )
        if isinstance(result, dict):
            md = result.get("data", {}).get("markdown") if isinstance(result.get("data"), dict) else result.get("markdown")
        else:
            md = None
        print(f"  Scrape latency: {scrape_r['latency_s']}s")
        print(f"  Scrape ID: {scrape_id or '(not found in response — check raw output)'}")
        print(f"  Scrape output (first 300 chars):\n{excerpt(md, 300)}")

    fp = save_result(STEP, "firecrawl_scrape", scrape_r)
    print(f"  [saved to {fp}]")

    if not scrape_id:
        print("\n  WARNING: scrape_id not found in response. Cannot proceed to /interact.")
        print("  Check results/raw/step7_firecrawl_scrape.json for the actual response shape.")
        print("  You may need to update the scrape_id extraction logic in this script.")
    else:
        # Step 2: interact
        print(f"\n  [Step 7b] Calling /interact with scrape_id={scrape_id}...")
        interact_r = timed_call(fc_runner.interact, scrape_id, INTERACT_PROMPT)

        if interact_r["error"]:
            print(f"  Interact ERROR: {interact_r['error']}")
        else:
            print(f"  Interact latency: {interact_r['latency_s']}s")
            print(f"  Output (first 500 chars):\n{excerpt(interact_r['result'])}")

        fp = save_result(STEP, "firecrawl_interact", interact_r)
        print(f"  [saved to {fp}]")

    # --- Spider (browser endpoint / actions on scrape) ---
    print_competitor_header("Spider")
    spider_actions = [{"type": "click", "selector": "button:has-text('Annual'), label:has-text('Annual')"}]
    spider_r = timed_call(spider_runner.browser_interact, INTERACT_TARGET_URL, spider_actions)
    if spider_r["error"]:
        print(f"  ERROR: {spider_r['error']}")
    else:
        print(f"  Latency: {spider_r['latency_s']}s")
        print(f"  Output (first 500 chars):\n{excerpt(spider_r['result'])}")
    fp = save_result(STEP, "spider", spider_r)
    print(f"  [saved to {fp}]")

    # --- Crawl4AI (browser interactions via js_code DSL) ---
    print_competitor_header("Crawl4AI")
    print("  Using js_code parameter to click annual toggle")
    c4_r = timed_call(crawl4ai_runner.interact, INTERACT_TARGET_URL, TOGGLE_JS, WAIT_FOR_SELECTOR)
    if c4_r["error"]:
        print(f"  ERROR: {c4_r['error']}")
    else:
        print(f"  Latency: {c4_r['latency_s']}s")
        print(f"  Output (first 500 chars):\n{excerpt(c4_r['result'])}")
    fp = save_result(STEP, "crawl4ai", c4_r)
    print(f"  [saved to {fp}]")

    # No-equivalent competitors
    for name in ["ScrapeGraphAI", "Apify", "Exa"]:
        print_competitor_header(name)
        print("  No browser interaction primitive — N/A")

    competitors = ["Firecrawl", "Spider", "Crawl4AI", "ScrapeGraphAI", "Apify", "Exa"]
    def lat(r):
        return f"{r['latency_s']}s" if r and not r.get("error") else ("ERROR" if r and r.get("error") else "N/A")
    rows = [
        ("Endpoint used", {
            "Firecrawl": "/scrape + /interact",
            "Spider": "browser actions on /v1/scrape",
            "Crawl4AI": "js_code on CrawlerRunConfig",
            "ScrapeGraphAI": "N/A", "Apify": "N/A", "Exa": "N/A",
        }),
        ("Interface style", {
            "Firecrawl": "natural-language prompt",
            "Spider": "actions array (selectors)",
            "Crawl4AI": "JavaScript DSL",
            "ScrapeGraphAI": "N/A", "Apify": "N/A", "Exa": "N/A",
        }),
        ("Has equivalent?", {
            "Firecrawl": "Yes", "Spider": "Yes", "Crawl4AI": "Yes",
            "ScrapeGraphAI": "No", "Apify": "No", "Exa": "No",
        }),
        ("Output quality (1-5)", {
            "Firecrawl": "___", "Spider": "___", "Crawl4AI": "___",
            "ScrapeGraphAI": "N/A", "Apify": "N/A", "Exa": "N/A",
        }),
        ("Latency", {
            "Firecrawl": f"{scrape_r['latency_s']}s scrape" if not scrape_r.get("error") else "ERROR",
            "Spider": lat(spider_r),
            "Crawl4AI": lat(c4_r),
            "ScrapeGraphAI": "N/A", "Apify": "N/A", "Exa": "N/A",
        }),
        ("Toggle detected?", {
            "Firecrawl": "___", "Spider": "___", "Crawl4AI": "___",
            "ScrapeGraphAI": "N/A", "Apify": "N/A", "Exa": "N/A",
        }),
        ("Cost", {
            "Firecrawl": "2 credits (scrape + interact)",
            "Spider": "not reported", "Crawl4AI": "free",
            "ScrapeGraphAI": "N/A", "Apify": "N/A", "Exa": "N/A",
        }),
        ("Failure behavior", {c: "N/A" for c in competitors}),
        ("Notes", {c: "" for c in competitors}),
    ]
    print_comparison_table(competitors, rows)


if __name__ == "__main__":
    main()
