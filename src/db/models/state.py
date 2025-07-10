import uuid
from datetime import UTC, datetime

from tortoise import fields

from src.core.base import Base


class State(Base):
    ref: uuid.UUID = fields.UUIDField(null=False)
    state: str = fields.CharField(max_length=32, null=False)
    extra: dict | list | None = fields.JSONField(null=True)

    class Meta:
        ordering = ["ref", "state"]
        unique_together = [("ref", "state")]
        table = "state"
        table_description = "State"

    def __str__(self) -> str:
        return f"[State: {self.ref}, {self.state}]"

    def is_expired(self, delay_s: int) -> bool:
        return (
            datetime.now(UTC) - self.updated_at
        ).total_seconds() > delay_s
