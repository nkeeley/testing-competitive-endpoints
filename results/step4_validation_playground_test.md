# Step 4 validation — playground test (manual)

**Date planned:** 2026-04-30
**Goal:** Validate yesterday's Step 4 API findings using each competitor's hosted playground UI, with a focus on **dropdown-gated content** (a harder test than the static page-top extraction we ran via API).

## Test setup

**Target URL:** `https://spider.cloud/pricing`

**What's being measured:**
- Did the playground accept the schema (drop-in compatibility check)?
- Did it find pricing **hidden under dropdowns/accordions/expandable sections** (interaction + JS render check)?
- What's the schema fidelity of the output (shape, completeness, drift)?
- Latency / credits / errors per provider?

## The schema (paste into every playground that takes one)

```json
{
  "type": "object",
  "properties": {
    "plans": {
      "type": "array",
      "description": "All pricing tiers visible on the page, including any hidden under dropdowns or expandable sections",
      "items": {
        "type": "object",
        "properties": {
          "plan_name": {
            "type": "string",
            "description": "Name of the pricing tier"
          },
          "price_monthly": {
            "type": "string",
            "description": "Monthly price in USD or pricing description (e.g. '$1/GB', 'Custom', 'Contact us')"
          },
          "credits_or_pages": {
            "type": "string",
            "description": "Included credits, page limits, or usage allotment"
          },
          "rate_limit": {
            "type": "string",
            "description": "Rate limit (e.g. '10K RPM')"
          },
          "key_features": {
            "type": "array",
            "items": {"type": "string"},
            "description": "Notable features or inclusions of this tier"
          }
        },
        "required": ["plan_name"]
      }
    }
  },
  "required": ["plans"]
}
```

**Why this schema, not yesterday's `PRICING_SCHEMA`:**
- No union types (`["string", "null"]`) — Exa rejects those
- `description` fields on every property — helps LLM-based extractors disambiguate
- `plan_name` required — prevents empty-object hallucinations
- `plans` and `plan_name` are the only required fields — keeps the schema permissive

## The user prompt / instruction (pair with the schema)

```
Extract every pricing plan visible on this page, including any tiers that may be hidden behind dropdowns, accordions, or expandable sections. For each plan, capture the plan name, monthly price (or pricing description if not a fixed monthly fee), included credits or page allotment, rate limits, and a list of key features. Do not skip plans that require clicking or expanding a section to reveal.
```

## Per-provider test plan

### 1. Firecrawl
- **Playground:** https://www.firecrawl.dev/playground
- **What to do:** Set URL → spider.cloud/pricing. Set format to "JSON" with the schema above. Submit.
- **Watch for:** Does it find dropdown-gated plans? How many plans returned? Schema-conformant output?
- **Yesterday's API result:** 2 plans found ("Pay as you go", "Volume Pricing"), 3.3s, 5 credits. Does the playground match or exceed?

### 2. ScrapeGraphAI
- **Playground:** https://dashboard.scrapegraphai.com (their dashboard has scrape/smartscraper interactive surfaces)
- **What to do:** Use the `/scrape` service (NOT smartscraper) with formats: [{type: "json", schema: ...}]. Paste schema and prompt.
- **Watch for:** Cache behavior — if you submit twice and get instant identical results both times, that's the same caching we saw via API. Schema fidelity. Plan count.
- **Yesterday's API result:** 1 plan found, cached on second call (id stayed identical, latency dropped 70%).

### 3. Crawl4AI
- **Playground:** https://crawl4ai.com/playground (verify URL when you go — they may host one or it may be local-only)
- **What to do:** If they have a hosted playground, configure LLMExtractionStrategy with schema. They'll likely require you to bring your own LLM API key.
- **Watch for:** Output shape — yesterday Crawl4AI returned `[{plans: [...], error: false}]` (array-wrapped). Does the playground also array-wrap, or is that a CLI/SDK artifact?
- **Yesterday's API result:** 1 plan with thorough features, but wrapped in an array at top level (schema fidelity broken).

### 4. Exa
- **Playground:** https://exa.ai (look for a "Try it" or playground link in nav, or try https://exa.ai/playground)
- **What to do:** `/contents` endpoint with summary.schema. Paste the schema.
- **Watch for:** Whether it actually populates the summary field this time. Yesterday it returned 200 OK with empty `summary` — silent failure. Does the playground UI surface this any more obviously than the API does?
- **Yesterday's API result:** 30s latency, 0 plans, **silent failure** (empty summary, no error).

### 5. Spider — SKIP (no JSON schema extraction)
- **Why skip:** Confirmed via docs and via Step 4 API run — Spider has no JSON schema parameter on any endpoint. They have `css_extraction_map` (selector-based) but that's not equivalent.
- **If you want to test anyway:** Use their playground with css_extraction_map and CSS selectors targeting `.pricing-tier` or similar. Note this is a fundamentally different test (selectors require knowing the page structure; schema doesn't).

### 6. Apify — SKIP (no schema-based actor primitive)
- **Why skip:** Standard actors (website-content-crawler) don't accept JSON schemas. Custom JS extraction in apify/web-scraper is selector/code-based, not schema-based.

### 7. Brave — SKIP (search-only, no scrape)

## Results table to fill in tomorrow

| Provider | Schema accepted? | Plans found | Hidden content captured? | Schema fidelity | Latency | Cost | Notes |
|---|---|---|---|---|---|---|---|
| Firecrawl |  |  |  |  |  |  |  |
| SGAI |  |  |  |  |  |  |  |
| Crawl4AI |  |  |  |  |  |  |  |
| Exa |  |  |  |  |  |  |  |

## Things to specifically look for

1. **Did the schema get accepted as-is?** If a playground rejected the schema (Exa rejected union types in our API run), that's a DX friction point — schemas don't transfer between providers.

2. **Does the playground expose interaction options?** Firecrawl's playground has waitFor/actions; SGAI may or may not; Crawl4AI may or may not; Exa won't. **Discoverability of "you need to click X to reveal Y" is its own DX dimension.**

3. **Did each provider find dropdown-gated plans?** This is the headline result. If Firecrawl finds them and others don't, that's a real differentiator on JS-render / interaction.

4. **For SGAI specifically — caching:** Submit the same query twice. If the second response is instantly identical, they cached. Note as DX observation.

5. **For Exa specifically — silent failure:** If the playground shows you an empty result without flagging it, that's reproduction of yesterday's worst-finding. If the playground UI flags it ("no content extracted"), that's a partial recovery.

## When done

Paste your filled-in table back to Claude. We'll fold it into the existing Step 4 reflections in `results/summary.md` as a second data point. Goal is to either (a) reinforce yesterday's findings — Firecrawl wins on completeness and consistency; LLM-based competitors each have a distinct failure mode — or (b) revise if the playground UIs reveal something the API runs missed.
