# Firecrawl Competitive Testing — Results & Reflections

> **Purpose of this doc:** Single paste-ready handoff for qualitative synthesis. Captures comparison tables + tester reflections per step, plus overall themes. Designed to be pasted whole into a fresh Claude conversation for synthesis.

---

## Context for the synthesis reader

**Who:** Nick Keeley, Product Operations Engineer at Firecrawl, prepping for a mock interview with the CTO.

**What:** Head-to-head test of Firecrawl's 8 primitives (search, map, scrape-md, scrape-json, crawl, agent, interact, parse) vs. five competitors: Spider, Crawl4AI, ScrapeGraphAI, Apify, Exa.

**How:** Each step is a Python script in `steps/stepN_*.py` that runs the same task on Firecrawl + each competitor with an equivalent primitive, prints raw output + a comparison table, and saves raw responses to `results/raw/`. Tester reviews output and assigns 1-5 quality scores manually.

**Methodology notes:**
- All testing via Python SDKs (not CLI). Internal friction log shows CLI-vs-SDK gaps — if SDK is smoother than CLI, that reinforces a known pattern.
- Quality scores are manual judgment, not automated.
- Cost data only available from Firecrawl response metadata; competitors mostly don't report cost in response.
- Latency is wall-clock, measured by a `timed_call()` wrapper around each SDK call.

**Quality rubric (1-5):**
- 5 = every field present, accurate, production-ready
- 4 = minor imperfections, usable as-is
- 3 = directionally right but needs cleanup
- 2 = mostly wrong or incomplete
- 1 = useless, empty, or wrong content served as success

**Failure behavior:**
- Loud = clear error, appropriate status, no credit charged
- Silent = 200 OK with wrong/partial/empty content, or credit charged on failure
- N/A = succeeded, no failure to evaluate

---

## Step 1: Search

**Target:** Find pricing pages for each of the 5 competitors via search query.
**Competitors with this primitive:** Firecrawl, Spider, Exa.

| Dimension | Firecrawl | Spider | Crawl4AI | ScrapeGraphAI | Apify | Exa |
|---|---|---|---|---|---|---|
| Endpoint used | /search | spider.search() | N/A | N/A | N/A (partial via actors) | exa.search_and_contents() |
| Has equivalent? | Yes | Yes | No | No | Partial | Yes |
| Output quality (1-5) | | | N/A | N/A | N/A | |
| Latency (first query) | | | N/A | N/A | N/A | |
| Cost | per credit | not reported | N/A | N/A | N/A | not reported |
| Failure behavior | | | N/A | N/A | N/A | |
| Notes | | | | | | |

### Reflections
*(to be filled in as we go)*

### Verbatim observations
*(direct quotes / reactions, captured as you share them)*

---

## Step 2: Map

**Target:** Discover all pages on each competitor's site (5 different sites mapped).
**Competitors with this primitive:** Firecrawl only.

| Dimension | Firecrawl | Spider | Crawl4AI | ScrapeGraphAI | Apify | Exa |
|---|---|---|---|---|---|---|
| Endpoint used | /map | N/A | N/A | N/A | N/A | N/A |
| Has equivalent? | Yes | No | No | No | No | No |
| Output quality (1-5) | | N/A | N/A | N/A | N/A | N/A |
| URLs returned | | N/A | N/A | N/A | N/A | N/A |
| Cost | per credit | N/A | N/A | N/A | N/A | N/A |
| Failure behavior | | N/A | N/A | N/A | N/A | N/A |
| Notes | | | | | | |

### Reflections
*(to be filled in as we go)*

### Verbatim observations
*(direct quotes / reactions, captured as you share them)*

---

## Step 3: Scrape (Markdown)

**Target:** Extract pricing page as clean markdown — `https://spider.cloud/pricing`.
**Competitors with this primitive:** Firecrawl, Spider, Crawl4AI, ScrapeGraphAI, Apify.

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

### Reflections
*(to be filled in as we go)*

### Verbatim observations
*(direct quotes / reactions, captured as you share them)*

---

## Step 4: Scrape (JSON schema)

**Target:** Structured extraction of pricing plans from `https://spider.cloud/pricing` — schema includes plan_name, price_monthly, credits_or_pages, rate_limit, key_features.
**Competitors with this primitive:** Firecrawl (native), ScrapeGraphAI (prompt-based). Others N/A.

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

### Reflections
*(to be filled in as we go)*

### Verbatim observations
*(direct quotes / reactions, captured as you share them)*

