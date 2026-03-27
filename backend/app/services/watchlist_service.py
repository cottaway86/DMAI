from datetime import datetime
from app.models.watchlist import WatchlistItem

watchlist = []


def get_watchlist() -> list[WatchlistItem]:
    return watchlist


def add_stock(ticker: str) -> WatchlistItem:
    upper = ticker.upper()
    if any(w.ticker == upper for w in watchlist):
        raise ValueError(f"{upper} is already on the watchlist")
    item = WatchlistItem(ticker=upper, date_added=datetime.utcnow())
    watchlist.append(item)
    return item


def remove_stock(ticker: str) -> None:
    global watchlist
    upper = ticker.upper()
    if not any(w.ticker == upper for w in watchlist):
        raise ValueError(f"{upper} not found on watchlist")
    watchlist = [w for w in watchlist if w.ticker != upper]
