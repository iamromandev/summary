import uuid
from datetime import UTC, datetime
from typing import TypeVar

from tortoise import fields, models, queryset

_T = TypeVar('_T', bound='Base')

class Base(models.Model):
    id = fields.UUIDField(pk=True, default=uuid.uuid4)
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)
    deleted_at = fields.DatetimeField(null=True)

    class Meta:
        abstract = True  # Prevent creation of a table for Base

    async def soft_delete(self) -> None:
        self.deleted_at = datetime.now(UTC)
        return await self.save()

    @classmethod
    async def get_active(cls: type[_T]) -> queryset.QuerySet[_T]:
        return cls.filter(deleted_at__isnull=True)