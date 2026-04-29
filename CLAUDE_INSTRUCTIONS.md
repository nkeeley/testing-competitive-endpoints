# Firecrawl Competitive Testing Suite — Instructions for Claude Code

## Context

I'm a Product Operations Engineer at Firecrawl, preparing for a mock interview with the CTO. I need to test Firecrawl's endpoints ("primitives") head-to-head against key competitors using a single realistic workflow. This is my first time testing competitors against non-search endpoints — I have zero data on scrape/crawl/agent/map comparisons.

## Implementation Approach

**Use Python SDKs as the primary interface for all testing.** I'm most comfortable with data science workflows and Python is the natural fit.

- Install the latest version of every SDK before running: `pip install --upgrade firecrawl-py exa-py apify-client crawl4ai spider-client scrapegraphai` (verify package names — some may differ)
- **Important: the correct Firecrawl package is `firecrawl-py`, NOT `firecrawl`.** The `firecrawl` package on PyPI is an unrelated project.
- If a Python SDK doesn't exist or is broken for a competitor, fall back to `requests` with their REST API directly.
- All curl examples in this doc are provided as reference for the API shape — translate them to Python SDK calls. The SDK methods will be cleaner.
- **Note in the results that testing was done via Python SDK, not CLI.** This matters because our internal friction log found significant CLI-vs-SDK capability gaps. If the SDK experience is smoother than what the CLI offers, that reinforces a known pattern.

### Python SDK Quick Reference

```python
# Firecrawl
from firecrawl import Firecrawl
fc = Firecrawl(api_key=os.environ["FIRECRAWL_API_KEY"])
# fc.search(), fc.scrape(), fc.crawl(), fc.map(), fc.agent(), fc.parse()

# Exa
from exa_py import Exa
exa = Exa(api_key=os.environ["EXA_API_KEY"])
# exa.search(), exa.search_and_contents()

# Spider
from spider import Spider
spider = Spider(api_key=os.environ["SPIDER_API_KEY"])
# spider.scrape_url(), spider.crawl_url()

# Apify
from apify_client import ApifyClient
apify = ApifyClient(os.environ["APIFY_API_TOKEN"])
# apify.actor("apify/website-content-crawler").call(run_input={...})

# Crawl4AI
from crawl4ai import AsyncWebCrawler, CrawlerRunConfig
# async with AsyncWebCrawler() as crawler: result = await crawler.arun(url=...)

# ScrapeGraphAI — verify current SDK interface, may need raw requests
import requests
# requests.post("https://api.scrapegraphai.com/v1/smartscraper", ...)
```

### Timing wrapper (use for every call)

```python
import time

def timed_call(fn, *args, **kwargs):
    start = time.time()
    try:
        result = fn(*args, **kwargs)
        elapsed = time.time() - start
        return {"result": result, "latency_s": round(elapsed, 3), "error": None}
    except Exception as e:
        elapsed = time.time() - start
        return {"result": None, "latency_s": round(elapsed, 3), "error": str(e)}
```

## The Workflow

**Task: Extract competitor pricing data.** One workflow that exercises every Firecrawl primitive, tested on Firecrawl first, then repeated on competitors where they have equivalent capabilities.

### Steps (in order)

1. **Search** — Find the pricing page URL for each competitor
2. **Map** — Discover all pages on each competitor's docs site
3. **Scrape (markdown)** — Extract pricing page content as clean markdown
4. **Scrape (JSON schema)** — Structured extraction of plan names, prices, credit/page limits, rate limits
5. **Crawl** — Crawl each competitor's docs site (limit 20 pages), return markdown
6. **Agent** — Autonomous: "Find the complete pricing tiers, per-endpoint costs, and rate limits for [competitor]"
7. **Interact/Browser** — Handle a pricing page that requires clicking (e.g., monthly/annual toggle, feature comparison accordion)
8. **Parse** — Upload a local file (PDF, DOCX, XLSX) and extract structured content. Download a competitor's PDF docs/whitepaper first, then parse it through Firecrawl's /parse and any competitor equivalent

### Target Competitors (in priority order)

