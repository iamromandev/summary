from src.core.base import BaseService
from src.core.clients import CacheClient
from src.core.common import get_app_version, get_cache_health
from src.core.types import Status
from src.db import get_db_health
from src.schemas.health import HealthSchema


class HealthService(BaseService):

    def __init__(self, cache_client: CacheClient) -> None:
        super().__init__(cache_client)

    async def check_health(self) -> HealthSchema:
        db_status = Status.SUCCESS if await get_db_health() else Status.ERROR
        cache_status = Status.SUCCESS if await get_cache_health(self._cache_client) else Status.ERROR
        app_version = await get_app_version()
        health: HealthSchema = HealthSchema(db=db_status, cache=cache_status, version=app_version)
        health.log()
        return health