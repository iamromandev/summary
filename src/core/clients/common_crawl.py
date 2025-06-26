
import aiohttp
from bs4 import BeautifulSoup

COMMON_CRAWL_INDEXES = [
    "CC-MAIN-2024-10",  # Replace with the latest
]

class CommonCrawlAgent:
    def __init__(self):
        self.index_base = "http://index.commoncrawl.org"

    async def search(self, query: str, limit: int = 5) -> list[dict]:
        results = []
        async with aiohttp.ClientSession() as session:
            for cc_index in COMMON_CRAWL_INDEXES:
                url = f"{self.index_base}/{cc_index}-index?url={query}&output=json"
                async with session.get(url) as resp:
                    if resp.status != 200:
                        continue
                    async for line in resp.content:
                        if len(results) >= limit:
                            break
                        results.append(eval(line.decode()))
        return results

    async def fetch_html(self, warc_path: str, offset: int, length: int) -> str:
        warc_url = f"https://commoncrawl.s3.amazonaws.com/{warc_path}"
        headers = {'Range': f"bytes={offset}-{offset+length}"}
        async with aiohttp.ClientSession() as session, session.get(warc_url, headers=headers) as resp:
                if resp.status != 206:
                    return ""
                content = await resp.read()
                return content.decode(errors="ignore")

    def extract_text(self, html: str) -> str:
        soup = BeautifulSoup(html, "html.parser")
        return soup.get_text(strip=True)

    async def run(self, query: str):
        results = await self.search(query)
        print(f"Found {len(results)} result(s)")
        for r in results:
            raw = await self.fetch_html(r["filename"], int(r["offset"]), int(r["length"]))
            text = self.extract_text(raw)
            print("="*80)
            print(f"URL: {r['url']}")
            print(f"Extract: {text[:500]}...")  # print first 500 chars