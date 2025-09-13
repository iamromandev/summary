import uuid
from datetime import UTC, datetime
from typing import Any

from tortoise import fields

from src.core.base import Base
from src.core.types import Action, State


class Task(Base):
    ref: uuid.UUID = fields.UUIDField()
    ref_type: str = fields.CharField(max_length=32)
    action: Action = fields.CharEnumField(
        Action,
        default=Action.OTHER,
    )
    state: State = fields.CharEnumField(
        State,
        default=State.OTHER,
    )
    meta: dict[str, Any] | list[None] | None = fields.JSONField(null=True, default=None)

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
