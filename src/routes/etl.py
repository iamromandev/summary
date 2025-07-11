from typing import Annotated

from fastapi import APIRouter, BackgroundTasks, Depends
from fastapi.responses import JSONResponse
from loguru import logger

from src.core.constants import WEB_URL
from src.core.success import Success
from src.services import get_extract_service
from src.services.extract import ExtractService

router = APIRouter(prefix="/etl", tags=["etl"])


@router.post(path="")
async def etl(
    extract_service: Annotated[ExtractService, Depends(get_extract_service)],
    bt: BackgroundTasks,
) -> JSONResponse:
    logger.debug(f"Running ETL {WEB_URL}")
    bt.add_task(extract_service.extract, WEB_URL)
    return Success.ok().to_resp()
