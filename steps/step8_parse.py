#!/usr/bin/env python3
"""Step 8: Parse — Upload a local PDF and extract structured content.
Two-step process:
  1. Download a PDF from a competitor's site (Apify docs PDF, Spider whitepaper, etc.)
  2. Parse it with Firecrawl /parse (markdown + JSON schema)
  3. Note competitor equivalents (ScrapeGraphAI partial, Apify partial via actors).

NOTE: /parse uses multipart/form-data — different from all other Firecrawl endpoints.
"""
import sys
import os
import json
import requests

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import runners.firecrawl_runner as fc_runner
import runners.spider_runner as spider_runner
import runners.crawl4ai_runner as crawl4ai_runner
from utils import timed_call, save_result, excerpt, print_step_header, print_competitor_header, print_comparison_table
from schemas import PARSE_SCHEMA
from config import PDF_CANDIDATES

STEP = 8

PDF_DOWNLOAD_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "results", "raw", "competitor_sample.pdf"
)


def download_pdf():
    os.makedirs(os.path.dirname(PDF_DOWNLOAD_PATH), exist_ok=True)
    for name, url in PDF_CANDIDATES:
        print(f"  Trying: {url}")
        try:
            resp = requests.get(url, timeout=15, headers={"User-Agent": "Mozilla/5.0"})
            if resp.status_code == 200 and b"%PDF" in resp.content[:10]:
                with open(PDF_DOWNLOAD_PATH, "wb") as f:
                    f.write(resp.content)
                size_kb = len(resp.content) // 1024
                print(f"  Downloaded '{name}' ({size_kb} KB) → {PDF_DOWNLOAD_PATH}")
                return PDF_DOWNLOAD_PATH, name, url
            else:
                print(f"  Not a PDF or request failed (status {resp.status_code}) — trying next")
        except Exception as e:
            print(f"  Failed: {e} — trying next")
    return None, None, None


