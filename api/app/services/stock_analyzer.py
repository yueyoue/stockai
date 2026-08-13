"""
股票分析引擎 - 生成 AI 决策仪表盘
基于 daily_stock_analysis 的分析逻辑
"""
import logging
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional
from enum import Enum

import numpy as np

from app.services.data_provider import DataProvider, RealtimeQuote, KlineBar

logger = logging.getLogger(__name__)


class TrendStatus(str, Enum):
    STRONG_BULL = "强势多头"
    BULL = "多头排列"
    WEAK_BULL = "弱势多头"
    CONSOLIDATION = "盘整"
    WEAK_BEAR = "弱势空头"
    BEAR = "空头排列"
    STRONG_BEAR = "强势空头"


class VolumeStatus(str, Enum):
    HEAVY_UP = "放量上涨"
    HEAVY_DOWN = "放量下跌"
    SHRINK_UP = "缩量上涨"
    SHRINK_DOWN = "缩量回调"
    NORMAL = "量能正常"


class BuySignal(str, Enum):
    STRONG_BUY = "强烈买入"
    BUY = "买入"
    HOLD = "持有"
    WAIT = "观望"
    SELL = "卖出"
    STRONG_SELL = "强烈卖出"


@dataclass
class TechnicalAnalysis:
    """技术面分析结果"""
    # 均线
    ma5: float = 0.0
    ma10: float = 0.0
    ma20: float = 0.0
    trend_status: str = "盘整"
    trend_score: int = 50
    
    # 乖离率
    bias5: float = 0.0
    bias_risk: str = "安全"
    
    # 量能
    volume_ratio: float = 0.0
    volume_status: str = "量能正常"
    
    # MACD
    macd_dif: float = 0.0
    macd_dea: float = 0.0
    macd_hist: float = 0.0
    macd_status: str = "中性"
    
    # RSI
    rsi_6: float = 50.0
    rsi_status: str = "中性"
    
    # 支撑压力
    support_price: float = 0.0
    resistance_price: float = 0.0
    
    # 综合
    overall_score: int = 50
    signal: str = "观望"


@dataclass
class AnalysisResult:
    """完整分析结果"""
    code: str
    name: str
    market: str = "A股"
    
    # 实时行情
    quote: Optional[RealtimeQuote] = None
    
    # 技术分析
    technical: Optional[TechnicalAnalysis] = None
    
    # 操作建议
    signal: str = "观望"
    signal_icon: str = "🟡"
    core_conclusion: str = ""
    
    # 仓位建议
    holder_advice: str = ""
    empty_advice: str = ""
    
    # 交易点位
    buy_zone_1: str = ""
    buy_zone_2: str = ""
    stop_loss: str = ""
    target_1: str = ""
    target_2: str = ""
    
    # 检查清单
    checklist: List[Dict[str, str]] = field(default_factory=list)
    
    # 评分
    overall_score: int = 50
    sentiment_label: str = "中性"


