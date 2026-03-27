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

### 3. Start the server

```bash
cd backend
uvicorn main:app --reload
```

The API will be running at `http://127.0.0.1:8000`.

### 4. Explore the docs

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
├── agents/
│   └── market_intelligence_agent.py  # AI agent (Claude)
└── app/
    ├── models/
    │   ├── company.py
    │   └── watchlist.py          # Pydantic schemas
    ├── routers/
    │   └── watchlist.py          # API route handlers
    └── services/
        └── watchlist_service.py  # Business logic
```

> **Note:** The watchlist is stored in memory and resets on server restart.

---

## Alpaca Market Data Setup

[Alpaca](https://alpaca.markets) is used as the market data provider for news, quotes, and bars.

### 1. Get your keys

Sign up at `https://alpaca.markets` and retrieve your keys from the dashboard:

- **API Key ID** — e.g. `PKXXXXXXXXXXXXXXXX`
- **Secret Key** — e.g. `xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx`

### 2. Set environment variables

```bash
export ALPACA_API_KEY="your-api-key-id"
export ALPACA_SECRET_KEY="your-secret-key"
```

### 3. Base URLs

| Data type | Base URL |
|-----------|----------|
| Market data (stocks) | `https://data.alpaca.markets` |
| Trading / account | `https://api.alpaca.markets` |
| Paper trading | `https://paper-api.alpaca.markets` |

### 4. Sample curl requests

**Get latest news for a ticker:**
```bash
curl -X GET "https://data.alpaca.markets/v1beta1/news?symbols=NVDA&limit=5" \
  -H "APCA-API-KEY-ID: $APCA_API_KEY_ID" \
  -H "APCA-API-SECRET-KEY: $APCA_API_SECRET_KEY"
```

**Get latest quote for a ticker:**
```bash
curl -X GET "https://data.alpaca.markets/v2/stocks/NVDA/quotes/latest" \
  -H "APCA-API-KEY-ID: $APCA_API_KEY_ID" \
  -H "APCA-API-SECRET-KEY: $APCA_API_SECRET_KEY"
```

**Get daily bars (OHLCV) for a ticker:**
```bash
curl -X GET "https://data.alpaca.markets/v2/stocks/NVDA/bars?timeframe=1Day&limit=10" \
  -H "APCA-API-KEY-ID: $APCA_API_KEY_ID" \
  -H "APCA-API-SECRET-KEY: $APCA_API_SECRET_KEY"
```

### 5. Install the Python SDK (optional)

```bash
pip install alpaca-py
```
