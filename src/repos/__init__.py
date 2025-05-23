from collections.abc import AsyncGenerator

from .url_repo import UrlRepo


async def get_url_repo() -> AsyncGenerator[UrlRepo]:
    yield UrlRepo()