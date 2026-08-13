"""
LLM 服务 - 支持多后端
支持 DeepSeek / 通义千问 / Claude / OpenAI / 本地模型
"""
import logging
import httpx
from typing import Optional, Dict, Any
from app.core.config import settings

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


# LLM 后端配置
LLM_BACKENDS = {
    "deepseek": {
        "base_url": "https://api.deepseek.com",
        "default_model": "deepseek-chat",
    },
    "qwen": {
        "base_url": "https://dashscope.aliyuncs.com/compatible-mode/v1",
        "default_model": "qwen-plus",
    },
    "openai": {
        "base_url": "https://api.openai.com",
        "default_model": "gpt-4o-mini",
    },
    "claude": {
        "base_url": "https://api.anthropic.com",
        "default_model": "claude-3-5-sonnet-20241022",
    },
}


class LLMService:
    """多后端 LLM 服务"""
    
    def __init__(self):
        self.api_key = settings.LLM_API_KEY
        self.base_url = settings.LLM_BASE_URL or "https://api.deepseek.com"
        self.model = settings.LLM_MODEL or "deepseek-chat"
    
    def is_configured(self) -> bool:
        return bool(self.api_key)
    
    async def analyze_report(self, title: str, content: str, stock_code: str = "", industry: str = "") -> Optional[str]:
        """分析研报"""
        prompt = f"研报标题：{title}\n关联股票：{stock_code}\n所属行业：{industry}\n\n研报内容：\n{content[:6000]}"
        return await self._call(REPORT_PROMPT, prompt)
    
    async def analyze_news(self, title: str, content: str, stock_code: str = "") -> Optional[str]:
        """分析资讯影响"""
        prompt = f"资讯标题：{title}\n关联股票：{stock_code}\n\n资讯内容：\n{content[:4000]}"
        return await self._call(NEWS_PROMPT, prompt)
    
    async def generate_dashboard(self, watchlist_info: str) -> Optional[str]:
        """生成决策看板"""
        return await self._call(DASHBOARD_PROMPT, watchlist_info)
    
    async def chat(self, system_prompt: str, user_message: str) -> Optional[str]:
        """通用对话"""
        return await self._call(system_prompt, user_message)
    
    async def _call(self, system_prompt: str, user_prompt: str) -> Optional[str]:
        """调用 LLM API（兼容 OpenAI 格式）"""
        if not self.api_key:
            logger.warning("LLM API key not configured")
            return None
        
        url = f"{self.base_url}/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": self.model,
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
