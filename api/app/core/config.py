from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = "postgresql+asyncpg://stockai:stockai123@localhost:5432/stockai"
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # JWT
    SECRET_KEY: str = "change-me-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440  # 24 hours
    
    # App
    APP_NAME: str = "StockAI"
    APP_VERSION: str = "1.0.0"
    
    # LLM
    LLM_API_KEY: Optional[str] = None
    LLM_BASE_URL: Optional[str] = None
    LLM_MODEL: str = "deepseek-chat"
    
    # Crawler
    CRAWLER_INTERVAL_MINUTES: int = 30
    REPORT_PDF_STORAGE: str = "/app/report_storage"
    
    class Config:
        env_file = ".env"


settings = Settings()
