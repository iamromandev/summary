from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger

from src.core.config import settings
from src.db import init_db
from src.routes.etl import router as etl_router

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

app.include_router(etl_router)

init_db(app)


@app.on_event("startup")
async def startup() -> None:
    logger.info("Starting up...")
    logger.info(f"Settings {settings}")


@app.on_event("shutdown")
async def shutdown() -> None:
    logger.info("Shutting down...")


@app.get("/")
async def root():
    return {"message": "Welcome to the Root!"}


@app.get("/home", tags=["home"])
async def home():
    return {"message": "This is the home page"}


@app.get("/scrape", tags=["scrape"])
async def scrape():
    text: str | None = "await get_raw_text(WEB_URL)"
    return {"body": text or ""}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
