from pydantic import Field
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

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="allow"
    )

    @property
    def is_prod(self) -> bool:
        return self.env == Env.PROD


settings = Settings()
