from typing import Annotated, Any

from pydantic import BaseModel

from .types import ErrorType


class Violation(BaseModel):
    field: Annotated[str | None, None]
    description: Annotated[str | None, None]


class ErrorDetail(BaseModel):
    subject: Annotated[str | None, None]
    description: Annotated[str | None, None]
    fields: Annotated[list[Any] | None, None]
    violations: Annotated[list[Violation] | None, None]


class Error(BaseModel, Exception):
    type: Annotated[ErrorType, ErrorType.SERVER_ERROR]
    details: Annotated[list[ErrorDetail] | None, None]
    retry_able: Annotated[bool, False]

    @classmethod
    def empty(cls) -> "Error":
        return cls(
            type=ErrorType.SERVER_ERROR,
            details=[ErrorDetail(
                subject=None,
                description=None,
                fields=None,
                violations=None
            )],
            retry_able=False,
        )
