from datetime import UTC, datetime
from typing import Annotated, Generic, TypeVar

from pydantic import BaseModel, Field

from .errors import Error
from .types import Code, Status

T = TypeVar("T", bound="BaseModel")


class Resp(Generic[T]):
    status: Annotated[Status, Field(default=Status.SUCCESS)]
    code: Annotated[Code, Field(default=Code.OK)]
    data: Annotated[T | None, Field(default=None)]
    message: Annotated[str | None, Field(default="Optional message for the response")]
    timestamp: Annotated[datetime, Field(default_factory=lambda: datetime.now(UTC))]

# Success
class Meta(BaseModel):
    page: Annotated[int, Field(default=1)]
    page_size: Annotated[int, Field(default=10)]
    total: Annotated[int, Field(default=100)]


class SuccessResp(Resp[T]):
    meta: Annotated[Meta | None, Field(default=None)]

    # @classmethod
    # def ok(
    #     cls,
    #     data: T,
    #     message: str | None = None,
    #     meta: Meta | None = None
    # ) -> "SuccessResp[T]":
    #     return cls(
    #         status=Status.SUCCESS,
    #         code=Code.OK,
    #         message=message,
    #         data=data,
    #         meta=meta
    #     )
    #
    # @classmethod
    # def created(cls, data: T, message: str = "Resource created") -> "SuccessResp[T]":
    #     return cls(
    #         status=Status.SUCCESS,
    #         code=Code.CREATED,
    #         message=message,
    #         data=data
    #     )
    #
    # @classmethod
    # def paginated(cls, data: T, page: int, page_size: int, total: int) -> "SuccessResp[T]":
    #     meta = Meta(page=page, page_size=page_size, total=total)
    #     return cls(
    #         status=Resp.Status.SUCCESS,
    #         code=Code.OK,
    #         data=data,
    #         meta=meta
    #     )


# Error
class ErrorResp(Resp[T]):
    error: Annotated[Error, Field(default=Error.empty)]
