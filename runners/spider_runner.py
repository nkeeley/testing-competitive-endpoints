"""Spider runner — wraps spider-client SDK."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import SPIDER_API_KEY


def _client():
    from spider import Spider
    return Spider(api_key=SPIDER_API_KEY)


def search(query, limit=5):
    return _client().search(query, params={"limit": limit, "return_format": "markdown"})


def scrape_markdown(url):
    return _client().scrape_url(url, params={"return_format": "markdown"})


def crawl(url, limit=20):
    return _client().crawl_url(url, params={"limit": limit, "return_format": "markdown"})
