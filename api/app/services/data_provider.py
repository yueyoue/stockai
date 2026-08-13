"""
行情数据服务 - 基于 efinance/akshare
复用 daily_stock_analysis 的数据源策略
"""
import logging
import random
import time
from typing import Optional, Dict, Any, List
from dataclasses import dataclass

logger = logging.getLogger(__name__)

# User-Agent 池
USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0',
]


@dataclass
class RealtimeQuote:
    """实时行情数据"""
    code: str
    name: str = ""
    price: float = 0.0
    change_pct: float = 0.0
    change_amount: float = 0.0
    volume: int = 0
    amount: float = 0.0
    turnover_rate: float = 0.0
    amplitude: float = 0.0
    high: float = 0.0
    low: float = 0.0
    open_price: float = 0.0
    pre_close: float = 0.0
    pe_ratio: float = 0.0
    total_mv: float = 0.0  # 总市值(亿)
    circ_mv: float = 0.0   # 流通市值(亿)


@dataclass
class KlineBar:
    """K线数据"""
    date: str
    open: float
    high: float
    low: float
    close: float
    volume: int
    amount: float
    pct_chg: float = 0.0
    turnover_rate: float = 0.0


class DataProvider:
    """行情数据提供器 - 支持 efinance 和 akshare 双数据源"""
    
    def __init__(self):
        self._efinance = None
        self._akshare = None
        self._last_request_time = 0
        self._min_interval = 1.5  # 最小请求间隔(秒)
    
    def _throttle(self):
        """请求限流"""
        elapsed = time.time() - self._last_request_time
        if elapsed < self._min_interval:
            time.sleep(self._min_interval - elapsed)
        self._last_request_time = time.time()
    
    def _get_efinance(self):
        if self._efinance is None:
            try:
                import efinance as ef
                self._efinance = ef
            except ImportError:
                logger.warning("efinance not installed")
        return self._efinance
    
    def _get_akshare(self):
        if self._akshare is None:
            try:
                import akshare as ak
                self._akshare = ak
            except ImportError:
                logger.warning("akshare not installed")
        return self._akshare
    
    def get_realtime_quote(self, stock_code: str) -> Optional[RealtimeQuote]:
        """获取实时行情 - 优先 efinance，回退 akshare"""
        quote = self._try_efinance_realtime(stock_code)
        if quote:
            return quote
        return self._try_akshare_realtime(stock_code)
    
    def get_realtime_quotes_batch(self, stock_codes: List[str]) -> Dict[str, RealtimeQuote]:
        """批量获取实时行情"""
        result = {}
        ef = self._get_efinance()
        if ef:
            try:
                self._throttle()
                df = ef.stock.get_quote_history(stock_codes, klt=1, beg='20260101')
                if df is not None and not df.empty:
                    for code in stock_codes:
                        code_df = df[df['股票代码'] == code]
                        if not code_df.empty:
                            row = code_df.iloc[-1]
                            result[code] = RealtimeQuote(
                                code=code,
                                name=str(row.get('股票名称', '')),
                                price=float(row.get('收盘', 0)),
                                change_pct=float(row.get('涨跌幅', 0)),
                            )
            except Exception as e:
                logger.error(f"efinance batch quote error: {e}")
        
        # Fallback: individual akshare
        for code in stock_codes:
            if code not in result:
                q = self._try_akshare_realtime(code)
                if q:
                    result[code] = q
        return result
    
    def _try_efinance_realtime(self, stock_code: str) -> Optional[RealtimeQuote]:
        """efinance 获取实时行情"""
        ef = self._get_efinance()
        if not ef:
            return None
        try:
            self._throttle()
            df = ef.stock.get_quote_history(stock_code, klt=1)
            if df is not None and not df.empty:
                row = df.iloc[-1]
                return RealtimeQuote(
                    code=stock_code,
                    name=str(row.get('股票名称', '')),
                    price=float(row.get('收盘', 0)),
                    change_pct=float(row.get('涨跌幅', 0)),
                    change_amount=float(row.get('涨跌额', 0)),
                    volume=int(row.get('成交量', 0)),
                    amount=float(row.get('成交额', 0)),
                    turnover_rate=float(row.get('换手率', 0)),
                    high=float(row.get('最高', 0)),
                    low=float(row.get('最低', 0)),
                    open_price=float(row.get('开盘', 0)),
                )
        except Exception as e:
            logger.debug(f"efinance realtime error for {stock_code}: {e}")
        return None
    
    def _try_akshare_realtime(self, stock_code: str) -> Optional[RealtimeQuote]:
        """akshare 获取实时行情"""
        ak = self._get_akshare()
        if not ak:
            return None
        try:
            self._throttle()
            df = ak.stock_zh_a_spot_em()
            if df is not None and not df.empty:
                row = df[df['代码'] == stock_code]
                if not row.empty:
                    r = row.iloc[0]
                    return RealtimeQuote(
                        code=stock_code,
                        name=str(r.get('名称', '')),
                        price=float(r.get('最新价', 0)),
                        change_pct=float(r.get('涨跌幅', 0)),
                        change_amount=float(r.get('涨跌额', 0)),
                        volume=int(r.get('成交量', 0)),
                        amount=float(r.get('成交额', 0)),
                        turnover_rate=float(r.get('换手率', 0)),
                        high=float(r.get('最高', 0)),
                        low=float(r.get('最低', 0)),
                        open_price=float(r.get('今开', 0)),
                        pe_ratio=float(r.get('市盈率-动态', 0)),
                        total_mv=float(r.get('总市值', 0)) / 1e8,
                        circ_mv=float(r.get('流通市值', 0)) / 1e8,
                    )
        except Exception as e:
            logger.debug(f"akshare realtime error for {stock_code}: {e}")
        return None
    
    def get_kline(self, stock_code: str, days: int = 60) -> List[KlineBar]:
        """获取K线数据"""
        bars = self._try_efinance_kline(stock_code, days)
        if bars:
            return bars
        return self._try_akshare_kline(stock_code, days)
    
    def _try_efinance_kline(self, stock_code: str, days: int) -> List[KlineBar]:
        """efinance 获取K线"""
        ef = self._get_efinance()
        if not ef:
            return []
        try:
            self._throttle()
            df = ef.stock.get_quote_history(stock_code, klt=101)
            if df is not None and not df.empty:
                df = df.tail(days)
                bars = []
                for _, row in df.iterrows():
                    bars.append(KlineBar(
                        date=str(row.get('日期', '')),
                        open=float(row.get('开盘', 0)),
                        high=float(row.get('最高', 0)),
                        low=float(row.get('最低', 0)),
                        close=float(row.get('收盘', 0)),
                        volume=int(row.get('成交量', 0)),
                        amount=float(row.get('成交额', 0)),
                        pct_chg=float(row.get('涨跌幅', 0)),
                        turnover_rate=float(row.get('换手率', 0)),
                    ))
                return bars
        except Exception as e:
            logger.debug(f"efinance kline error for {stock_code}: {e}")
        return []
    
    def _try_akshare_kline(self, stock_code: str, days: int) -> List[KlineBar]:
        """akshare 获取K线"""
        ak = self._get_akshare()
        if not ak:
            return []
        try:
            self._throttle()
            df = ak.stock_zh_a_hist(symbol=stock_code, period="daily", adjust="qfq")
            if df is not None and not df.empty:
                df = df.tail(days)
                bars = []
                for _, row in df.iterrows():
                    bars.append(KlineBar(
                        date=str(row.get('日期', '')),
                        open=float(row.get('开盘', 0)),
                        high=float(row.get('最高', 0)),
                        low=float(row.get('最低', 0)),
                        close=float(row.get('收盘', 0)),
                        volume=int(row.get('成交量', 0)),
                        amount=float(row.get('成交额', 0)),
                        pct_chg=float(row.get('涨跌幅', 0)),
                        turnover_rate=float(row.get('换手率', 0)),
                    ))
                return bars
        except Exception as e:
            logger.debug(f"akshare kline error for {stock_code}: {e}")
        return []
    
    def get_market_indices(self) -> Dict[str, RealtimeQuote]:
        """获取大盘指数"""
        indices = {}
        ak = self._get_akshare()
        if ak:
            try:
                self._throttle()
                df = ak.stock_zh_index_spot_em()
                if df is not None and not df.empty:
                    target = ['上证指数', '深证成指', '创业板指', '沪深300']
                    for name in target:
                        row = df[df['名称'] == name]
                        if not row.empty:
                            r = row.iloc[0]
                            indices[name] = RealtimeQuote(
                                code=str(r.get('代码', '')),
                                name=name,
                                price=float(r.get('最新价', 0)),
                                change_pct=float(r.get('涨跌幅', 0)),
                            )
            except Exception as e:
                logger.error(f"akshare market indices error: {e}")
        return indices
    
    def get_market_stats(self) -> Dict[str, Any]:
        """获取全市场涨跌统计"""
        ak = self._get_akshare()
        if ak:
            try:
                self._throttle()
                df = ak.stock_zh_a_spot_em()
                if df is not None and not df.empty:
                    up = len(df[df['涨跌幅'] > 0])
                    down = len(df[df['涨跌幅'] < 0])
                    flat = len(df[df['涨跌幅'] == 0])
                    limit_up = len(df[df['涨跌幅'] >= 9.9])
                    limit_down = len(df[df['涨跌幅'] <= -9.9])
                    return {
                        'up_count': up,
                        'down_count': down,
                        'flat_count': flat,
                        'limit_up': limit_up,
                        'limit_down': limit_down,
                    }
            except Exception as e:
                logger.error(f"akshare market stats error: {e}")
        return {}


# 全局实例
data_provider = DataProvider()
