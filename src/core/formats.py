import uuid
from datetime import UTC, date, datetime, time
from enum import Enum
from typing import Any

from pydantic import BaseModel, HttpUrl, RedisDsn, SecretStr, WebsocketUrl


def exclude_empty(data: dict) -> dict:
    return {k: v for k, v in data.items() if v not in (None, "", (), [], {})}


def utc_iso_timestamp() -> str:
    return datetime.now(UTC).isoformat().replace("+00:00", "Z")


def serialize(obj: Any, instructions: dict[type, type] | None = None) -> Any:
    if instructions:
        for key, value in instructions.items():
            if isinstance(obj, key):
                return value(obj)

    if isinstance(obj, HttpUrl | RedisDsn | WebsocketUrl):
        return str(obj).strip("/")
    elif isinstance(obj, BaseModel):
        return serialize(obj.model_dump())

    elif isinstance(obj, dict):
        return {key: serialize(value) for key, value in obj.items()}

    elif isinstance(obj, list | tuple | set):
        return [serialize(item) for item in obj]

    elif isinstance(obj, Enum):
        return obj.value

    elif isinstance(obj, datetime | date | time):
        return obj.isoformat()

    elif isinstance(obj, uuid.UUID | SecretStr):
        return str(obj)

    elif hasattr(obj, "__dict__"):
        # For ORM objects like Tortoise, SQLAlchemy, etc.
        return serialize(obj.__dict__)

    elif isinstance(obj, str | int | float | bool) or obj is None:
        return obj  # Native JSON types

    else:
        raise TypeError(f"Object of type {type(obj)} is not serializable")
