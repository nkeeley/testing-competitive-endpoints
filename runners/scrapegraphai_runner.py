"""ScrapeGraphAI runner — uses requests against REST API directly.

Confirmed endpoints (per docs.scrapegraphai.com):
  - search: POST https://v2-api.scrapegraphai.com/api/search
            body: {query, numResults, prompt?, schema?}
  - smartscraper / smartcrawler: v1 URL — not yet doc-verified, will fix
    when step 3/5 runs surface issues.

Auth: SGAI-APIKEY header (not Bearer).
"""
import os
import sys
import requests

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import SCRAPEGRAPHAI_API_KEY

# v2 API base for endpoints we've confirmed against docs
V2_BASE_URL = "https://v2-api.scrapegraphai.com/api"

# v1 API base — used by smartscraper / smartcrawler. May need updating; docs
# pending verification on those endpoints.
V1_BASE_URL = "https://api.scrapegraphai.com/v1"


def _headers():
    return {
        "SGAI-APIKEY": SCRAPEGRAPHAI_API_KEY,
        "Content-Type": "application/json",
    }


def smartscraper(url, prompt, output_schema=None):
    """Single-page LLM extraction.

    Verified against docs.scrapegraphai.com/services/smartscraper:
      - Endpoint: POST https://api.scrapegraphai.com/v1/smartscraper
      - Body: {website_url, user_prompt, output_schema?}
      - output_schema accepts Pydantic-style JSON schema dict (or model_json_schema())

    For fair comparison with Firecrawl's schema-enforced extraction, callers
    should pass output_schema, not just a prompt.
    """
    body = {"website_url": url, "user_prompt": prompt}
    if output_schema is not None:
        body["output_schema"] = output_schema
    resp = requests.post(
        f"{V1_BASE_URL}/smartscraper",
        headers=_headers(),
        json=body,
    )
    resp.raise_for_status()
    return resp.json()


def search(query, num_results=5):
    """Search — verified against docs.scrapegraphai.com/services/search."""
    resp = requests.post(
        f"{V2_BASE_URL}/search",
        headers=_headers(),
        json={"query": query, "numResults": num_results},
    )
    resp.raise_for_status()
    return resp.json()


def scrape(url, formats):
    """Verified against docs.scrapegraphai.com/services/scrape.
    Drop-in equivalent to Firecrawl's /scrape with formats array.
    formats: list of dicts like [{"type": "markdown"}] or
             [{"type": "json", "prompt": "...", "schema": {...}}]
    """
    resp = requests.post(
        f"{V2_BASE_URL}/scrape",
        headers=_headers(),
        json={"url": url, "formats": formats},
    )
    resp.raise_for_status()
    return resp.json()


def scrape_json(url, schema, prompt="Extract structured data following the schema"):
    """Schema-based extraction via /scrape with formats: [{type: 'json', ...}].
    Most direct apples-to-apples comparison with Firecrawl /scrape JSON schema.
    Schema enforcement is LLM-based, not server-enforced (per docs review).
    """
    return scrape(url, formats=[{"type": "json", "prompt": prompt, "schema": schema}])


def crawl(url, prompt="Extract all content as markdown", limit=20):
    """Crawl via SGAI's smartcrawler endpoint.
    NOTE: endpoint/fields not yet verified against current docs.
    Address when step 5 runs.
    """
    resp = requests.post(
        f"{V1_BASE_URL}/smartcrawler",
        headers=_headers(),
        json={"url": url, "prompt": prompt, "depth": 2, "max_pages": limit},
    )
    resp.raise_for_status()
    return resp.json()
