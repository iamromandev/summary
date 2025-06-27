from datetime import datetime, timedelta
from typing import Any

from src.core.base import BaseRepo
from src.db.models import Raw, Url


class RawRepo(BaseRepo[Raw]):
    def __init__(self) -> None:
        super().__init__(Raw)

    async def create_or_update(
        self, url: Url, html: str, **kwargs: Any
    ) -> Raw:
        latest_raw = await self._model.filter(url=url).order_by("-updated_at").first()

        if latest_raw:
            time_diff = datetime.utcnow() - latest_raw.updated_at.replace(tzinfo=None)
            if time_diff >= timedelta(weeks=1):
                latest_raw.html = html
                for attr, value in kwargs.items():
                    setattr(latest_raw, attr, value)
                await latest_raw.save()
                return latest_raw

        # Create new raw if no recent record found or latest is recent
        return await self._model.create(url=url, html=html, **kwargs)
