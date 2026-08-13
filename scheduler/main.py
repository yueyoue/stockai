"""
StockAI Scheduler - 定时任务调度
负责分时段推送、数据清理等定时任务
"""
import asyncio
import logging
import os
import sys
from datetime import datetime, timezone, timedelta
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
import httpx

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("scheduler")

API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")


async def push_morning_briefing():
    """08:30 开盘前推送"""
    logger.info("执行开盘前推送任务...")
    await _trigger_push("morning")


async def push_intraday_update():
    """盘中增量推送 (09:30-11:30, 13:00-15:00 每30分钟)"""
    logger.info("执行盘中增量推送...")
    await _trigger_push("intraday")


async def push_midday_summary():
    """11:40 午盘推送"""
    logger.info("执行午盘推送...")
    await _trigger_push("midday")


async def push_closing_summary():
    """15:30 盘后总结推送"""
    logger.info("执行盘后总结推送...")
    await _trigger_push("closing")


async def _trigger_push(push_type: str):
    """Trigger push via API."""
    try:
        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.post(
                f"{API_BASE_URL}/api/push/trigger",
                json={"type": push_type},
            )
            if resp.status_code == 200:
                logger.info(f"推送触发成功: {push_type}")
            else:
                logger.error(f"推送触发失败: {resp.status_code}")
    except Exception as e:
        logger.error(f"推送触发异常: {e}")


def is_trading_day() -> bool:
    """Check if today is a trading day (simplified)."""
    now = datetime.now()
    # Weekend check
    if now.weekday() >= 5:
        return False
    # TODO: Add holiday calendar
    return True


async def main():
    logger.info("StockAI Scheduler 启动中...")
    
    scheduler = AsyncIOScheduler(timezone="Asia/Shanghai")
    
    # 开盘前推送 08:30
    scheduler.add_job(
        push_morning_briefing,
        CronTrigger(hour=8, minute=30, day_of_week="mon-fri"),
        id="morning_briefing",
    )
    
    # 盘中增量推送 (每30分钟)
    scheduler.add_job(
        push_intraday_update,
        CronTrigger(hour="9-11", minute="*/30", day_of_week="mon-fri"),
        id="intraday_morning",
    )
    scheduler.add_job(
        push_intraday_update,
        CronTrigger(hour="13-14", minute="*/30", day_of_week="mon-fri"),
        id="intraday_afternoon",
    )
    
    # 午盘推送 11:40
    scheduler.add_job(
        push_midday_summary,
        CronTrigger(hour=11, minute=40, day_of_week="mon-fri"),
        id="midday_summary",
    )
    
    # 盘后总结推送 15:30
    scheduler.add_job(
        push_closing_summary,
        CronTrigger(hour=15, minute=30, day_of_week="mon-fri"),
        id="closing_summary",
    )
    
    scheduler.start()
    logger.info("定时推送任务已启动:")
    logger.info("  - 08:30 开盘前推送")
    logger.info("  - 09:00-11:30 盘中增量推送 (每30分钟)")
    logger.info("  - 11:40 午盘推送")
    logger.info("  - 13:00-15:00 盘中增量推送 (每30分钟)")
    logger.info("  - 15:30 盘后总结推送")
    
    try:
        while True:
            await asyncio.sleep(3600)
    except (KeyboardInterrupt, SystemExit):
        scheduler.shutdown()
        logger.info("Scheduler 已停止")


if __name__ == "__main__":
    asyncio.run(main())
