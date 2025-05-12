from typing import NoReturn

from fastapi import FastAPI
from tortoise.contrib.fastapi import register_tortoise

DB_CONFIG = {
    "connections": {
        "default": {
            "engine": "tortoise.backends.mysql"
        }
    },
    "apps": {

    }
}


def init_db(app: FastAPI) -> NoReturn:
    register_tortoise(
        app,
        config=DB_CONFIG
    )
