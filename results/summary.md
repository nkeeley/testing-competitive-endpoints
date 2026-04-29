# Firecrawl Competitive Testing — Summary

**Date:** 2026-04-28  
**Tester:** nkeeley  
**Method:** Python SDK (not CLI). Note: SDK experience may differ from CLI — known pattern per internal friction log.

---

## Step 1: Search

| Dimension | Firecrawl | Spider | Crawl4AI | ScrapeGraphAI | Apify | Exa |
|---|---|---|---|---|---|---|
| Endpoint used | /search | spider.search() | N/A | N/A | N/A (partial via actors) | exa.search_and_contents() |
| Has equivalent? | Yes | Yes | No | No | Partial | Yes |
| Output quality (1-5) | | | N/A | N/A | N/A | |
| Latency (first query) | | | N/A | N/A | N/A | |
| Cost | per credit | not reported | N/A | N/A | N/A | not reported |
| Failure behavior | | | N/A | N/A | N/A | |
| Notes | | | | | | |

---

## Step 2: Map

| Dimension | Firecrawl | Spider | Crawl4AI | ScrapeGraphAI | Apify | Exa |
|---|---|---|---|---|---|---|
| Endpoint used | /map | N/A | N/A | N/A | N/A | N/A |
| Has equivalent? | Yes | No | No | No | No | No |
| Output quality (1-5) | | N/A | N/A | N/A | N/A | N/A |
| URLs returned | | N/A | N/A | N/A | N/A | N/A |
| Cost | per credit | N/A | N/A | N/A | N/A | N/A |
| Failure behavior | | N/A | N/A | N/A | N/A | N/A |
| Notes | | | | | | |

---

## Step 3: Scrape (Markdown)

| Dimension | Firecrawl | Spider | Crawl4AI | ScrapeGraphAI | Apify | Exa |
|---|---|---|---|---|---|---|
| Endpoint used | /scrape | scrape_url() | AsyncWebCrawler | smartscraper | website-content-crawler | N/A |
| Has equivalent? | Yes | Yes | Yes | Yes (schema-first) | Yes (via actor) | No |
| Output quality (1-5) | | | | | | N/A |
| Latency | | | | | | N/A |
| Cost | credit(s) | not reported | free | not reported | not reported | N/A |
| Cost matched docs? | | N/A | N/A | N/A | N/A | N/A |
| Failure behavior | | | | | | N/A |
| Notes | | | | | | |

---

## Step 4: Scrape (JSON schema)

| Dimension | Firecrawl | Spider | Crawl4AI | ScrapeGraphAI | Apify | Exa |
|---|---|---|---|---|---|---|
| Endpoint used | /scrape (JSON schema) | N/A | N/A | smartscraper (prompt) | N/A | N/A |
| Has equivalent? | Yes (native) | No | No | Yes (prompt-based) | No | No |
| Output quality (1-5) | | N/A | N/A | | N/A | N/A |
| Latency | | N/A | N/A | | N/A | N/A |
| Cost | credit(s) | N/A | N/A | not reported | N/A | N/A |
| Schema fidelity | exact schema enforced | N/A | N/A | prompt-inferred | N/A | N/A |
| Failure behavior | | N/A | N/A | | N/A | N/A |
| Notes | | | | | | |

---

## Step 5: Crawl

| Dimension | Firecrawl | Spider | Crawl4AI | ScrapeGraphAI | Apify | Exa |
|---|---|---|---|---|---|---|
| Endpoint used | /crawl | crawl_url() | AsyncWebCrawler (sequential) | N/A | website-content-crawler | N/A |
| Has equivalent? | Yes | Yes | Yes (manual link-follow) | No | Yes (via actor) | No |
| Output quality (1-5) | | | | N/A | | N/A |
| Latency | | | | N/A | | N/A |
| Pages returned | | | | N/A | | N/A |
| Cost | credit(s) | not reported | free | N/A | not reported | N/A |
| Failure behavior | | | | N/A | | N/A |
| Notes | | | | | | |

---

## Step 6: Agent

| Dimension | Firecrawl | Spider | Crawl4AI | ScrapeGraphAI | Apify | Exa |
|---|---|---|---|---|---|---|
| Endpoint used | /agent (spark-1-mini) | N/A | N/A | N/A | N/A | N/A |
| Has equivalent? | Yes | No | No | No | No | No |
| Output quality (1-5) | | N/A | N/A | N/A | N/A | N/A |
| Latency (incl. polling) | | N/A | N/A | N/A | N/A | N/A |
| Cost | per agent credit | N/A | N/A | N/A | N/A | N/A |
| Failure behavior | | N/A | N/A | N/A | N/A | N/A |
| Notes | | | | | | |

---

## Step 7: Interact

| Dimension | Firecrawl | Spider | Crawl4AI | ScrapeGraphAI | Apify | Exa |
|---|---|---|---|---|---|---|
| Endpoint used | /scrape + /interact | N/A | N/A | N/A | N/A | N/A |
| Has equivalent? | Yes | No | No | No | No | No |
| Output quality (1-5) | | N/A | N/A | N/A | N/A | N/A |
| Scrape latency | | N/A | N/A | N/A | N/A | N/A |
| Interact latency | | N/A | N/A | N/A | N/A | N/A |
| Toggle detected? | | N/A | N/A | N/A | N/A | N/A |
| Cost | 2 credits (scrape + interact) | N/A | N/A | N/A | N/A | N/A |
| Failure behavior | | N/A | N/A | N/A | N/A | N/A |
| Notes | | | | | | |

---

## Step 8: Parse

| Dimension | Firecrawl | Spider | Crawl4AI | ScrapeGraphAI | Apify | Exa |
|---|---|---|---|---|---|---|
| Endpoint used | /parse (multipart/form-data) | N/A | N/A | N/A (URL-only) | N/A (actor required) | N/A |
| Has equivalent? | Yes | No | No | Partial (URL only) | Partial (actor required) | No |
| Markdown quality (1-5) | | N/A | N/A | N/A | N/A | N/A |
| JSON schema quality (1-5) | | N/A | N/A | N/A | N/A | N/A |
| Latency (markdown) | | N/A | N/A | N/A | N/A | N/A |
| Latency (JSON schema) | | N/A | N/A | N/A | N/A | N/A |
| Content-Type | multipart/form-data | N/A | N/A | N/A | N/A | N/A |
| Failure behavior | | N/A | N/A | N/A | N/A | N/A |
| Notes | | | | | | |

---

## Overall Observations

*(fill in after completing all steps)*

### Firecrawl unique primitives (no competitor equivalent)
- /map — site URL discovery
- /agent — autonomous research
- /interact — browser interaction after scrape
- /parse — local file upload + structured extraction

### Firecrawl competitive strengths
- 

### Areas where competitors matched or exceeded
- 

### Surprises
- 
