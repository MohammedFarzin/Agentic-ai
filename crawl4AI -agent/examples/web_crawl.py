import asyncio
from crawl4ai import *

async def main():
    async with AsyncWebCrawler() as crawler:
        result = await crawler.arun(
            url="https://www.geeksforgeeks.org/check-if-two-given-strings-are-isomorphic-to-each-other/",
        )
        print(result.markdown)

if __name__ == "__main__":
    asyncio.run(main())