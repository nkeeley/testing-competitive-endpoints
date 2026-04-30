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


def smartscraper(url, prompt):
    """Single-page LLM extraction. Used in step 3+.
    NOTE: v1 URL/field names not yet verified against current docs — may need
    updating to v2 shape. Address when step 3 runs.
    """
    resp = requests.post(
        f"{V1_BASE_URL}/smartscraper",
        headers=_headers(),
        json={"website_url": url, "user_prompt": prompt},
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
