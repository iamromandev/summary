from collections.abc import Generator

from fastapi import Depends

from src.repos.url_repo import UrlRepo

from .extract import ExtractService


def get_extract_service(
    url_repo: UrlRepo = Depends()
) -> Generator[ExtractService]:
    yield ExtractService(url_repo)
