"""
StockAI Crawler - 数据采集服务
持续采集研报、资讯、公告，存入数据库
"""
import asyncio
import logging
import os
import sys
from datetime import datetime, timezone
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy import select

# Add parent to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("crawler")

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+asyncpg://stockai:stockai123@localhost:5432/stockai")
engine = create_async_engine(DATABASE_URL, pool_size=5)
async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

# Import after path setup
from sources.eastmoney import EastMoneySource
from sources.news_crawler import NewsCrawler


async def crawl_reports():
    """Crawl research reports from all sources."""
    logger.info("开始采集研报...")
    async with async_session() as db:
        source = EastMoneySource(db)
        count = await source.fetch_reports()
        logger.info(f"本次采集研报: {count} 条")


async def crawl_news():
    """Crawl market news from all sources."""
    logger.info("开始采集资讯...")
    async with async_session() as db:
        source = NewsCrawler(db)
        count = await source.fetch_news()
        logger.info(f"本次采集资讯: {count} 条")


async def main():
    logger.info("StockAI Crawler 启动中...")
    
    # Initial crawl
    await crawl_reports()
    await crawl_news()
    
    # Schedule periodic crawling
    scheduler = AsyncIOScheduler()
    scheduler.add_job(crawl_reports, "interval", minutes=30, id="crawl_reports")
    scheduler.add_job(crawl_news, "interval", minutes=5, id="crawl_news")
    scheduler.start()
    
    logger.info("定时采集任务已启动: 研报每30分钟, 资讯每5分钟")
    
    # Keep running
    try:
        while True:
            await asyncio.sleep(3600)
    except (KeyboardInterrupt, SystemExit):
        scheduler.shutdown()
        logger.info("Crawler 已停止")


if __name__ == "__main__":
    asyncio.run(main())
