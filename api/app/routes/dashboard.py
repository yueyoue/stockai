"""
数据看板 API - 个股分析 + 大盘复盘
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.watchlist import UserWatchlist
from app.models.market_news import MarketNews
from app.models.research_report import ResearchReport
from app.services.data_provider import data_provider
from app.services.stock_analyzer import StockAnalyzer, generate_dashboard_markdown, generate_market_dashboard
from app.services.llm_service import llm_service

router = APIRouter(prefix="/dashboard", tags=["数据看板"])

analyzer = StockAnalyzer(data_provider)


@router.get("/stock/{stock_code}")
async def get_stock_dashboard(
    stock_code: str,
    stock_name: str = "",
    current_user: User = Depends(get_current_user),
):
    """获取单只股票的 AI 决策仪表盘"""
    result = analyzer.analyze(stock_code, stock_name)
    
    # 获取关联资讯
    db_gen = get_db()
    db = await db_gen.__anext__()
    try:
        news_result = await db.execute(
            select(MarketNews)
            .where(MarketNews.related_stock.contains(stock_code))
            .order_by(MarketNews.publish_time.desc())
            .limit(10)
        )
        news_list = news_result.scalars().all()
        
        # 获取关联研报
        report_result = await db.execute(
            select(ResearchReport)
            .where(ResearchReport.related_stock.contains(stock_code))
            .order_by(ResearchReport.publish_time.desc())
            .limit(5)
        )
        report_list = report_result.scalars().all()
    finally:
        await db.close()
    
    # 生成 Markdown
    markdown = generate_dashboard_markdown(result)
    
    return {
        "code": stock_code,
        "name": result.name,
        "score": result.overall_score,
        "signal": result.signal,
        "signal_icon": result.signal_icon,
        "sentiment": result.sentiment_label,
        "conclusion": result.core_conclusion,
        "markdown": markdown,
        "technical": {
            "ma5": result.technical.ma5 if result.technical else 0,
            "ma10": result.technical.ma10 if result.technical else 0,
            "ma20": result.technical.ma20 if result.technical else 0,
            "trend": result.technical.trend_status if result.technical else "",
            "trend_score": result.technical.trend_score if result.technical else 50,
            "bias5": result.technical.bias5 if result.technical else 0,
            "bias_risk": result.technical.bias_risk if result.technical else "",
            "volume_status": result.technical.volume_status if result.technical else "",
            "volume_ratio": result.technical.volume_ratio if result.technical else 0,
            "macd_status": result.technical.macd_status if result.technical else "",
            "rsi_6": result.technical.rsi_6 if result.technical else 50,
            "rsi_status": result.technical.rsi_status if result.technical else "",
            "support": result.technical.support_price if result.technical else 0,
            "resistance": result.technical.resistance_price if result.technical else 0,
        },
        "quote": {
            "price": result.quote.price if result.quote else 0,
            "change_pct": result.quote.change_pct if result.quote else 0,
            "volume": result.quote.volume if result.quote else 0,
            "amount": result.quote.amount if result.quote else 0,
            "turnover_rate": result.quote.turnover_rate if result.quote else 0,
            "high": result.quote.high if result.quote else 0,
            "low": result.quote.low if result.quote else 0,
        } if result.quote else None,
        "advice": {
            "holder": result.holder_advice,
            "empty": result.empty_advice,
        },
        "trade_plan": {
            "buy_zone_1": result.buy_zone_1,
            "buy_zone_2": result.buy_zone_2,
            "stop_loss": result.stop_loss,
            "target_1": result.target_1,
            "target_2": result.target_2,
        },
        "checklist": result.checklist,
        "related_news": [
            {
                "news_id": n.news_id,
                "title": n.title,
                "sentiment": n.sentiment,
                "publish_time": str(n.publish_time) if n.publish_time else "",
                "source": n.source,
            }
            for n in news_list
        ],
        "related_reports": [
            {
                "report_id": r.report_id,
                "title": r.title,
                "source": r.source,
                "publish_time": str(r.publish_time) if r.publish_time else "",
            }
            for r in report_list
        ],
    }


@router.get("/market")
async def get_market_dashboard(
    current_user: User = Depends(get_current_user),
):
    """获取大盘复盘仪表盘"""
    markdown = generate_market_dashboard(data_provider)
    
    indices = data_provider.get_market_indices()
    stats = data_provider.get_market_stats()
    
    return {
        "markdown": markdown,
        "indices": {
            name: {
                "price": idx.price,
                "change_pct": idx.change_pct,
            }
            for name, idx in indices.items()
        },
        "stats": stats,
    }


@router.get("/watchlist")
async def get_watchlist_dashboard(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """获取自选股看板汇总"""
    result = await db.execute(
        select(UserWatchlist).where(UserWatchlist.user_id == current_user.user_id)
    )
    watchlist = result.scalars().all()
    
    if not watchlist:
        return {"stocks": [], "message": "暂无自选股"}
    
    stocks = []
    for w in watchlist:
        try:
            analysis = analyzer.analyze(w.stock_code, w.stock_name)
            stocks.append({
                "code": w.stock_code,
                "name": analysis.name or w.stock_name,
                "score": analysis.overall_score,
                "signal": analysis.signal,
                "signal_icon": analysis.signal_icon,
                "price": analysis.quote.price if analysis.quote else 0,
                "change_pct": analysis.quote.change_pct if analysis.quote else 0,
                "conclusion": analysis.core_conclusion,
            })
        except Exception as e:
            stocks.append({
                "code": w.stock_code,
                "name": w.stock_name,
                "score": 0,
                "signal": "数据异常",
                "signal_icon": "⚠️",
                "price": 0,
                "change_pct": 0,
                "conclusion": str(e),
            })
    
    return {"stocks": stocks}