| Competitor | What they are | Has search? | Has scrape? | Has crawl? | Has agent? | Has map? | Has interact? | Has parse? |
|---|---|---|---|---|---|---|---|---|
| Spider | Rust-based scraping API, fastest throughput | Yes | Yes | Yes | No | No | No | No |
| Crawl4AI | Open-source self-hosted crawler | No (self-hosted only) | Yes | Yes | No | No | No | No |
| ScrapeGraphAI | LLM-powered structured extraction | No | Yes (schema-first) | Partial | No | No | No | Partial (can extract from URLs but not file upload) |
| Apify | Marketplace of 10K+ pre-built actors | Partial (via actors) | Yes (via actors) | Yes (via actors) | No | No | No | Partial (PDF actors exist) |
| Exa | Semantic search API | Yes | Partial (contents endpoint) | No | No | No | No | No |

### Target URLs for the workflow

Use these competitors' own sites as the scraping targets:

- Spider: `https://spider.cloud`, docs at `https://spider.cloud/docs`
- Crawl4AI: `https://crawl4ai.com`, docs at `https://docs.crawl4ai.com`
- ScrapeGraphAI: `https://scrapegraphai.com`, docs at `https://docs.scrapegraphai.com`
- Apify: `https://apify.com`, docs at `https://docs.apify.com`
- Exa: `https://exa.ai`, docs at `https://docs.exa.ai`

## Environment Variables

The following API keys should be set as environment variables. I will have these loaded before running.

```
FIRECRAWL_API_KEY=fc-...
SPIDER_API_KEY=...
EXA_API_KEY=...
APIFY_API_TOKEN=...
SCRAPEGRAPHAI_API_KEY=...
```

Crawl4AI is self-hosted / open-source — no API key needed but requires local installation (`pip install crawl4ai`).

## Firecrawl API Reference

Base URL: `https://api.firecrawl.dev/v2/`
Auth: `Authorization: Bearer $FIRECRAWL_API_KEY`
All endpoints are POST.

### /search
```bash
curl -X POST https://api.firecrawl.dev/v2/search \
  -H 'Content-Type: application/json' \
  -H "Authorization: Bearer $FIRECRAWL_API_KEY" \
  -d '{"query": "Spider cloud pricing", "limit": 5}'
```

### /map
```bash
curl -X POST https://api.firecrawl.dev/v2/map \
  -H 'Content-Type: application/json' \
  -H "Authorization: Bearer $FIRECRAWL_API_KEY" \
  -d '{"url": "https://spider.cloud"}'
```

### /scrape (markdown)
```bash
curl -X POST https://api.firecrawl.dev/v2/scrape \
  -H 'Content-Type: application/json' \
  -H "Authorization: Bearer $FIRECRAWL_API_KEY" \
  -d '{"url": "https://spider.cloud/pricing", "formats": ["markdown"]}'
```

### /scrape (JSON schema)
```bash
curl -X POST https://api.firecrawl.dev/v2/scrape \
  -H 'Content-Type: application/json' \
  -H "Authorization: Bearer $FIRECRAWL_API_KEY" \
  -d '{
    "url": "https://spider.cloud/pricing",
    "formats": [{
      "type": "json",
      "schema": {
        "type": "object",
        "properties": {
          "plans": {
            "type": "array",
            "items": {
              "type": "object",
              "properties": {
                "plan_name": {"type": ["string", "null"]},
                "price_monthly": {"type": ["string", "null"]},
                "credits_or_pages": {"type": ["string", "null"]},
                "rate_limit": {"type": ["string", "null"]},
                "key_features": {"type": ["array", "null"], "items": {"type": "string"}}
              }
            }
          }
        }
      }
    }]
  }'
```

### /crawl
```bash
curl -X POST https://api.firecrawl.dev/v2/crawl \
  -H 'Content-Type: application/json' \
  -H "Authorization: Bearer $FIRECRAWL_API_KEY" \
  -d '{"url": "https://spider.cloud/docs", "limit": 20, "wait": true}'
```
Note: `wait: true` returns results inline. Without it, you get a job ID and must poll.

