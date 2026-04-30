"""ScrapeGraphAI runner — uses requests against REST API directly.
NOTE: Endpoint paths are best-guess based on smartscraper pattern.
Verify against ScrapeGraphAI docs if calls 404.
"""
import os
import sys
import requests

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import SCRAPEGRAPHAI_API_KEY

BASE_URL = "https://api.scrapegraphai.com/v1"


def _headers():
    return {
        "SGAI-APIKEY": SCRAPEGRAPHAI_API_KEY,
        "Content-Type": "application/json",
    }


def smartscraper(url, prompt):
    resp = requests.post(
        f"{BASE_URL}/smartscraper",
        headers=_headers(),
        json={"website_url": url, "user_prompt": prompt},
    )
    resp.raise_for_status()
    return resp.json()


def search(query, num_results=5):
    """Search via SGAI's search endpoint.
    VERIFY: endpoint name guessed as /searchscraper based on smartscraper pattern.
    """
    resp = requests.post(
        f"{BASE_URL}/searchscraper",
        headers=_headers(),
        json={"user_prompt": query, "num_results": num_results},
    )
    resp.raise_for_status()
    return resp.json()


def crawl(url, prompt="Extract all content as markdown", limit=20):
    """Crawl via SGAI's smartcrawler endpoint.
    VERIFY: endpoint name guessed as /smartcrawler.
    """
    resp = requests.post(
        f"{BASE_URL}/smartcrawler",
        headers=_headers(),
        json={"url": url, "prompt": prompt, "depth": 2, "max_pages": limit},
    )
    resp.raise_for_status()
    return resp.json()