def main():
    print_step_header(STEP, "Parse", "Local PDF file upload + structured extraction")

    print("\n[Step 8a] Downloading a PDF from a competitor site...")
    pdf_path, pdf_name, pdf_url = download_pdf()

    if not pdf_path:
        print("\n  ERROR: Could not download any candidate PDF.")
        print("  To run this step manually:")
        print(f"    curl -o {PDF_DOWNLOAD_PATH} <pdf-url>")
        print("  Then re-run this script.")
        return

    print(f"\n[Step 8b] Parsing with Firecrawl /parse (markdown mode)...")
    print_competitor_header("Firecrawl — markdown")
    r_md = timed_call(fc_runner.parse_file, pdf_path)
    if r_md["error"]:
        print(f"  ERROR: {r_md['error']}")
    else:
        print(f"  Latency: {r_md['latency_s']}s")
        result = r_md["result"]
        md = result.get("markdown") or result.get("data", {}).get("markdown") if isinstance(result, dict) else None
        print(f"  Output (first 500 chars):\n{excerpt(md)}")
    fp = save_result(STEP, "firecrawl_parse_md", r_md)
    print(f"  [saved to {fp}]")

    print(f"\n[Step 8c] Parsing with Firecrawl /parse (JSON schema mode)...")
    print_competitor_header("Firecrawl — JSON schema")
    print(f"  Schema: {json.dumps(PARSE_SCHEMA, indent=2)}")
    r_json = timed_call(fc_runner.parse_file, pdf_path, PARSE_SCHEMA)
    if r_json["error"]:
        print(f"  ERROR: {r_json['error']}")
    else:
        print(f"  Latency: {r_json['latency_s']}s")
        result = r_json["result"]
        extracted = (
            result.get("json")
            or result.get("extract")
            or result.get("data")
            if isinstance(result, dict) else result
        )
        print(f"  Output (full JSON):")
        print(json.dumps(extracted, indent=2, default=str)[:2000])
    fp = save_result(STEP, "firecrawl_parse_json", r_json)
    print(f"  [saved to {fp}]")

    # --- Spider (transform endpoint) ---
    # Spider's transform takes a content string, not a file upload, so we read the
    # PDF as bytes and pass it through. Comparison is structurally awkward.
    print_competitor_header("Spider")
    print("  Note: Spider's /v1/transform takes content (not file upload). Reading PDF text first.")
    try:
        from pypdf import PdfReader
        reader = PdfReader(pdf_path)
        pdf_text = "\n".join(page.extract_text() or "" for page in reader.pages)
        spider_r = timed_call(spider_runner.transform, pdf_text, "markdown")
    except ImportError:
        spider_r = {"result": None, "latency_s": 0, "error": "pypdf not installed — pip install pypdf"}
    if spider_r["error"]:
        print(f"  ERROR: {spider_r['error']}")
    else:
        print(f"  Latency: {spider_r['latency_s']}s")
        print(f"  Output (first 500 chars):\n{excerpt(spider_r['result'])}")
    fp = save_result(STEP, "spider", spider_r)
    print(f"  [saved to {fp}]")

    # --- Crawl4AI (PDF parsing) ---
    print_competitor_header("Crawl4AI")
    print(f"  Passing local PDF to AsyncWebCrawler via file:// URL")
    c4_r = timed_call(crawl4ai_runner.parse_pdf, pdf_path)
    if c4_r["error"]:
        print(f"  ERROR: {c4_r['error']}")
    else:
        print(f"  Latency: {c4_r['latency_s']}s")
        result = c4_r["result"]
        md = result.get("markdown") if isinstance(result, dict) else None
        print(f"  Output (first 500 chars):\n{excerpt(md)}")
    fp = save_result(STEP, "crawl4ai", c4_r)
    print(f"  [saved to {fp}]")

    print_competitor_header("ScrapeGraphAI")
    print("  Partial: can extract from URLs, but no local file upload endpoint.")
    print("  Skipping — no equivalent to Firecrawl /parse for local files.")

    print_competitor_header("Apify")
    print("  Partial: PDF parsing actors exist (e.g. apify/pdf-text-extractor).")
    print("  Not tested here — requires actor setup and file upload via Apify storage.")

    print_competitor_header("Exa")
    print("  No file upload / parse primitive — N/A")

    competitors = ["Firecrawl", "Spider", "Crawl4AI", "ScrapeGraphAI", "Apify", "Exa"]
    def lat(r):
        return f"{r['latency_s']}s" if r and not r.get("error") else ("ERROR" if r.get("error") else "N/A")

    rows = [
        ("Endpoint used", {
            "Firecrawl": "/parse (multipart/form-data)",
            "Spider": "/v1/transform (content, not file)",
            "Crawl4AI": "AsyncWebCrawler with file:// URL",
            "ScrapeGraphAI": "N/A (URL-only)",
            "Apify": "N/A (actor required)",
            "Exa": "N/A",
        }),
        ("Has equivalent?", {
            "Firecrawl": "Yes",
            "Spider": "Partial (content-based, not file-upload)",
            "Crawl4AI": "Partial (file:// hack)",
            "ScrapeGraphAI": "Partial (URL only)",
            "Apify": "Partial (actor required)",
            "Exa": "No",
        }),
        ("PDF source", {
            "Firecrawl": f"{pdf_name} ({pdf_url})" if pdf_name else "N/A",
            "Spider": "same PDF (text extracted via pypdf)",
            "Crawl4AI": "same PDF (file:// URL)",
            "ScrapeGraphAI": "N/A", "Apify": "N/A", "Exa": "N/A",
        }),
        ("Markdown quality (1-5)", {
            "Firecrawl": "___", "Spider": "___", "Crawl4AI": "___",
            "ScrapeGraphAI": "N/A", "Apify": "N/A", "Exa": "N/A",
        }),
        ("JSON schema quality (1-5)", {"Firecrawl": "___", **{c: "N/A" for c in competitors[1:]}}),
        ("Latency (markdown)", {
            "Firecrawl": lat(r_md),
            "Spider": lat(spider_r),
            "Crawl4AI": lat(c4_r),
            "ScrapeGraphAI": "N/A", "Apify": "N/A", "Exa": "N/A",
        }),
        ("Latency (JSON schema)", {"Firecrawl": lat(r_json), **{c: "N/A" for c in competitors[1:]}}),
        ("Content-Type", {
            "Firecrawl": "multipart/form-data (different from all other FC endpoints)",
            "Spider": "application/json (content as string)",
            "Crawl4AI": "Python lib, no HTTP",
            "ScrapeGraphAI": "N/A", "Apify": "N/A", "Exa": "N/A",
        }),
        ("Failure behavior", {c: "N/A" for c in competitors}),
        ("Notes", {c: "" for c in competitors}),
    ]
    print_comparison_table(competitors, rows)


if __name__ == "__main__":
    main()
