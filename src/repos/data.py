from datetime import UTC, datetime, timedelta
from typing import Any

from src.core.base import BaseRepo
from src.db.models import Data, Url


class DataRepo(BaseRepo[Data]):
    def __init__(self) -> None:
        super().__init__(Data)

    async def create_or_update(
        self, url: Url, content: str, **kwargs: Any
    ) -> Data:
        latest_raw = await self._model.filter(url=url).order_by("-updated_at").first()

        if latest_raw:
            time_diff = datetime.now(UTC) - latest_raw.updated_at.astimezone(UTC)
            if time_diff >= timedelta(weeks=1):
                latest_raw.content = content
                for attr, value in kwargs.items():
                    setattr(latest_raw, attr, value)
                await latest_raw.save()
                return latest_raw

        # Create new raw if no recent record found or latest is recent
        return await self._model.create(url=url, content=content, **kwargs)
