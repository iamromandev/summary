from collections.abc import Generator

from .extract import ExtractService


def get_extract_service()-> Generator[ExtractService]:
    yield ExtractService()