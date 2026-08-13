from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, or_
from typing import Optional
from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.market_news import MarketNews, NewsType
from app.schemas.report import NewsResponse, NewsListResponse

router = APIRouter(prefix="/news", tags=["资讯"])


@router.get("", response_model=NewsListResponse)
async def list_news(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    news_type: Optional[str] = None,
    keyword: Optional[str] = None,
    sentiment: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    query = select(MarketNews)
    count_query = select(func.count(MarketNews.news_id))
    
    if news_type:
        query = query.where(MarketNews.news_type == news_type)
        count_query = count_query.where(MarketNews.news_type == news_type)
    
    if keyword:
        filter_cond = or_(
            MarketNews.title.contains(keyword),
            MarketNews.related_stock.contains(keyword),
        )
        query = query.where(filter_cond)
        count_query = count_query.where(filter_cond)
    
    if sentiment:
        query = query.where(MarketNews.sentiment == sentiment)
        count_query = count_query.where(MarketNews.sentiment == sentiment)
    
    total_result = await db.execute(count_query)
    total = total_result.scalar()
    
    query = query.order_by(MarketNews.publish_time.desc())
    query = query.offset((page - 1) * page_size).limit(page_size)
    
    result = await db.execute(query)
    news_list = result.scalars().all()
    
    return NewsListResponse(
        total=total,
        items=[NewsResponse.model_validate(n) for n in news_list],
    )


@router.get("/{news_id}", response_model=NewsResponse)
async def get_news(
    news_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    from fastapi import HTTPException
    result = await db.execute(
        select(MarketNews).where(MarketNews.news_id == news_id)
    )
    news = result.scalar_one_or_none()
    if not news:
        raise HTTPException(status_code=404, detail="资讯不存在")
    return NewsResponse.model_validate(news)
