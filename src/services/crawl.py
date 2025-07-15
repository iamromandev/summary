
from loguru import logger
from pydantic import HttpUrl

import src.core.common as common
from src.core.base import BaseService
from src.core.clients import PlaywrightClient
from src.core.formats import serialize
from src.core.types import Action, ModelType, State
from src.db.models import Raw, Task, Url
from src.repos import RawRepo, TaskRepo, UrlRepo


class CrawlService(BaseService):
    _playwright_client: PlaywrightClient
    _task_repo: TaskRepo
    _url_repo: UrlRepo
    _raw_repo: RawRepo

    def __init__(
        self,
        playwright_client: PlaywrightClient,
        task_repo: TaskRepo,
        url_repo: UrlRepo,
        raw_repo: RawRepo,
        crawl_url_expiration: int
    ) -> None:
        super().__init__()
        self._playwright_client = playwright_client
        self._task_repo = task_repo
        self._url_repo = url_repo
        self._raw_repo = raw_repo
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
            html: str = await self._playwright_client.get_html(url)
            raw: Raw = await  self._raw_repo.create_or_update(
                url=next_db_url,
                html=html,
                meta={
                    "size": len(html.encode("utf-8")),
                }
            )
            logger.debug(f"{self._tag}|crawl(): Raw HTML saved: {raw}")
            await self._task_repo.update_by_id(
                task_id=next_db_task.id,
                action=Action.CRAWL,
                state=State.COMPLETED
            )

            extracted_urls: list[HttpUrl] | None = await self._playwright_client.get_urls(url)
            if extracted_urls:
                await self._store_new_extracted_urls(extracted_urls)

            next_db_url, next_db_task = await self._find_next_url_task()
            logger.debug(f"{self._tag}|crawl(): Extracted URLs: {extracted_urls}")

        return
