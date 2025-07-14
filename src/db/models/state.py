from datetime import UTC, datetime

from tortoise import fields

from src.core.base import Base


class State(Base):
    ref: fields.UUIDField = fields.UUIDField(null=False)
    ref_type: fields.CharField = fields.CharField(max_length=32, null=False)
    state: fields.CharField = fields.CharField(max_length=32, null=False)
    extra: fields.JSONField[dict | list | None] = fields.JSONField(null=True)

    class Meta:
        ordering = ["ref", "ref_type"]
        unique_together = [("ref", "ref_type")]
        table = "state"
        table_description = "State"

    def __str__(self) -> str:
        return f"[State: {self.ref}, {self.ref_type}, {self.state}]"

    def is_expired(self, delay_s: int) -> bool:
        return (
            datetime.now(UTC) - self.updated_at
        ).total_seconds() > delay_s
