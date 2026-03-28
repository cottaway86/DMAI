from fastapi import APIRouter, HTTPException

from app.models.market_data import CompanyProfile, StockQuote, StockSnapshot
from app.services.market_data_service import (
    get_company_profile,
    get_stock_quote,
    get_stock_snapshot,
)

router = APIRouter(prefix="/market-data", tags=["market-data"], redirect_slashes=False)


@router.get("/quote/{ticker}", response_model=StockQuote)
def read_stock_quote(ticker: str):
    try:
        return get_stock_quote(ticker)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    except RuntimeError as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@router.get("/profile/{ticker}", response_model=CompanyProfile)
def read_company_profile(ticker: str):
    try:
        return get_company_profile(ticker)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    except RuntimeError as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@router.get("/snapshot/{ticker}", response_model=StockSnapshot)
def read_stock_snapshot(ticker: str):
    try:
        return get_stock_snapshot(ticker)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    except RuntimeError as exc:
        raise HTTPException(status_code=500, detail=str(exc))
