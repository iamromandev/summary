import uuid
from typing import Any

from src.core.base import BaseRepo
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
        url_obj, created = await self._model.get_or_create(
            ref=ref, ref_type=ref_type, defaults=defaults or {}
        )
        if not created and kwargs:
            for attr, value in kwargs.items():
                setattr(url_obj, attr, value)
            await url_obj.save()
        return url_obj
