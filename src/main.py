from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.core.config import settings
from src.core.error import config_global_errors
from src.db import init_db
from src.routes import etl_router
from src.routes.health import health_router

app = FastAPI(
    title="Summary Application",
    debug=settings.debug
)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health_router)
app.include_router(etl_router)

config_global_errors(app)
init_db(app)

if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
