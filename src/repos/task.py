import uuid
from datetime import UTC, datetime, timedelta
from typing import Any

from loguru import logger

from src.core.base import BaseRepo
from src.core.types import ModelType
from src.db.models import Task


class TaskRepo(BaseRepo[Task]):
    def __init__(self) -> None:
        super().__init__(Task)

    async def create_or_update(
        self,
        ref: uuid.UUID,
        ref_type: str,
        defaults: dict = None,
        **kwargs: Any
    ) -> Task:
        obj, created = await self._model.get_or_create(
            ref=ref, ref_type=ref_type, defaults=defaults or {}
        )
        if not created and kwargs:
            for attr, value in kwargs.items():
                setattr(obj, attr, value)
            await obj.save()
        return obj

    async def get_first_expired(
        self,
        ref_type: ModelType,
        expire_after_s: int,
    ) -> Task | None:
        expire_threshold = datetime.now(UTC) - timedelta(seconds=expire_after_s)

        return await self._model.filter(
            ref_type=ref_type,
            updated_at__lt=expire_threshold
        ).order_by("updated_at").first()

    async def update_by_id(self, task_id: uuid.UUID, **kwargs: Any) -> Task | None:
        obj = await self.get_by_pk(task_id)
        if not obj:
            logger.warning(f"{self._tag}|update_by_id(): Task not found with id={task_id}")
            return None

        for attr, value in kwargs.items():
            setattr(obj, attr, value)
        await obj.save(update_fields=list(kwargs.keys()))
        logger.info(f"{self._tag}|update_by_id(): Updated {obj} with {kwargs}")
        return obj
