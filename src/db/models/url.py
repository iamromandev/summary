import uuid

from tortoise.fields import DatetimeField, UUIDField
from tortoise.models import Model

from ..db_fields import UrlField


class Url(Model):
    id = UUIDField(pk=True, default=uuid.uuid4)
    url = UrlField(null=False)
    base = UrlField(null=True)
    created_at = DatetimeField(auto_now_add=True)
    updated_at = DatetimeField(auto_now=True)

    def __str__(self) -> str:
        return str(self.url)
