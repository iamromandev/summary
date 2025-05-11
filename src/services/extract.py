from typing import NoReturn

from loguru import logger

from core.clients import PlaywrightClient


class ExtractService:
    def __init__(self) -> NoReturn:
        pass

    async def extract_urls(self, url: str) -> list[str] | None:
        async with PlaywrightClient() as pc:
            urls: list[str] | None = await pc.get_urls(url)
            logger.info(f"Success|ExtractService|extract_urls {urls}")
            return urls
