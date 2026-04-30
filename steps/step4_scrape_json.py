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
import runners.crawl4ai_runner as crawl4ai_runner
import runners.exa_runner as exa_runner
from utils import timed_call, save_result, excerpt, credits_used, print_step_header, print_competitor_header, print_comparison_table
from schemas import PRICING_SCHEMA
from config import PRIMARY_PRICING_URL

STEP = 4
TARGET_URL = PRIMARY_PRICING_URL
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

    # --- ScrapeGraphAI (using their /scrape endpoint with formats — closest
    #     apples-to-apples with Firecrawl /scrape) ---
    print_competitor_header("ScrapeGraphAI")
    print("  Using /scrape with formats: [{type:'json', schema}] — drop-in shape vs Firecrawl")
    r = timed_call(sgai_runner.scrape_json, TARGET_URL, PRICING_SCHEMA, SGAI_PROMPT)
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

    # --- Exa (schema-based via /contents summary.schema) ---
    print_competitor_header("Exa")
    print("  Schema-based extraction via /contents summary.schema (LLM-based)")
    r = timed_call(exa_runner.contents_with_schema, TARGET_URL, PRICING_SCHEMA, SGAI_PROMPT)
    data["exa"] = r
    if r["error"]:
        print(f"  ERROR: {r['error']}")
    else:
        print(f"  Latency: {r['latency_s']}s")
        print(f"  Cost: per request (Exa pricing per call)")
        print(f"  Output (full JSON):")
        print(json.dumps(r["result"], indent=2, default=str)[:2000])
    fp = save_result(STEP, "exa", r)
    print(f"  [saved to {fp}]")

    # --- Crawl4AI (LLM extraction strategy) ---
    print_competitor_header("Crawl4AI")
    print("  (uses OPENAI_API_KEY for LLM extraction — gpt-4o-mini)")
    r = timed_call(crawl4ai_runner.scrape_json, TARGET_URL, PRICING_SCHEMA)
    data["crawl4ai"] = r
    if r["error"]:
        print(f"  ERROR: {r['error']}")
    else:
        print(f"  Latency: {r['latency_s']}s")
        print(f"  Cost: free scaffolding + buyer's LLM tokens")
        print(f"  Output (full JSON):")
        result = r["result"]
        if isinstance(result, dict):
            extracted = result.get("extracted")
        else:
            extracted = result
        print(json.dumps(extracted, indent=2, default=str)[:2000])
    fp = save_result(STEP, "crawl4ai", r)
    print(f"  [saved to {fp}]")

    # --- No-equivalent competitors (per WebFetch verification of their docs) ---
    for name, note in [
        ("Spider", "CONFIRMED ABSENT in docs — no JSON schema parameter on any endpoint, only css_extraction_map (selector-based)"),
        ("Apify", "Standard actors (website-content-crawler, web-scraper) don't accept JSON schemas — actor-specific extraction logic"),
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
            "Crawl4AI": "LLMExtractionStrategy",
            "ScrapeGraphAI": "/scrape (formats:[{type:json,schema}])",
            "Apify": "N/A",
            "Exa": "/contents (summary.schema)",
        }),
        ("Has equivalent?", {
            "Firecrawl": "Yes (native, server-enforced)",
            "Spider": "No",
            "Crawl4AI": "Yes (LLM-based)",
            "ScrapeGraphAI": "Yes (LLM-based)",
            "Apify": "No",
            "Exa": "Yes (LLM-based)",
        }),
        ("Latency", {
            "Firecrawl": lat("firecrawl"),
            "Spider": "N/A",
            "Crawl4AI": lat("crawl4ai"),
            "ScrapeGraphAI": lat("scrapegraphai"),
            "Apify": "N/A",
            "Exa": lat("exa"),
        }),
        ("Cost", {
            "Firecrawl": str(credits_used(data.get("firecrawl", {}).get("result"))) + " credit(s)",
            "Spider": "N/A",
            "Crawl4AI": "free + buyer's LLM tokens",
            "ScrapeGraphAI": "not reported",
            "Apify": "N/A",
            "Exa": "per request",
        }),
        ("Schema fidelity", {
            "Firecrawl": "EXACT — server enforces schema",
            "Spider": "N/A",
            "Crawl4AI": "LLM best-effort (model-dependent)",
            "ScrapeGraphAI": "LLM best-effort",
            "Apify": "N/A",
            "Exa": "LLM best-effort",
        }),
        ("Failure behavior", {c: "N/A" for c in competitors}),
        ("Notes", {c: "" for c in competitors}),
    ]
    print_comparison_table(competitors, rows)


if __name__ == "__main__":
    main()
