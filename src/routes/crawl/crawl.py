from typing import Annotated

from fastapi import APIRouter, BackgroundTasks, Depends
from fastapi.responses import JSONResponse
from loguru import logger

from src.core.constants import WEB_URL
from src.core.success import Success
from src.services import get_crawl_service
from src.services.crawl import CrawlService

router = APIRouter(prefix="/crawl", tags=["crawl"])


@router.post(path="")
async def etl(
    service: Annotated[CrawlService, Depends(get_crawl_service)],
    bt: BackgroundTasks,
) -> JSONResponse:
    logger.debug(f"Running crawl {WEB_URL}")
    bt.add_task(service.crawl, WEB_URL)
    return Success.ok().to_resp()
