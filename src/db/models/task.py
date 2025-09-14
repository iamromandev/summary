import uuid
from datetime import UTC, datetime
from typing import Any

from tortoise import fields

from src.core.base import Base
from src.core.types import Action, State


class Task(Base):
    type: str = fields.CharField(max_length=32)
    ref: uuid.UUID = fields.UUIDField()

    state: State = fields.CharEnumField(
        State,
        null=True,
        default=None,
    )
    action: Action | None = fields.CharEnumField(
        Action,
        null=True,
        default=None,
    )
    meta: dict[str, Any] | list[None] | None = fields.JSONField(null=True, default=None)

    class Meta:
        ordering = ["type", "ref"]
        unique_together = [("type", "ref")]
        table = "task"
        table_description = "Task"

    def __str__(self) -> str:
        return f"[Task: {self.type}, {self.ref}, {self.state}]"

    def is_expired(self, delay_s: int) -> bool:
        return (
            datetime.now(UTC) - self.updated_at
        ).total_seconds() > delay_s
