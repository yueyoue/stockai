from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.push_config import UserPushConfig, PushChannel
from app.models.push_record import PushRecord
from app.schemas.push import (
    PushConfigCreate, PushConfigUpdate, PushConfigResponse,
    PushRecordResponse, PushRecordListResponse,
)

router = APIRouter(prefix="/push", tags=["推送"])


@router.get("/config", response_model=List[PushConfigResponse])
async def get_push_configs(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(UserPushConfig).where(UserPushConfig.user_id == current_user.user_id)
    )
    return [PushConfigResponse.model_validate(c) for c in result.scalars().all()]


@router.post("/config", response_model=PushConfigResponse)
async def create_push_config(
    data: PushConfigCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    config = UserPushConfig(
        user_id=current_user.user_id,
        push_channel=PushChannel(data.push_channel),
        webhook_key=data.webhook_key,
        email_address=data.email_address,
        push_switch=data.push_switch,
        push_filter=data.push_filter,
    )
    db.add(config)
    await db.commit()
    await db.refresh(config)
    return PushConfigResponse.model_validate(config)


@router.put("/config/{config_id}", response_model=PushConfigResponse)
async def update_push_config(
    config_id: int,
    data: PushConfigUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(UserPushConfig).where(
            UserPushConfig.config_id == config_id,
            UserPushConfig.user_id == current_user.user_id,
        )
    )
    config = result.scalar_one_or_none()
    if not config:
        raise HTTPException(status_code=404, detail="推送配置不存在")
    
    if data.webhook_key is not None:
        config.webhook_key = data.webhook_key
    if data.email_address is not None:
        config.email_address = data.email_address
    if data.push_switch is not None:
        config.push_switch = data.push_switch
    if data.push_filter is not None:
        config.push_filter = data.push_filter
    
    await db.commit()
    await db.refresh(config)
    return PushConfigResponse.model_validate(config)


@router.delete("/config/{config_id}")
async def delete_push_config(
    config_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(UserPushConfig).where(
            UserPushConfig.config_id == config_id,
            UserPushConfig.user_id == current_user.user_id,
        )
    )
    config = result.scalar_one_or_none()
    if not config:
        raise HTTPException(status_code=404, detail="推送配置不存在")
    
    await db.delete(config)
    await db.commit()
    return {"message": "推送配置已删除"}


@router.get("/records", response_model=PushRecordListResponse)
async def get_push_records(
    page: int = 1,
    page_size: int = 20,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    count_result = await db.execute(
        select(PushRecord).where(PushRecord.user_id == current_user.user_id)
    )
    total = len(count_result.scalars().all())
    
    result = await db.execute(
        select(PushRecord)
        .where(PushRecord.user_id == current_user.user_id)
        .order_by(PushRecord.pushed_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
    )
    
    return PushRecordListResponse(
        total=total,
        items=[PushRecordResponse.model_validate(r) for r in result.scalars().all()],
    )
