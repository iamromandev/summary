from collections.abc import AsyncGenerator
from typing import Annotated

from pydantic import Field, RedisDsn

from src.core.config import settings

from .cache import CacheClient
from .playwright import PlaywrightClient


async def get_cache_client(
) -> AsyncGenerator[CacheClient]:
    yield CacheClient(
        cache_url=settings.cache_url
    )


async def get_playwright_client() -> AsyncGenerator[PlaywrightClient]:
    client = PlaywrightClient(
        playwright_url=settings.playwright_url,
        headless=settings.playwright_headless,
        user_agent=settings.playwright_user_agent
    )
    await client.start()
    yield client
    await client.close()
