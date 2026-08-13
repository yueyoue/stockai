import enum
from datetime import datetime
from sqlalchemy import Column, Integer, String, Enum, DateTime, Text
from app.core.database import Base


class NewsType(str, enum.Enum):
    STOCK = "个股资讯"
    INDUSTRY = "行业资讯"
    MACRO = "大盘宏观"
    ANNOUNCEMENT = "公告"


class MarketNews(Base):
    __tablename__ = "market_news"

    news_id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(500), nullable=False)
    content = Column(Text, nullable=True)
    news_type = Column(Enum(NewsType), default=NewsType.STOCK)
    related_stock = Column(String(200), nullable=True)
    publish_time = Column(DateTime, nullable=True)
    ai_impact = Column(Text, nullable=True)  # AI分析：利好/中性/利空
    sentiment = Column(String(10), nullable=True)  # 利好/中性/利空
    source = Column(String(100), nullable=True)
    url = Column(String(1000), nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.utcnow())
