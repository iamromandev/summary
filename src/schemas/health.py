from typing import Annotated

from pydantic import Field

from src.core.base import BaseSchema
from src.core.types import Status


class HealthSchema(BaseSchema):
    db: Annotated[Status, Field(default=Status.SUCCESS)]
    cache: Annotated[Status, Field(default=Status.SUCCESS)]
    version: Annotated[str, Field(default="0.0.1", description="Application version")]