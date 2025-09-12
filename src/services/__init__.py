from collections.abc import AsyncGenerator
from typing import Annotated

from fastapi import Depends
from pydantic import Field

from src.core.clients import (
    CacheClient,
    HttpClientFactory,
    SoupClient,
    get_cache_client,
    get_http_client_factory,
    get_soup_client,
)
from src.core.config import settings
from src.repos import RawRepo, TaskRepo, UrlRepo, get_raw_repo, get_task_repo, get_url_repo

from .crawl import CrawlService
from .health import HealthService


async def get_health_service(
    cache_client: CacheClient = Depends(get_cache_client)
) -> AsyncGenerator[HealthService]:
    yield HealthService(cache_client)


async def get_crawl_service(
    http_client_factory: Annotated[HttpClientFactory, Field(...)] = Depends(get_http_client_factory),
    soup_client: Annotated[SoupClient, Field(...)] = Depends(get_soup_client),
    state_repo: Annotated[TaskRepo, Field(...)] = Depends(get_task_repo),
    url_repo: Annotated[UrlRepo, Field(...)] = Depends(get_url_repo),
    raw_repo: Annotated[RawRepo, Field(...)] = Depends(get_raw_repo)
) -> AsyncGenerator[CrawlService]:
    yield CrawlService(
        http_client_factory,
        soup_client,
        state_repo,
        url_repo,
        raw_repo,
        settings.crawl_base_url,
        settings.crawl_url_expiration
    )
