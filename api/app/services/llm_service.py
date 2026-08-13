import httpx
import logging
from typing import Optional
from app.core.config import settings

logger = logging.getLogger(__name__)

SYSTEM_PROMPT_REPORT = """你是一位专业的股票分析师助手。请对以下研报进行客观分析总结。

请按以下结构输出：
1. **券商核心观点**：总结研报的主要结论
2. **业绩预测要点**：关键财务数据预测
3. **行业驱动逻辑**：行业层面的驱动因素
4. **个股潜在风险**：需要注意的风险点
5. **客观中性总结**：综合评价

⚠️ 免责声明：以上分析仅基于公开研报内容的客观拆解，不构成任何投资建议。"""

SYSTEM_PROMPT_NEWS = """你是一位专业的股票分析师助手。请分析以下资讯对相关股票的影响。

请按以下结构输出：
1. **情绪标签**：利好/中性/利空（选择一个）
2. **短期催化逻辑**：短期内可能的影响
3. **潜在负面风险**：可能的负面影响
4. **中长期影响简述**：中长期展望

⚠️ 免责声明：以上分析仅基于公开资讯的客观拆解，不构成任何投资建议。"""

SYSTEM_PROMPT_SUMMARY = """你是一位专业的股票分析师助手。请根据以下自选股的资讯和研报，生成一份标准化的决策看板。

要求：
- 使用Markdown格式
- 分为：大盘概况、自选股资讯汇总、重点关注、风险提示
- 语言简洁专业
- 每部分附带AI解读

⚠️ 免责声明：以上分析仅基于公开信息的客观拆解，不构成任何投资建议。"""


async def analyze_report(title: str, content: str, stock_code: str = "", industry: str = "") -> Optional[str]:
    """Analyze a research report using LLM."""
    prompt = f"研报标题：{title}\n关联股票：{stock_code}\n所属行业：{industry}\n\n研报内容：\n{content[:6000]}"
    return await _call_llm(SYSTEM_PROMPT_REPORT, prompt)


async def analyze_news(title: str, content: str, stock_code: str = "") -> Optional[str]:
    """Analyze news impact using LLM."""
    prompt = f"资讯标题：{title}\n关联股票：{stock_code}\n\n资讯内容：\n{content[:4000]}"
    return await _call_llm(SYSTEM_PROMPT_NEWS, prompt)


async def generate_dashboard(watchlist_info: str) -> Optional[str]:
    """Generate a decision dashboard for user's watchlist."""
    return await _call_llm(SYSTEM_PROMPT_SUMMARY, watchlist_info)


async def _call_llm(system_prompt: str, user_prompt: str) -> Optional[str]:
    """Call LLM API."""
    if not settings.LLM_API_KEY:
        logger.warning("LLM API key not configured")
        return None
    
    base_url = settings.LLM_BASE_URL or "https://api.deepseek.com"
    url = f"{base_url}/v1/chat/completions"
    
    headers = {
        "Authorization": f"Bearer {settings.LLM_API_KEY}",
        "Content-Type": "application/json",
    }
    
    payload = {
        "model": settings.LLM_MODEL,
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
                logger.error(f"LLM API error: {resp.status_code} {resp.text}")
                return None
    except Exception as e:
        logger.error(f"LLM call failed: {e}")
        return None
