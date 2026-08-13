"""
LLM 服务 - 支持多后端
支持 DeepSeek / 通义千问 / Claude / OpenAI / 本地模型
配置从 settings.json 读取，支持图形化设置
"""
import logging
import httpx
from typing import Optional
from app.core.config import settings as env_settings

logger = logging.getLogger(__name__)

# 研报分析 Prompt
REPORT_PROMPT = """你是一位专业的股票分析师。请对以下研报进行客观分析。

按以下结构输出：
1. **券商核心观点**
2. **业绩预测要点**
3. **行业驱动逻辑**
4. **个股潜在风险**
5. **客观总结**

⚠️ 免责声明：以上分析仅基于公开研报内容的客观拆解，不构成任何投资建议。"""

# 资讯影响分析 Prompt
NEWS_PROMPT = """你是一位专业的股票分析师。请分析以下资讯对相关股票的影响。

输出结构：
1. **情绪标签**：利好/中性/利空
2. **短期催化逻辑**
3. **潜在风险**
4. **中长期影响**

⚠️ 免责声明：以上分析仅基于公开资讯的客观拆解，不构成任何投资建议。"""

# 决策看板 Prompt
DASHBOARD_PROMPT = """你是一位专业的股票分析师。请根据以下自选股的资讯和研报，生成标准化决策看板。

要求：
- Markdown格式
- 分为：大盘概况、自选股资讯汇总、重点关注、风险提示
- 语言简洁专业

⚠️ 免责声明：以上分析仅基于公开信息的客观拆解，不构成任何投资建议。"""


def _get_settings() -> dict:
    """从 settings.json 读取配置（每次调用重新读取，支持热更新）"""
    import json
    from pathlib import Path
    
    config_file = Path("/app/config/settings.json")
    if config_file.exists():
        try:
            with open(config_file) as f:
                return json.load(f)
        except Exception:
            pass
    return {}


class LLMService:
    """多后端 LLM 服务 - 配置优先从 settings.json 读取"""

    def _get_api_key(self) -> str:
        s = _get_settings()
        return s.get("llm_api_key") or env_settings.LLM_API_KEY or ""

    def _get_base_url(self) -> str:
        s = _get_settings()
        return s.get("llm_base_url") or env_settings.LLM_BASE_URL or "https://api.deepseek.com"

    def _get_model(self) -> str:
        s = _get_settings()
        return s.get("llm_model") or env_settings.LLM_MODEL or "deepseek-chat"

    def is_configured(self) -> bool:
        return bool(self._get_api_key())

    async def analyze_report(self, title: str, content: str, stock_code: str = "", industry: str = "") -> Optional[str]:
        prompt = f"研报标题：{title}\n关联股票：{stock_code}\n所属行业：{industry}\n\n研报内容：\n{content[:6000]}"
        return await self._call(REPORT_PROMPT, prompt)

    async def analyze_news(self, title: str, content: str, stock_code: str = "") -> Optional[str]:
        prompt = f"资讯标题：{title}\n关联股票：{stock_code}\n\n资讯内容：\n{content[:4000]}"
        return await self._call(NEWS_PROMPT, prompt)

    async def generate_dashboard(self, watchlist_info: str) -> Optional[str]:
        return await self._call(DASHBOARD_PROMPT, watchlist_info)

    async def chat(self, system_prompt: str, user_message: str) -> Optional[str]:
        return await self._call(system_prompt, user_message)

    async def _call(self, system_prompt: str, user_prompt: str) -> Optional[str]:
        api_key = self._get_api_key()
        base_url = self._get_base_url()
        model = self._get_model()

        if not api_key:
            logger.warning("LLM API key not configured")
            return None

        url = f"{base_url}/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "temperature": 0.3,
            "max_tokens": 2000,
        }

        try:
            async with httpx.AsyncClient(timeout=60) as client:
                resp = await client.post(url, json=payload, headers=headers)
                if resp.status_code == 200:
                    data = resp.json()
                    return data["choices"][0]["message"]["content"]
                else:
                    logger.error(f"LLM API error: {resp.status_code} {resp.text[:200]}")
                    return None
        except Exception as e:
            logger.error(f"LLM call failed: {e}")
            return None


# 全局实例
llm_service = LLMService()
