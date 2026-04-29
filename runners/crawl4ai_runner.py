"""Crawl4AI runner — wraps AsyncWebCrawler in a sync interface."""
import asyncio
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


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
    return asyncio.run(_run())


def crawl(start_url, limit=20):
    """Crawl by following links — Crawl4AI doesn't have a native site crawler,
    so this runs a single deep crawl with link following enabled."""
    async def _run():
        from crawl4ai import AsyncWebCrawler, CrawlerRunConfig, CrawlResult
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
                # Follow same-domain links
                if result.links and len(results) < limit:
                    base = start_url.split("/")[2]
                    for link in (result.links.get("internal") or []):
                        href = link.get("href", "")
                        if href and base in href and href not in visited:
                            queue.append(href)
        return results
    return asyncio.run(_run())
