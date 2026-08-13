import logging
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, or_
from typing import Optional
from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.market_news import MarketNews, NewsType
from app.schemas.report import NewsResponse, NewsListResponse

logger = logging.getLogger(__name__)
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
    result = await db.execute(
        select(MarketNews).where(MarketNews.news_id == news_id)
    )
    news = result.scalar_one_or_none()
    if not news:
        raise HTTPException(status_code=404, detail="资讯不存在")
    return NewsResponse.model_validate(news)


@router.get("/{news_id}/detail")
async def get_news_detail(
    news_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """获取资讯详情（含全文抓取）"""
    result = await db.execute(
        select(MarketNews).where(MarketNews.news_id == news_id)
    )
    news = result.scalar_one_or_none()
    if not news:
        raise HTTPException(status_code=404, detail="资讯不存在")
    
    # 如果数据库有完整内容，直接返回
    full_content = news.content or ""
    
    # 如果有URL但内容不完整，尝试抓取全文
    if news.url and (not full_content or len(full_content) < 100):
        try:
            full_content = await _fetch_article_content(news.url)
        except Exception as e:
            logger.debug(f"Fetch article failed: {e}")
    
    return {
        "news_id": news.news_id,
        "title": news.title,
        "content": full_content,
        "news_type": str(news.news_type.value) if news.news_type else "",
        "related_stock": news.related_stock,
        "publish_time": str(news.publish_time) if news.publish_time else "",
        "ai_impact": news.ai_impact,
        "sentiment": news.sentiment,
        "source": news.source,
        "url": news.url,
    }


async def _fetch_article_content(url: str) -> str:
    """抓取文章全文"""
    import httpx
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36"
    }
    
    try:
        async with httpx.AsyncClient(timeout=10, follow_redirects=True) as client:
            resp = await client.get(url, headers=headers)
            if resp.status_code != 200:
                return ""
            
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(resp.text, "lxml")
            
            # 移除脚本和样式
            for tag in soup(["script", "style", "nav", "header", "footer", "aside"]):
                tag.decompose()
            
            # 尝试找文章正文
            article = soup.find("article") or soup.find("div", class_=lambda x: x and "content" in str(x).lower()) or soup.find("div", class_=lambda x: x and "article" in str(x).lower())
            
            if article:
                text = article.get_text(separator="\n", strip=True)
            else:
                text = soup.get_text(separator="\n", strip=True)
            
            # 清理空行
            lines = [line.strip() for line in text.split("\n") if line.strip()]
            return "\n".join(lines)[:5000]
    except Exception as e:
        logger.debug(f"Fetch content error: {e}")
        return ""
