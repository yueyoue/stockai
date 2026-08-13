"""
东方财富研报采集器
"""
import logging
import httpx
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)


class EastMoneySource:
    """东方财富研报数据源"""
    
    # 东方财富研报列表API
    REPORT_API = "https://reportapi.eastmoney.com/report/list"
    REPORT_SEARCH = "https://search-api-web.eastmoney.com/search/jsonp"
    
    HEADERS = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Referer": "https://data.eastmoney.com/",
    }
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def fetch_reports(self, page_size: int = 50) -> int:
        """Fetch research reports from EastMoney API."""
        # Import models - use string import to avoid circular deps
        import sys, os
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
        from app.models.research_report import ResearchReport, ReportType
        
        count = 0
        params = {
            "industryCode": "*",
            "pageSize": str(page_size),
            "industry": "*",
            "rating": "*",
            "ratingChange": "*",
            "beginTime": "",
            "endTime": "",
            "pageNo": "1",
            "fields": "",
            "qType": "0",
            "orgCode": "",
            "rcode": "",
            "researcher": "",
            "order": "publishDate",
            "sort": "desc",
        }
        
        try:
            async with httpx.AsyncClient(timeout=30) as client:
                resp = await client.get(self.REPORT_API, params=params, headers=self.HEADERS)
                if resp.status_code != 200:
                    logger.error(f"EastMoney API error: {resp.status_code}")
                    return 0
                
                data = resp.json()
                reports = data.get("data", [])
                
                for item in reports:
                    title = item.get("title", "")
                    if not title:
                        continue
                    
                    # Check duplicate
                    existing = await self.db.execute(
                        select(ResearchReport).where(ResearchReport.title == title)
                    )
                    if existing.scalar_one_or_none():
                        continue
                    
                    # Parse report type
                    report_type = ReportType.STOCK
                    if "行业" in title:
                        report_type = ReportType.INDUSTRY
                    elif "宏观" in title or "策略" in title:
                        report_type = ReportType.MACRO
                    
                    publish_time = None
                    if item.get("publishDate"):
                        try:
                            publish_time = datetime.fromisoformat(item["publishDate"].replace("Z", "+00:00"))
                        except:
                            pass
                    
                    report = ResearchReport(
                        title=title,
                        source=item.get("orgSName", "东方财富"),
                        report_type=report_type,
                        related_stock=item.get("stockCode", ""),
                        industry=item.get("industryName", ""),
                        publish_time=publish_time,
                        url=item.get("infoCode", ""),
                    )
                    self.db.add(report)
                    count += 1
                
                await self.db.commit()
                logger.info(f"东方财富研报采集完成: {count} 条新增")
                
        except Exception as e:
            logger.error(f"东方财富研报采集失败: {e}")
            await self.db.rollback()
        
        return count
