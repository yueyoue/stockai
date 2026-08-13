"""
行情数据服务 - 腾讯API为主
服务器环境东方财富被拦截，改用腾讯/新浪
"""
import logging
import time
import json
import re
import httpx
from typing import Optional, Dict, Any, List
from dataclasses import dataclass

logger = logging.getLogger(__name__)

HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36"}


@dataclass
class RealtimeQuote:
    code: str = ""
    name: str = ""
    price: float = 0.0
    change_pct: float = 0.0
    change_amount: float = 0.0
    volume: int = 0
    amount: float = 0.0
    turnover_rate: float = 0.0
    high: float = 0.0
    low: float = 0.0
    open_price: float = 0.0
    pre_close: float = 0.0
    pe_ratio: float = 0.0
    total_mv: float = 0.0
    circ_mv: float = 0.0


@dataclass
class KlineBar:
    date: str = ""
    open: float = 0.0
    high: float = 0.0
    low: float = 0.0
    close: float = 0.0
    volume: int = 0
    amount: float = 0.0
    pct_chg: float = 0.0
    turnover_rate: float = 0.0


def _to_qq_code(stock_code: str) -> str:
    """转换为腾讯格式 sh600519 / sz000001"""
    if stock_code.startswith(('6', '5')):
        return f"sh{stock_code}"
    return f"sz{stock_code}"


