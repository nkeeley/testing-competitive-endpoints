"""Apify runner — wraps apify-client SDK via website-content-crawler actor."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import APIFY_API_TOKEN


def _client():
    from apify_client import ApifyClient
    return ApifyClient(APIFY_API_TOKEN)


def scrape_url(url):
    client = _client()
    run = client.actor("apify/website-content-crawler").call(
        run_input={"startUrls": [{"url": url}], "maxCrawlPages": 1}
    )
    return list(client.dataset(run["defaultDatasetId"]).iterate_items())


def crawl(url, limit=20):
    client = _client()
    run = client.actor("apify/website-content-crawler").call(
        run_input={"startUrls": [{"url": url}], "maxCrawlPages": limit}
    )
    return list(client.dataset(run["defaultDatasetId"]).iterate_items())