### /agent
```bash
curl -X POST https://api.firecrawl.dev/v2/agent \
  -H 'Content-Type: application/json' \
  -H "Authorization: Bearer $FIRECRAWL_API_KEY" \
  -d '{
    "prompt": "Find the complete pricing tiers, per-endpoint costs, and rate limits for Spider.cloud",
    "model": "spark-1-mini"
  }'
```
Note: /agent is async. You'll get a job ID and need to poll for results, or use `wait: true` if supported.

### /interact
```bash
# First scrape the page
curl -X POST https://api.firecrawl.dev/v2/scrape \
  -H 'Content-Type: application/json' \
  -H "Authorization: Bearer $FIRECRAWL_API_KEY" \
  -d '{"url": "https://apify.com/pricing", "formats": ["markdown"]}'

# Then interact with the returned scrape ID
curl -X POST https://api.firecrawl.dev/v2/interact \
  -H 'Content-Type: application/json' \
  -H "Authorization: Bearer $FIRECRAWL_API_KEY" \
  -d '{
    "scrape_id": "SCRAPE_ID_FROM_ABOVE",
    "prompt": "Click the annual pricing toggle and extract all plan prices"
  }'
```

### /parse
```bash
# Step 1: Download a PDF from a competitor site (e.g., a whitepaper or docs PDF)
curl -o competitor_doc.pdf "https://example.com/docs/whitepaper.pdf"

# Step 2: Parse with markdown output
curl -X POST https://api.firecrawl.dev/v2/parse \
  -H "Authorization: Bearer $FIRECRAWL_API_KEY" \
  -H 'Content-Type: multipart/form-data' \
  -F 'file=@./competitor_doc.pdf' \
  -F 'options={"formats": ["markdown"], "onlyMainContent": true, "parsers": [{"type": "pdf", "mode": "auto"}]}'

# Step 3: Parse with structured JSON extraction
curl -X POST https://api.firecrawl.dev/v2/parse \
  -H "Authorization: Bearer $FIRECRAWL_API_KEY" \
  -H 'Content-Type: multipart/form-data' \
  -F 'file=@./competitor_doc.pdf' \
  -F 'options={"formats": [{"type": "json", "schema": {"type": "object", "properties": {"title": {"type": "string"}, "key_topics": {"type": "array", "items": {"type": "string"}}, "summary": {"type": "string"}}}}], "onlyMainContent": true, "parsers": [{"type": "pdf", "mode": "auto"}]}'
```
Notes on /parse:
- Uses `multipart/form-data`, NOT `application/json` — different from all other Firecrawl endpoints.
- The `file` field uses `@` prefix to reference a local file path.
- Supported file types: `.pdf`, `.docx`, `.doc`, `.odt`, `.rtf`, `.xlsx`, `.xls`, `.html`, `.htm`
- Max file size: 50 MB per request.
- PDF parser modes: `fast` (text-only), `auto` (text + OCR fallback, default), `ocr` (force OCR every page).
- Supports same `formats` as /scrape: `markdown`, `html`, `rawHtml`, `links`, `images`, `summary`, and `json` with schema.
- Does NOT support browser-only options: `actions`, `waitFor`, `location`, `mobile`, change tracking.
- No batch upload — call /parse per file in parallel for batches.
- For the test: download a PDF from each competitor's site first, then parse it through Firecrawl and any competitor that supports local file parsing.

## Competitor API References (quick start)

### Spider
Base URL: `https://api.spider.cloud/`
Auth: `Authorization: Bearer $SPIDER_API_KEY`
```python
# pip install spider-client
from spider import Spider
s = Spider(api_key=SPIDER_API_KEY)
# Scrape
result = s.scrape_url("https://example.com", params={"return_format": "markdown"})
# Crawl
result = s.crawl_url("https://example.com", params={"limit": 20, "return_format": "markdown"})
```

### Exa
```python
# pip install exa-py
from exa_py import Exa
exa = Exa(api_key=EXA_API_KEY)
# Search
results = exa.search("Spider cloud pricing", num_results=5)
# Search + contents
results = exa.search_and_contents("Spider cloud pricing", num_results=5, text=True)
```