class DataProvider:
    """行情数据提供器 - 腾讯API"""
    
    def __init__(self):
        self._last_req = 0
        self._min_interval = 0.3
        self._quote_cache: Dict[str, RealtimeQuote] = {}
        self._quote_cache_time = 0
        self._quote_cache_ttl = 30
    
    def _throttle(self):
        elapsed = time.time() - self._last_req
        if elapsed < self._min_interval:
            time.sleep(self._min_interval - elapsed)
        self._last_req = time.time()
    
    def get_realtime_quote(self, stock_code: str) -> Optional[RealtimeQuote]:
        """获取单只股票实时行情 - 腾讯API"""
        # 先检查缓存
        if stock_code in self._quote_cache:
            if time.time() - self._quote_cache_time < self._quote_cache_ttl:
                return self._quote_cache[stock_code]
        
        qq_code = _to_qq_code(stock_code)
        url = f"https://qt.gtimg.cn/q={qq_code}"
        
        try:
            self._throttle()
            resp = httpx.get(url, headers=HEADERS, timeout=10)
            if resp.status_code != 200:
                return None
            
            # 解析腾讯行情格式: v_sh600519="1~贵州茅台~600519~1355.29~1343.00~..."
            text = resp.text
            match = re.search(r'"(.+?)"', text)
            if not match:
                return None
            
            parts = match.group(1).split("~")
            if len(parts) < 50:
                return None
            
            quote = RealtimeQuote(
                code=stock_code,
                name=parts[1],
                price=float(parts[3] or 0),
                pre_close=float(parts[4] or 0),
                open_price=float(parts[5] or 0),
                volume=int(float(parts[6] or 0)),
                change_amount=float(parts[31] or 0),
                change_pct=float(parts[32] or 0),
                high=float(parts[33] or 0),
                low=float(parts[34] or 0),
                amount=float(parts[37] or 0) * 10000,
                turnover_rate=float(parts[38] or 0),
                pe_ratio=float(parts[39] or 0),
                total_mv=float(parts[45] or 0) / 100000000,
            )
            
            self._quote_cache[stock_code] = quote
            self._quote_cache_time = time.time()
            return quote
        except Exception as e:
            logger.error(f"Tencent quote error for {stock_code}: {e}")
            return None
    
    def get_realtime_quotes_batch(self, stock_codes: List[str]) -> Dict[str, RealtimeQuote]:
        """批量获取实时行情"""
        result = {}
        codes_str = ",".join([_to_qq_code(c) for c in stock_codes])
        url = f"https://qt.gtimg.cn/q={codes_str}"
        
        try:
            self._throttle()
            resp = httpx.get(url, headers=HEADERS, timeout=10)
            if resp.status_code != 200:
                return result
            
            for line in resp.text.strip().split(";"):
                match = re.search(r'v_(\w+)="(.+?)"', line)
                if not match:
                    continue
                
                qq_code = match.group(1)
                parts = match.group(2).split("~")
                if len(parts) < 50:
                    continue
                
                # 从qq_code提取股票代码
                code = qq_code[2:]  # remove sh/sz prefix
                
                result[code] = RealtimeQuote(
                    code=code,
                    name=parts[1],
                    price=float(parts[3] or 0),
                    pre_close=float(parts[4] or 0),
                    open_price=float(parts[5] or 0),
                    volume=int(float(parts[6] or 0)),
                    change_amount=float(parts[31] or 0),
                    change_pct=float(parts[32] or 0),
                    high=float(parts[33] or 0),
                    low=float(parts[34] or 0),
                    amount=float(parts[37] or 0) * 10000,
                    turnover_rate=float(parts[38] or 0),
                )
        except Exception as e:
            logger.error(f"Tencent batch quote error: {e}")
        
        return result
    
    def get_kline(self, stock_code: str, days: int = 60) -> List[KlineBar]:
        """获取K线 - 腾讯API"""
        qq_code = _to_qq_code(stock_code)
        url = "https://web.ifzq.gtimg.cn/appstock/app/fqkline/get"
        params = {"param": f"{qq_code},day,,,{days},qfq"}
        
        try:
            self._throttle()
            resp = httpx.get(url, params=params, headers=HEADERS, timeout=15)
            if resp.status_code != 200:
                return []
            
            data = resp.json()
            stock_data = data.get("data", {}).get(qq_code, {})
            klines = stock_data.get("qfqday", []) or stock_data.get("day", [])
            
            bars = []
            prev_close = 0
            for k in klines:
                if len(k) >= 5:
                    close = float(k[2])
                    pct_chg = ((close - prev_close) / prev_close * 100) if prev_close > 0 else 0
                    bars.append(KlineBar(
                        date=k[0],
                        open=float(k[1]),
                        close=close,
                        high=float(k[3]),
                        low=float(k[4]),
                        volume=int(float(k[5])) if len(k) > 5 else 0,
                        pct_chg=round(pct_chg, 2),
                    ))
                    prev_close = close
            return bars
        except Exception as e:
            logger.error(f"Tencent kline error for {stock_code}: {e}")
            return []
    
    def get_market_indices(self) -> Dict[str, RealtimeQuote]:
        """获取大盘指数 - 腾讯API"""
        indices = {}
        # 腾讯指数代码
        index_codes = {
            'sh000001': '上证指数',
            'sz399001': '深证成指',
            'sz399006': '创业板指',
            'sh000300': '沪深300',
        }
        
        codes_str = ",".join(index_codes.keys())
        url = f"https://qt.gtimg.cn/q={codes_str}"
        
        try:
            self._throttle()
            resp = httpx.get(url, headers=HEADERS, timeout=10)
            if resp.status_code != 200:
                return indices
            
            for line in resp.text.strip().split(";"):
                match = re.search(r'v_(\w+)="(.+?)"', line)
                if not match:
                    continue
                
                qq_code = match.group(1)
                name = index_codes.get(qq_code, "")
                if not name:
                    continue
                
                parts = match.group(2).split("~")
                if len(parts) < 5:
                    continue
                
                indices[name] = RealtimeQuote(
                    code=qq_code,
                    name=name,
                    price=float(parts[3] or 0),
                    pre_close=float(parts[4] or 0),
                    change_pct=float(parts[32] or 0) if len(parts) > 32 else 0,
                )
        except Exception as e:
            logger.error(f"Market indices error: {e}")
        
        return indices
    
    def get_market_stats(self) -> Dict[str, Any]:
        """获取全市场涨跌统计 - 使用腾讯涨跌榜"""
        stats = {'up_count': 0, 'down_count': 0, 'flat_count': 0, 'limit_up': 0, 'limit_down': 0}
        
        try:
            # 腾讯涨跌榜API
            self._throttle()
            resp = httpx.get(
                "https://proxy.finance.qq.com/ifzqgtimg/appstock/app/rank3/get",
                params={"t": "ranka/chr", "p": "1", "n": "100", "o": "0", "v": "list_data"},
                headers=HEADERS,
                timeout=10,
            )
            if resp.status_code == 200:
                data = resp.json()
                items = data.get("data", {}).get("list_data", [])
                up = sum(1 for i in items if float(i.get("zdf", 0) or 0) > 0)
                down = sum(1 for i in items if float(i.get("zdf", 0) or 0) < 0)
                limit_up = sum(1 for i in items if float(i.get("zdf", 0) or 0) >= 9.9)
                limit_down = sum(1 for i in items if float(i.get("zdf", 0) or 0) <= -9.9)
                stats = {
                    'up_count': up,
                    'down_count': down,
                    'flat_count': len(items) - up - down,
                    'limit_up': limit_up,
                    'limit_down': limit_down,
                }
        except Exception as e:
            logger.error(f"Market stats error: {e}")
        
        return stats


# 全局实例
data_provider = DataProvider()
