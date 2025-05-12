
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # core
    env: str = Field(...)
    debug: bool = Field(...)
    # db
    db_root_password: str = Field(...)
    db_name: str = Field(...)
    db_user: str = Field(...)
    db_password: str = Field(...)
    db_host: str = Field(...)
    db_port: int = Field(...)

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="allow"
    )


settings = Settings()
