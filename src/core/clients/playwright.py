import urllib.parse
from typing import Annotated, Self

from loguru import logger
from playwright.async_api import Browser, BrowserContext, Page, Playwright, async_playwright
from pydantic import Field

from src.core.constants import PW_USER_AGENT
from src.core.mixins import BaseMixin


class PlaywrightClient(BaseMixin):
    _playwright: Annotated[Playwright, Field(...)]
    _browser: Annotated[Browser, Field(...)]
    _context: Annotated[BrowserContext, Field(...)]
    _page: Annotated[Page, Field(...)]

    def __init__(
        self,
        headless: bool = True,
        user_agent: str | None = None
    ) -> None:
        super().__init__()
        self._headless = headless
        self._user_agent = user_agent or PW_USER_AGENT

    async def start(self) -> None:
        self._playwright: Playwright = await async_playwright().start()
        self._browser: Browser = await self._playwright.chromium.launch(headless=self._headless)
        self._context: BrowserContext = await self._browser.new_context(user_agent=PW_USER_AGENT)
        self._page: Page = await self._context.new_page()

    async def _load(self, url: str) -> Page:
        await self._page.goto(url, wait_until="domcontentloaded")
        return self._page

    async def get_text(self, html_selector: str = "body") -> str:
        return await self._page.text_content(html_selector)

    async def get_urls(self, url: str) -> list[str]:
        try:
            page: Page = await self._load(url)
            urls = [
                urllib.parse.urljoin(page.url, await a_tag.get_attribute('href'))
                for a_tag in await page.locator("a").all()
                if await a_tag.get_attribute('href')
            ]
            return urls
        except Exception as error:
            logger.error(f"{self._tag}|get_urls(): {error}")
            raise

    async def close(self) -> None:
        logger.info(f"{self._tag}|Closing Playwright client...")
        await self._context.close()
        await self._browser.close()
        await self._playwright.stop()

    # Optional: Async context manager support
    async def __aenter__(self) -> Self:
        await self.start()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        await self.close()
