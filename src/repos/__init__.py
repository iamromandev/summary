from collections.abc import AsyncGenerator

from .data import DataRepo
from .task import TaskRepo
from .url import UrlRepo


async def get_task_repo() -> AsyncGenerator[TaskRepo]:
    yield TaskRepo()

async def get_url_repo() -> AsyncGenerator[UrlRepo]:
    yield UrlRepo()

async def get_data_repo() -> AsyncGenerator[DataRepo]:
    yield DataRepo()