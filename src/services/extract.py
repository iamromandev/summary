from loguru import logger
from pydantic import HttpUrl

import src.core.common as common
from src.core.base import BaseService
from src.core.clients import PlaywrightClient
from src.core.formats import serialize
from src.db.models import Raw, Url
from src.repos.raw_repo import RawRepo
from src.repos.url_repo import UrlRepo


class ExtractService(BaseService):
    _playwright_client: PlaywrightClient
    _url_repo: UrlRepo
    _raw_repo: RawRepo

    def __init__(
        self,
        playwright_client: PlaywrightClient,
        url_repo: UrlRepo,
        raw_repo: RawRepo
    ) -> None:
        super().__init__()
        self._playwright_client = playwright_client
        self._url_repo = url_repo
        self._raw_repo = raw_repo

    # async def extract_urls(self, url: HttpUrl) -> list[str] | None:
    #     async with PlaywrightClient() as pc:
    #         extracted_urls: list[str] | None = await pc.get_urls(url)
    #         logger.debug(f"{self._tag}|extract_urls(): Extracted URLs: {extracted_urls}")
    #         for extracted_url in extracted_urls or []:
    #             try:
    #                 url_obj: Url = await  self._url_repo.create_or_update(
    #                     url=extracted_url,
    #                     base_url=common.get_base_url(extracted_url)
    #                 )
    #                 logger.debug(f"{self._tag}|extract_urls(): URL saved: {url_obj}")
    #             except ValidationError as error:
    #                 logger.error(f"{self._tag}|extract_urls(): Validation error: {error}")
    #         return extracted_urls

    async def extract(self, url: HttpUrl) -> None:
        logger.debug(f"{self._tag}|extract(): Starting extraction for {url}")

        db_url: Url = await  self._url_repo.create_or_update(
            url=serialize(url),
            base_url=serialize(common.get_base_url(url))
        )
        logger.debug(f"{self._tag}|extract(): URL saved: {db_url}")

        html: str = await self._playwright_client.get_html(url)
        raw: Raw = await  self._raw_repo.create_or_update(
            url=db_url,
            html=html
        )
        logger.debug(f"{self._tag}|extract(): Raw HTML saved: {raw}")

        extracted_urls: list[HttpUrl] | None = await self._playwright_client.get_urls(url)
        if not extracted_urls:
            logger.debug(f"{self._tag}|extract(): No URLs extracted from {url}")
            return
        logger.debug(f"{self._tag}|extract(): Extracted URLs: {extracted_urls}")
        for extracted_url in extracted_urls:
            await self.extract(extracted_url)
        return
