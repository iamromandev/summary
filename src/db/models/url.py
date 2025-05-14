
from tortoise import fields

from ..validators import UrlValidator
from .base import Base


class Url(Base):
    url = fields.CharField(max_length=2048, unique=True, null=False, validators=[UrlValidator()])
    base = fields.CharField(max_length=2048, null=True)

    class Meta:
        ordering = ["url"]

    def __str__(self) -> str:
        return str(self.url)
