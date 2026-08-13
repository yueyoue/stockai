"""
自选股 API - 支持搜索添加
"""
import json as json_lib
from fastapi import APIRouter, Depends, HTTPException, Query, Response
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from typing import List

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.watchlist import UserWatchlist
from app.schemas.watchlist import WatchlistAdd, WatchlistResponse
from app.services.stock_search import search_stocks

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


@router.get("/search")
async def search_stock(
    q: str = Query(..., min_length=1, description="搜索关键词（代码/名称/拼音）"),
    limit: int = Query(10, ge=1, le=30),
    current_user: User = Depends(get_current_user),
):
    """搜索股票 - 输入代码/名称/拼音即可搜索"""
    results = await search_stocks(q, limit)
    # ensure_ascii=False 让中文直接显示，不转义为 \uXXXX
    content = json_lib.dumps({"results": results}, ensure_ascii=False)
    return Response(content=content, media_type="application/json; charset=utf-8")


@router.post("", response_model=WatchlistResponse)
async def add_to_watchlist(
    data: WatchlistAdd,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
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
