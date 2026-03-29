# DMAI — AlphaForge API

AI investment committee backend for disruptive growth stocks.

## Quick Start

### 1. Install dependencies

```bash
pip install fastapi uvicorn anthropic
```

### 2. Set your API key

```bash
export ANTHROPIC_API_KEY="your-api-key"
```

### 3. Activate virtual environment

```
source venv/bin/activate
```

### 4. Start the server

```bash
cd backend
uvicorn main:app --reload
```

The API will be running at `http://127.0.0.1:8000`.

### 5. Explore the docs

Open `http://127.0.0.1:8000/docs` for the interactive Swagger UI.

---

## Watchlist Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/watchlist` | Get all tickers on the watchlist |
| `POST` | `/watchlist` | Add a ticker `{"ticker": "NVDA"}` |
| `DELETE` | `/watchlist/{ticker}` | Remove a ticker |

### Example

```bash
# Add a ticker
curl -X POST "http://127.0.0.1:8000/watchlist" \
  -H "Content-Type: application/json" \
  -d '{"ticker": "NVDA"}'

# Get watchlist
curl "http://127.0.0.1:8000/watchlist"

# Remove a ticker
curl -X DELETE "http://127.0.0.1:8000/watchlist/NVDA"
```

---

## Project Structure

```
backend/
├── main.py                       # FastAPI app entry point
├── data/
│   └── alphaforge.db             # SQLite cache (created on first startup)
├── agents/
│   └── market_intelligence_agent.py  # AI agent (Claude)
└── app/
    ├── models/
    │   ├── company.py
    │   ├── market_data.py        # StockQuote, CompanyProfile, StockSnapshot schemas
    │   └── watchlist.py          # Pydantic schemas
    ├── routers/
    │   ├── market_data.py        # Market data API route handlers
    │   └── watchlist.py          # API route handlers
    └── services/
        ├── cache_db.py           # SQLite cache layer
        ├── market_data_service.py # FMP API calls + cache integration
        └── watchlist_service.py  # Business logic
```

> **Note:** The watchlist is stored in memory and resets on server restart.

---

## Financial Modeling Prep (FMP) API Setup

[Financial Modeling Prep](https://financialmodelingprep.com/developer/docs) is used as the market data provider for company profiles, news, quotes, and historical data.

### 1. Create an FMP account

Sign up at `https://financialmodelingprep.com` and generate your API key.

### Source environment variable bash
```
set -a
source .env
set +a
```

### 2. Set environment variable

```bash
export FMP_API_KEY="your-fmp-api-key"
```

### 3. Base URL

Use this base URL for all requests:

`https://financialmodelingprep.com/stable`

### 4. Sample curl requests

**Get company profile:**
```bash
curl "https://financialmodelingprep.com/stable/profile?symbol=NVDA&apikey=$FMP_API_KEY"
```

**Get latest quote:**
```bash
curl "https://financialmodelingprep.com/stable/quote?symbol=NVDA&apikey=$FMP_API_KEY"
```

**Get recent stock news:**
```bash
curl "https://financialmodelingprep.com/stable/news/stock?symbols=NVDA&limit=5&apikey=$FMP_API_KEY"
```

**Get historical daily prices:**
```bash
curl "https://financialmodelingprep.com/stable/historical-price-eod/full?symbol=NVDA&apikey=$FMP_API_KEY"
```

### 5. Optional Python integration

```python
import os
import requests

api_key = os.getenv("FMP_API_KEY")
url = f"https://financialmodelingprep.com/stable/profile?symbol=NVDA&apikey={api_key}"
data = requests.get(url, timeout=10).json()
print(data)
```

> Note: current agent methods such as `fetch_news` are placeholders. Wire those methods to FMP endpoints when you implement market data ingestion.

---

## SQLite Cache

Stock snapshots are cached locally in a SQLite database to avoid redundant FMP API calls. The cache is populated automatically when a snapshot endpoint is hit.

### How it works

1. `GET /market-data/snapshot/{ticker}` checks the local DB first
2. If a fresh entry exists (within TTL), it is returned immediately — no FMP call made
3. If the entry is missing or expired, FMP is called and the result is saved to the DB

The DB file persists across server restarts. `init_db()` runs on startup and only creates the table if it does not already exist — existing data is never wiped.

### Configuration

| Env var | Default | Description |
|---|---|---|
| `CACHE_DB_PATH` | `backend/data/alphaforge.db` | Path to the SQLite file |
| `SNAPSHOT_CACHE_TTL_SECONDS` | `900` | Seconds before a cached entry is considered stale (default 15 min) |

Add either to your `.env` file to override:

```env
SNAPSHOT_CACHE_TTL_SECONDS=300   # 5 minutes
CACHE_DB_PATH=/tmp/alphaforge.db
```

### Initialise the DB without starting the server

The `data/` directory and `.db` file are created on first server startup. To set them up manually:

```bash
mkdir -p /Users/christine/Projects/DMAI/backend/data
cd /Users/christine/Projects/DMAI/backend
python -c "from app.services.cache_db import init_db; init_db()"
```

### Querying the DB directly

Use the `sqlite3` CLI with the full absolute path:

```bash
sqlite3 /Users/christine/Projects/DMAI/backend/data/alphaforge.db
```

Useful queries:

```sql
-- View all cached snapshots
SELECT * FROM stock_snapshots;

-- View ticker, price, and human-readable cache time
SELECT ticker, price, datetime(cached_at, 'unixepoch', 'localtime') AS cached_at
FROM stock_snapshots;

-- Check how old a specific ticker's cache entry is (in minutes)
SELECT ticker, round((strftime('%s','now') - cached_at) / 60.0, 1) AS age_minutes
FROM stock_snapshots
WHERE ticker = 'AAPL';

-- Clear the entire cache
DELETE FROM stock_snapshots;

-- Exit
.quit
```

Or run a one-liner without entering the shell:

```bash
sqlite3 /Users/christine/Projects/DMAI/backend/data/alphaforge.db "SELECT * FROM stock_snapshots;"
```
