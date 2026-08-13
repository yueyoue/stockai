from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class ReportResponse(BaseModel):
    report_id: int
    title: str
    source: Optional[str] = None
    report_type: Optional[str] = None
    related_stock: Optional[str] = None
    industry: Optional[str] = None
    publish_time: Optional[datetime] = None
    ai_summary: Optional[str] = None
    url: Optional[str] = None
    has_pdf: bool = False

    class Config:
        from_attributes = True


class ReportListResponse(BaseModel):
    total: int
    items: List[ReportResponse]


class NewsResponse(BaseModel):
    news_id: int
    title: str
    content: Optional[str] = None
    news_type: Optional[str] = None
    related_stock: Optional[str] = None
    publish_time: Optional[datetime] = None
    ai_impact: Optional[str] = None
    sentiment: Optional[str] = None
    source: Optional[str] = None
    url: Optional[str] = None

    class Config:
        from_attributes = True


class NewsListResponse(BaseModel):
    total: int
    items: List[NewsResponse]
