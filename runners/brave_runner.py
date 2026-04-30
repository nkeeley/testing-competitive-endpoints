"""Brave Search runner — search-only, used in step 1.

Verified against api-dashboard.search.brave.com/documentation/quickstart:
  - URL: https://api.search.brave.com/res/v1/web/search
  - Auth header: X-Subscription-Token
  - Query param: q
  - Recommended headers: Accept, Accept-Encoding

Returns a flattened structure (just the web.results array) so the step output
isn't dominated by Brave's response metadata (mixed/videos/news/locations etc.).
The full raw response is preserved server-side; this is a display-layer cleanup.
"""
import os
import sys
import requests

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import BRAVE_API_KEY

BASE_URL = "https://api.search.brave.com/res/v1"


def _headers():
    return {
        "X-Subscription-Token": BRAVE_API_KEY,
        "Accept": "application/json",
        "Accept-Encoding": "gzip",
    }


def search(query, limit=5):
    """Standard web search. Returns a flattened structure with the actual
    web results, not the full JSON envelope (which is metadata-heavy)."""
    resp = requests.get(
        f"{BASE_URL}/web/search",
        headers=_headers(),
        params={"q": query, "count": limit},
    )
    resp.raise_for_status()
    data = resp.json()

    web_results = (data.get("web") or {}).get("results", []) or []
    flattened = {
        "query_echo": (data.get("query") or {}).get("original"),
        "results_count": len(web_results),
        "results": [
            {
                "title": r.get("title"),
                "url": r.get("url"),
                "description": r.get("description"),
                "age": r.get("age"),
            }
            for r in web_results[:limit]
        ],
    }
    return flattened
