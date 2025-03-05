import os
import sys
import psutil
import asyncio
import requests
from xml.etree import ElementTree
from typing import List
from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig, CacheMode


__location__ = os.path.dirname(os.path.abspath(__file__))
__output__ = os.path.join(__location__, "output")

parent_dir = os.path.dirname(os.path.dirname(__file__))
sys.path.append(parent_dir)


def get_pydantic_ai_docs_url():
    sitemap_url = "https://ai.pydantic.dev/sitemap.xml"

    try:
        response = requests.get(sitemap_url)
        response.raise_for_status()

        root = ElementTree.fromstring(response.content)

        namespace = {"ns": "http://www.sitemaps.org/schemas/sitemap/0.9"}
        urls = [loc.text for loc in root.findall(".//ns:loc", namespace)]
        return urls
    except Exception as e:
        print(f"Error fetching sitemap: {e}")
        return []
    
    

async def crawl_parallel(urls: List[str], max_concurrent: int=3):
    peak_memory = 0
    process = psutil.Process(os.getpid())

    def log_memory(prefix: str=""):
        nonlocal peak_memory
        current_mem = process.memory_info().rss
        if current_mem > peak_memory:
            peak_memory = current_mem
        print(f"{prefix} Current Memory: {current_mem // (1024 * 1024)} MB, Peak: {peak_memory // (1024 * 1024)} MB")

    
    # browser config
    browser = BrowserConfig(
        headless=True, 
        verbose=False,
        extra_args=["--disable-gpu", "--disable-dev-shm-usage", "--no-sandbox"]
    )

    crawl_config =CrawlerRunConfig(cache_mode=CacheMode.BYPASS)

    crawler = AsyncWebCrawler(config=browser)
    await crawler.start()

    try:
        success_count = 0
        fail_count = 0
        for i in range(0, len(urls), max_concurrent):
            batch = urls[i: i + max_concurrent]
            tasks = []

            for j, url in enumerate(batch):
                session_id = f"parallel_session {i + j}"
                task = crawler.arun(url=url, config=crawl_config, session_id=session_id)
                tasks.append(task)
            
            # Log memory usage before and after batch
            log_memory(prefix=f"Before batch {i/ max_concurrent + 1}: ")
            
            # Run tasks in parallel
            result = await asyncio.gather(*tasks, return_exceptions=True)

            log_memory(prefix=f"After batch {i/ max_concurrent + 1}: ")

            # Evaluate results
            for url, result in zip(batch, result):
                if isinstance(result, Exception):
                    print(f"Failed to crawl {url}: {result}")
                    fail_count += 1
                elif result.success:
                    print(f"Crawled {url}: {result}")
                    success_count += 1
                else:
                    fail_count += 1
        
        print(f"\n Summary:")
        print(f"   - Successfully crawled: {success_count}")
        print(f"   - Failed to crawl: {fail_count}")

    except Exception as e:
        print(e)


    finally:
        print("\n Closing Crawler...")
        await crawler.close()
        # Final memory usage
        log_memory(prefix="Final:  ")
        print(f"\n Peak memory usage: {peak_memory // (1024 * 1024)}")


            
async def main():
    urls = get_pydantic_ai_docs_url()
    if urls:
        print(f"Found {len(urls)} URLS to crawl")
        await crawl_parallel(urls, max_concurrent=53)
    else:
        print("No URLs found")


if __name__ == "__main__":
    asyncio.run(main())