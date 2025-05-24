import gc
from dataclasses import dataclass
from functools import reduce
from typing import Annotated, Any, cast

from fastapi import FastAPI, Request
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from loguru import logger
from pydantic import Field

from .base import BaseSchema, Response
from .types import Code, ErrorType, Status


class Violation(BaseSchema):
    field: Annotated[str | None, Field(default=None)]
    description: Annotated[str | None, Field(default=None)]


class ErrorDetail(BaseSchema):
    subject: Annotated[str | None, Field(default=None)]
    description: Annotated[str | None, Field(default=None)]
    fields: Annotated[list[Any] | None, Field(default=None)]
    violations: Annotated[list[Violation] | None, Field(default=None)]


class Error(Exception):
    def __init__(
        self,
        code: Annotated[Code, Field(default=Code.INTERNAL_SERVER_ERROR)] = Code.INTERNAL_SERVER_ERROR,
        message: Annotated[str | None, Field(default=None)] = None,
        type: Annotated[ErrorType, Field(default=ErrorType.SERVER_ERROR)] = ErrorType.SERVER_ERROR,
        details: Annotated[list[ErrorDetail] | None, Field(default=None)] = None,
        retry_able: Annotated[bool, Field(default=False)] = False
    ) -> None:
        self.code = code
        self.message = message
        self.type = type
        self.details = details
        self.retry_able = retry_able

    @classmethod
    def empty(cls: type["Error"]) -> "Error":
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

    @classmethod
    def create(
        cls: type["Error"],
        code: Code = Code.INTERNAL_SERVER_ERROR,
        message: str | None = None,
        type: ErrorType = ErrorType.SERVER_ERROR
    ) -> "Error":
        return cls(
            code=code,
            message=message,
            type=type
        )

    @classmethod
    def bad_request(
        cls: type["Error"],
        message: str | None = None
    ) -> "Error":
        return cls(
            code=cast(Code, Code.BAD_REQUEST),
            message=message,
            type=ErrorType.BAD_REQUEST,
        )

    @classmethod
    def unauthorized(
        cls: type["Error"],
        message: str | None = None
    ) -> "Error":
        return cls(
            code=cast(Code, Code.UNAUTHORIZED),
            message=message,
            type=ErrorType.UNAUTHORIZED,
        )

    @classmethod
    def not_found(
        cls: type["Error"],
        message: str | None = None
    ) -> "Error":
        return cls(
            code=cast(Code, Code.NOT_FOUND),
            message=message,
            type=ErrorType.NOT_FOUND,
        )


# error response
@dataclass
class ErrorResponse(Response):
    error: Annotated[Error | Exception, Field(default=Error.empty)] = Error.empty()

    def __post_init__(self) -> None:
        self.status = Status.ERROR
        self.code = self.error.code
        self.message = self.error.message
        # to exclude
        self.error.code = None
        self.error.message = None

    def to_json(self, exclude_none: bool = True) -> Any:
        json = jsonable_encoder(
            self,
            # exclude={"error": {"code"}},
            exclude_none=exclude_none
        )
        logger.info(f"{self._tag}|to_json: {json}")
        return json


def config_global_errors(app: FastAPI) -> None:
    @app.exception_handler(Exception)
    async def catch_exception(request: Request, error: Exception) -> JSONResponse:
        error_arg_str = reduce(
            lambda arg_str, arg: arg_str + "\n" + str(arg), error.args, ""
        )
        logger.error(
            f"{type(error).__name__} in {request.url}: {error_arg_str}",
            exc_info=error.__traceback__,
        )
        gc.collect()

        return ErrorResponse(
            error=error
        ).to_resp()

    @app.exception_handler(Error)
    async def catch_error(request: Request, error: Error) -> JSONResponse:
        logger.error(f"Global|Error|catch_error(): {str(error)}")
        return ErrorResponse(error=error).to_resp()
