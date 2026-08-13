import enum
from datetime import datetime
from sqlalchemy import Column, Integer, String, Enum, DateTime, Text
from app.core.database import Base


class ReportType(str, enum.Enum):
    STOCK = "个股研报"
    INDUSTRY = "行业研报"
    MACRO = "大盘宏观研报"


class ResearchReport(Base):
    __tablename__ = "research_report"

    report_id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(500), nullable=False)
    source = Column(String(100), nullable=True)
    report_type = Column(Enum(ReportType), default=ReportType.STOCK)
    related_stock = Column(String(200), nullable=True)  # comma-separated stock codes
    industry = Column(String(100), nullable=True)
    publish_time = Column(DateTime, nullable=True)
    file_path = Column(String(500), nullable=True)
    ai_summary = Column(Text, nullable=True)
    url = Column(String(1000), nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.utcnow())
