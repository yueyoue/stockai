"""
股票搜索服务 - 支持代码/名称/拼音搜索
"""
import logging
import httpx
import json as json_lib
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36"}


def _decode_unicode(s: str) -> str:
    """解码Unicode转义字符，如 \u8d35\u5dde -> 贵州"""
    if not s or '\\u' not in s:
        return s
    try:
        # json.loads 可以正确解码 Unicode 转义
        return json_lib.loads(f'"{s}"')
    except:
        return s


async def search_stocks(keyword: str, limit: int = 10) -> List[Dict[str, Any]]:
    """
    搜索股票 - 支持代码、名称、拼音
    返回: [{"code": "600519", "name": "贵州茅台", "market": "A股"}, ...]
    """
    if not keyword or len(keyword) < 1:
        return []
    
    results = []
    
    # 方法1: 腾讯股票搜索API
    try:
        results = await _tencent_search(keyword, limit)
        if results:
            return results
    except Exception as e:
        logger.debug(f"Tencent search error: {e}")
    
    # 方法2: 新浪股票搜索API
    try:
        results = await _sina_search(keyword, limit)
        if results:
            return results
    except Exception as e:
        logger.debug(f"Sina search error: {e}")
    
    return results


async def _tencent_search(keyword: str, limit: int) -> List[Dict[str, Any]]:
    """
    腾讯股票搜索
    返回格式: v_hint="sh~600519~贵州茅台~gzmt~GP-A"
    解析: market~code~name~pinyin~type
    """
    url = "https://smartbox.gtimg.cn/s3/"
    params = {"v": "2", "q": keyword, "t": "gp", "c": "1"}
    
    async with httpx.AsyncClient(timeout=10) as client:
        resp = await client.get(url, params=params, headers=HEADERS)
        if resp.status_code != 200:
            return []
        
        text = resp.text
        # 提取引号内的内容
        start = text.find('"')
        end = text.rfind('"')
        if start == -1 or end == -1 or start == end:
            return []
        
        data = text[start+1:end]
        if not data:
            return []
        
        results = []
        for item in data.split(";")[:limit]:
            parts = item.split("~")
            if len(parts) >= 4:
                market_prefix = parts[0]  # sh/sz/hk
                code = parts[1]
                name = parts[2]
                pinyin = parts[3] if len(parts) > 3 else ""
                
                # 判断市场
                market = "A股"
                if market_prefix == "hk":
                    market = "港股"
                elif market_prefix == "us":
                    market = "美股"
                
                # 只返回A股
                if market_prefix in ("sh", "sz"):
                    results.append({
                        "code": code,
                        "name": _decode_unicode(name),
                        "market": market,
                        "pinyin": pinyin,
                    })
        
        return results


async def _sina_search(keyword: str, limit: int) -> List[Dict[str, Any]]:
    """
    新浪股票搜索
    返回格式: var suggestdata="sh600519,11,600519,sh600519,贵州茅台,,贵州茅台,99,1,ESG,,";
    解析: raw_code,type,code,full_code,name,...
    """
    url = "https://suggest3.sinajs.cn/suggest/"
    params = {"key": keyword, "name": "suggestdata"}
    
    async with httpx.AsyncClient(timeout=10) as client:
        resp = await client.get(url, params=params, headers=HEADERS)
        if resp.status_code != 200:
            return []
        
        text = resp.text
        start = text.find('"')
        end = text.rfind('"')
        if start == -1 or end == -1 or start == end:
            return []
        
        data = text[start+1:end]
        if not data:
            return []
        
        results = []
        for item in data.split(";")[:limit]:
            parts = item.split(",")
            if len(parts) >= 5:
                raw_code = parts[0]  # sh600519
                code = parts[2]      # 600519
                name = parts[4]      # 贵州茅台
                
                if not code or not name:
                    continue
                
                # 判断市场
                prefix = raw_code[:2] if len(raw_code) > 2 else ""
                market = "A股"
                if prefix == "hk":
                    market = "港股"
                
                # 只返回A股（sh/sz开头）
                if prefix in ("sh", "sz"):
                    results.append({
                        "code": code,
                        "name": name,
                        "market": market,
                    })
        
        return results
