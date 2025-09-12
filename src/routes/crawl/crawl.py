from typing import Annotated

from fastapi import APIRouter, BackgroundTasks, Depends, Query
from fastapi.responses import JSONResponse
from pydantic import Field, HttpUrl

from src.core.success import Success
from src.services import get_crawl_service
from src.services.crawl import CrawlService

router = APIRouter(prefix="/crawl", tags=["crawl"])


@router.get(path="")
async def crawl(
    url: Annotated[HttpUrl, Query(...)],
    service: Annotated[CrawlService, Depends(get_crawl_service)],
    bt: Annotated[BackgroundTasks, Field(...)],
) -> JSONResponse:
    bt.add_task(service.crawl, url)
    return Success.ok(
        message=f"Crawling in background for {url}"
    ).to_resp()
