from __future__ import annotations

import json
import logging
import os
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import urlopen

from app.models.market_data import CompanyProfile, StockQuote, StockSnapshot
from app.services.cache_db import get_cached_snapshot, save_snapshot


FMP_BASE_URL = os.getenv(
    "MARKET_DATA_BASE_URL", "https://financialmodelingprep.com/stable"
).rstrip("/")
logger = logging.getLogger(__name__)


def _safe_float(value: object) -> float | None:
    if value is None:
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        logger.debug("Failed to parse numeric value", extra={"value": value})
        return None


def _fmp_get(path: str, params: dict[str, object] | None = None) -> object:
    api_key = os.getenv("FMP_API_KEY")
    if not api_key:
        raise RuntimeError("FMP_API_KEY is not set")

    query_params = dict(params or {})
    query_params["apikey"] = api_key
    url = f"{FMP_BASE_URL}/{path}?{urlencode(query_params)}"
    redacted_query_params = dict(query_params)
    redacted_query_params["apikey"] = "***"
    logger.debug(
        "Calling FMP endpoint",
        extra={"path": path, "params": redacted_query_params},
    )

    try:
        with urlopen(url, timeout=10) as response:
            payload = response.read().decode("utf-8")
            logger.debug("Received response from FMP", extra={"path": path})
            return json.loads(payload)
    except HTTPError as exc:
        logger.warning(
            "FMP HTTP error",
            extra={"path": path, "status_code": exc.code},
        )
        if exc.code == 404:
            raise ValueError("ticker not found") from exc
        raise RuntimeError("Failed to fetch data from FMP") from exc
    except URLError as exc:
        logger.exception("FMP connection error", extra={"path": path})
        raise RuntimeError("Failed to connect to FMP") from exc
    except json.JSONDecodeError as exc:
        logger.exception("FMP returned invalid JSON", extra={"path": path})
        raise RuntimeError("Invalid JSON returned by FMP") from exc


def _first_or_none(payload: object) -> dict[str, object] | None:
    if isinstance(payload, list) and payload:
        first = payload[0]
        if isinstance(first, dict):
            return first
    return None


def get_stock_quote(ticker: str) -> StockQuote:
    symbol = ticker.strip().upper()
    logger.info("Fetching stock quote", extra={"ticker": symbol})
    quote_payload = _fmp_get("quote", {"symbol": symbol})
    quote_data = _first_or_none(quote_payload)
    if not quote_data:
        logger.warning("Quote not found", extra={"ticker": symbol})
        raise ValueError(f"{symbol} not found")

    return StockQuote(
        ticker=symbol,
        price=_safe_float(quote_data.get("price")),
        market_cap=_safe_float(quote_data.get("marketCap")),
        currency=(quote_data.get("currency") or quote_data.get("exchange") or None),
    )


def get_company_profile(ticker: str) -> CompanyProfile:
    symbol = ticker.strip().upper()
    logger.info("Fetching company profile", extra={"ticker": symbol})
    profile_payload = _fmp_get("profile", {"symbol": symbol})
    profile_data = _first_or_none(profile_payload)
    if not profile_data:
        logger.warning("Profile not found", extra={"ticker": symbol})
        raise ValueError(f"{symbol} not found")

    return CompanyProfile(
        ticker=symbol,
        name=profile_data.get("companyName"),
        sector=profile_data.get("sector"),
        industry=profile_data.get("industry"),
    )


def get_stock_snapshot(ticker: str) -> StockSnapshot:
    symbol = ticker.strip().upper()
    logger.info("Fetching stock snapshot", extra={"ticker": symbol})

    cached = get_cached_snapshot(symbol)
    if cached is not None:
        return cached

    quote = get_stock_quote(symbol)
    profile = get_company_profile(symbol)

    ratios_payload = _fmp_get("ratios-ttm", {"symbol": symbol})
    ratios_data = _first_or_none(ratios_payload) or {}

    growth_payload = _fmp_get("financial-growth", {"symbol": symbol, "limit": 1})
    growth_data = _first_or_none(growth_payload) or {}

    pe_ratio = _safe_float(ratios_data.get("peRatioTTM") or ratios_data.get("peRatio"))
    revenue_growth = _safe_float(
        growth_data.get("revenueGrowth") or growth_data.get("growthRevenue")
    )

    snapshot = StockSnapshot(
        ticker=symbol,
        name=profile.name,
        sector=profile.sector,
        industry=profile.industry,
        price=quote.price,
        market_cap=quote.market_cap,
        pe_ratio=pe_ratio,
        revenue_growth=revenue_growth,
    )
    logger.debug("Stock snapshot assembled", extra={"ticker": symbol})
    save_snapshot(snapshot)
    return snapshot
