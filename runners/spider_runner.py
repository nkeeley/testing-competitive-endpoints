"""Spider runner — wraps spider-client SDK + REST fallback for endpoints
the SDK may not expose (links, transform, browser interactions).
"""
import os
import sys
import requests

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import SPIDER_API_KEY

BASE_URL = "https://api.spider.cloud"


def _client():
    from spider import Spider
    return Spider(api_key=SPIDER_API_KEY)


def _rest_headers():
    return {
        "Authorization": f"Bearer {SPIDER_API_KEY}",
        "Content-Type": "application/json",
    }


def search(query, limit=5):
    return _client().search(query, params={"limit": limit, "return_format": "markdown"})


def scrape_markdown(url):
    return _client().scrape_url(url, params={"return_format": "markdown"})


def crawl(url, limit=20):
    return _client().crawl_url(url, params={"limit": limit, "return_format": "markdown"})


def links(url, limit=100):
    """Spider's map equivalent — returns links from a URL.
    VERIFY: REST endpoint /v1/links.
    """
    resp = requests.post(
        f"{BASE_URL}/v1/links",
        headers=_rest_headers(),
        json={"url": url, "limit": limit, "return_format": "raw"},
    )
    resp.raise_for_status()
    return resp.json()


def browser_interact(url, actions=None, prompt=None):
    """Spider's interact equivalent — executes browser actions on a URL.
    VERIFY: Spider may use 'actions' parameter on /v1/scrape, or have a
    dedicated /v1/browser endpoint. Trying scrape with actions first.
    """
    payload = {"url": url, "return_format": "markdown"}
    if actions:
        payload["actions"] = actions  # list of action dicts
    if prompt:
        payload["prompt"] = prompt
    resp = requests.post(
        f"{BASE_URL}/v1/scrape",
        headers=_rest_headers(),
        json=payload,
    )
    resp.raise_for_status()
    return resp.json()


def transform(content, return_format="markdown"):
    """Spider's parse equivalent — transforms content (HTML/PDF text) to markdown.
    Note: Spider's transform takes content, not a file upload — different shape from
    Firecrawl /parse which takes multipart file upload. We'd extract text from the PDF
    first and pass it as a string.
    """
    resp = requests.post(
        f"{BASE_URL}/v1/transform",
        headers=_rest_headers(),
        json={"data": [{"html": content}], "return_format": return_format},
    )
    resp.raise_for_status()
    return resp.json()
