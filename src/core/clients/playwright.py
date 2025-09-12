# import urllib.parse
# from typing import Annotated, Self
#
# from loguru import logger
# from playwright.async_api import Browser, BrowserContext, Page, Playwright, async_playwright
# from pydantic import Field, HttpUrl, WebsocketUrl
#
# from src.core.constants import PW_USER_AGENT
# from src.core.factory import SingletonMeta
# from src.core.formats import serialize
# from src.core.mixins import BaseMixin
#
#
# class PlaywrightClient(BaseMixin, metaclass=SingletonMeta):
#     _playwright: Annotated[Playwright, Field(...)]
#     _browser: Annotated[Browser, Field(...)]
#     _context: Annotated[BrowserContext, Field(...)]
#     _page: Annotated[Page, Field(...)]
#     _pages: Annotated[dict[HttpUrl, Page], Field(...)]
#     _loaded: Annotated[dict[HttpUrl, bool], Field(...)]
#     _started: Annotated[bool, Field(...)]
#
#     def __init__(
#         self,
#         playwright_url: WebsocketUrl,
#         headless: bool = True,
#         user_agent: str = PW_USER_AGENT
#     ) -> None:
#         super().__init__()
#         self._playwright_url = playwright_url
#         self._headless: bool = headless
#         self._user_agent: str = user_agent
#         self._pages: dict[HttpUrl, Page] = {}
#         self._loaded: dict[HttpUrl, bool] = {}
#         self._started = False
#
#     async def start(self) -> None:
#         if self._started:
#             return
#         self._playwright: Playwright = await async_playwright().start()
#         self._browser: Browser = await self._playwright.chromium.launch(headless=self._headless)
#         self._context: BrowserContext = await self._browser.new_context(user_agent=PW_USER_AGENT)
#         self._started = True
#
#     async def load_page(
#         self, url: HttpUrl, reload: bool = False
#     ) -> Page:
#         logger.debug(f"{self._tag}|load_page(): Loading page for {url}")
#         await self.start()
#
#         if url in self._pages and self._loaded.get(url, False) and not reload:
#             logger.debug(f"{self._tag}|load_page(): Using cached page for {url}")
#             return self._pages[url]
#
#         if url not in self._pages or reload:
#             if url in self._pages:
#                 await self._pages[url].close()
#             self._pages[url] = await self._context.new_page()
#             self._loaded[url] = False
#
#         page = self._pages[url]
#         await page.goto(
#             url=serialize(url), wait_until="domcontentloaded"
#         )
#         self._loaded[url] = True
#         logger.debug(f"{self._tag}|load_page(): Page loaded for {url}")
#         return page
#
#     async def get_text(self, url: HttpUrl, selector: str = "body") -> str:
#         page = await self.load_page(url)
#         return await page.text_content(selector)
#
#     async def get_html(self, url: HttpUrl) -> str:
#         page = await self.load_page(url)
#         return await page.content()
#
#     async def get_urls(self, url: HttpUrl) -> list[HttpUrl] | None:
#         try:
#             page = await self.load_page(url)
#             anchors = await page.locator("a").all()
#             urls: list[HttpUrl] = []
#
#             for anchor in anchors:
#                 href = await anchor.get_attribute('href')
#                 if href:
#                     full_url = urllib.parse.urljoin(page.url, href)
#                     urls.append(HttpUrl(full_url))
#
#             return urls
#         except Exception as error:
#             logger.error(f"{self._tag}|get_urls(): Error while extracting URLs from {url}: {error}")
#             return None
#
#     async def close_page(self, url: HttpUrl) -> None:
#         if url in self._pages:
#             logger.debug(f"{self._tag}|close_page(): Closing page for {url}")
#             await self._pages[url].close()
#             self._pages.pop(url, None)
#             self._loaded.pop(url, None)
#             logger.debug(f"{self._tag}|close_page(): Page closed for {url}")
#         else:
#             logger.debug(f"{self._tag}|close_page(): No page found for {url}")
#
#     async def close_all_pages(self) -> None:
#         logger.debug(f"{self._tag}|close_all_pages(): Closing all pages...")
#         for url in list(self._pages.keys()):
#             await self.close_page(url)
#         logger.debug(f"{self._tag}|close_all_pages(): All pages closed.")
#
#     async def close(self) -> None:
#         logger.info(f"{self._tag}|Closing Playwright client...")
#         await self.close_all_pages()
#         if not self._started:
#             return
#         await self._context.close()
#         await self._browser.close()
#         await self._playwright.stop()
#         self._started = False
#
#     # Optional: Async context manager support
#     async def __aenter__(self) -> Self:
#         await self.start()
#         return self
#
#     async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
#         logger.debug(f"{self._tag}|__aexit__()")
#         await self.close()