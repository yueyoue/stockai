"""
财经资讯采集器
多源采集：东方财富、新浪财经等
"""
import logging
import httpx
import uuid
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)


class NewsCrawler:
    """财经新闻采集器"""
    
    # 东方财富财经新闻API
    NEWS_API = "https://np-listapi.eastmoney.com/comm/web/getNewsByColumns"
    
    HEADERS = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Referer": "https://finance.eastmoney.com/",
    }
    
    # 栏目ID
    COLUMNS = {
        "350": "大盘宏观",
        "35": "个股资讯",
        "36": "行业资讯",
    }
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def fetch_news(self) -> int:
        """Fetch market news from multiple sources."""
        from app.models.market_news import MarketNews, NewsType
        
        total_count = 0
        
        for column_id, column_name in self.COLUMNS.items():
            count = await self._fetch_eastmoney_news(column_id, column_name)
            total_count += count
        
        logger.info(f"资讯采集完成: {total_count} 条新增")
        return total_count
    
    async def _fetch_eastmoney_news(self, column_id: str, column_name: str) -> int:
        """Fetch news from EastMoney by column."""
        from app.models.market_news import MarketNews, NewsType
        
        count = 0
        params = {
            "client": "web",
            "biz": "web_news_col",
            "column": column_id,
            "order": "1",
            "needInteractData": "0",
            "page_index": "1",
            "page_size": "30",
            "req_trace": str(uuid.uuid4()),
        }
        
        try:
            async with httpx.AsyncClient(timeout=30) as client:
                resp = await client.get(self.NEWS_API, params=params, headers=self.HEADERS)
                if resp.status_code != 200:
                    logger.error(f"News API error for column {column_id}: {resp.status_code}")
                    return 0
                
                data = resp.json()
                news_list = data.get("data", {})
                if news_list is None:
                    logger.warning(f"No data for column {column_id}")
                    return 0
                
                # Handle both list and dict response formats
                if isinstance(news_list, dict):
                    news_list = news_list.get("list", [])
                elif not isinstance(news_list, list):
                    logger.warning(f"Unexpected data format for column {column_id}: {type(news_list)}")
                    return 0
                
                for item in news_list:
                    title = item.get("title", "").strip()
                    if not title:
                        continue
                    
                    # Check duplicate
                    existing = await self.db.execute(
                        select(MarketNews).where(MarketNews.title == title)
                    )
                    if existing.scalar_one_or_none():
                        continue
                    
                    # Determine news type
                    news_type = NewsType.MACRO
                    if column_name == "个股资讯":
                        news_type = NewsType.STOCK
                    elif column_name == "行业资讯":
                        news_type = NewsType.INDUSTRY
                    
                    publish_time = None
                    if item.get("showTime"):
                        try:
                            publish_time = datetime.strptime(item["showTime"], "%Y-%m-%d %H:%M:%S")
                        except:
                            pass
                    
                    news = MarketNews(
                        title=title,
                        content=item.get("digest", ""),
                        news_type=news_type,
                        related_stock=self._extract_stock_code(item),
                        publish_time=publish_time,
                        source=item.get("source", "东方财富"),
                        url=item.get("url", ""),
                    )
                    self.db.add(news)
                    count += 1
                
                await self.db.commit()
                logger.info(f"东方财富资讯 ({column_name}): {count} 条新增")
                
        except Exception as e:
            logger.error(f"东方财富资讯采集失败 (column {column_id}): {e}")
            await self.db.rollback()
        
        return count
    
    def _extract_stock_code(self, item: dict) -> str:
        """Extract stock code from news item."""
        code = item.get("stockCode", "") or item.get("code", "")
        if code:
            return code
        
        import re
        title = item.get("title", "") + item.get("digest", "")
        match = re.search(r'[036]\d{5}', title)
        return match.group(0) if match else ""
