from functools import cached_property

from loguru import logger

from src.core.error import Error


class BaseMixins:

    def __init__(self) -> None:
        pass

    @cached_property
    def _tag(self) -> str:
        return self.__class__.__name__

    def log(self, log: str | Error) -> None:
        if isinstance(log, Error):
            logger.error(f"[{self._tag}] {log.message}")
        else:
            logger.info(f"[{self._tag}] {log}")
        