### Apify
```python
# pip install apify-client
from apify_client import ApifyClient
client = ApifyClient(APIFY_API_TOKEN)
# Website Content Crawler actor
run = client.actor("apify/website-content-crawler").call(
    run_input={"startUrls": [{"url": "https://spider.cloud/pricing"}], "maxCrawlPages": 20}
)
items = list(client.dataset(run["defaultDatasetId"]).iterate_items())
```

### ScrapeGraphAI
```python
# pip install scrapegraphai
# Check their docs for current API client — may use requests directly
import requests
response = requests.post(
    "https://api.scrapegraphai.com/v1/smartscraper",
    headers={"Authorization": f"Bearer {SCRAPEGRAPHAI_API_KEY}"},
    json={
        "url": "https://spider.cloud/pricing",
        "prompt": "Extract all pricing plans with plan name, price, credits, and rate limits"
    }
)
```

### Crawl4AI
```python
# pip install crawl4ai
from crawl4ai import AsyncWebCrawler, CrawlerRunConfig
import asyncio

async def scrape(url):
    async with AsyncWebCrawler() as crawler:
        result = await crawler.arun(url=url, config=CrawlerRunConfig())
        return result.markdown

asyncio.run(scrape("https://spider.cloud/pricing"))
```

## What to Build

### Project Structure
```
firecrawl-competitive-test/
├── README.md              # How to run, what each step tests
├── requirements.txt       # firecrawl-py, exa-py, apify-client, spider-client, crawl4ai, scrapegraphai, requests
├── config.py              # env vars, target URLs, competitor list
├── schemas.py             # shared Pydantic/dict schema for pricing extraction
├── utils.py               # timed_call wrapper, result saving, table formatting
├── runners/               # one module per competitor, wrapping their SDK
│   ├── firecrawl_runner.py
│   ├── spider_runner.py
│   ├── exa_runner.py
│   ├── apify_runner.py
│   ├── scrapegraphai_runner.py
│   └── crawl4ai_runner.py
├── steps/                 # one script per workflow step — run individually
│   ├── step1_search.py
│   ├── step2_map.py
│   ├── step3_scrape_md.py
│   ├── step4_scrape_json.py
│   ├── step5_crawl.py
│   ├── step6_agent.py
│   ├── step7_interact.py
│   └── step8_parse.py
└── results/
    ├── raw/               # raw JSON responses, auto-saved per step per competitor
    └── summary.md         # I fill this in manually after reviewing each step
```

### How I'll use this

Each step script is run independently from the command line:

```bash
python steps/step1_search.py       # runs search on Firecrawl + Exa + Spider
python steps/step2_map.py          # runs map on Firecrawl only (no competitor equivalent)
python steps/step3_scrape_md.py    # runs scrape on Firecrawl + Spider + Crawl4AI + ScrapeGraphAI + Apify
# ... etc
```

Each step script should:

1. Run the task on Firecrawl first, then on each competitor that has the equivalent primitive
2. Print the raw output (or a meaningful excerpt — first 500 chars of markdown, full JSON for structured extraction) to stdout so I can review it immediately
3. Print a pre-formatted comparison table to stdout with blanks for the "Output quality" row — I fill in the 1-5 score after reviewing
4. Auto-save full raw responses to `results/raw/step{N}_{competitor}.json`
5. Print the file paths it saved to so I can go back and re-read if needed

**I will manually:**
- Review stdout output after each step
- Assign output quality scores (1-5)
- Note failure behavior (Loud / Silent / N/A)
- Copy the completed table into `results/summary.md`
- Skip or reorder steps based on what I'm learning as I go

**The scripts should NOT:**
- Auto-score output quality — that requires my judgment
- Auto-advance to the next step — I decide when to move on
- Block on failure — if a competitor errors out, print the error and continue to the next competitor
- Require running in order — each step is standalone (though the workflow makes most sense in order)

### Each step script should:

1. Run the same task on Firecrawl + each competitor that has the equivalent primitive
2. Print a clear header per competitor so I can scan output quickly
3. Print readable output to stdout: first 500 chars of markdown, full JSON for structured extraction, error messages in full
4. Print a pre-formatted comparison table with blanks where I need to fill in manual scores
5. Save raw responses to `results/raw/step{N}_{competitor}.json`
6. Print the saved file paths at the end

### Example stdout for one step:

