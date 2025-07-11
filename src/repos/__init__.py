from collections.abc import AsyncGenerator

from .raw_repo import RawRepo
from .url_repo import UrlRepo


async def get_url_repo() -> AsyncGenerator[UrlRepo]:
    yield UrlRepo()

async def get_raw_repo() -> AsyncGenerator[RawRepo]:
    yield RawRepo()