import httpx
import logging
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.push_config import UserPushConfig, PushChannel
from app.models.push_record import PushRecord

logger = logging.getLogger(__name__)


async def send_push(
    db: AsyncSession,
    user_id: int,
    content: str,
    content_type: str = "summary",
    content_id: Optional[int] = None,
):
    """Send push notification to all configured channels for a user."""
    result = await db.execute(
        select(UserPushConfig).where(
            UserPushConfig.user_id == user_id,
            UserPushConfig.push_switch == True,
        )
    )
    configs = result.scalars().all()
    
    for config in configs:
        success = False
        error_msg = None
        
        try:
            if config.push_channel == PushChannel.FEISHU:
                success = await _send_feishu(config.webhook_key, content)
            elif config.push_channel == PushChannel.WECOM:
                success = await _send_wecom(config.webhook_key, content)
            elif config.push_channel == PushChannel.TELEGRAM:
                success = await _send_telegram(config.webhook_key, content)
            elif config.push_channel == PushChannel.EMAIL:
                success = await _send_email(config.email_address, content)
        except Exception as e:
            error_msg = str(e)
            logger.error(f"Push failed for user {user_id} channel {config.push_channel}: {e}")
        
        record = PushRecord(
            user_id=user_id,
            channel=config.push_channel.value,
            content_type=content_type,
            content_id=content_id,
            push_content=content[:2000],
            success=success,
            error_msg=error_msg,
        )
        db.add(record)
    
    await db.commit()


async def _send_feishu(webhook_key: str, content: str) -> bool:
    """Send message via Feishu webhook."""
    url = f"https://open.feishu.cn/open-apis/bot/v2/hook/{webhook_key}"
    payload = {
        "msg_type": "text",
        "content": {"text": content},
    }
    async with httpx.AsyncClient(timeout=10) as client:
        resp = await client.post(url, json=payload)
        return resp.status_code == 200


async def _send_wecom(webhook_key: str, content: str) -> bool:
    """Send message via WeCom webhook."""
    url = f"https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key={webhook_key}"
    payload = {
        "msgtype": "markdown",
        "markdown": {"content": content},
    }
    async with httpx.AsyncClient(timeout=10) as client:
        resp = await client.post(url, json=payload)
        return resp.status_code == 200


async def _send_telegram(bot_token_and_chat: str, content: str) -> bool:
    """Send message via Telegram bot."""
    parts = bot_token_and_chat.split(":")
    if len(parts) < 2:
        return False
    token = parts[0]
    chat_id = parts[1] if len(parts) > 1 else ""
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": content[:4000],
        "parse_mode": "Markdown",
    }
    async with httpx.AsyncClient(timeout=10) as client:
        resp = await client.post(url, json=payload)
        return resp.status_code == 200


async def _send_email(email_address: str, content: str) -> bool:
    """Send email notification (placeholder - needs SMTP config)."""
    logger.info(f"Email push to {email_address}: {content[:100]}...")
    return True
