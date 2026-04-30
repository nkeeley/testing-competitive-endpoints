"""Brave Search runner — search-only, used in step 1.
Brave Search API: https://api.search.brave.com/res/v1/web/search
Auth: X-Subscription-Token header.
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
    }


def search(query, limit=5):
    """Standard web search."""
    resp = requests.get(
        f"{BASE_URL}/web/search",
        headers=_headers(),
        params={"q": query, "count": limit},
    )
    resp.raise_for_status()
    return resp.json()
