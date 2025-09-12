from functools import cached_property
from typing import Annotated
from urllib.parse import quote_plus

from pydantic import Field, HttpUrl, RedisDsn
from pydantic_settings import BaseSettings, SettingsConfigDict

from .types import Env


class Settings(BaseSettings):
    # core
    env: Annotated[Env, Field(description="Application environment")]
    debug: Annotated[bool, Field(description="Enable debug mode")]
    # db
    db_connection: Annotated[str, Field(description="Database connection type")]
    db_host: Annotated[str, Field(description="Database host")]
    db_port: Annotated[int, Field(description="Database port")]
    db_name: Annotated[str, Field(description="Database name")]
    db_user: Annotated[str, Field(description="Database user")]
    db_password: Annotated[str, Field(description="Database password")]
    db_root_password: Annotated[str, Field(description="Root database password")]
    # cache
    cache_connection: Annotated[str, Field(description="Cache connection type")]
    cache_host: Annotated[str, Field(description="Cache host")]
    cache_port: Annotated[int, Field(description="Cache port")]
    cache_user: Annotated[str, Field(description="Cache user")]
    cache_password: Annotated[str, Field(description="Cache password")]
    # crawl
    crawl_server_schema: Annotated[str, Field(description="Crawl server schema")]
    crawl_server_host: Annotated[str, Field(description="Crawl server host")]
    crawl_server_port: Annotated[int, Field(description="Crawl server port")]
    crawl_url_expiration: Annotated[int, Field(description="URL expiration time (seconds)")]
    # httpx
    httpx_connect: Annotated[float, Field(description="HTTPX connect timeout")]
    httpx_read: Annotated[float, Field(description="HTTPX read timeout")]
    httpx_write: Annotated[float, Field(description="HTTPX write timeout")]
    httpx_pool: Annotated[float, Field(description="HTTPX pool timeout")]

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="allow"
    )

    @cached_property
    def is_local(self) -> bool:
        return self.env == Env.LOCAL

    @cached_property
    def is_prod(self) -> bool:
        return self.env == Env.PROD

    @cached_property
    def db_url(self) -> str:
        return f"{self.db_connection}://{self.db_user}:{self.db_password}@{self.db_host}:{self.db_port}/{self.db_name}"

    @cached_property
    def cache_url(self) -> RedisDsn:
        if self.is_local:
            return RedisDsn.build(
                scheme=self.cache_connection,
                host=self.cache_host,
                port=self.cache_port,
            )
        return RedisDsn.build(
            scheme=self.cache_connection,
            host=self.cache_host,
            port=self.cache_port,
            username=self.cache_user,
            password=quote_plus(self.cache_password),
        )

    @cached_property
    def crawl_base_url(self) -> HttpUrl:
        return HttpUrl.build(
            scheme=self.crawl_server_schema,
            host=self.crawl_server_host,
            port=self.crawl_server_port,
        )


settings = Settings()
