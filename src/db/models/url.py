from tortoise import fields

from src.core.base import Base
from src.db.validators import UrlValidator


class Url(Base):
    url: fields.CharField = fields.CharField(
        max_length=2048, unique=True, null=False, validators=[UrlValidator()]
    )
    base_url: fields.CharField = fields.CharField(max_length=2048, null=True)
    title: fields.CharField = fields.CharField(max_length=256, null=True)
    meta: fields.JSONField[dict | list | None] = fields.JSONField(null=True)

    class Meta:
        ordering = ["url"]
        table = "url"
        table_description = "Url"

    def __str__(self) -> str:
        return f"[Url: url - {self.url}, base_url - {self.base_url}, title - {self.title}]"
