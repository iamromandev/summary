from typing import Any

from src.core.repos import BaseRepo
from src.db.models import Url


class UrlRepo(BaseRepo[Url]):
    def __init__(self) -> None:
        super().__init__(Url)

    async def create_or_update(
        self, url: str, base: str | None,
        defaults: dict = None, **kwargs: Any
    ) -> Url:
        url_obj, created = await self.model.get_or_create(
            url=url, base=base, defaults=defaults or {}
        )
        if not created and kwargs:
            for attr, value in kwargs.items():
                setattr(url_obj, attr, value)
            await url_obj.save()
        return url_obj

