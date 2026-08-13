"""
搜索引擎服务 - 全网资讯搜索
支持 Tavily / Bocha / Brave / SearXNG 多搜索引擎
参考 daily_stock_analysis 的搜索架构
"""
import logging
import time
import json
import re
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
from pathlib import Path

import httpx

logger = logging.getLogger(__name__)

CONFIG_FILE = Path("/app/config/settings.json")


def _get_search_settings() -> dict:
    """读取搜索相关配置"""
    if CONFIG_FILE.exists():
        try:
            with open(CONFIG_FILE) as f:
                return json.load(f)
        except Exception:
            pass
    return {}


@dataclass
class SearchResult:
    """搜索结果"""
    title: str = ""
    snippet: str = ""  # 摘要
    url: str = ""
    source: str = ""  # 来源网站
    published_date: Optional[str] = None


@dataclass
class SearchResponse:
    """搜索响应"""
    query: str = ""
    results: List[SearchResult] = field(default_factory=list)
    provider: str = ""
    success: bool = True
    error_message: Optional[str] = None
    search_time: float = 0.0


class SearchService:
    """多引擎搜索服务"""

    async def search(self, query: str, max_results: int = 5, days: int = 7) -> SearchResponse:
        """搜索 - 按优先级尝试多个搜索引擎"""
        settings = _get_search_settings()

        # 按优先级尝试
        providers = [
            ("bocha", self._search_bocha),
            ("tavily", self._search_tavily),
            ("brave", self._search_brave),
            ("searxng", self._search_searxng),
        ]

        for name, func in providers:
            api_key = settings.get(f"{name}_api_key", "")
            if not api_key:
                continue
            try:
                result = await func(query, api_key, max_results, days)
                if result.success and result.results:
                    return result
            except Exception as e:
                logger.debug(f"{name} search error: {e}")

        # 全部失败，返回空
        return SearchResponse(
            query=query,
            results=[],
            provider="none",
            success=False,
            error_message="未配置任何搜索引擎 API Key，或全部搜索失败",
        )

    async def search_stock_news(self, stock_name: str, stock_code: str, max_results: int = 10) -> SearchResponse:
        """搜索个股相关新闻"""
        queries = [
            f"{stock_name} {stock_code} 最新消息",
            f"{stock_name} 公告 研报",
        ]
        all_results = []
        for q in queries:
            resp = await self.search(q, max_results=max_results // 2, days=3)
            all_results.extend(resp.results)

        # 去重
        seen = set()
        unique = []
        for r in all_results:
            if r.title not in seen:
                seen.add(r.title)
                unique.append(r)

        return SearchResponse(
            query=stock_name,
            results=unique[:max_results],
            provider="multi",
            success=True,
        )

    async def _search_tavily(self, query: str, api_key: str, max_results: int, days: int) -> SearchResponse:
        """Tavily 搜索 - 专为AI优化的搜索API"""
        start = time.time()
        try:
            async with httpx.AsyncClient(timeout=15) as client:
                resp = await client.post(
                    "https://api.tavily.com/search",
                    json={
                        "api_key": api_key,
                        "query": query,
                        "max_results": max_results,
                        "search_depth": "advanced",
                        "include_answer": True,
                        "days": days,
                    },
                )
                if resp.status_code != 200:
                    return SearchResponse(query=query, provider="Tavily", success=False,
                                          error_message=f"HTTP {resp.status_code}")

                data = resp.json()
                results = []
                for item in data.get("results", []):
                    results.append(SearchResult(
                        title=item.get("title", ""),
                        snippet=item.get("content", "")[:500],
                        url=item.get("url", ""),
                        source=self._extract_domain(item.get("url", "")),
                    ))

                return SearchResponse(
                    query=query, results=results, provider="Tavily",
                    success=True, search_time=time.time() - start,
                )
        except Exception as e:
            return SearchResponse(query=query, provider="Tavily", success=False, error_message=str(e))

    async def _search_bocha(self, query: str, api_key: str, max_results: int, days: int) -> SearchResponse:
        """博查搜索 - 中文AI搜索API"""
        start = time.time()
        freshness = "oneDay" if days <= 1 else ("oneWeek" if days <= 7 else "oneMonth")

        try:
            async with httpx.AsyncClient(timeout=15) as client:
                resp = await client.post(
                    "https://api.bocha.cn/v1/web-search",
                    headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
                    json={
                        "query": query,
                        "freshness": freshness,
                        "summary": True,
                        "count": max_results,
                    },
                )
                if resp.status_code != 200:
                    return SearchResponse(query=query, provider="Bocha", success=False,
                                          error_message=f"HTTP {resp.status_code}")

                data = resp.json()
                results = []
                for item in data.get("data", {}).get("webPages", {}).get("value", []):
                    results.append(SearchResult(
                        title=item.get("name", ""),
                        snippet=item.get("snippet", "")[:500],
                        url=item.get("url", ""),
                        source=self._extract_domain(item.get("url", "")),
                        published_date=item.get("dateLastCrawled", ""),
                    ))

                return SearchResponse(
                    query=query, results=results, provider="Bocha",
                    success=True, search_time=time.time() - start,
                )
        except Exception as e:
            return SearchResponse(query=query, provider="Bocha", success=False, error_message=str(e))

    async def _search_brave(self, query: str, api_key: str, max_results: int, days: int) -> SearchResponse:
        """Brave Search - 隐私优先搜索引擎"""
        start = time.time()
        freshness = "pd" if days <= 1 else ("pw" if days <= 7 else "pm")

        try:
            async with httpx.AsyncClient(timeout=15) as client:
                resp = await client.get(
                    "https://api.search.brave.com/res/v1/web/search",
                    headers={"X-Subscription-Token": api_key, "Accept": "application/json"},
                    params={"q": query, "count": max_results, "freshness": freshness},
                )
                if resp.status_code != 200:
                    return SearchResponse(query=query, provider="Brave", success=False,
                                          error_message=f"HTTP {resp.status_code}")

                data = resp.json()
                results = []
                for item in data.get("web", {}).get("results", []):
                    results.append(SearchResult(
                        title=item.get("title", ""),
                        snippet=item.get("description", "")[:500],
                        url=item.get("url", ""),
                        source=self._extract_domain(item.get("url", "")),
                        published_date=item.get("page_age", ""),
                    ))

                return SearchResponse(
                    query=query, results=results, provider="Brave",
                    success=True, search_time=time.time() - start,
                )
        except Exception as e:
            return SearchResponse(query=query, provider="Brave", success=False, error_message=str(e))

    async def _search_searxng(self, query: str, api_key: str, max_results: int, days: int) -> SearchResponse:
        """SearXNG - 自建元搜索引擎（免费开源）"""
        start = time.time()
        # api_key 存的是 SearXNG 实例地址
        base_url = api_key.rstrip("/")
        time_range = "day" if days <= 1 else ("week" if days <= 7 else "month")

        try:
            async with httpx.AsyncClient(timeout=15) as client:
                resp = await client.get(
                    f"{base_url}/search",
                    params={
                        "q": query,
                        "format": "json",
                        "time_range": time_range,
                        "categories": "news",
                        "pageno": 1,
                    },
                )
                if resp.status_code != 200:
                    return SearchResponse(query=query, provider="SearXNG", success=False,
                                          error_message=f"HTTP {resp.status_code}")

                data = resp.json()
                results = []
                for item in data.get("results", [])[:max_results]:
                    results.append(SearchResult(
                        title=item.get("title", ""),
                        snippet=item.get("content", "")[:500],
                        url=item.get("url", ""),
                        source=item.get("engine", ""),
                        published_date=item.get("publishedDate", ""),
                    ))

                return SearchResponse(
                    query=query, results=results, provider="SearXNG",
                    success=True, search_time=time.time() - start,
                )
        except Exception as e:
            return SearchResponse(query=query, provider="SearXNG", success=False, error_message=str(e))

    def _extract_domain(self, url: str) -> str:
        """提取域名"""
        try:
            from urllib.parse import urlparse
            return urlparse(url).netloc.replace("www.", "")
        except:
            return ""


# 全局实例
search_service = SearchService()
