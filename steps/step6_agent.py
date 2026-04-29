#!/usr/bin/env python3
"""Step 6: Agent — Autonomous research: find complete pricing tiers, per-endpoint costs,
and rate limits for Spider.cloud. Firecrawl-only primitive.
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import runners.firecrawl_runner as fc_runner
from utils import timed_call, save_result, excerpt, print_step_header, print_competitor_header, print_comparison_table
from config import PRIMARY_DISPLAY_NAME, PRIMARY_BASE_URL

STEP = 6
PROMPT = (
    f"Find the complete pricing tiers, per-endpoint costs, and rate limits for {PRIMARY_DISPLAY_NAME} "
    f"({PRIMARY_BASE_URL}). Include plan names, monthly prices, credits or pages included, "
    f"and any overage costs."
)


def main():
    print_step_header(STEP, "Agent", f"{PRIMARY_DISPLAY_NAME} pricing research (autonomous)")

    print_competitor_header("Firecrawl")
    print(f"  Prompt: {PROMPT}")
    print("  (agent is async — polling every 5s, up to 5 minutes)")

    r = timed_call(fc_runner.agent, PROMPT)

    if r["error"]:
        print(f"  ERROR: {r['error']}")
    else:
        print(f"  Latency (incl. polling): {r['latency_s']}s")
        result = r["result"]
        status = result.get("status") if isinstance(result, dict) else "unknown"
        print(f"  Final status: {status}")
        output = None
        if isinstance(result, dict):
            output = (
                result.get("output")
                or result.get("result")
                or result.get("answer")
                or result.get("data")
                or result
            )
        print(f"  Output (first 500 chars):\n{excerpt(output)}")

    fp = save_result(STEP, "firecrawl", r)
    print(f"  [saved to {fp}]")

    # All competitors — no agent equivalent
    for name in ["Spider", "Crawl4AI", "ScrapeGraphAI", "Apify", "Exa"]:
        print_competitor_header(name)
        print("  No agent/autonomous research primitive — N/A")

    competitors = ["Firecrawl", "Spider", "Crawl4AI", "ScrapeGraphAI", "Apify", "Exa"]
    rows = [
        ("Endpoint used", {
            "Firecrawl": "/agent (spark-1-mini)",
            **{c: "N/A" for c in competitors[1:]},
        }),
        ("Has equivalent?", {
            "Firecrawl": "Yes",
            **{c: "No" for c in competitors[1:]},
        }),
        ("Output quality (1-5)", {"Firecrawl": "___", **{c: "N/A" for c in competitors[1:]}}),
        ("Latency", {
            "Firecrawl": f"{r['latency_s']}s" if not r.get("error") else "ERROR",
            **{c: "N/A" for c in competitors[1:]},
        }),
        ("Cost", {"Firecrawl": "per agent credit", **{c: "N/A" for c in competitors[1:]}}),
        ("Failure behavior", {c: "N/A" for c in competitors}),
        ("Notes", {c: "" for c in competitors}),
    ]
    print_comparison_table(competitors, rows)


if __name__ == "__main__":
    main()
