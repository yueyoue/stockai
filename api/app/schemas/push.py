from pydantic import BaseModel, Field
from typing import Optional, Dict, List
from datetime import datetime


class PushConfigCreate(BaseModel):
    push_channel: str
    webhook_key: Optional[str] = None
    email_address: Optional[str] = None
    push_switch: bool = True
    push_filter: Optional[Dict] = None


class PushConfigUpdate(BaseModel):
    webhook_key: Optional[str] = None
    email_address: Optional[str] = None
    push_switch: Optional[bool] = None
    push_filter: Optional[Dict] = None


class PushConfigResponse(BaseModel):
    config_id: int
    push_channel: str
    webhook_key: Optional[str] = None
    email_address: Optional[str] = None
    push_switch: bool
    push_filter: Optional[Dict] = None
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class PushRecordResponse(BaseModel):
    id: int
    channel: str
    content_type: str
    push_content: Optional[str] = None
    success: bool
    error_msg: Optional[str] = None
    pushed_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class PushRecordListResponse(BaseModel):
    total: int
    items: List[PushRecordResponse]
