from __future__ import annotations

import logging
import os
import sqlite3
import time
from pathlib import Path

from app.models.market_data import StockSnapshot


logger = logging.getLogger(__name__)

_DB_PATH = os.getenv(
    "CACHE_DB_PATH",
    str(Path(__file__).resolve().parents[3] / "data" / "alphaforge.db"),
)
_CACHE_TTL = int(os.getenv("SNAPSHOT_CACHE_TTL_SECONDS", "900"))  # 15 minutes default


def _connect() -> sqlite3.Connection:
    Path(_DB_PATH).parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(_DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    """Create the stock_snapshots cache table if it does not exist."""
    with _connect() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS stock_snapshots (
                ticker        TEXT PRIMARY KEY,
                name          TEXT,
                sector        TEXT,
                industry      TEXT,
                price         REAL,
                market_cap    REAL,
                pe_ratio      REAL,
                revenue_growth REAL,
                cached_at     REAL NOT NULL
            )
            """
        )
    logger.info("Cache DB initialised", extra={"db_path": _DB_PATH, "ttl_seconds": _CACHE_TTL})


def get_cached_snapshot(ticker: str) -> StockSnapshot | None:
    """Return a cached snapshot if one exists and has not expired."""
    with _connect() as conn:
        row = conn.execute(
            "SELECT * FROM stock_snapshots WHERE ticker = ?", (ticker,)
        ).fetchone()

    if row is None:
        logger.debug("Cache miss", extra={"ticker": ticker})
        return None

    age = time.time() - row["cached_at"]
    if age > _CACHE_TTL:
        logger.debug("Cache expired", extra={"ticker": ticker, "age_seconds": round(age)})
        return None

    logger.info(
        "Cache hit",
        extra={"ticker": ticker, "age_seconds": round(age), "ttl_seconds": _CACHE_TTL},
    )
    return StockSnapshot(
        ticker=row["ticker"],
        name=row["name"],
        sector=row["sector"],
        industry=row["industry"],
        price=row["price"],
        market_cap=row["market_cap"],
        pe_ratio=row["pe_ratio"],
        revenue_growth=row["revenue_growth"],
    )


def save_snapshot(snapshot: StockSnapshot) -> None:
    """Insert or replace a snapshot, stamping it with the current time."""
    with _connect() as conn:
        conn.execute(
            """
            INSERT OR REPLACE INTO stock_snapshots
                (ticker, name, sector, industry, price, market_cap, pe_ratio, revenue_growth, cached_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                snapshot.ticker,
                snapshot.name,
                snapshot.sector,
                snapshot.industry,
                snapshot.price,
                snapshot.market_cap,
                snapshot.pe_ratio,
                snapshot.revenue_growth,
                time.time(),
            ),
        )
    logger.debug("Snapshot cached", extra={"ticker": snapshot.ticker})
