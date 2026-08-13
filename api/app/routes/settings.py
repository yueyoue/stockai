"""
系统设置 API - 图形化配置管理
"""
import os
import json
from pathlib import Path
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional

from app.core.security import get_admin_user
from app.models.user import User

router = APIRouter(prefix="/settings", tags=["系统设置"])

# 配置文件路径
CONFIG_DIR = Path("/app/config")
CONFIG_FILE = CONFIG_DIR / "settings.json"

# 默认配置
DEFAULT_SETTINGS = {
    "llm_api_key": "",
    "llm_base_url": "https://api.deepseek.com",
    "llm_model": "deepseek-chat",
    "crawler_interval": 30,
    "push_enabled": True,
}


class SettingsUpdate(BaseModel):
    llm_api_key: Optional[str] = None
    llm_base_url: Optional[str] = None
    llm_model: Optional[str] = None
    crawler_interval: Optional[int] = None
    push_enabled: Optional[bool] = None


def _load_settings() -> dict:
    """从配置文件加载设置"""
    if CONFIG_FILE.exists():
        try:
            with open(CONFIG_FILE, "r") as f:
                saved = json.load(f)
                # 合并默认值
                merged = {**DEFAULT_SETTINGS, **saved}
                return merged
        except Exception:
            pass
    return DEFAULT_SETTINGS.copy()


def _save_settings(settings: dict):
    """保存设置到配置文件"""
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    with open(CONFIG_FILE, "w") as f:
        json.dump(settings, f, indent=2, ensure_ascii=False)


def get_settings() -> dict:
    """获取当前设置（供其他模块调用）"""
    return _load_settings()


@router.get("")
async def read_settings(admin: User = Depends(get_admin_user)):
    """获取系统设置（仅管理员）"""
    settings = _load_settings()
    # 隐藏 API Key 中间部分
    if settings.get("llm_api_key"):
        key = settings["llm_api_key"]
        if len(key) > 8:
            settings["llm_api_key_masked"] = key[:4] + "****" + key[-4:]
        else:
            settings["llm_api_key_masked"] = "****"
    else:
        settings["llm_api_key_masked"] = ""
    return settings


@router.put("")
async def update_settings(
    data: SettingsUpdate,
    admin: User = Depends(get_admin_user),
):
    """更新系统设置（仅管理员）"""
    settings = _load_settings()
    
    if data.llm_api_key is not None:
        settings["llm_api_key"] = data.llm_api_key
    if data.llm_base_url is not None:
        settings["llm_base_url"] = data.llm_base_url
    if data.llm_model is not None:
        settings["llm_model"] = data.llm_model
    if data.crawler_interval is not None:
        settings["crawler_interval"] = max(5, min(120, data.crawler_interval))
    if data.push_enabled is not None:
        settings["push_enabled"] = data.push_enabled
    
    _save_settings(settings)
    
    # 热更新环境变量
    if data.llm_api_key is not None:
        os.environ["LLM_API_KEY"] = data.llm_api_key
    if data.llm_base_url is not None:
        os.environ["LLM_BASE_URL"] = data.llm_base_url
    if data.llm_model is not None:
        os.environ["LLM_MODEL"] = data.llm_model
    
    return {"message": "设置已保存", "settings": settings}


@router.post("/test-llm")
async def test_llm_connection(admin: User = Depends(get_admin_user)):
    """测试 LLM 连接"""
    from app.services.llm_service import llm_service
    
    if not llm_service.is_configured():
        return {"success": False, "message": "未配置 LLM API Key"}
    
    result = await llm_service.chat("你好，请回复OK", "测试连接")
    if result:
        return {"success": True, "message": f"连接成功！模型回复: {result[:100]}"}
    else:
        return {"success": False, "message": "连接失败，请检查 API Key 和 Base URL"}
