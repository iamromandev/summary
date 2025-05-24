import uuid
from abc import ABC, abstractmethod
from dataclasses import dataclass
from dataclasses import field as DCField
from datetime import UTC, datetime
from functools import cached_property
from typing import Annotated, Any, Generic, TypeVar

from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from loguru import logger
from pydantic import BaseModel, ConfigDict, Field
from tortoise import fields, models, queryset

from .formats import utc_iso_timestamp
from .types import Code, Status

# database - mode + repo
_ModelT = TypeVar("_ModelT", bound=models.Model)


class Base(models.Model):
    id = fields.UUIDField(pk=True, default=uuid.uuid4)
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)
    deleted_at = fields.DatetimeField(null=True)

    class Meta:
        abstract = True

    async def soft_delete(self) -> None:
        self.deleted_at = datetime.now(UTC)
        return await self.save()

    @classmethod
    async def get_active(cls: type[_ModelT]) -> queryset.QuerySet[_ModelT]:
        return cls.filter(deleted_at__isnull=True)


# repo - operation on the database
class BaseRepo(Generic[_ModelT]):
    model: type[_ModelT]

    def __init__(self, model: type[_ModelT]) -> None:
        self.model = model

    @cached_property
    def _tag(self) -> str:
        return self.__class__.__name__

    async def get_by_pk(self, pk: str | uuid.UUID) -> _ModelT | None:
        return await self.model.get_or_none(pk=pk)

    async def get_all(self, sort: str | None = None) -> list[_ModelT]:
        query: queryset.QuerySet = self.model.all()

        if sort:
            order_fields = [field.strip() for field in sort.split(",")]
            query = query.order_by(*order_fields)

        return await query

    async def exists(self, **kwargs: Any) -> bool:
        return await self.model.filter(**kwargs).exists()

    async def filter(self, **kwargs: Any) -> list[_ModelT]:
        return await self.model.filter(**kwargs).all()

    async def first(self, **kwargs: Any) -> list[_ModelT]:
        return await self.model.filter(**kwargs).first()

    async def get_or_create(self, **defaults: Any) -> tuple[_ModelT, bool]:
        return await self.model.get_or_create(**defaults)

    async def create(self, **kwargs: Any) -> _ModelT:
        return await self.model.create(**kwargs)

    async def update(self, instance: _ModelT, **kwargs: Any) -> _ModelT | None:
        for attr, value in kwargs.items():
            setattr(instance, attr, value)
        await instance.save()
        return instance

    async def update_by_pk(self, pk: str | uuid.UUID, **kwargs: Any) -> _ModelT | None:
        instance = await self.get_by_pk(pk)
        if instance:
            return await self.update(instance, **kwargs)
        return None

    async def delete(self, instance: _ModelT) -> None:
        await instance.delete()

    async def delete_by_pk(self, pk: str | uuid.UUID) -> bool:
        instance = await self.get_by_pk(pk)
        if instance:
            await instance.delete()
            return True
        return False


# schema - request + response + validation
class BaseSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    @cached_property
    def _tag(self) -> str:
        return self.__class__.__name__

    def to_json(self, exclude_none: bool = True) -> Any:
        json = jsonable_encoder(self, exclude_none=exclude_none)
        logger.info(f"{self._tag}|to_json(): {json}")
        return json

    def to_dict(
        self,
        exclude_fields: Annotated[set[str] | None, Field(...)] = None,
        exclude_none: Annotated[bool, Field(...)] = None,
        exclude_unset: Annotated[bool, Field(...)] = None,
    ) -> dict[str, Any]:
        data = self.model_dump(
            exclude=exclude_fields,
            exclude_none=exclude_none,
            exclude_unset=exclude_unset
        )
        logger.info(f"{self._tag}|to_dict(): {data}")
        return data

    def safe_dump(
        self, exclude_fields: Annotated[set[str] | None, Field(...)] = None,
    ) -> dict[str, Any]:
        data = self.to_dict(
            exclude_fields=exclude_fields,
            exclude_none=True,
            exclude_unset=True
        )
        logger.info(f"{self._tag}|to_dict(): {data}")
        return data

    def log(self) -> None:
        data = self.model_dump()
        logger.info(f"{self._tag}|log(): {data}")


# response
_DataT = TypeVar("_DataT", bound=BaseSchema)


@dataclass
class Response(ABC, Generic[_DataT]):
    status: Annotated[Status, Field(default=Status.SUCCESS)] = Status.SUCCESS
    code: Annotated[Code, Field(default=Code.OK)] = Code.OK
    data: Annotated[BaseSchema | list[BaseSchema] | Any, Field(default=None)] = None
    message: Annotated[str | None, Field(default=None)] = None
    timestamp: Annotated[str, Field(...)] = DCField(default_factory=lambda: utc_iso_timestamp())

    @cached_property
    def _tag(self) -> str:
        return self.__class__.__name__

    @abstractmethod
    def to_json(self) -> Any:
        pass

    def to_resp(self) -> JSONResponse:
        return JSONResponse(
            content=self.to_json(),
            status_code=self.code.value,
        )


# service
class BaseService:
    _cache_client: Annotated[Any, Field(...)]

    def __init__(self, cache_client: Any) -> None:
        self._cache_client = cache_client

    @cached_property
    def _tag(self) -> str:
        return self.__class__.__name__
