from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class WatchlistAdd(BaseModel):
    stock_code: str = Field(..., max_length=20)
    stock_name: str = Field(..., max_length=50)
    market_type: str = Field(default="A股", max_length=10)


class WatchlistBatchAdd(BaseModel):
    stocks: List[WatchlistAdd]


class WatchlistResponse(BaseModel):
    id: int
    stock_code: str
    stock_name: str
    market_type: str
    add_time: Optional[datetime] = None

    class Config:
        from_attributes = True


class StockNewsResponse(BaseModel):
    news_id: int
    title: str
    news_type: Optional[str] = None
    publish_time: Optional[datetime] = None
    ai_impact: Optional[str] = None
    sentiment: Optional[str] = None
    source: Optional[str] = None

    class Config:
        from_attributes = True


class StockReportResponse(BaseModel):
    report_id: int
    title: str
    source: Optional[str] = None
    report_type: Optional[str] = None
    publish_time: Optional[datetime] = None
    ai_summary: Optional[str] = None

    class Config:
        from_attributes = True
