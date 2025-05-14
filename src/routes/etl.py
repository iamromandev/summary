from typing import Annotated

from fastapi import APIRouter, BackgroundTasks, Depends
from loguru import logger

from src.core.constants import WEB_URL
from src.db.models import Url
from src.services.deps import get_extract_service
from src.services.extract import ExtractService

router = APIRouter(prefix="/etl", tags=["etl"])


@router.post("/")
async def run_etl(
   extract_service: Annotated[ExtractService, Depends(get_extract_service)],
    bt: BackgroundTasks,
):
    logger.info(f"Running ETL {WEB_URL}")
    bt.add_task(extract_service.extract_urls, WEB_URL)
    await Url.create(url=WEB_URL, base=WEB_URL)
    #await extract_service.extract_urls(WEB_URL)
    return None
