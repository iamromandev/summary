import uuid
from datetime import datetime
from typing import Any

from tortoise import fields

from src.core import common
from src.core.base import Base
from src.core.types import DataSource, DataStatus, DataSubType, DataType, DataVisibility


class Data(Base):
    # identity & linkage
    source: DataSource | None = fields.CharEnumField(
        DataSource, null=True
    )
    parent: fields.ForeignKeyRelation["Data"] = fields.ForeignKeyField(
        model_name="models.Data",
        related_name="children",
        on_delete=fields.SET_NULL,
        null=True,
    )
    # classification
    type: DataType | None = fields.CharEnumField(
        DataType, null=True, default=None
    )
    subtype: DataSubType | None = fields.CharEnumField(
        DataSubType, null=True, default=None
    )
    # ownership
    owner_id: uuid.UUID | None = fields.UUIDField(null=True, index=True)
    organization: str | None = fields.CharField(max_length=256, null=True)
    # lifecycle
    status: DataStatus | None = fields.CharEnumField(
        DataStatus,
        null=True, default=None
    )
    visibility: DataVisibility | None = fields.CharEnumField(
        DataVisibility, null=True, default=None
    )
    version: int = fields.IntField(default=1)

    # core
    content: dict[str, Any] | list[Any] | None = fields.JSONField(null=True, default=None)
    checksum: str | None = fields.CharField(max_length=64, null=True, index=True)

    # quality
    score: float | None = fields.FloatField(null=True)
    is_encrypted: bool = fields.BooleanField(default=False)

    # tags & access control
    tags: list[Any] | None = fields.JSONField(null=True, default=None)
    permissions : dict[str, Any] | None = fields.JSONField(null=True, default=None)

    # expiration
    expires_at: datetime | None = fields.DatetimeField(null=True)

    meta: dict[str, Any] | list[Any] | None = fields.JSONField(null=True, default=None)

    class Meta:
        ordering = ["source", "type", "subtype"]
        table = "data"
        table_description = "Data"

    def __str__(self) -> str:
        return f"[Data: {self.source}, {self.type}, {self.subtype}, {self.status}]"

    async def save(self, *args, **kwargs):
        if self.content:
            self.checksum = common.compute_checksum(self.content)
        await super().save(*args, **kwargs)
