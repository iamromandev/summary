from functools import cached_property
from urllib.parse import urljoin

from bs4 import BeautifulSoup
from loguru import logger
from pydantic import HttpUrl, ValidationError

import src.core.common as common
from src.core.factory import SingletonMeta
from src.core.formats import serialize


class SoupClient(metaclass=SingletonMeta):
    _initialized: bool = False

    def __init__(self):
        if self._initialized:
            return
        self._initialized = True

    @cached_property
    def _tag(self) -> str:
        return self.__class__.__name__

    async def extract_urls(
        self,
        url: HttpUrl,
        content: str,
        parser: str = "html.parser",
    ) -> list[HttpUrl]:
        soup = BeautifulSoup(content, parser)
        raw_urls = [a["href"] for a in soup.find_all("a", href=True)]

        logger.debug(f"{self._tag}|extract_urls(): urls {raw_urls}")


        base_url = common.get_base_url(url)
        urls: set[HttpUrl] = set()
        for href in raw_urls:
            # Skip bad or useless hrefs
            if (
                not href
                or href.startswith("#")
                or href.lower().startswith("javascript:")
                or href.lower().startswith("mailto:")
                or href == "/undefined"
            ):
                continue

            # Resolve relative URL → absolute
            absolute_url = urljoin(serialize(base_url), href)

            try:
                urls.add(HttpUrl(absolute_url))
            except ValidationError:
                logger.warning(
                    f"{self._tag}|extract_urls(): Skipped invalid URL -> {absolute_url}"
                )

        clean_urls = list(urls)
        logger.debug(
            f"{self._tag}|extract_urls(): extracted {len(clean_urls)} unique valid urls"
        )
        return clean_urls