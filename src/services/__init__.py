from collections.abc import AsyncGenerator

from fastapi import Depends

from src.core.clients import CacheClient, PlaywrightClient, get_cache_client, get_playwright_client
from src.repos import RawRepo, StateRepo, UrlRepo, get_raw_repo, get_state_repo, get_url_repo

from .extract import ExtractService
from .health import HealthService


async def get_health_service(
    cache_client: CacheClient = Depends(get_cache_client)
) -> AsyncGenerator[HealthService]:
    yield HealthService(cache_client)


async def get_extract_service(
    playwright_client: PlaywrightClient = Depends(get_playwright_client),
    state_repo: StateRepo = Depends(get_state_repo),
    url_repo: UrlRepo = Depends(get_url_repo),
    raw_repo: RawRepo = Depends(get_raw_repo)
) -> AsyncGenerator[ExtractService]:
    yield ExtractService(
        playwright_client,
        state_repo,
        url_repo,
        raw_repo
    )
