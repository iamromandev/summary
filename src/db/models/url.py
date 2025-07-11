
from tortoise import fields

from src.core.base import Base
from src.db.validators import UrlValidator


class Url(Base):
    url: str = fields.CharField(
        max_length=2048, unique=True, null=False, validators=[UrlValidator()]
    )
    base_url: str | None = fields.CharField(max_length=2048, null=True)
    title: str | None = fields.CharField(max_length=256, null=True)

    class Meta:
        ordering = ["url"]
        table = "url"
        table_description = "Url"

    def __str__(self) -> str:
        return f"[Url: url - {self.url}, base_url - {self.base_url}, title - {self.title}]"