class StockAnalyzer:
    """股票分析器"""
    
    def __init__(self, data_provider: DataProvider):
        self.dp = data_provider
    
    def analyze(self, stock_code: str, stock_name: str = "") -> AnalysisResult:
        """完整分析一只股票"""
        result = AnalysisResult(code=stock_code, name=stock_name)
        
        # 1. 获取实时行情
        quote = self.dp.get_realtime_quote(stock_code)
        if quote:
            result.quote = quote
            if not result.name:
                result.name = quote.name
        
        # 2. 获取K线数据
        klines = self.dp.get_kline(stock_code, days=60)
        if not klines:
            result.core_conclusion = "数据获取失败，无法分析"
            return result
        
        # 3. 技术分析
        tech = self._analyze_technical(klines, quote)
        result.technical = tech
        
        # 4. 生成信号和建议
        result.signal = tech.signal
        result.overall_score = tech.overall_score
        result.signal_icon = self._get_signal_icon(tech.signal)
        result.sentiment_label = self._get_sentiment_label(tech.overall_score)
        result.core_conclusion = self._generate_conclusion(result)
        result.holder_advice = self._generate_holder_advice(tech)
        result.empty_advice = self._generate_empty_advice(tech)
        
        # 5. 交易点位
        result.buy_zone_1 = self._calc_buy_zone_1(klines, tech)
        result.buy_zone_2 = self._calc_buy_zone_2(klines, tech)
        result.stop_loss = self._calc_stop_loss(klines, tech)
        result.target_1 = self._calc_target_1(klines, tech)
        result.target_2 = self._calc_target_2(klines, tech)
        
        # 6. 操作检查清单
        result.checklist = self._generate_checklist(tech, quote)
        
        return result
    
    def _analyze_technical(self, klines: List[KlineBar], quote: Optional[RealtimeQuote]) -> TechnicalAnalysis:
        """技术面分析"""
        tech = TechnicalAnalysis()
        
        if len(klines) < 20:
            return tech
        
        closes = [k.close for k in klines]
        volumes = [k.volume for k in klines]
        
        # 均线
        tech.ma5 = np.mean(closes[-5:])
        tech.ma10 = np.mean(closes[-10:])
        tech.ma20 = np.mean(closes[-20:])
        
        current_price = closes[-1]
        
        # 趋势判断
        tech.trend_status, tech.trend_score = self._calc_trend(tech.ma5, tech.ma10, tech.ma20)
        
        # 乖离率
        tech.bias5 = (current_price - tech.ma5) / tech.ma5 * 100 if tech.ma5 > 0 else 0
        tech.bias_risk = "安全" if abs(tech.bias5) < 3 else ("警戒" if abs(tech.bias5) < 5 else "危险")
        
        # 量能
        avg_vol_5 = np.mean(volumes[-5:])
        avg_vol_10 = np.mean(volumes[-10:])
        tech.volume_ratio = avg_vol_5 / avg_vol_10 if avg_vol_10 > 0 else 1.0
        tech.volume_status = self._calc_volume_status(klines)
        
        # MACD
        tech.macd_dif, tech.macd_dea, tech.macd_hist = self._calc_macd(closes)
        tech.macd_status = self._calc_macd_status(tech.macd_dif, tech.macd_dea, tech.macd_hist)
        
        # RSI
        tech.rsi_6 = self._calc_rsi(closes, 6)
        tech.rsi_status = self._calc_rsi_status(tech.rsi_6)
        
        # 支撑压力
        tech.support_price = self._calc_support(klines, tech)
        tech.resistance_price = self._calc_resistance(klines, tech)
        
        # 综合评分
        tech.overall_score = self._calc_overall_score(tech)
        tech.signal = self._calc_signal(tech)
        
        return tech
    
    def _calc_trend(self, ma5: float, ma10: float, ma20: float) -> tuple:
        """计算趋势"""
        if ma5 > ma10 > ma20:
            gap = (ma5 - ma20) / ma20 * 100
            if gap > 3:
                return TrendStatus.STRONG_BULL.value, 85
            return TrendStatus.BULL.value, 75
        elif ma5 > ma10:
            return TrendStatus.WEAK_BULL.value, 60
        elif ma5 < ma10 < ma20:
            gap = (ma20 - ma5) / ma20 * 100
            if gap > 3:
                return TrendStatus.STRONG_BEAR.value, 15
            return TrendStatus.BEAR.value, 25
        elif ma5 < ma10:
            return TrendStatus.WEAK_BEAR.value, 40
        return TrendStatus.CONSOLIDATION.value, 50
    
    def _calc_volume_status(self, klines: List[KlineBar]) -> str:
        """计算量能状态"""
        if len(klines) < 5:
            return VolumeStatus.NORMAL.value
        
        recent_vol = klines[-1].volume
        avg_vol = np.mean([k.volume for k in klines[-5:-1]])
        price_chg = klines[-1].pct_chg
        
        if recent_vol > avg_vol * 1.5:
            return VolumeStatus.HEAVY_UP.value if price_chg > 0 else VolumeStatus.HEAVY_DOWN.value
        elif recent_vol < avg_vol * 0.7:
            return VolumeStatus.SHRINK_UP.value if price_chg > 0 else VolumeStatus.SHRINK_DOWN.value
        return VolumeStatus.NORMAL.value
    
    def _calc_macd(self, closes: List[float]) -> tuple:
        """计算MACD"""
        if len(closes) < 26:
            return 0, 0, 0
        
        ema12 = self._ema(closes, 12)
        ema26 = self._ema(closes, 26)
        dif = ema12 - ema26
        
        # 简化DEA计算
        dif_list = []
        e12 = closes[0]
        e26 = closes[0]
        for c in closes:
            e12 = e12 * 11/13 + c * 2/13
            e26 = e26 * 25/27 + c * 2/27
            dif_list.append(e12 - e26)
        
        dea = dif_list[0]
        for d in dif_list:
            dea = dea * 8/10 + d * 2/10
        
        hist = (dif_list[-1] - dea) * 2
        return dif_list[-1], dea, hist
    
    def _ema(self, data: List[float], period: int) -> float:
        """计算EMA"""
        multiplier = 2 / (period + 1)
        ema = data[0]
        for val in data[1:]:
            ema = val * multiplier + ema * (1 - multiplier)
        return ema
    
    def _calc_macd_status(self, dif: float, dea: float, hist: float) -> str:
        if dif > dea and dif > 0:
            return "零轴上金叉" if hist > 0 else "多头"
        elif dif > dea:
            return "金叉"
        elif dif < dea and dif < 0:
            return "空头"
        elif dif < dea:
            return "死叉"
        return "中性"
    
    def _calc_rsi(self, closes: List[float], period: int = 6) -> float:
        """计算RSI"""
        if len(closes) < period + 1:
            return 50.0
        
        gains = []
        losses = []
        for i in range(len(closes) - period, len(closes)):
            change = closes[i] - closes[i-1]
            if change > 0:
                gains.append(change)
                losses.append(0)
            else:
                gains.append(0)
                losses.append(abs(change))
        
        avg_gain = np.mean(gains)
        avg_loss = np.mean(losses)
        
        if avg_loss == 0:
            return 100.0
        rs = avg_gain / avg_loss
        return 100 - (100 / (1 + rs))
    
    def _calc_rsi_status(self, rsi: float) -> str:
        if rsi > 80:
            return "超买"
        elif rsi > 60:
            return "强势"
        elif rsi > 40:
            return "中性"
        elif rsi > 20:
            return "弱势"
        return "超卖"
    
    def _calc_support(self, klines: List[KlineBar], tech: TechnicalAnalysis) -> float:
        """计算支撑位"""
        lows = [k.low for k in klines[-20:]]
        return min(lows)
    
    def _calc_resistance(self, klines: List[KlineBar], tech: TechnicalAnalysis) -> float:
        """计算压力位"""
        highs = [k.high for k in klines[-20:]]
        return max(highs)
    
    def _calc_overall_score(self, tech: TechnicalAnalysis) -> int:
        """综合评分"""
        score = 50
        
        # 趋势权重40%
        score += (tech.trend_score - 50) * 0.4
        
        # MACD权重20%
        if "金叉" in tech.macd_status or "多头" in tech.macd_status:
            score += 10
        elif "死叉" in tech.macd_status or "空头" in tech.macd_status:
            score -= 10
        
        # RSI权重20%
        if tech.rsi_6 > 60:
            score += 5
        elif tech.rsi_6 < 40:
            score -= 5
        
        # 量能权重20%
        if "放量上涨" in tech.volume_status:
            score += 10
        elif "缩量回调" in tech.volume_status:
            score += 5
        elif "放量下跌" in tech.volume_status:
            score -= 10
        
        return max(0, min(100, int(score)))
    
    def _calc_signal(self, tech: TechnicalAnalysis) -> str:
        """计算操作信号"""
        score = tech.overall_score
        if score >= 80:
            return BuySignal.STRONG_BUY.value
        elif score >= 65:
            return BuySignal.BUY.value
        elif score >= 50:
            return BuySignal.HOLD.value
        elif score >= 35:
            return BuySignal.WAIT.value
        elif score >= 20:
            return BuySignal.SELL.value
        return BuySignal.STRONG_SELL.value
    
    def _get_signal_icon(self, signal: str) -> str:
        icons = {
            "强烈买入": "🟢", "买入": "🟢", "持有": "🟡",
            "观望": "🟡", "卖出": "🔴", "强烈卖出": "🔴",
        }
        return icons.get(signal, "⚠️")
    
    def _get_sentiment_label(self, score: int) -> str:
        if score >= 70:
            return "看多"
        elif score >= 40:
            return "中性"
        return "看空"
    
    def _generate_conclusion(self, result: AnalysisResult) -> str:
        tech = result.technical
        if not tech:
            return "数据不足，无法判断"
        
        parts = []
        parts.append(f"趋势{tech.trend_status}")
        parts.append(f"综合评分{result.overall_score}")
        
        if result.overall_score >= 70:
            parts.append("建议持仓")
        elif result.overall_score >= 50:
            parts.append("可持有观望")
        else:
            parts.append("建议空仓")
        
        return "，".join(parts)
    
    def _generate_holder_advice(self, tech: TechnicalAnalysis) -> str:
        if tech.overall_score >= 70:
            return f"继续持有，趋势{tech.trend_status}。关注{tech.resistance_price:.2f}压力位突破情况。"
        elif tech.overall_score >= 50:
            return f"谨慎持有，设置止损。若跌破{tech.support_price:.2f}考虑减仓。"
        else:
            return f"趋势转弱，建议逢高减仓。止损位{tech.support_price:.2f}。"
    
    def _generate_empty_advice(self, tech: TechnicalAnalysis) -> str:
        if tech.overall_score >= 70:
            return f"趋势良好，可考虑分批建仓。回踩均线支撑{tech.support_price:.2f}附近买入。"
        elif tech.overall_score >= 50:
            return "暂不建议入场，等待趋势明确。"
        else:
            "趋势向下，空仓观望。"
    
    def _calc_buy_zone_1(self, klines: List[KlineBar], tech: TechnicalAnalysis) -> str:
        return f"{tech.ma5:.2f} - {tech.ma10:.2f}"
    
    def _calc_buy_zone_2(self, klines: List[KlineBar], tech: TechnicalAnalysis) -> str:
        return f"{tech.ma10:.2f} - {tech.ma20:.2f}"
    
    def _calc_stop_loss(self, klines: List[KlineBar], tech: TechnicalAnalysis) -> str:
        return f"{tech.support_price:.2f}"
    
    def _calc_target_1(self, klines: List[KlineBar], tech: TechnicalAnalysis) -> str:
        return f"{tech.resistance_price:.2f}"
    
    def _calc_target_2(self, klines: List[KlineBar], tech: TechnicalAnalysis) -> str:
        return f"{tech.resistance_price * 1.05:.2f}"
    
    def _generate_checklist(self, tech: TechnicalAnalysis, quote: Optional[RealtimeQuote]) -> List[Dict[str, str]]:
        """生成操作检查清单"""
        items = []
        
        # 均线多头排列
        if "多头" in tech.trend_status:
            items.append({"item": "均线多头排列", "status": "✅", "detail": tech.trend_status})
        elif "空头" in tech.trend_status:
            items.append({"item": "均线多头排列", "status": "❌", "detail": tech.trend_status})
        else:
            items.append({"item": "均线多头排列", "status": "⚠️", "detail": tech.trend_status})
        
        # 乖离率
        if tech.bias_risk == "安全":
            items.append({"item": "乖离率安全", "status": "✅", "detail": f"BIAS5={tech.bias5:.2f}%"})
        elif tech.bias_risk == "警戒":
            items.append({"item": "乖离率安全", "status": "⚠️", "detail": f"BIAS5={tech.bias5:.2f}%，接近追高"})
        else:
            items.append({"item": "乖离率安全", "status": "❌", "detail": f"BIAS5={tech.bias5:.2f}%，不追高"})
        
        # 量能
        if "放量上涨" in tech.volume_status or "缩量回调" in tech.volume_status:
            items.append({"item": "量能健康", "status": "✅", "detail": tech.volume_status})
        elif "放量下跌" in tech.volume_status:
            items.append({"item": "量能健康", "status": "❌", "detail": tech.volume_status})
        else:
            items.append({"item": "量能健康", "status": "⚠️", "detail": tech.volume_status})
        
        # MACD
        if "金叉" in tech.macd_status or "多头" in tech.macd_status:
            items.append({"item": "MACD信号", "status": "✅", "detail": tech.macd_status})
        elif "死叉" in tech.macd_status or "空头" in tech.macd_status:
            items.append({"item": "MACD信号", "status": "❌", "detail": tech.macd_status})
        else:
            items.append({"item": "MACD信号", "status": "⚠️", "detail": tech.macd_status})
        
        # RSI
        if tech.rsi_status in ["强势", "中性"]:
            items.append({"item": "RSI状态", "status": "✅", "detail": f"RSI6={tech.rsi_6:.1f}({tech.rsi_status})"})
        elif tech.rsi_status == "超买":
            items.append({"item": "RSI状态", "status": "⚠️", "detail": f"RSI6={tech.rsi_6:.1f}(超买)"})
        else:
            items.append({"item": "RSI状态", "status": "❌", "detail": f"RSI6={tech.rsi_6:.1f}({tech.rsi_status})"})
        
        return items


