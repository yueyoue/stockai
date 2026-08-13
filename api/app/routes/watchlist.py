from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from typing import List
from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.watchlist import UserWatchlist
from app.models.market_news import MarketNews
from app.models.research_report import ResearchReport
from app.schemas.watchlist import (
    WatchlistAdd, WatchlistBatchAdd, WatchlistResponse,
    StockNewsResponse, StockReportResponse,
)

router = APIRouter(prefix="/watchlist", tags=["自选股"])


@router.get("", response_model=List[WatchlistResponse])
async def get_watchlist(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(UserWatchlist).where(UserWatchlist.user_id == current_user.user_id)
    )
    return [WatchlistResponse.model_validate(w) for w in result.scalars().all()]


@router.post("", response_model=WatchlistResponse)
async def add_to_watchlist(
    data: WatchlistAdd,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    # Check if already exists
    existing = await db.execute(
        select(UserWatchlist).where(
            and_(
                UserWatchlist.user_id == current_user.user_id,
                UserWatchlist.stock_code == data.stock_code,
            )
        )
    )
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="该股票已在自选列表中")
    
    watchlist = UserWatchlist(
        user_id=current_user.user_id,
        stock_code=data.stock_code,
        stock_name=data.stock_name,
        market_type=data.market_type,
    )
    db.add(watchlist)
    await db.commit()
    await db.refresh(watchlist)
    return WatchlistResponse.model_validate(watchlist)


@router.post("/batch", response_model=List[WatchlistResponse])
async def batch_add_to_watchlist(
    data: WatchlistBatchAdd,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    added = []
    for stock in data.stocks:
        existing = await db.execute(
            select(UserWatchlist).where(
                and_(
                    UserWatchlist.user_id == current_user.user_id,
                    UserWatchlist.stock_code == stock.stock_code,
                )
            )
        )
        if not existing.scalar_one_or_none():
            watchlist = UserWatchlist(
                user_id=current_user.user_id,
                stock_code=stock.stock_code,
                stock_name=stock.stock_name,
                market_type=stock.market_type,
            )
            db.add(watchlist)
            added.append(watchlist)
    
    await db.commit()
    for w in added:
        await db.refresh(w)
    return [WatchlistResponse.model_validate(w) for w in added]


@router.delete("/{stock_code}")
async def remove_from_watchlist(
    stock_code: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(UserWatchlist).where(
            and_(
                UserWatchlist.user_id == current_user.user_id,
                UserWatchlist.stock_code == stock_code,
            )
        )
    )
    watchlist = result.scalar_one_or_none()
    if not watchlist:
        raise HTTPException(status_code=404, detail="自选股票不存在")
    
    await db.delete(watchlist)
    await db.commit()
    return {"message": "已从自选列表移除"}


@router.get("/{stock_code}/news", response_model=List[StockNewsResponse])
async def get_stock_news(
    stock_code: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(MarketNews)
        .where(MarketNews.related_stock.contains(stock_code))
        .order_by(MarketNews.publish_time.desc())
        .limit(50)
    )
    return [StockNewsResponse.model_validate(n) for n in result.scalars().all()]


@router.get("/{stock_code}/reports", response_model=List[StockReportResponse])
async def get_stock_reports(
    stock_code: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(ResearchReport)
        .where(ResearchReport.related_stock.contains(stock_code))
        .order_by(ResearchReport.publish_time.desc())
        .limit(50)
    )
    return [StockReportResponse.model_validate(r) for r in result.scalars().all()]
