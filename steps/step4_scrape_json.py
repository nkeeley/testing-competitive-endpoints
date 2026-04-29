#!/usr/bin/env python3
"""Step 4: Scrape (JSON schema) — Structured extraction of pricing plans.
Firecrawl uses native JSON schema extraction.
ScrapeGraphAI is the closest competitor (schema-first by design).
Others return markdown only — marked N/A for structured extraction.
"""
import sys
import os
import time
import json

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import runners.firecrawl_runner as fc_runner
import runners.scrapegraphai_runner as sgai_runner
from utils import timed_call, save_result, excerpt, credits_used, print_step_header, print_competitor_header, print_comparison_table
from schemas import PRICING_SCHEMA

STEP = 4
TARGET_URL = "https://spider.cloud/pricing"
SGAI_PROMPT = (
    "Extract all pricing plans. For each plan return: plan_name, price_monthly, "
    "credits_or_pages included, rate_limit, and key_features as a list."
)


def main():
    print_step_header(STEP, "Scrape (JSON schema)", TARGET_URL)

    data = {}

    # --- Firecrawl ---
    print_competitor_header("Firecrawl")
    r = timed_call(fc_runner.scrape_json, TARGET_URL, PRICING_SCHEMA)
    data["firecrawl"] = r
    if r["error"]:
        print(f"  ERROR: {r['error']}")
    else:
        cost = credits_used(r["result"])
        print(f"  Latency: {r['latency_s']}s")
        print(f"  Credits used: {cost}")
        print(f"  Output (full JSON):")
        extracted = r["result"]
        if isinstance(extracted, dict):
            json_part = extracted.get("json") or extracted.get("extract") or extracted
        else:
            json_part = extracted
        print(json.dumps(json_part, indent=2, default=str)[:2000])
    fp = save_result(STEP, "firecrawl", r)
    print(f"  [saved to {fp}]")
    time.sleep(2)

    # --- ScrapeGraphAI ---
    print_competitor_header("ScrapeGraphAI")
    r = timed_call(sgai_runner.smartscraper, TARGET_URL, SGAI_PROMPT)
    data["scrapegraphai"] = r
    if r["error"]:
        print(f"  ERROR: {r['error']}")
    else:
        print(f"  Latency: {r['latency_s']}s")
        print(f"  Cost: not reported in response")
        print(f"  Output (full JSON):")
        print(json.dumps(r["result"], indent=2, default=str)[:2000])
    fp = save_result(STEP, "scrapegraphai", r)
    print(f"  [saved to {fp}]")

    # --- No-equivalent competitors ---
    for name, note in [
        ("Spider", "Returns markdown only — no native JSON schema extraction"),
        ("Crawl4AI", "Returns markdown only — no native JSON schema extraction"),
        ("Apify", "Structured extraction requires a custom actor — not comparable"),
        ("Exa", "No scrape primitive"),
    ]:
        print_competitor_header(name)
        print(f"  {note} — N/A")

    competitors = ["Firecrawl", "Spider", "Crawl4AI", "ScrapeGraphAI", "Apify", "Exa"]
    def lat(key):
        r = data.get(key, {})
        return f"{r['latency_s']}s" if r and not r.get("error") else ("ERROR" if r.get("error") else "N/A")

    rows = [
        ("Endpoint used", {
            "Firecrawl": "/scrape (JSON schema)",
            "Spider": "N/A",
            "Crawl4AI": "N/A",
            "ScrapeGraphAI": "smartscraper (prompt)",
            "Apify": "N/A",
            "Exa": "N/A",
        }),
        ("Has equivalent?", {
            "Firecrawl": "Yes (native)", "Spider": "No", "Crawl4AI": "No",
            "ScrapeGraphAI": "Yes (prompt-based)", "Apify": "No", "Exa": "No",
        }),
        ("Output quality (1-5)", {
            "Firecrawl": "___", "Spider": "N/A", "Crawl4AI": "N/A",
            "ScrapeGraphAI": "___", "Apify": "N/A", "Exa": "N/A",
        }),
        ("Latency", {
            "Firecrawl": lat("firecrawl"),
            "Spider": "N/A", "Crawl4AI": "N/A",
            "ScrapeGraphAI": lat("scrapegraphai"),
            "Apify": "N/A", "Exa": "N/A",
        }),
        ("Cost", {
            "Firecrawl": str(credits_used(data.get("firecrawl", {}).get("result"))) + " credit(s)",
            "Spider": "N/A", "Crawl4AI": "N/A",
            "ScrapeGraphAI": "not reported",
            "Apify": "N/A", "Exa": "N/A",
        }),
        ("Schema fidelity", {
            "Firecrawl": "exact schema enforced",
            "Spider": "N/A", "Crawl4AI": "N/A",
            "ScrapeGraphAI": "prompt-inferred",
            "Apify": "N/A", "Exa": "N/A",
        }),
        ("Failure behavior", {c: "N/A" for c in competitors}),
        ("Notes", {c: "" for c in competitors}),
    ]
    print_comparison_table(competitors, rows)


if __name__ == "__main__":
    main()
