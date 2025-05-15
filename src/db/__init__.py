from fastapi import FastAPI
from tortoise.contrib.fastapi import register_tortoise

from src.core.config import settings

DB_CONFIG = {
    "connections": {
        "default": {
            "engine": "tortoise.backends.mysql",
            "credentials": {
                "host": settings.db_host,
                "port": settings.db_port,
                "database": settings.db_name,
                "user": settings.db_user,
                "password": settings.db_password,
            }
        }
    },
    "apps": {
        "models": {
            "models": ["src.db.models"],
            "default_connection": "default",
        },
        "aerich": {
            "models": ["aerich.models"],
            "default_connection": "default",
        }
    }
}


def init_db(app: FastAPI) -> None:
    register_tortoise(
        app,
        config=DB_CONFIG,
        generate_schemas=False,  # make a decision using settings Env
        add_exception_handlers=True,
    )
