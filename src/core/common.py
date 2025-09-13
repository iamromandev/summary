import hashlib
import json
import re
from collections.abc import Mapping, Sequence
from datetime import UTC, datetime
from pathlib import Path
from typing import Annotated, Any, TypeVar
from urllib.parse import urlparse

import redis.asyncio as redis
import toml
from bs4 import BeautifulSoup
from pydantic import Field, HttpUrl

from src.core.clients import CacheClient
from src.core.formats import serialize

K = TypeVar("K")
V = TypeVar("V")
T = TypeVar("T")
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
        port=parsed_url.port,  # optional
        path=""  # empty path
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


def current_timestamp(format: str | None = None) -> str:
    # "%Y%m%d%H%M%S"
    dt = datetime.now(UTC)
    timestamp = dt.strftime(format) if format else dt.isoformat()
    return timestamp


def safely_deep_get(
    data: Mapping[K, V] | Sequence[V] | object,
    keys: str,
    default: T | None = None,
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


def html_to_json(url: HttpUrl, html: str) -> dict[str, Any]:
    """
    Convert arbitrary HTML to JSON with:
    - structured fields (headings, paragraphs, lists, tables, links, images)
    - full_text: flattened text for LLM-friendly processing
    - text_elements: intermediate pieces of extracted text
    - extracted_at: timestamp of extraction
    """

    soup = BeautifulSoup(html, "lxml")

    # Remove noise
    for tag in soup([
        "script",
        "style",
        "noscript",
        "header",
        "footer",
        "nav",
        "aside",
        "form",
        "iframe"
    ]):
        tag.decompose()

    content = {
        "headings": [],
        "paragraphs": [],
        "lists": [],
        "tables": [],
        "links": [],
        "images": [],
        "full_text": "",
        "meta": {
            "url": serialize(url),
            "processed_at": current_timestamp(),
        }
    }

    # Flattened text accumulator
    text_elements = []

    # Extract headings
    for h in soup.find_all(re.compile("^h[1-6]$")):
        text = h.get_text(strip=True)
        if text:
            content["headings"].append(text)
            text_elements.append(text.upper())  # uppercase to highlight headings

    # Extract paragraphs
    for p in soup.find_all("p"):
        text = p.get_text(strip=True)
        if text:
            content["paragraphs"].append(text)
            text_elements.append(text)

    # Extract lists (ul/ol)
    for ul in soup.find_all(["ul", "ol"]):
        items = [li.get_text(strip=True) for li in ul.find_all("li") if li.get_text(strip=True)]
        if items:
            content["lists"].append(items)
            text_elements.append(" • " + " ; ".join(items))  # bullet + join

    # Extract tables
    for table in soup.find_all("table"):
        rows = []
        table_text_rows = []
        for tr in table.find_all("tr"):
            cells = [td.get_text(strip=True) for td in tr.find_all(["td", "th"]) if td.get_text(strip=True)]
            if cells:
                rows.append(cells)
                table_text_rows.append(" | ".join(cells))
        if rows:
            content["tables"].append(rows)
            text_elements.append("\n".join(table_text_rows))

    # Extract links
    for a in soup.find_all("a", href=True):
        text = a.get_text(strip=True)
        href = a["href"]
        if text or href:
            content["links"].append({"text": text, "href": href})
            text_elements.append(f"{text} ({href})")

    # Extract images
    for img in soup.find_all("img", src=True):
        alt = img.get("alt", "")
        src = img["src"]
        content["images"].append({"alt": alt, "src": src})
        if alt:
            text_elements.append(f"Image: {alt}")

    # Combine all parts into full_text
    full_text = " ".join(text_elements)
    full_text = re.sub(r'\s+', ' ', full_text).strip()
    content["full_text"] = full_text

    return content

def compute_checksum(content: dict[str, Any]) -> str:
    content_str: str = json.dumps(content, sort_keys=True)
    content_bytes: bytes = content_str.encode('utf-8')
    return hashlib.sha256(content_bytes).hexdigest()