from typing import NoReturn, Self

from playwright.async_api import Browser, BrowserContext, Page, Playwright, async_playwright

from ..constants import PW_USER_AGENT


class PlaywrightClient:
    playwright: Playwright
    page: Page

    def __init__(self, headless: bool = True) -> NoReturn:
        self.headless = headless

    async def start(self) -> None:
        self.playwright: Playwright = await async_playwright().start()
        browser: Browser = await self.playwright.chromium.launch(headless=self.headless)
        context: BrowserContext = await browser.new_context(user_agent=PW_USER_AGENT)
        self.page: Page = await context.new_page()

    async def load(self, url: str) -> NoReturn:
        await self.page.goto(url, wait_until="networkidle")

    async def get_text(self, html_selector: str = "body") -> str:
        return await self.page.text_content(html_selector)

    async def close(self) -> NoReturn:
        await self.playwright.stop()

    # Optional: Async context manager support
    async def __aenter__(self) -> Self:
        await self.start()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        await self.close()
