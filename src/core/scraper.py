
from loguru import logger
from playwright.async_api import Browser, BrowserContext, Page, async_playwright


async def get_raw_text(url: str) -> str | None:
    async with async_playwright() as pr:
        browser: Browser = await pr.chromium.launch(
            headless=True
        )
        context: BrowserContext = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) ..."
        )
        page: Page = await context.new_page()

        try:
            await page.goto(url, wait_until="networkidle")

            text: str = await page.inner_text("body")
            return text
        except Exception as error:
            logger.error(f"Error||get_raw_text {url} {error}")
            return None
        finally:
            await browser.close()
