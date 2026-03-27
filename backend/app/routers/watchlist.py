from fastapi import APIRouter, HTTPException
from app.models.watchlist import WatchlistItem, WatchlistCreate
from app.services.watchlist_service import get_watchlist, add_stock, remove_stock

router = APIRouter(prefix="/watchlist", tags=["watchlist"], redirect_slashes=False)


@router.get("/", response_model=list[WatchlistItem])
def read_watchlist():
    return get_watchlist()


@router.post("/", response_model=WatchlistItem, status_code=201)
def create_watchlist_item(body: WatchlistCreate):
    try:
        return add_stock(body.ticker)
    except ValueError as e:
        raise HTTPException(status_code=409, detail=str(e))


@router.delete("/{ticker}", status_code=204)
def delete_watchlist_item(ticker: str):
    try:
        remove_stock(ticker)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
