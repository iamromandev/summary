import asyncio

from fastapi import FastAPI
from loguru import logger
from tortoise import Tortoise
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

async def run_migrations() -> None:
    process = await asyncio.create_subprocess_exec(
        "aerich", "upgrade",
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    stdout, stderr = await process.communicate()

    if process.returncode != 0:
        logger.debug(f"Aerich failed with error:\n{stderr.decode().strip()}")
    else:
        logger.debug(f"Aerich succeeded:\n{stdout.decode().strip()}")

async def get_db_health() -> bool:
    try:
        await Tortoise.get_connection("default").execute_script("SELECT 1;")
        return True
    except Exception as error:
        logger.error(f"Error|get_db_health(): {str(error)}")
        return False
