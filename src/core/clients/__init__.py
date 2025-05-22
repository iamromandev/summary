from collections.abc import AsyncGenerator
from typing import Annotated

from src.core.config import settings

from .cache import CacheClient
from .playwright import PlaywrightClient


async def get_cache(
    cache_url: Annotated[str, ...] = settings.cache_url
) -> AsyncGenerator[CacheClient]:
    yield CacheClient(cache_url)