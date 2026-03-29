from fastapi import FastAPI
from app.logging_config import setup_logging
from app.routers import market_data, watchlist
from app.services.cache_db import init_db

setup_logging()

app = FastAPI(
    title="AlphaForge API",
    version="0.1.0",
    description="AI investment committee backend for disruptive growth stocks.",
    redirect_slashes=False,
)

init_db()

app.include_router(watchlist.router)
app.include_router(market_data.router)


@app.get("/")
def read_root():
    return {"message": "AlphaForge API is running"}

@app.get("/health")
def health_check():
    return {"status": "ok"}