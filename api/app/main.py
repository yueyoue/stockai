from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.core.database import init_db
from app.routes import auth, watchlist, reports, news, push, dashboard


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await init_db()
    # Create default admin if not exists
    await _ensure_admin()
    yield
    # Shutdown


async def _ensure_admin():
    """Ensure at least one admin user exists."""
    from app.core.database import async_session
    from app.models.user import User, UserRole
    from app.core.security import get_password_hash
    from sqlalchemy import select
    
    async with async_session() as db:
        result = await db.execute(select(User).where(User.role == UserRole.ADMIN))
        admin = result.scalar_one_or_none()
        if not admin:
            admin = User(
                username="admin",
                password_hash=get_password_hash("admin123"),
                role=UserRole.ADMIN,
            )
            db.add(admin)
            await db.commit()


app = FastAPI(
    title="StockAI API",
    description="智能股票资讯研报分析平台",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routes
app.include_router(auth.router, prefix="/api")
app.include_router(watchlist.router, prefix="/api")
app.include_router(reports.router, prefix="/api")
app.include_router(news.router, prefix="/api")
app.include_router(push.router, prefix="/api")
app.include_router(dashboard.router, prefix="/api")


@app.get("/api/health")
async def health():
    return {"status": "ok", "version": "1.0.0"}


@app.get("/api/stats")
async def stats():
    from app.core.database import async_session
    from app.models.research_report import ResearchReport
    from app.models.market_news import MarketNews
    from app.models.user import User
    from sqlalchemy import func, select
    
    async with async_session() as db:
        reports_count = (await db.execute(select(func.count(ResearchReport.report_id)))).scalar()
        news_count = (await db.execute(select(func.count(MarketNews.news_id)))).scalar()
        users_count = (await db.execute(select(func.count(User.user_id)))).scalar()
    
    return {
        "reports": reports_count or 0,
        "news": news_count or 0,
        "users": users_count or 0,
    }
