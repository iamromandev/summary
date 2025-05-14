import uuid
from typing import Any, Generic, TypeVar

from tortoise import models

_T = TypeVar("_T", bound=models.Model)


class BaseRepo(Generic[_T]):
    model: type[_T]

    def __init__(self, model: type[_T]) -> None:
        self.model = model

    async def get_by_pk(self, pk: str | uuid.UUID) -> _T | None:
        return await self.model.get_or_none(pk=pk)

    async def get_all(self) -> list[_T]:
        return await self.model.all()

    async def exists(self, **kwargs: Any) -> bool:
        return await self.model.filter(**kwargs).exists()

    async def filter(self, **kwargs: Any) -> list[_T]:
        return await self.model.filter(**kwargs).all()

    async def create(self, **kwargs: Any) -> _T:
        return await self.model.create(**kwargs)

    async def update(self, instance: _T, **kwargs: Any) -> _T | None:
        for attr, value in kwargs.items():
            setattr(instance, attr, value)
        await instance.save()
        return instance

    async def update_by_pk(self, pk: str | uuid.UUID, **kwargs: Any) -> _T | None:
        instance = await self.get_by_pk(pk)
        if instance:
            return await self.update(instance, **kwargs)
        return None

    async def delete(self, instance: _T) -> None:
        await instance.delete()

    async def delete_by_pk(self, pk: str | uuid.UUID) -> bool:
        instance = await self.get_by_pk(pk)
        if instance:
            await instance.delete()
            return True
        return False
