import enum
from datetime import datetime
from sqlalchemy import Column, Integer, String, Enum, DateTime, ForeignKey, Boolean, JSON
from app.core.database import Base


class PushChannel(str, enum.Enum):
    FEISHU = "feishu"
    WECOM = "wecom"
    TELEGRAM = "telegram"
    EMAIL = "email"


class UserPushConfig(Base):
    __tablename__ = "user_push_config"

    config_id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False, index=True)
    push_channel = Column(Enum(PushChannel), nullable=False)
    webhook_key = Column(String(500), nullable=True)
    email_address = Column(String(200), nullable=True)
    push_switch = Column(Boolean, default=True, nullable=False)
    push_filter = Column(JSON, nullable=True)  # {"news_types": ["个股资讯", "公告"], "report_types": ["个股研报"]}
    created_at = Column(DateTime, default=lambda: datetime.utcnow())
