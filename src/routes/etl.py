from typing import Annotated

from fastapi import APIRouter, Depends
from loguru import logger

from core.constants import WEB_URL
from services.deps import get_extract_service
from services.extract import ExtractService

router = APIRouter(prefix="/etl", tags=["etl"])


@router.post("/")
async def run_etl(
    extract_service: Annotated[ExtractService, Depends(get_extract_service)]
):
    logger.info("Running ETL")
    await extract_service.extract_urls(WEB_URL)
    return None
