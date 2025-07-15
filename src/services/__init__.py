from collections.abc import AsyncGenerator

from fastapi import Depends

from src.core.clients import CacheClient, PlaywrightClient, get_cache_client, get_playwright_client
from src.core.config import settings
from src.repos import RawRepo, TaskRepo, UrlRepo, get_raw_repo, get_task_repo, get_url_repo

from .crawl import CrawlService
from .health import HealthService


async def get_health_service(
    cache_client: CacheClient = Depends(get_cache_client)
) -> AsyncGenerator[HealthService]:
    yield HealthService(cache_client)


async def get_crawl_service(
    playwright_client: PlaywrightClient = Depends(get_playwright_client),
    state_repo: TaskRepo = Depends(get_task_repo),
    url_repo: UrlRepo = Depends(get_url_repo),
    raw_repo: RawRepo = Depends(get_raw_repo)
) -> AsyncGenerator[CrawlService]:
    yield CrawlService(
        playwright_client,
        state_repo,
        url_repo,
        raw_repo,
        settings.crawl_url_expiration
    )