def generate_dashboard_markdown(result: AnalysisResult) -> str:
    """生成决策仪表盘 Markdown"""
    q = result.quote
    tech = result.technical
    
    lines = []
    lines.append(f"# 📊 {result.name}({result.code}) AI 决策仪表盘\n")
    lines.append(f"**{result.signal_icon} {result.signal}** | 综合评分: **{result.overall_score}/100** ({result.sentiment_label})")
    lines.append(f"> {result.core_conclusion}\n")
    
    # 实时行情
    if q:
        lines.append("## 📈 实时行情\n")
        lines.append(f"| 指标 | 数值 |")
        lines.append(f"|------|------|")
        lines.append(f"| 最新价 | **{q.price:.2f}** ({q.change_pct:+.2f}%) |")
        lines.append(f"| 开盘 | {q.open_price:.2f} |")
        lines.append(f"| 最高/最低 | {q.high:.2f} / {q.low:.2f} |")
        lines.append(f"| 成交量 | {q.volume/10000:.0f}万手 |")
        lines.append(f"| 成交额 | {q.amount/1e8:.2f}亿 |")
        lines.append(f"| 换手率 | {q.turnover_rate:.2f}% |")
        if q.pe_ratio:
            lines.append(f"| 市盈率 | {q.pe_ratio:.2f} |")
        if q.total_mv:
            lines.append(f"| 总市值 | {q.total_mv:.0f}亿 |")
        lines.append("")
    
    # 技术面
    if tech:
        lines.append("## 📐 技术面分析\n")
        lines.append(f"**趋势**: {tech.trend_status} (评分: {tech.trend_score}/100)")
        lines.append(f"- MA5: {tech.ma5:.2f} | MA10: {tech.ma10:.2f} | MA20: {tech.ma20:.2f}")
        lines.append(f"- 乖离率: {tech.bias5:.2f}% ({tech.bias_risk})")
        lines.append(f"- 量比: {tech.volume_ratio:.2f} ({tech.volume_status})")
        lines.append(f"- MACD: DIF={tech.macd_dif:.3f} DEA={tech.macd_dea:.3f} ({tech.macd_status})")
        lines.append(f"- RSI(6): {tech.rsi_6:.1f} ({tech.rsi_status})")
        lines.append(f"- 支撑位: {tech.support_price:.2f} | 压力位: {tech.resistance_price:.2f}")
        lines.append("")
    
    # 操作建议
    lines.append("## 💡 操作建议\n")
    lines.append(f"**持仓者**: {result.holder_advice}")
    lines.append(f"**空仓者**: {result.empty_advice}")
    lines.append("")
    
    # 交易狙击方案
    lines.append("## 🎯 交易狙击方案\n")
    lines.append(f"| 点位 | 价格 |")
    lines.append(f"|------|------|")
    lines.append(f"| 🟢 理想买入区间 | {result.buy_zone_1} |")
    lines.append(f"| 🟢 二次加仓区间 | {result.buy_zone_2} |")
    lines.append(f"| 🔴 硬性止损 | {result.stop_loss} |")
    lines.append(f"| 🎯 第一目标 | {result.target_1} |")
    lines.append(f"| 🎯 第二目标 | {result.target_2} |")
    lines.append("")
    
    # 操作检查清单
    if result.checklist:
        lines.append("## ✅ 操作检查清单\n")
        for item in result.checklist:
            lines.append(f"- {item['status']} **{item['item']}**: {item['detail']}")
        lines.append("")
    
    lines.append("---")
    lines.append("⚠️ *以上分析仅基于技术指标客观拆解，不构成任何投资建议。*")
    
    return "\n".join(lines)


