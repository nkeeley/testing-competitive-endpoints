"""Firecrawl runner — wraps all v2 primitives via SDK + requests fallback."""
import os
import sys
import time
import json
import requests

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import FIRECRAWL_API_KEY

BASE_URL = "https://api.firecrawl.dev/v2"


def _headers():
    return {"Authorization": f"Bearer {FIRECRAWL_API_KEY}"}


def _json_headers():
    return {"Authorization": f"Bearer {FIRECRAWL_API_KEY}", "Content-Type": "application/json"}


def _client():
    from firecrawl import Firecrawl
    return Firecrawl(api_key=FIRECRAWL_API_KEY)


def search(query, limit=5):
    return _client().search(query, limit=limit)


def map_url(url):
    return _client().map(url)


def scrape_markdown(url):
    return _client().scrape(url, formats=["markdown"])


def scrape_json(url, schema):
    return _client().scrape(url, formats=[{"type": "json", "schema": schema}])


def crawl(url, limit=20):
    return _client().crawl(url, limit=limit)


def agent(prompt, model="spark-1-mini"):
    resp = requests.post(
        f"{BASE_URL}/agent",
        headers=_json_headers(),
        json={"prompt": prompt, "model": model},
    )
    resp.raise_for_status()
    data = resp.json()

    job_id = data.get("id") or data.get("jobId")
    if not job_id:
        return data

    for _ in range(60):
        time.sleep(5)
        poll = requests.get(f"{BASE_URL}/agent/{job_id}", headers=_json_headers())
        poll.raise_for_status()
        status_data = poll.json()
        if status_data.get("status") in ("completed", "failed", "done"):
            return status_data

    return {"error": "agent polling timed out", "last": status_data}


def scrape_for_interact(url):
    """Returns raw response dict including the scrape id needed for /interact."""
    resp = requests.post(
        f"{BASE_URL}/scrape",
        headers=_json_headers(),
        json={"url": url, "formats": ["markdown"]},
    )
    resp.raise_for_status()
    return resp.json()


def interact(scrape_id, prompt):
    resp = requests.post(
        f"{BASE_URL}/interact",
        headers=_json_headers(),
        json={"scrape_id": scrape_id, "prompt": prompt},
    )
    resp.raise_for_status()
    return resp.json()


def parse_file(filepath, schema=None):
    if schema:
        options = {
            "formats": [{"type": "json", "schema": schema}],
            "onlyMainContent": True,
            "parsers": [{"type": "pdf", "mode": "auto"}],
        }
    else:
        options = {
            "formats": ["markdown"],
            "onlyMainContent": True,
            "parsers": [{"type": "pdf", "mode": "auto"}],
        }
    with open(filepath, "rb") as f:
        resp = requests.post(
            f"{BASE_URL}/parse",
            headers=_headers(),
            files={"file": f},
            data={"options": json.dumps(options)},
        )
    resp.raise_for_status()
    return resp.json()
