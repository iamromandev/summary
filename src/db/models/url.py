import uuid

from tortoise.fields import CharField, DatetimeField, UUIDField
from tortoise.models import Model


class Url(Model):
    id = UUIDField(pk=True, default=uuid.uuid4)
    url = CharField(max_length=4096, null=False, unique=True)
    base = CharField(max_length=2048, null=True)
    created_at = DatetimeField(auto_now_add=True)
    updated_at = DatetimeField(auto_now=True)

    def __str__(self) -> str:
        return str(self.url)