def generate_market_dashboard(provider: DataProvider) -> str:
    """生成大盘复盘仪表盘"""
    lines = []
    lines.append("# 📊 大盘复盘仪表盘\n")
    
    # 大盘指数
    indices = provider.get_market_indices()
    if indices:
        lines.append("## 📈 主要指数\n")
        lines.append("| 指数 | 点位 | 涨跌幅 |")
        lines.append("|------|------|--------|")
        for name, idx in indices.items():
            icon = "🟢" if idx.change_pct > 0 else "🔴"
            lines.append(f"| {name} | {idx.price:.2f} | {icon} {idx.change_pct:+.2f}% |")
        lines.append("")
    
    # 涨跌统计
    stats = provider.get_market_stats()
    if stats:
        lines.append("## 📊 市场统计\n")
        lines.append(f"- 上涨: **{stats.get('up_count', 0)}** | 下跌: **{stats.get('down_count', 0)}** | 平盘: {stats.get('flat_count', 0)}")
        lines.append(f"- 涨停: **{stats.get('limit_up', 0)}** | 跌停: **{stats.get('limit_down', 0)}**")
        lines.append("")
    
    # 情绪判定
    if indices:
        sh_idx = indices.get('上证指数')
        if sh_idx:
            if sh_idx.change_pct > 1:
                lines.append("**整体情绪**: 🟢 偏多，市场活跃")
            elif sh_idx.change_pct > 0:
                lines.append("**整体情绪**: 🟡 中性偏多")
            elif sh_idx.change_pct > -1:
                lines.append("**整体情绪**: 🟡 中性偏空")
            else:
                lines.append("**整体情绪**: 🔴 偏空，注意风险")
    
    lines.append("\n---")
    lines.append("⚠️ *以上数据仅供参考，不构成任何投资建议。*")
    
    return "\n".join(lines)
