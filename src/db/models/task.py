from datetime import UTC, datetime

from tortoise import fields

from src.core.base import Base
from src.core.types import Action, State


class Task(Base):
    ref: fields.UUIDField = fields.UUIDField(null=False)
    ref_type: fields.CharField = fields.CharField(max_length=32, null=False)
    action: fields.CharEnumField = fields.CharEnumField(
        Action,
        default=Action.UNKNOWN,
    )
    state: fields.CharEnumField = fields.CharEnumField(
        State,
        default=State.UNKNOWN,
    )
    meta: fields.JSONField[dict | list | None] = fields.JSONField(null=True)

    class Meta:
        ordering = ["ref", "ref_type"]
        unique_together = [("ref", "ref_type")]
        table = "task"
        table_description = "Task"

    def __str__(self) -> str:
        return f"[Task: {self.ref}, {self.ref_type}, {self.state}]"

    def is_expired(self, delay_s: int) -> bool:
        return (
            datetime.now(UTC) - self.updated_at
        ).total_seconds() > delay_s
