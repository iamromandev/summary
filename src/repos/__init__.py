from collections.abc import AsyncGenerator

from .raw import RawRepo
from .task import TaskRepo
from .url import UrlRepo


async def get_state_repo() -> AsyncGenerator[TaskRepo]:
    yield TaskRepo()

async def get_url_repo() -> AsyncGenerator[UrlRepo]:
    yield UrlRepo()

async def get_raw_repo() -> AsyncGenerator[RawRepo]:
    yield RawRepo()