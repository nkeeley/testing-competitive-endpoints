import os
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env"))

FIRECRAWL_API_KEY = os.environ.get("FIRECRAWL_API_KEY", "")
SPIDER_API_KEY = os.environ.get("SPIDER_API_KEY", "")
EXA_API_KEY = os.environ.get("EXA_API_KEY", "")
APIFY_API_TOKEN = os.environ.get("APIFY_API_TOKEN", "")
SCRAPEGRAPHAI_API_KEY = os.environ.get("SCRAPEGRAPHAI_API_KEY", "")

COMPETITORS = {
    "spider": {
        "name": "Spider",
        "base_url": "https://spider.cloud",
        "docs_url": "https://spider.cloud/docs",
        "pricing_url": "https://spider.cloud/pricing",
        "has_search": True,
        "has_scrape": True,
        "has_crawl": True,
        "has_agent": False,
        "has_map": False,
        "has_interact": False,
        "has_parse": False,
    },
    "crawl4ai": {
        "name": "Crawl4AI",
        "base_url": "https://crawl4ai.com",
        "docs_url": "https://docs.crawl4ai.com",
        "pricing_url": "https://crawl4ai.com",
        "has_search": False,
        "has_scrape": True,
        "has_crawl": True,
        "has_agent": False,
        "has_map": False,
        "has_interact": False,
        "has_parse": False,
    },
    "scrapegraphai": {
        "name": "ScrapeGraphAI",
        "base_url": "https://scrapegraphai.com",
        "docs_url": "https://docs.scrapegraphai.com",
        "pricing_url": "https://scrapegraphai.com/pricing",
        "has_search": False,
        "has_scrape": True,
        "has_crawl": False,
        "has_agent": False,
        "has_map": False,
        "has_interact": False,
        "has_parse": False,
    },
    "apify": {
        "name": "Apify",
        "base_url": "https://apify.com",
        "docs_url": "https://docs.apify.com",
        "pricing_url": "https://apify.com/pricing",
        "has_search": False,
        "has_scrape": True,
        "has_crawl": True,
        "has_agent": False,
        "has_map": False,
        "has_interact": False,
        "has_parse": False,
    },
    "exa": {
        "name": "Exa",
        "base_url": "https://exa.ai",
        "docs_url": "https://docs.exa.ai",
        "pricing_url": "https://exa.ai/pricing",
        "has_search": True,
        "has_scrape": False,
        "has_crawl": False,
        "has_agent": False,
        "has_map": False,
        "has_interact": False,
        "has_parse": False,
    },
}

# Step 7 interact target — has a monthly/annual pricing toggle
INTERACT_TARGET_URL = "https://apify.com/pricing"
