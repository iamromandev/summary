from tortoise import fields

from src.core.base import Base

from .url import Url


class Raw(Base):
    url: "Url" = fields.ForeignKeyField(
        model_name="models.Url",
        related_name="raws",
        on_delete=fields.CASCADE
    )
    content: str = fields.TextField()
    meta: dict | list | None = fields.JSONField(null=True)

    class Meta:
        ordering = ["-created_at"]
        table = "raw"
        table_description = "Raw"

    def __str__(self) -> str:
        return f"[Raw: url - {self.url.url}, created_at - {self.created_at}]"
