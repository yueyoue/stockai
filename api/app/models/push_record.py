from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, Boolean
from app.core.database import Base


class PushRecord(Base):
    __tablename__ = "push_record"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False, index=True)
    channel = Column(String(20), nullable=False)
    content_type = Column(String(20), nullable=False)  # news/report/summary
    content_id = Column(Integer, nullable=True)
    push_content = Column(Text, nullable=True)
    success = Column(Boolean, default=True)
    error_msg = Column(Text, nullable=True)
    pushed_at = Column(DateTime, default=lambda: datetime.utcnow())
