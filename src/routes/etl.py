from fastapi import APIRouter
from loguru import logger

router = APIRouter(prefix="/etl", tags=["etl"])


@router.post("/")
async def run_etl():
    logger.info("Running ETL")
    return None
