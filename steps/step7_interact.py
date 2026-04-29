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
from utils import timed_call, save_result, excerpt, print_step_header, print_competitor_header, print_comparison_table
from config import INTERACT_TARGET_URL

STEP = 7
INTERACT_PROMPT = "Click the annual pricing toggle and extract all plan names and prices for both monthly and annual billing."


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

    # All competitors
    for name in ["Spider", "Crawl4AI", "ScrapeGraphAI", "Apify", "Exa"]:
        print_competitor_header(name)
        print("  No browser interaction primitive — N/A")

    competitors = ["Firecrawl", "Spider", "Crawl4AI", "ScrapeGraphAI", "Apify", "Exa"]
    rows = [
        ("Endpoint used", {
            "Firecrawl": "/scrape + /interact",
            **{c: "N/A" for c in competitors[1:]},
        }),
        ("Has equivalent?", {
            "Firecrawl": "Yes",
            **{c: "No" for c in competitors[1:]},
        }),
        ("Output quality (1-5)", {"Firecrawl": "___", **{c: "N/A" for c in competitors[1:]}}),
        ("Scrape latency", {
            "Firecrawl": f"{scrape_r['latency_s']}s" if not scrape_r.get("error") else "ERROR",
            **{c: "N/A" for c in competitors[1:]},
        }),
        ("Interact latency", {
            "Firecrawl": "(see raw output — only available if scrape_id found)",
            **{c: "N/A" for c in competitors[1:]},
        }),
        ("Toggle detected?", {"Firecrawl": "___", **{c: "N/A" for c in competitors[1:]}}),
        ("Cost", {"Firecrawl": "2 credits (scrape + interact)", **{c: "N/A" for c in competitors[1:]}}),
        ("Failure behavior", {c: "N/A" for c in competitors}),
        ("Notes", {c: "" for c in competitors}),
    ]
    print_comparison_table(competitors, rows)


if __name__ == "__main__":
    main()
