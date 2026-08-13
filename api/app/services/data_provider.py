"""
行情数据服务 - 腾讯API + 东方财富datacenter
实时行情: 腾讯 qt.gtimg.cn
K线数据: 腾讯 web.ifzq.gtimg.cn
板块/资金/龙虎榜: 东方财富 datacenter-web.eastmoney.com
"""
import logging
import time
import json
import re
import httpx
from typing import Optional, Dict, Any, List
from dataclasses import dataclass, field

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


@dataclass
class SectorInfo:
    """板块信息"""
    board_name: str = ""
    board_rank: int = 0


@dataclass
class BillboardRecord:
    """龙虎榜记录"""
    trade_date: str = ""
    close_price: float = 0.0
    change_rate: float = 0.0
    deal_amount_ratio: float = 0.0
    billboard_amt: float = 0.0
    explain: str = ""


@dataclass
class NorthboundFlow:
    """北向资金"""
    trade_date: str = ""
    net_deal_amt: float = 0.0
    buy_amt: float = 0.0
    sell_amt: float = 0.0


def _to_qq_code(stock_code: str) -> str:
    if stock_code.startswith(('6', '5')):
        return f"sh{stock_code}"
    return f"sz{stock_code}"


class DataProvider:
    """行情数据提供器 - 腾讯 + 东方财富datacenter"""

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

    # ========== 实时行情 ==========

    def get_realtime_quote(self, stock_code: str) -> Optional[RealtimeQuote]:
        if stock_code in self._quote_cache and time.time() - self._quote_cache_time < self._quote_cache_ttl:
            return self._quote_cache[stock_code]
        qq_code = _to_qq_code(stock_code)
        url = f"https://qt.gtimg.cn/q={qq_code}"
        try:
            self._throttle()
            resp = httpx.get(url, headers=HEADERS, timeout=10)
            if resp.status_code != 200:
                return None
            match = re.search(r'"(.+?)"', resp.text)
            if not match:
                return None
            parts = match.group(1).split("~")
            if len(parts) < 50:
                return None
            quote = RealtimeQuote(
                code=stock_code, name=parts[1],
                price=float(parts[3] or 0), pre_close=float(parts[4] or 0),
                open_price=float(parts[5] or 0), volume=int(float(parts[6] or 0)),
                change_amount=float(parts[31] or 0), change_pct=float(parts[32] or 0),
                high=float(parts[33] or 0), low=float(parts[34] or 0),
                amount=float(parts[37] or 0) * 10000, turnover_rate=float(parts[38] or 0),
                pe_ratio=float(parts[39] or 0), total_mv=float(parts[45] or 0) / 1e8,
            )
            self._quote_cache[stock_code] = quote
            self._quote_cache_time = time.time()
            return quote
        except Exception as e:
            logger.error(f"Quote error for {stock_code}: {e}")
            return None

    # ========== K线 ==========

    def get_kline(self, stock_code: str, days: int = 60) -> List[KlineBar]:
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
                    bars.append(KlineBar(date=k[0], open=float(k[1]), close=close, high=float(k[3]),
                                         low=float(k[4]), volume=int(float(k[5])) if len(k) > 5 else 0,
                                         pct_chg=round(pct_chg, 2)))
                    prev_close = close
            return bars
        except Exception as e:
            logger.error(f"Kline error for {stock_code}: {e}")
            return []

    # ========== 大盘指数 ==========

    def get_market_indices(self) -> Dict[str, RealtimeQuote]:
        indices = {}
        index_codes = {'sh000001': '上证指数', 'sz399001': '深证成指', 'sz399006': '创业板指', 'sh000300': '沪深300'}
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
                if len(parts) > 32:
                    indices[name] = RealtimeQuote(code=qq_code, name=name,
                                                   price=float(parts[3] or 0), pre_close=float(parts[4] or 0),
                                                   change_pct=float(parts[32] or 0))
        except Exception as e:
            logger.error(f"Indices error: {e}")
        return indices

    def get_market_stats(self) -> Dict[str, Any]:
        # 简化实现 - 使用腾讯涨跌榜
        return {}

    # ========== 板块概念 (东方财富datacenter) ==========

    def get_stock_sectors(self, stock_code: str) -> List[SectorInfo]:
        """获取股票所属板块概念"""
        sectors = []
        try:
            self._throttle()
            resp = httpx.get("https://datacenter-web.eastmoney.com/api/data/v1/get",
                params={"sortColumns": "BOARD_RANK", "sortTypes": "1", "pageSize": "10", "pageNumber": "1",
                        "reportName": "RPT_F10_CORETHEME_BOARDTYPE", "columns": "ALL", "source": "WEB", "client": "WEB",
                        "filter": f"(SECURITY_CODE=\"{stock_code}\")"},
                headers=HEADERS, timeout=10)
            d = resp.json()
            if d.get("result") and d["result"].get("data"):
                for item in d["result"]["data"]:
                    sectors.append(SectorInfo(
                        board_name=item.get("BOARD_NAME", ""),
                        board_rank=item.get("BOARD_RANK", 0),
                    ))
        except Exception as e:
            logger.debug(f"Sectors error for {stock_code}: {e}")
        return sectors

    # ========== 同行业个股 ==========

    def get_peer_stocks(self, stock_code: str, limit: int = 10) -> List[Dict[str, str]]:
        """获取同行业个股"""
        peers = []
        # 先获取板块代码
        try:
            self._throttle()
            resp = httpx.get("https://datacenter-web.eastmoney.com/api/data/v1/get",
                params={"sortColumns": "BOARD_RANK", "sortTypes": "1", "pageSize": "1", "pageNumber": "1",
                        "reportName": "RPT_F10_CORETHEME_BOARDTYPE", "columns": "ALL", "source": "WEB", "client": "WEB",
                        "filter": f"(SECURITY_CODE=\"{stock_code}\")"},
                headers=HEADERS, timeout=10)
            d = resp.json()
            if d.get("result") and d["result"].get("data"):
                board_code = d["result"]["data"][0].get("BOARD_CODE", "")
                if board_code:
                    # 获取同板块个股
                    self._throttle()
                    resp2 = httpx.get("https://datacenter-web.eastmoney.com/api/data/v1/get",
                        params={"sortColumns": "SECURITY_CODE", "sortTypes": "1", "pageSize": str(limit), "pageNumber": "1",
                                "reportName": "RPT_F10_CORETHEME_BOARDTYPE", "columns": "ALL", "source": "WEB", "client": "WEB",
                                "filter": f"(BOARD_CODE=\"{board_code}\")"},
                        headers=HEADERS, timeout=10)
                    d2 = resp2.json()
                    if d2.get("result") and d2["result"].get("data"):
                        for item in d2["result"]["data"]:
                            code = item.get("SECURITY_CODE", "")
                            if code != stock_code:
                                peers.append({"code": code, "name": item.get("SECURITY_NAME_ABBR", "")})
        except Exception as e:
            logger.debug(f"Peer stocks error for {stock_code}: {e}")
        return peers

    # ========== 龙虎榜 ==========

    def get_billboard(self, stock_code: str, limit: int = 5) -> List[BillboardRecord]:
        """获取龙虎榜数据"""
        records = []
        try:
            self._throttle()
            resp = httpx.get("https://datacenter-web.eastmoney.com/api/data/v1/get",
                params={"sortColumns": "TRADE_DATE", "sortTypes": "-1", "pageSize": str(limit), "pageNumber": "1",
                        "reportName": "RPT_DAILYBILLBOARD_DETAILSNEW", "columns": "ALL", "source": "WEB", "client": "WEB",
                        "filter": f"(SECURITY_CODE=\"{stock_code}\")"},
                headers=HEADERS, timeout=10)
            d = resp.json()
            if d.get("result") and d["result"].get("data"):
                for item in d["result"]["data"]:
                    records.append(BillboardRecord(
                        trade_date=str(item.get("TRADE_DATE", ""))[:10],
                        close_price=float(item.get("CLOSE_PRICE", 0) or 0),
                        change_rate=float(item.get("CHANGE_RATE", 0) or 0),
                        deal_amount_ratio=float(item.get("DEAL_AMOUNT_RATIO", 0) or 0),
                        billboard_amt=float(item.get("BILLBOARD_DEAL_AMT", 0) or 0),
                        explain=item.get("EXPLAIN", ""),
                    ))
        except Exception as e:
            logger.debug(f"Billboard error for {stock_code}: {e}")
        return records

    # ========== 北向资金 ==========

    def get_northbound_flow(self, limit: int = 5) -> List[NorthboundFlow]:
        """获取北向资金数据"""
        flows = []
        try:
            self._throttle()
            resp = httpx.get("https://datacenter-web.eastmoney.com/api/data/v1/get",
                params={"sortColumns": "TRADE_DATE", "sortTypes": "-1", "pageSize": str(limit), "pageNumber": "1",
                        "reportName": "RPT_MUTUAL_DEAL_HISTORY", "columns": "ALL", "source": "WEB", "client": "WEB"},
                headers=HEADERS, timeout=10)
            d = resp.json()
            if d.get("result") and d["result"].get("data"):
                for item in d["result"]["data"]:
                    flows.append(NorthboundFlow(
                        trade_date=str(item.get("TRADE_DATE", ""))[:10],
                        net_deal_amt=float(item.get("NET_DEAL_AMT", 0) or 0),
                        buy_amt=float(item.get("BUY_AMT", 0) or 0),
                        sell_amt=float(item.get("SELL_AMT", 0) or 0),
                    ))
        except Exception as e:
            logger.debug(f"Northbound flow error: {e}")
        return flows


# 全局实例
data_provider = DataProvider()
