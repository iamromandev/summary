from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from core.scraper import get_raw_text
from core.constants import WEB_URL

app = FastAPI(title="Summary Application")

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    return {"message": "Welcome to the Root!"}


@app.get("/home", tags=["home"])
async def home():
    return {"message": "This is the home page"}


@app.get("/scrape", tags=["scrape"])
async def scrape():
    text: str | None = await get_raw_text(WEB_URL)
    return {"body": text or ""}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
