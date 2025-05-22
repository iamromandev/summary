from functools import cached_property

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

from .types import Env


class Settings(BaseSettings):
    # core
    env: Env = Field(...)
    debug: bool = Field(...)
    # cache
    redis_host: str = Field(...)
    redis_port: int = Field(...)
    # db
    db_host: str = Field(...)
    db_port: int = Field(...)
    db_name: str = Field(...)
    db_user: str = Field(...)
    db_password: str = Field(...)
    db_root_password: str = Field(...)

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="allow"
    )

    @property
    def is_prod(self) -> bool:
        return self.env == Env.PROD

    @cached_property
    def cache_url(self) -> str:
        return f"redis://{settings.redis_host}:{settings.redis_port}/0"

    @cached_property
    def db_url(self) -> str:
        return f"{self.db_connection}://{self.db_user}:{self.db_password}@{self.db_host}:{self.db_port}/{self.db_name}"



settings = Settings()
