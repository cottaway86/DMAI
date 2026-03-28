from __future__ import annotations

from typing import Optional

from pydantic import BaseModel


class StockQuote(BaseModel):
    ticker: str
    price: Optional[float] = None
    market_cap: Optional[float] = None
    currency: Optional[str] = None


class CompanyProfile(BaseModel):
    ticker: str
    name: Optional[str] = None
    sector: Optional[str] = None
    industry: Optional[str] = None


class StockSnapshot(BaseModel):
    ticker: str
    name: Optional[str] = None
    sector: Optional[str] = None
    industry: Optional[str] = None
    price: Optional[float] = None
    market_cap: Optional[float] = None
    pe_ratio: Optional[float] = None
    revenue_growth: Optional[float] = None
