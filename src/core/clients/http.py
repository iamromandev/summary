from functools import cached_property
from typing import Any

import httpx
from loguru import logger
from pydantic import HttpUrl

import src.core.common as common
from src.core.config import settings
from src.core.factory import SingletonMeta


class HttpClient:
    _initialized: bool = False
    _client: httpx.AsyncClient

    def __init__(
        self,
        base_url: HttpUrl | None = None,
        headers: dict[str, str] | None = None,
        timeout: httpx.Timeout | float | None = None,
    ) -> None:
        base_url: str = str(base_url).rstrip("/") if base_url else ""
        headers: dict[str, str] | None = headers
        timeout = timeout or httpx.Timeout(
            connect=settings.httpx_connect,
            read=settings.httpx_read,
            write=settings.httpx_write,
            pool=settings.httpx_pool,
        )
        self._client = httpx.AsyncClient(
            base_url=base_url,
            headers=headers,
            timeout=timeout,
            follow_redirects=True,
        )

    @cached_property
    def _tag(self) -> str:
        return self.__class__.__name__

    async def close(self) -> None:
        logger.debug(f"{self._tag}|close(): Closing HTTP client")
        await self._client.aclose()

    async def get(
        self,
        url: HttpUrl,
        params: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
        as_text: bool = False,
    ) -> str | dict[str, Any]:
        path = common.get_path(url)
        logger.debug(
            f"{self._tag}|get(): base_url[{self._client.base_url}] "
            f"path[{path}] full_url[{url}] params[{params}] headers[{headers}]"
        )

        response = await self._client.get(path, params=params, headers=headers)
        response.raise_for_status()

        if as_text:
            content = response.text
            logger.debug(
                f"{self._tag}|get(): status_code[{response.status_code}] "
                f"response_text_length[{len(content)}]"
            )
        else:
            content = response.json()
            logger.debug(
                f"{self._tag}|get(): status_code[{response.status_code}] "
                f"response_json[{content}]"
            )

        return content

    async def post(
        self,
        url: HttpUrl,
        data: dict[str, Any],
        headers: dict[str, str] | None = None,
        as_text: bool = False,
    ) -> str | dict[str, Any]:
        path = common.get_path(url)
        logger.debug(
            f"{self._tag}|post(): base_url[{self._client.base_url}] "
            f"path[{path}] data[{data}] headers[{headers}]"
        )

        response = await self._client.post(path, json=data, headers=headers)
        response.raise_for_status()

        if as_text:
            content = response.text
            logger.debug(
                f"{self._tag}|post(): status_code[{response.status_code}] "
                f"response_text_length[{len(content)}]"
            )
        else:
            content = response.json()
            logger.debug(
                f"{self._tag}|post(): status_code[{response.status_code}] "
                f"response_json[{content}]"
            )

        return content


class HttpClientFactory(metaclass=SingletonMeta):
    _initialized: bool = False
    _clients: dict[HttpUrl, HttpClient]

    def __init__(self) -> None:
        if self._initialized:
            return
        self._clients: dict[HttpUrl, HttpClient] = {}
        self._initialized = True

    @cached_property
    def _tag(self) -> str:
        return self.__class__.__name__

    def get_client(
        self,
        url: HttpUrl,
        headers: dict[str, str] | None = None,
    ) -> HttpClient:
        base_url: HttpUrl = common.get_base_url(url)
        logger.debug(f"{self._tag}|get_client(): base_url[{base_url}]")
        if base_url not in self._clients:
            logger.debug(
                f"{self._tag}|get_client(): Creating new HttpClient for base_url[{base_url}]"
            )
            client = HttpClient(base_url=base_url, headers=headers)
            self._clients[base_url] = client

        return self._clients[base_url]

    async def close_all(self):
        logger.debug(f"{self._tag}|close_all(): Closing all HttpClient instances")
        for client in self._clients.values():
            await client.close()
        self._clients.clear()
