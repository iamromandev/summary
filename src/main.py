from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.core.common import get_app_version
from src.core.config import settings
from src.core.error import config_global_errors
from src.db import init_db, run_migrations
from src.routes import etl_router
from src.routes.health import health_router


@asynccontextmanager
async def lifespan(fa: FastAPI):
    await run_migrations()
    yield  # startup complete
    # any shutdown code here


app = FastAPI(
    title="Summary Application",
    version=get_app_version(),
    debug=settings.debug,
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

config_global_errors(app)
init_db(app)

app.include_router(health_router)
app.include_router(etl_router)

if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
