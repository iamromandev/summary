from datetime import UTC, datetime
from pathlib import Path
from typing import Annotated, Any, TypeVar
from urllib.parse import urlparse

import redis.asyncio as redis
import toml
from pydantic import Field, HttpUrl

from src.core.clients import CacheClient
from src.core.formats import serialize

K = TypeVar("K")
V = TypeVar("V")
VarTuple = tuple[V] | tuple[V, V] | tuple[V, V, V]

def get_app_version() -> str:
    try:
        with open("pyproject.toml") as f:
            data = toml.load(f)
            return data['project']['version']
    except FileNotFoundError:
        return "Version information not found"
    except KeyError:
        return "Version key not found in pyproject.toml"


async def get_cache_health(
    cache: Annotated[CacheClient, Field(...)],
) -> bool:
    try:
        await cache.ping()
        await cache.close()
        return True
    except redis.ConnectionError:
        return False


def get_base_url(url: HttpUrl) -> HttpUrl:
    """
    Extracts the base URL from a given URL.

    Parameters:
        url (HttpUrl): The full URL.

    Returns:
        HttpUrl: The base URL (scheme + domain).
    """
    parsed_url = urlparse(serialize(url))
    return HttpUrl.build(
        scheme=parsed_url.scheme,
        host=parsed_url.hostname,  # hostname only, no port
        port=parsed_url.port,      # optional
        path=""                    # empty path
    )


def get_path(url: HttpUrl) -> str:
    """
    Extracts the path and query string from a given URL.

    Parameters:
        url (HttpUrl): The full URL.

    Returns:
        str: The path and query portion of the URL.
    """
    parsed_url = urlparse(serialize(url))
    path = parsed_url.path or "/"
    if parsed_url.query:
        path += f"?{parsed_url.query}"
    return path


def get_file_extension_with_dot(filename: str) -> str | None:
    ext = Path(filename).suffix
    return ext


def get_file_extension(filename: str) -> str | None:
    ext = Path(filename).suffix
    file_extension = ext.lstrip('.') if ext else None
    return file_extension


def current_timestamp(format: str = "%Y%m%d%H%M%S") -> str:
    timestamp = datetime.now(UTC).strftime(format)
    return timestamp

def safely_deep_get(
    data: dict[K, Any] | list[V] | VarTuple[V] | object,
    keys: str,
    default: Any = None,
) -> Any | None:
    """
    Returns a value from nested dictionary/list/tuple/object using dot-separated keys.

    Args:
        data: Nested dictionary, list/tuple, or object.
        keys: Dot-separated keys, e.g., "user.profile.name".
        default: Value to return if key not found. Defaults to None.

    Returns:
        The value at the nested key path or `default` if not found.
    """
    node = data
    for key in keys.split("."):
        if isinstance(node, dict):
            node = node.get(key, None)
        elif isinstance(node, (list, tuple)) and key.isdigit():
            index = int(key)
            node = node[index] if 0 <= index < len(node) else None
        elif hasattr(node, key):
            node = getattr(node, key)
        else:
            return default

        if node is None:
            return default

    return node