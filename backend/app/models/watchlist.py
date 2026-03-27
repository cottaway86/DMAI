from pydantic import BaseModel, field_validator
from datetime import datetime


class WatchlistItem(BaseModel):
    ticker: str
    date_added: datetime


class WatchlistCreate(BaseModel):
    ticker: str

    @field_validator("ticker")
    @classmethod
    def validate_ticker(cls, v: str) -> str:
        v = v.strip().upper()
        if not v:
            raise ValueError("ticker cannot be empty")
        if len(v) > 10:
            raise ValueError("ticker must be 10 characters or fewer")
        return v
