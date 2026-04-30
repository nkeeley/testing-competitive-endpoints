"""Crawl4AI runner — wraps AsyncWebCrawler in a sync interface.

All async calls are wrapped in `asyncio.wait_for(..., timeout=DEFAULT_TIMEOUT)`
so a hung page render (e.g. heavy JS, anti-bot page that never resolves) will
fail loudly with TimeoutError instead of blocking the test suite.
"""
import asyncio
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import OPENAI_API_KEY

DEFAULT_TIMEOUT = 60  # seconds — adjust if a step's runtime legitimately needs more


def _run_with_timeout(coro_factory, timeout=DEFAULT_TIMEOUT):
    """Run a 0-arg coroutine factory under a wall-clock timeout."""
    return asyncio.run(asyncio.wait_for(coro_factory(), timeout=timeout))


def scrape_markdown(url):
    async def _run():
        from crawl4ai import AsyncWebCrawler, CrawlerRunConfig
        async with AsyncWebCrawler() as crawler:
            result = await crawler.arun(url=url, config=CrawlerRunConfig())
            return {
                "url": url,
                "markdown": result.markdown,
                "success": result.success,
            }
    return _run_with_timeout(_run)


def crawl(start_url, limit=20):
    """Crawl by following links — Crawl4AI doesn't have a native site crawler,
    so this runs a single deep crawl with link following enabled."""
    async def _run():
        from crawl4ai import AsyncWebCrawler, CrawlerRunConfig
        results = []
        visited = set()
        queue = [start_url]

        async with AsyncWebCrawler() as crawler:
            while queue and len(results) < limit:
                url = queue.pop(0)
                if url in visited:
                    continue
                visited.add(url)
                result = await crawler.arun(url=url, config=CrawlerRunConfig())
                results.append({
                    "url": url,
                    "markdown": result.markdown,
                    "success": result.success,
                })
                if result.links and len(results) < limit:
                    base = start_url.split("/")[2]
                    for link in (result.links.get("internal") or []):
                        href = link.get("href", "")
                        if href and base in href and href not in visited:
                            queue.append(href)
        return results
    return _run_with_timeout(_run, timeout=DEFAULT_TIMEOUT * 4)  # crawl can be longer


def url_seeding(url, limit=100):
    """Crawl4AI map equivalent — discovers URLs from sitemap/robots.txt + page links.
    VERIFY: Crawl4AI has a URL Seeder feature in newer versions. Trying to import it,
    falling back to scraping the URL and returning extracted links.
    """
    async def _run():
        try:
            # Newer Crawl4AI versions
            from crawl4ai import AsyncUrlSeeder, SeedingConfig
            async with AsyncUrlSeeder() as seeder:
                config = SeedingConfig(source="sitemap", max_urls=limit)
                seeded = await seeder.urls(url, config)
                return {"urls": seeded, "method": "AsyncUrlSeeder"}
        except ImportError:
            pass
        # Fallback: extract links from the page
        from crawl4ai import AsyncWebCrawler, CrawlerRunConfig
        async with AsyncWebCrawler() as crawler:
            result = await crawler.arun(url=url, config=CrawlerRunConfig())
            internal = (result.links or {}).get("internal", []) if result.links else []
            external = (result.links or {}).get("external", []) if result.links else []
            return {
                "urls": [l.get("href") for l in internal[:limit] if l.get("href")],
                "external_urls": [l.get("href") for l in external[:limit] if l.get("href")],
                "method": "fallback_link_extraction",
            }
    return _run_with_timeout(_run)


def scrape_json(url, schema):
    """Crawl4AI structured outputs via LLMExtractionStrategy.
    Requires OPENAI_API_KEY in env (uses gpt-4o-mini by default).
    """
    async def _run():
        from crawl4ai import AsyncWebCrawler, CrawlerRunConfig
        from crawl4ai.extraction_strategy import LLMExtractionStrategy
        if not OPENAI_API_KEY:
            return {"error": "OPENAI_API_KEY not set — Crawl4AI structured outputs require an LLM"}
        strategy = LLMExtractionStrategy(
            provider="openai/gpt-4o-mini",
            api_token=OPENAI_API_KEY,
            schema=schema,
            extraction_type="schema",
            instruction="Extract pricing plans from this page following the schema.",
        )
        config = CrawlerRunConfig(extraction_strategy=strategy)
        async with AsyncWebCrawler() as crawler:
            result = await crawler.arun(url=url, config=config)
            try:
                extracted = json.loads(result.extracted_content) if result.extracted_content else None
            except Exception:
                extracted = result.extracted_content
            return {
                "url": url,
                "extracted": extracted,
                "success": result.success,
            }
    return _run_with_timeout(_run)


def interact(url, js_code=None, wait_for=None):
    """Crawl4AI browser interaction via js_code parameter.
    User-facing 'DSL' is JavaScript executed in the page context.
    """
    async def _run():
        from crawl4ai import AsyncWebCrawler, CrawlerRunConfig
        config_kwargs = {}
        if js_code:
            config_kwargs["js_code"] = js_code if isinstance(js_code, list) else [js_code]
        if wait_for:
            config_kwargs["wait_for"] = wait_for
        config = CrawlerRunConfig(**config_kwargs)
        async with AsyncWebCrawler() as crawler:
            result = await crawler.arun(url=url, config=config)
            return {
                "url": url,
                "markdown": result.markdown,
                "success": result.success,
            }
    return _run_with_timeout(_run)


def parse_pdf(pdf_path_or_url):
    """Crawl4AI PDF parsing.
    VERIFY: Crawl4AI's AsyncWebCrawler may handle PDF URLs natively. If pdf_path_or_url
    is a local file, prefix with file:// or pass through to a PDF lib.
    """
    async def _run():
        from crawl4ai import AsyncWebCrawler, CrawlerRunConfig
        url = pdf_path_or_url
        if os.path.isfile(pdf_path_or_url):
            url = "file://" + os.path.abspath(pdf_path_or_url)
        async with AsyncWebCrawler() as crawler:
            result = await crawler.arun(url=url, config=CrawlerRunConfig())
            return {
                "url": url,
                "markdown": result.markdown,
                "success": result.success,
            }
    return _run_with_timeout(_run)
