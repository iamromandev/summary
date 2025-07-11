from functools import cached_property
from urllib.parse import quote_plus

from pydantic import Field, RedisDsn, WebsocketUrl
from pydantic_settings import BaseSettings, SettingsConfigDict

from .types import Env


class Settings(BaseSettings):
    # core
    env: Env = Field(...)
    debug: bool = Field(...)
    # db
    db_host: str = Field(...)
    db_port: int = Field(...)
    db_name: str = Field(...)
    db_user: str = Field(...)
    db_password: str = Field(...)
    db_root_password: str = Field(...)
    # cache
    cache_connection: str = Field(...)
    cache_host: str = Field(...)
    cache_port: int = Field(...)
    cache_user: str = Field(...)
    cache_password: str = Field(...)
    # playwright
    playwright_connection: str = Field(...)
    playwright_host: str = Field(...)
    playwright_port: int = Field(...)
    playwright_headless: bool = Field(...)
    playwright_user_agent: str = Field(...)

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
    def playwright_url(self) -> WebsocketUrl:
        return WebsocketUrl.build(
            scheme=self.playwright_connection,
            host=self.playwright_host,
            port=self.playwright_port,
        )


settings = Settings()
