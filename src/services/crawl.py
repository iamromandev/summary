from typing import Any

import httpx
from loguru import logger
from pydantic import HttpUrl

import src.core.common as common
from src.core.base import BaseService
from src.core.clients import HttpClientFactory, SoupClient
from src.core.formats import clean_url, serialize
from src.core.types import Action, ModelType, State
from src.db.models import Raw, Task, Url
from src.repos import RawRepo, TaskRepo, UrlRepo


class CrawlService(BaseService):
    _http_client_factory: HttpClientFactory
    _soup_client: SoupClient
    _task_repo: TaskRepo
    _url_repo: UrlRepo
    _raw_repo: RawRepo

    def __init__(
        self,
        http_client_factory: HttpClientFactory,
        soup_client: SoupClient,
        task_repo: TaskRepo,
        url_repo: UrlRepo,
        raw_repo: RawRepo,
        crawl_base_url: HttpUrl,
        crawl_url_expiration: int
    ) -> None:
        super().__init__()
        self._http_client_factory = http_client_factory
        self._soup_client = soup_client
        self._task_repo = task_repo
        self._url_repo = url_repo
        self._raw_repo = raw_repo
        self._crawl_url = HttpUrl(f"{crawl_base_url}crawl")
        self._crawl_url_expiration = crawl_url_expiration

    async def _ensure_url_task_status(self, url: HttpUrl, delay_s: int = 3600) -> tuple[Url, Task, bool]:
        base_url = serialize(common.get_base_url(url))
        url_str = serialize(url)

        # Get or create the URL
        db_url, url_created = await self._url_repo.get_or_create(
            url=url_str,
            base_url=base_url,
        )

        # Try to get existing task
        db_task = await self._task_repo.get_or_none(
            ref=db_url.pk,
            ref_type=ModelType.URL,
        )

        # If no task exists or URL is newly created, create task
        if db_task is None:
            db_task = await self._task_repo.create(
                ref=db_url.pk,
                ref_type=ModelType.URL,
                state=State.NEW,
                action=Action.UNKNOWN,
            )
            return db_url, db_task, True

        # Task exists — check if it's NEW or expired
        return db_url, db_task, db_task.state == State.NEW or db_task.is_expired(delay_s)

    async def _find_next_url_task(self) -> tuple[Url | None, Task | None]:
        logger.debug(f"{self._tag}|_find_next_url_task()")

        # Step 1: Try finding a NEW, RUNNING task first
        states = [State.NEW, State.RUNNING]
        next_task = await self._task_repo.get_first_by_states(
            ref_type=ModelType.URL,
            states=states,
        )
        logger.debug(f"{self._tag}|_find_next_url_task()| NEW task: {next_task}")

        # Step 2: If no NEW task, look for expired ones
        if not next_task:
            next_task = await self._task_repo.get_first_expired(
                ref_type=ModelType.URL,
                expire_after_s=self._crawl_url_expiration
            )
            if next_task:
                logger.debug(f"{self._tag}|_find_next_url_task()| Expired task: {next_task.id}")

        # Step 3: Get the associated URL
        if next_task:
            url = await self._url_repo.get_by_pk(next_task.ref)
            if url:
                return url, next_task

        return None, None

    async def _store_new_extracted_urls(self, urls: list[HttpUrl]) -> None:
        logger.debug(f"{self._tag}|_store_new_extracted_urls(): Storing {len(urls)} extracted URLs")

        for extracted_url in urls:
            base_url = serialize(common.get_base_url(extracted_url))
            url_str = serialize(extracted_url)

            # Create or get the Url entry
            db_url, url_created = await self._url_repo.get_or_create(
                url=url_str,
                base_url=base_url,
            )

            # Create task only if URL was newly created or no task exists
            db_task = await self._task_repo.get_or_none(
                ref=db_url.pk,
                ref_type=ModelType.URL,
            )

            if db_task is None:
                await self._task_repo.create(
                    ref=db_url.pk,
                    ref_type=ModelType.URL,
                    state=State.NEW,
                )

    async def crawl(self, url: HttpUrl) -> None:
        url = clean_url(url)
        logger.debug(f"{self._tag}|crawl(): Starting crawl for {url}")
        next_db_url, next_db_task, task_status = await self._ensure_url_task_status(url)

        logger.debug(f"{self._tag}|crawl(): _ensure_url_task_status: {next_db_url.url} {task_status}")

        if not task_status:
            next_db_url, next_db_task = await self._find_next_url_task()

        logger.debug(f"{self._tag}|crawl(): next_db_url: {next_db_url}")

        while next_db_url and next_db_task:
            await self._task_repo.update_by_id(
                task_id=next_db_task.id,
                action=Action.CRAWL,
                state=State.RUNNING
            )
            url = HttpUrl(next_db_url.url)
            logger.debug(f"{self._tag}|crawl(): Crawling Server URL: {self._crawl_url}")
            http_client = self._http_client_factory.get_client(
                url=self._crawl_url
            )
            try:
                params = {"url": HttpUrl(next_db_url.url)}
                content: dict[str, Any] = await http_client.get(
                    url=self._crawl_url, params=params,
                )
            except httpx.ConnectError as error:
                logger.error(f"{self._tag}|crawl(): Connection error fetching {url}: {error}")
                await self._task_repo.update_by_id(
                    task_id=next_db_task.id,
                    action=Action.CRAWL,
                    state=State.FAILED
                )
                next_db_url, next_db_task = await self._find_next_url_task()
                continue
            except httpx.ReadTimeout as error:
                logger.error(f"{self._tag}|crawl(): Timeout fetching {url}: {error}")
                await self._task_repo.update_by_id(
                    task_id=next_db_task.id,
                    action=Action.CRAWL,
                    state=State.TIMEOUT
                )
                next_db_url, next_db_task = await self._find_next_url_task()
                continue
            logger.debug(f"{self._tag}|crawl(): Fetched content from {url}")
            html = common.safely_deep_get(content,keys= "data.html")
            urls = common.safely_deep_get(content, keys="data.urls", default=[])
            if urls:
                await self._store_new_extracted_urls(urls)
            if not html:
                logger.error(f"{self._tag}|crawl(): No HTML content found for {url}")
                await self._task_repo.update_by_id(
                    task_id=next_db_task.id,
                    action=Action.CRAWL,
                    state=State.FAILED
                )
                next_db_url, next_db_task = await self._find_next_url_task()
                continue

            raw: Raw = await  self._raw_repo.create_or_update(
                url=next_db_url,
                content=html,
                meta={
                    "size": len(html.encode("utf-8")),
                }
            )
            logger.debug(f"{self._tag}|crawl(): Raw content saved: {raw}")
            await self._task_repo.update_by_id(
                task_id=next_db_task.id,
                action=Action.CRAWL,
                state=State.COMPLETED
            )
            next_db_url, next_db_task = await self._find_next_url_task()
            logger.debug(f"{self._tag}|crawl(): Extracted URLs: {urls}")

        return None
