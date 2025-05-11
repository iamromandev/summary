import urllib.parse
from typing import NoReturn, Self

from loguru import logger
from playwright.async_api import Browser, BrowserContext, Page, Playwright, async_playwright

from core.constants import PW_USER_AGENT


class PlaywrightClient:
    playwright: Playwright
    browser: Browser
    context: BrowserContext
    page: Page

    def __init__(self, headless: bool = True) -> NoReturn:
        self.headless = headless

    async def start(self) -> None:
        self.playwright: Playwright = await async_playwright().start()
        self.browser: Browser = await self.playwright.chromium.launch(headless=self.headless)
        self.context: BrowserContext = await self.browser.new_context(user_agent=PW_USER_AGENT)
        self.page: Page = await self.context.new_page()

    async def _load(self, url: str) -> Page:
        await self.page.goto(url, wait_until="networkidle")
        return self.page

    async def get_text(self, html_selector: str = "body") -> str:
        return await self.page.text_content(html_selector)

    async def get_urls(self, url: str) -> list[str] | None:
        try:
            page: Page = await self._load(url)
            urls = [
                urllib.parse.urljoin(page.url, await a_tag.get_attribute('href'))
                for a_tag in await page.locator("a").all()
                if await a_tag.get_attribute('href')
            ]
            return urls
        except Exception as error:
            logger.error(f"Error|PlaywrightClient|get_links {error}")
        return None

    async def close(self) -> NoReturn:
        await self.context.close()
        await self.browser.close()
        await self.playwright.stop()

    # Optional: Async context manager support
    async def __aenter__(self) -> Self:
        await self.start()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        await self.close()
