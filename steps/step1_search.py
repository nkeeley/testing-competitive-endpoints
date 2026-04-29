#!/usr/bin/env python3
"""Step 1: Search — Find pricing pages for each competitor.
Competitors with search: Firecrawl, Spider, Exa.
"""
import sys
import os
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import runners.firecrawl_runner as fc_runner
import runners.spider_runner as spider_runner
import runners.exa_runner as exa_runner
from utils import timed_call, save_result, excerpt, print_step_header, print_competitor_header, print_comparison_table

STEP = 1
QUERIES = [
    "Spider cloud pricing page",
    "Crawl4AI pricing tiers",
    "ScrapeGraphAI pricing plans",
    "Apify pricing page",
    "Exa AI pricing",
]


def run_queries(runner_fn, queries, sleep_s=2, **kwargs):
    out = []
    for q in queries:
        r = timed_call(runner_fn, q, **kwargs)
        out.append({"query": q, **r})
        if r["error"]:
            print(f"  [{q}] ERROR: {r['error']}")
        else:
            print(f"  [{q}] Latency: {r['latency_s']}s")
            print(f"  Output: {excerpt(r['result'])}")
        time.sleep(sleep_s)
    return out


def rep_latency(out):
    if not out:
        return "N/A"
    r = out[0]
    return f"{r['latency_s']}s" if not r.get("error") else f"ERROR"


def main():
    print_step_header(STEP, "Search", "Finding competitor pricing pages")

    # --- Firecrawl ---
    print_competitor_header("Firecrawl")
    fc_out = run_queries(fc_runner.search, QUERIES, limit=3)
    fp = save_result(STEP, "firecrawl", fc_out)
    print(f"  [saved to {fp}]")

    # --- Spider ---
    print_competitor_header("Spider")
    spider_out = run_queries(spider_runner.search, QUERIES, limit=3)
    fp = save_result(STEP, "spider", spider_out)
    print(f"  [saved to {fp}]")

    # --- Exa ---
    print_competitor_header("Exa")
    exa_out = run_queries(exa_runner.search_and_contents, QUERIES, num_results=3)
    fp = save_result(STEP, "exa", exa_out)
    print(f"  [saved to {fp}]")

    # --- No-equivalent competitors ---
    for name in ["Crawl4AI", "ScrapeGraphAI", "Apify"]:
        print_competitor_header(name)
        print("  No search equivalent — N/A")

    competitors = ["Firecrawl", "Spider", "Crawl4AI", "ScrapeGraphAI", "Apify", "Exa"]
    rows = [
        ("Endpoint used", {
            "Firecrawl": "/search",
            "Spider": "spider.search()",
            "Crawl4AI": "N/A",
            "ScrapeGraphAI": "N/A",
            "Apify": "N/A (partial via actors)",
            "Exa": "exa.search_and_contents()",
        }),
        ("Has equivalent?", {
            "Firecrawl": "Yes", "Spider": "Yes", "Crawl4AI": "No",
            "ScrapeGraphAI": "No", "Apify": "Partial", "Exa": "Yes",
        }),
        ("Output quality (1-5)", {c: "___" for c in competitors}),
        ("Latency (first query)", {
            "Firecrawl": rep_latency(fc_out),
            "Spider": rep_latency(spider_out),
            "Crawl4AI": "N/A", "ScrapeGraphAI": "N/A", "Apify": "N/A",
            "Exa": rep_latency(exa_out),
        }),
        ("Cost", {
            "Firecrawl": "per credit",
            "Spider": "not reported",
            "Crawl4AI": "N/A", "ScrapeGraphAI": "N/A", "Apify": "N/A",
            "Exa": "not reported",
        }),
        ("Failure behavior", {c: "N/A" for c in competitors}),
        ("Notes", {c: "" for c in competitors}),
    ]
    print_comparison_table(competitors, rows)


if __name__ == "__main__":
    main()