---

## Step 5: Crawl

**Target:** Crawl `https://spider.cloud/docs` with a 20-page limit, return markdown.
**Competitors with this primitive:** Firecrawl, Spider, Crawl4AI (manual link-follow), Apify.

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

### Reflections
*(to be filled in as we go)*

### Verbatim observations
*(direct quotes / reactions, captured as you share them)*

---

## Step 6: Agent

**Target:** Autonomous research — "Find the complete pricing tiers, per-endpoint costs, and rate limits for Spider.cloud."
**Competitors with this primitive:** Firecrawl only.

| Dimension | Firecrawl | Spider | Crawl4AI | ScrapeGraphAI | Apify | Exa |
|---|---|---|---|---|---|---|
| Endpoint used | /agent (spark-1-mini) | N/A | N/A | N/A | N/A | N/A |
| Has equivalent? | Yes | No | No | No | No | No |
| Output quality (1-5) | | N/A | N/A | N/A | N/A | N/A |
| Latency (incl. polling) | | N/A | N/A | N/A | N/A | N/A |
| Cost | per agent credit | N/A | N/A | N/A | N/A | N/A |
| Failure behavior | | N/A | N/A | N/A | N/A | N/A |
| Notes | | | | | | |

### Reflections
*(to be filled in as we go)*

### Verbatim observations
*(direct quotes / reactions, captured as you share them)*

---

## Step 7: Interact

**Target:** `https://apify.com/pricing` (monthly/annual toggle). Two-step flow: scrape → /interact with scrape_id.
**Competitors with this primitive:** Firecrawl only.

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

### Reflections
*(to be filled in as we go)*

### Verbatim observations
*(direct quotes / reactions, captured as you share them)*

---

## Step 8: Parse

**Target:** Download a PDF from a competitor site, parse with Firecrawl `/parse` (multipart/form-data) for both markdown and JSON schema extraction.
**Competitors with this primitive:** Firecrawl. ScrapeGraphAI partial (URL-only), Apify partial (actor required), others N/A.

| Dimension | Firecrawl | Spider | Crawl4AI | ScrapeGraphAI | Apify | Exa |
|---|---|---|---|---|---|---|
| Endpoint used | /parse (multipart/form-data) | N/A | N/A | N/A (URL-only) | N/A (actor required) | N/A |
| Has equivalent? | Yes | No | No | Partial (URL only) | Partial (actor required) | No |
| PDF source | | N/A | N/A | N/A | N/A | N/A |
| Markdown quality (1-5) | | N/A | N/A | N/A | N/A | N/A |
| JSON schema quality (1-5) | | N/A | N/A | N/A | N/A | N/A |
| Latency (markdown) | | N/A | N/A | N/A | N/A | N/A |
| Latency (JSON schema) | | N/A | N/A | N/A | N/A | N/A |
| Content-Type | multipart/form-data | N/A | N/A | N/A | N/A | N/A |
| Failure behavior | | N/A | N/A | N/A | N/A | N/A |
| Notes | | | | | | |

### Reflections
*(to be filled in as we go)*

### Verbatim observations
*(direct quotes / reactions, captured as you share them)*

---

## Cross-cutting themes

*(populated as patterns emerge across steps)*

### Firecrawl unique primitives (no competitor equivalent)
- /map — site URL discovery
- /agent — autonomous research
- /interact — browser interaction after scrape
- /parse — local file upload + structured extraction

### Where Firecrawl wins
*(quality, latency, DX, cost — fill in as we go)*

### Where competitors match or exceed
*(fill in as we go)*

### Surprises
*(unexpected findings worth surfacing in the interview)*

### SDK vs CLI observations
*(per the methodology note — capture any place SDK was clearly better/worse than CLI would be)*

### Failure-mode patterns
*(silent failures, charged-on-failure, error message quality)*

---

## Synthesis prompt for the next Claude instance

When you paste this file into a fresh Claude conversation, prompt it with something like:

> I just ran a head-to-head competitive test of Firecrawl vs. five competitors across 8 primitives. The full results, per-step reflections, and cross-cutting themes are below. Help me synthesize this into:
> 1. A 3-bullet executive summary I can lead the CTO interview with
> 2. The 2-3 strongest "Firecrawl differentiator" claims, each backed by a specific data point from the tests
> 3. The 1-2 weakest spots competitors revealed — and how I'd respond if asked
> 4. One surprise or non-obvious finding the CTO is unlikely to already know
>
> [paste this whole file]
