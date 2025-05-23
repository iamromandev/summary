from dataclasses import dataclass
from typing import Annotated, Any

from fastapi.encoders import jsonable_encoder
from loguru import logger
from pydantic import Field

from .base import BaseSchema, Response


class Meta(BaseSchema):
    page: Annotated[int, Field(default=1)] = 1
    page_size: Annotated[int, Field(default=10)] = 10
    total: Annotated[int, Field(default=100)] = 100


@dataclass
class SuccessResponse(Response):
    meta: Annotated[Meta | None, None] = None

    def to_json(self, exclude_none: bool = True) -> Any:
        json = jsonable_encoder(self, exclude_none=exclude_none)
        logger.info(f"{self._tag}|to_json(): {json}")
        return json