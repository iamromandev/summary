
from loguru import logger
from tortoise.exceptions import ValidationError

from src.core.clients import PlaywrightClient
from src.db.models import Url


class ExtractService:
    def __init__(self) -> None:
        pass

    async def extract_urls(self, url: str) -> list[str] | None:
        async with PlaywrightClient() as pc:
            urls: list[str] | None = await pc.get_urls(url)
            logger.info(f"Success|ExtractService|extract_urls {urls}")
            for url in urls or []:
                try:
                    url: Url = await Url.create(url=url, base=url)
                    logger.info(f"Valid URL created {url}")
                except ValidationError as error:
                    logger.error(f"Validation Error: {error}")
            return urls
