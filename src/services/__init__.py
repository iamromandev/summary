from collections.abc import AsyncGenerator

from fastapi import Depends

from src.core.clients import CacheClient, get_cache
from src.repos import UrlRepo, get_url_repo

from .extract import ExtractService
from .health import HealthService


async def get_health_service(
    cache: CacheClient = Depends(get_cache)
) -> AsyncGenerator[HealthService]:
    yield HealthService(cache)


async def get_extract_service(
    url_repo: UrlRepo = Depends(get_url_repo)
) -> AsyncGenerator[ExtractService]:
    yield ExtractService(url_repo)
