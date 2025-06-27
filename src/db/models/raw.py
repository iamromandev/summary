from tortoise import fields

from src.core.base import Base
from src.db.models import Url


class Raw(Base):
    url: fields.ForeignKeyRelation["Url"] = fields.ForeignKeyField(
        model_name="models.Url", related_name="raws", on_delete=fields.CASCADE
    )
    html = fields.TextField(null=False, description="HTML content of the raw data")

    class Meta:
        ordering = ["-created_at"]
        table = "raw"
        table_description = "Raw"

    def __str__(self) -> str:
        return f"[Raw: url - {self.url.url}, created_at - {self.created_at}]"
