from typing import Any

from pydantic import HttpUrl
from tortoise.exceptions import DoesNotExist

from src.core.base import BaseRepo
from src.db.models import Url


class UrlRepo(BaseRepo[Url]):
    def __init__(self) -> None:
        super().__init__(Url)

    async def get_or_create(
        self,
        url: HttpUrl,
        base_url: HttpUrl | None = None,
        **kwargs: Any
    ) -> tuple[Url, bool]:
        try:
            obj = await self._model.get(url=url)
            return obj, False
        except DoesNotExist:
            obj = await self._model.create(url=url, base_url=base_url, **kwargs)
            return obj, True

    async def create_or_update(
        self, url: str, base_url: str | None,
        defaults: dict = None, **kwargs: Any
    ) -> Url:
        url_obj, created = await self._model.get_or_create(
            url=url, base_url=base_url, defaults=defaults or {}
        )
        if not created and kwargs:
            for attr, value in kwargs.items():
                setattr(url_obj, attr, value)
            await url_obj.save()
        return url_obj
