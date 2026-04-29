"""ScrapeGraphAI runner — uses requests against REST API directly."""
import os
import sys
import requests

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import SCRAPEGRAPHAI_API_KEY

BASE_URL = "https://api.scrapegraphai.com/v1"


def _headers():
    return {
        "Authorization": f"Bearer {SCRAPEGRAPHAI_API_KEY}",
        "Content-Type": "application/json",
    }


def smartscraper(url, prompt):
    resp = requests.post(
        f"{BASE_URL}/smartscraper",
        headers=_headers(),
        json={"url": url, "prompt": prompt},
    )
    resp.raise_for_status()
    return resp.json()
