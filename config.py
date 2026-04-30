import os
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env"))

FIRECRAWL_API_KEY = os.environ.get("FIRECRAWL_API_KEY", "")
SPIDER_API_KEY = os.environ.get("SPIDER_API_KEY", "")
EXA_API_KEY = os.environ.get("EXA_API_KEY", "")
APIFY_API_TOKEN = os.environ.get("APIFY_API_TOKEN", "")
SCRAPEGRAPHAI_API_KEY = os.environ.get("SCRAPEGRAPHAI_API_KEY", "")
BRAVE_API_KEY = os.environ.get("BRAVE_API_KEY", "")
# OPENAI_API_KEY needed for Crawl4AI's LLM extraction (step 4)
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "")

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

# --- URL accessors ---
# Use these throughout step scripts instead of hardcoding URLs.

def base_url(competitor_key):
    return COMPETITORS[competitor_key]["base_url"]

def docs_url(competitor_key):
    return COMPETITORS[competitor_key]["docs_url"]

def pricing_url(competitor_key):
    return COMPETITORS[competitor_key]["pricing_url"]

def display_name(competitor_key):
    return COMPETITORS[competitor_key]["name"]

ALL_BASE_URLS = [c["base_url"] for c in COMPETITORS.values()]
ALL_DOCS_URLS = [c["docs_url"] for c in COMPETITORS.values()]
ALL_PRICING_URLS = [c["pricing_url"] for c in COMPETITORS.values()]

# Primary head-to-head target — most steps scrape/crawl this competitor's site
PRIMARY_COMPETITOR_KEY = "spider"
PRIMARY_BASE_URL = base_url(PRIMARY_COMPETITOR_KEY)
PRIMARY_DOCS_URL = docs_url(PRIMARY_COMPETITOR_KEY)
PRIMARY_PRICING_URL = pricing_url(PRIMARY_COMPETITOR_KEY)
PRIMARY_DISPLAY_NAME = display_name(PRIMARY_COMPETITOR_KEY)

# Step 7 interact target — picked because it has a monthly/annual pricing toggle
INTERACT_TARGET_KEY = "apify"
INTERACT_TARGET_URL = pricing_url(INTERACT_TARGET_KEY)

# Step 8 parse target — PDFs to try downloading from competitor sites (first success wins)
PDF_CANDIDATES = [
    ("Apify whitepaper", "https://apify.com/pdf/apify-whitepaper.pdf"),
    ("Spider docs PDF", "https://spider.cloud/spider-documentation.pdf"),
    ("W3C sample PDF (fallback)", "https://www.w3.org/WAI/WCAG21/Techniques/pdf/pdf-sample.pdf"),
]