```
=== STEP 3: Scrape (Markdown) — https://spider.cloud/pricing ===

--- Firecrawl ---
Latency: 1.23s
Credits used: 1
Output (first 500 chars):
# Spider Pricing

Spider offers simple, pay-as-you-go pricing...
[saved to results/raw/step3_firecrawl.json]

--- Spider ---
Latency: 0.89s
Cost: not reported in response
Output (first 500 chars):
# Pricing - Spider

Get started for free with...
[saved to results/raw/step3_spider.json]

--- Crawl4AI ---
Latency: 2.41s
Cost: free (self-hosted)
Output (first 500 chars):
Spider   Pricing  Get started...
[saved to results/raw/step3_crawl4ai.json]

--- COMPARISON TABLE (fill in quality scores manually) ---

| Dimension | Firecrawl | Spider | Crawl4AI |
|---|---|---|---|
| Endpoint used | /scrape | scrape_url | AsyncWebCrawler |
| Has equivalent? | Yes | Yes | Yes |
| Output quality (1-5) | ___ | ___ | ___ |
| Cost | 1 credit | not reported | free |
| Cost matched docs? | yes | N/A | N/A |
| Failure behavior | N/A | N/A | N/A |
| Notes | | | |
```

**Output Quality scoring rubric:**
- 5 = every field present, accurate, production-ready
- 4 = minor imperfections, usable as-is
- 3 = directionally right but needs cleanup (e.g., category links instead of products)
- 2 = mostly wrong or incomplete
- 1 = useless, empty, or wrong content served as success

**Failure behavior:**
- Loud = clear error message, appropriate status code, no credit charged
- Silent = 200 OK with wrong/partial/empty content, or credit charged on failure
- N/A = succeeded, no failure to evaluate

### Important implementation notes:

- **Output quality scores require human judgment.** The test suite should save raw outputs and print them clearly so I can assign the 1-5 score manually. Don't try to auto-score quality.
- **Cost data lives in Firecrawl response metadata** under `creditsUsed`. Other competitors may not report cost in the response — note "not reported" if so.
- **Competitors that don't have an equivalent primitive** should be marked N/A in the table, not skipped silently. The absence of a primitive IS a data point.
- **Latency** should be measured as wall-clock time from request send to response received. Use `time.time()` around each call.
- **Error handling is critical.** If a competitor call fails, catch the exception, record the error message, and continue. Don't let one failure block the rest of the suite.
- **Rate limits.** Add a 2-second sleep between calls to the same provider to avoid throttling.
- **The /interact test (Step 7)** is Firecrawl-only — no competitor has an equivalent. Still run it and record the result. Use Apify's pricing page as the target since it has a monthly/annual toggle.
- **The /agent test (Step 6)** is also likely Firecrawl-only. Run it and note that competitors don't offer this.
- **The /parse test (Step 8)** requires a two-step process: first download a PDF from a competitor site (look for whitepapers, documentation PDFs, or terms-of-service PDFs), then upload that file to Firecrawl's /parse endpoint. Test both markdown and JSON schema extraction. Note that /parse uses `multipart/form-data`, not `application/json` — this is different from every other Firecrawl endpoint. Most competitors don't have a direct file-upload parse equivalent; ScrapeGraphAI and Apify may have partial support. Mark others as N/A.
- **For Crawl4AI**, you'll need to install it locally first: `pip install crawl4ai` then `crawl4ai-setup`. It runs Playwright under the hood.

### What I'll do with the output:

1. Review the raw responses and assign output quality scores manually
2. Fill in the comparison tables in our Notion Competitive Intelligence page
3. Use the results in my mock interview to say "I tested X against Y and here's what I found"

### Don't worry about:

- Making the code production-quality — this is a one-time test suite
- Building a UI or dashboard — stdout tables and saved files are fine
- Testing every competitor on every step — follow the matrix above (some competitors only overlap on 1-2 primitives)
- Caching or retries — one clean run is enough

### Do prioritize:

- Clear, readable output that I can scan quickly
- Raw response saving so I can re-examine results later
- The comparison table format in summary.md — that's what I'll paste into Notion
- Running all Firecrawl steps first (Steps 1-7), then running competitor equivalents