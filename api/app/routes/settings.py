"""
系统设置 API - 图形化配置管理
支持 AI 模型、搜索引擎、爬虫等配置
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

CONFIG_DIR = Path("/app/config")
CONFIG_FILE = CONFIG_DIR / "settings.json"

# 默认配置
DEFAULT_SETTINGS = {
    # AI 模型
    "llm_api_key": "",
    "llm_base_url": "https://api.deepseek.com",
    "llm_model": "deepseek-chat",
    # 搜索引擎
    "bocha_api_key": "",
    "tavily_api_key": "",
    "brave_api_key": "",
    "searxng_api_key": "",
    # 爬虫
    "crawler_interval": 30,
    "push_enabled": True,
}


class SettingsUpdate(BaseModel):
    # AI 模型
    llm_api_key: Optional[str] = None
    llm_base_url: Optional[str] = None
    llm_model: Optional[str] = None
    # 搜索引擎
    bocha_api_key: Optional[str] = None
    tavily_api_key: Optional[str] = None
    brave_api_key: Optional[str] = None
    searxng_api_key: Optional[str] = None
    # 爬虫
    crawler_interval: Optional[int] = None
    push_enabled: Optional[bool] = None


def _load_settings() -> dict:
    if CONFIG_FILE.exists():
        try:
            with open(CONFIG_FILE) as f:
                return {**DEFAULT_SETTINGS, **json.load(f)}
        except Exception:
            pass
    return DEFAULT_SETTINGS.copy()


def _save_settings(settings: dict):
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    with open(CONFIG_FILE, "w") as f:
        json.dump(settings, f, indent=2, ensure_ascii=False)


def get_settings() -> dict:
    return _load_settings()


def _mask_key(key: str) -> str:
    if not key:
        return ""
    if len(key) > 8:
        return key[:4] + "****" + key[-4:]
    return "****"


@router.get("")
async def read_settings(admin: User = Depends(get_admin_user)):
    """获取系统设置"""
    settings = _load_settings()
    # 隐藏敏感信息
    for field in ["llm_api_key", "bocha_api_key", "tavily_api_key", "brave_api_key", "searxng_api_key"]:
        settings[f"{field}_masked"] = _mask_key(settings.get(field, ""))
    return settings


@router.put("")
async def update_settings(data: SettingsUpdate, admin: User = Depends(get_admin_user)):
    """更新系统设置"""
    settings = _load_settings()

    for field in ["llm_api_key", "llm_base_url", "llm_model", "bocha_api_key", "tavily_api_key",
                  "brave_api_key", "searxng_api_key", "crawler_interval", "push_enabled"]:
        val = getattr(data, field, None)
        if val is not None:
            settings[field] = val

    _save_settings(settings)

    # 热更新环境变量
    for env_key in ["LLM_API_KEY", "LLM_BASE_URL", "LLM_MODEL"]:
        field = env_key.lower()
        if getattr(data, field, None) is not None:
            os.environ[env_key] = getattr(data, field)

    return {"message": "设置已保存"}


@router.post("/test-llm")
async def test_llm_connection(admin: User = Depends(get_admin_user)):
    """测试 AI 模型连接"""
    from app.services.llm_service import llm_service
    if not llm_service.is_configured():
        return {"success": False, "message": "未配置 AI API Key"}
    result = await llm_service.chat("你好，请回复OK", "测试连接")
    if result:
        return {"success": True, "message": f"连接成功！回复: {result[:80]}"}
    return {"success": False, "message": "连接失败，请检查配置"}


@router.post("/test-search")
async def test_search_engine(admin: User = Depends(get_admin_user)):
    """测试搜索引擎连接"""
    from app.services.search_service import search_service
    result = await search_service.search("贵州茅台 最新消息", max_results=3, days=1)
    if result.success and result.results:
        return {"success": True, "message": f"搜索成功！使用 {result.provider}，找到 {len(result.results)} 条结果",
                "results": [{"title": r.title, "source": r.source} for r in result.results[:3]]}
    return {"success": False, "message": result.error_message or "搜索失败，请配置搜索引擎 API Key"}
