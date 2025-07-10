from loguru import logger
from tortoise.exceptions import ValidationError

import src.core.common as common
from src.core.base import BaseService
from src.core.clients import PlaywrightClient
from src.db.models import Url
from src.repos.url_repo import UrlRepo


class ExtractService(BaseService):
    _url_repo: UrlRepo

    def __init__(self, url_repo: UrlRepo) -> None:
        super().__init__()
        self._url_repo = url_repo

    async def extract_urls(self, url: str) -> list[str] | None:
        async with PlaywrightClient() as pc:
            urls: list[str] | None = await pc.get_urls(url)
            logger.info(f"Success|ExtractService|extract_urls {urls}")
            for url in urls or []:
                try:
                    url_obj: Url = await  self._url_repo.create_or_update(
                        url=url, base_url=common.get_base_url(url)
                    )
                    logger.info(f"Valid URL created {url_obj}")
                except ValidationError as error:
                    logger.error(f"Validation Error: {error}")
            return urls
