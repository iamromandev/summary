import uuid
from datetime import UTC, datetime

from tortoise import fields, models, queryset


class State(models.Model):
    id: uuid.UUID = fields.UUIDField(pk=True, default=uuid.uuid4)
    ref: uuid.UUID = fields.UUIDField(null=False)
    state: str = fields.CharField(max_length=32, null=False)
    extra: str | None = fields.CharField(max_length=32, null=True)
    created_at: datetime = fields.DatetimeField(auto_now_add=True)
    updated_at: datetime = fields.DatetimeField(auto_now=True)
    deleted_at = fields.DatetimeField(null=True)

    class Meta:
        ordering = ["ref", "state"]
        unique_together = [("ref", "state")]
        table_description = "State"
        table = "state"

    def __str__(self) -> str:
        return f"[State: {self.ref}, {self.state}]"

    async def soft_delete(self) -> None:
        self.deleted_at = datetime.now(UTC)
        return await self.save()

    def is_expired(self, delay_s: int) -> bool:
        return (
            datetime.now(UTC) - self.updated_at
        ).total_seconds() > delay_s

    @classmethod
    async def get_active(cls: type["State"]) -> queryset.QuerySet["State"]:
        return cls.filter(deleted_at__isnull=True)
