
from loguru import logger
from playwright.async_api import Browser, Page, async_playwright


async def get_raw_text(url: str) -> str | None:
    async with async_playwright() as pr:
        browser: Browser = await pr.chromium.launch(
            headless=True
        )
        page: Page = await browser.new_page()

        try:
            await page.goto(url)
            await page.wait_for_load_state("networkidle")

            text: str = await page.text_content("body")
            return text
        except Exception as error:
            logger.error(f"Error||get_raw_text {url} {error}")
            return None
        finally:
            await browser.close()
