# -*- coding: utf-8 -*-
"""
===================================
黄金趋势分析器 - 基于黄金市场特性优化
===================================

基于用户交易理念，针对黄金市场特性进行优化：
1. 严进策略 - 不追高，追求每笔交易成功率
2. 趋势交易 - MA5>MA10>MA20 多头排列，顺势而为
3. 效率优先 - 关注黄金市场特有的量价关系
4. 买点偏好 - 在 MA5/MA10 附近回踩买入

技术标准：
- 多头排列：MA5 > MA10 > MA20
- 乖离率：(Close - MA5) / MA5 < 3%（不追高，黄金波动相对较小）
- 量能形态：缩量回调优先，黄金交易量特性不同
"""

import logging
from dataclasses import dataclass, field
from typing import Optional, Dict, Any, List, Tuple
from enum import Enum

import pandas as pd
import numpy as np

from .stock_analyzer import StockTrendAnalyzer, TrendStatus, VolumeStatus, BuySignal, MACDStatus, RSIStatus, TrendAnalysisResult
from .search_service import get_search_service, SearchResponse
from .macro_data_provider import GoldMacroAnalyzer

logger = logging.getLogger(__name__)


class GoldTrendAnalyzer(StockTrendAnalyzer):
    """
    黄金趋势分析器

    基于股票趋势分析器扩展，针对黄金市场特性进行优化：
    1. 趋势判断 - MA5>MA10>MA20 多头排列
    2. 乖离率检测 - 不追高，偏离 MA5 超过 3% 不买（黄金波动相对较小）
    3. 量能分析 - 偏好缩量回调，调整量能判断阈值
    4. 买点识别 - 回踩 MA5/MA10 支撑
    5. MACD 指标 - 趋势确认和金叉死叉信号
    6. RSI 指标 - 超买超卖判断
    """
    
    # 黄金特有的交易参数配置
    BIAS_THRESHOLD = 3.0        # 乖离率阈值（%），黄金波动相对较小，设为3%
    VOLUME_SHRINK_RATIO = 0.7   # 缩量判断阈值（当日量/5日均量）
    VOLUME_HEAVY_RATIO = 1.8    # 放量判断阈值，黄金交易量特性不同，设为1.8
    MA_SUPPORT_TOLERANCE = 0.02  # MA 支撑判断容忍度（2%）

    def __init__(self):
        """初始化黄金分析器"""
        super().__init__()
        self.search_service = get_search_service()
        self.macro_analyzer = GoldMacroAnalyzer()
        logger.info("初始化黄金趋势分析器")
    
    def _analyze_volume(self, df: pd.DataFrame, result: TrendAnalysisResult) -> None:
        """
        针对黄金期货优化的量能分析
        
        黄金特有的量能判断逻辑：
        1. 调整放量判断阈值为1.8
        2. 考虑黄金作为避险资产的特性
        3. 优化量能趋势描述，添加黄金特有的分析视角
        """
        if len(df) < 5:
            return
        
        latest = df.iloc[-1]
        vol_5d_avg = df['volume'].iloc[-6:-1].mean()
        
        if vol_5d_avg > 0:
            result.volume_ratio_5d = float(latest['volume']) / vol_5d_avg
        
        # 判断价格变化
        prev_close = df.iloc[-2]['close']
        price_change = (latest['close'] - prev_close) / prev_close * 100
        
        # 黄金特有的量能判断逻辑
        if result.volume_ratio_5d >= self.VOLUME_HEAVY_RATIO:
            if price_change > 0:
                result.volume_status = VolumeStatus.HEAVY_VOLUME_UP
                result.volume_trend = "放量上涨，多头力量强劲（黄金）"
            else:
                result.volume_status = VolumeStatus.HEAVY_VOLUME_DOWN
                result.volume_trend = "放量下跌，注意风险（黄金）"
        elif result.volume_ratio_5d <= self.VOLUME_SHRINK_RATIO:
            if price_change > 0:
                result.volume_status = VolumeStatus.SHRINK_VOLUME_UP
                result.volume_trend = "缩量上涨，上攻动能不足（黄金）"
            else:
                result.volume_status = VolumeStatus.SHRINK_VOLUME_DOWN
                result.volume_trend = "缩量回调，洗盘特征明显（黄金，好）"
        else:
            result.volume_status = VolumeStatus.NORMAL
            result.volume_trend = "量能正常（黄金）"
    
    def _analyze_trend(self, df: pd.DataFrame, result: TrendAnalysisResult) -> None:
        """
        分析黄金趋势状态
        
        基于股票趋势分析逻辑，针对黄金特性进行优化：
        1. 黄金趋势形成和持续时间不同
        2. 黄金作为避险资产的特性
        """
        super()._analyze_trend(df, result)
        
        # 添加黄金特有的趋势分析逻辑
        if result.trend_status in [TrendStatus.STRONG_BULL, TrendStatus.BULL]:
            # 黄金多头趋势可能更持久
            result.ma_alignment += "（黄金多头趋势可能更持久）"
        elif result.trend_status in [TrendStatus.STRONG_BEAR, TrendStatus.BEAR]:
            # 黄金空头趋势可能相对短暂，往往是回调
            result.ma_alignment += "（黄金空头趋势可能相对短暂，关注反弹）"
    
    def _generate_signal(self, result: TrendAnalysisResult) -> None:
        """
        生成黄金特有的买入信号
        
        基于股票信号生成逻辑，针对黄金特性进行优化：
        1. 考虑黄金作为避险资产的特性
        2. 黄金价格波动相对较小，信号阈值调整
        """
        super()._generate_signal(result)
        
        # 添加黄金特有的信号分析
        if result.buy_signal in [BuySignal.STRONG_BUY, BuySignal.BUY]:
            # 黄金买入信号可能更可靠
            result.signal_reasons.append("✅ 黄金买入信号，避险资产特性增强可靠性")
        elif result.buy_signal in [BuySignal.SELL, BuySignal.STRONG_SELL]:
            # 黄金卖出信号可能需要更谨慎判断
            result.risk_factors.append("⚠️ 黄金卖出信号，需考虑避险需求对价格的支撑")
    
    def _analyze_macro_factors(self, macro_news: dict) -> dict:
        """
        分析宏观因素对黄金的影响
        
        Args:
            macro_news: 宏观新闻搜索结果
            
        Returns:
            包含宏观分析结果的字典
        """
        factors = {}
        total_score = 50
        
        # 利好关键词
        bullish_keywords = ['加息', '通胀', '地缘政治', '避险', '央行购金', '不确定性']
        # 利空关键词
        bearish_keywords = ['降息', '经济强劲', '美元走强', '通胀缓解']
        
        for category, response in macro_news.items():
            if not response.success or not response.results:
                continue
            
            category_score = 50
            bullish_count = 0
            bearish_count = 0
            
            for result in response.results:
                content = f"{result.title} {result.snippet}"
                # 统计关键词
                for kw in bullish_keywords:
                    if kw in content:
                        bullish_count += 1
                for kw in bearish_keywords:
                    if kw in content:
                        bearish_count += 1
            
            # 计算得分
            if bullish_count > bearish_count:
                category_score = min(80, 50 + (bullish_count - bearish_count) * 10)
            elif bearish_count > bullish_count:
                category_score = max(20, 50 - (bearish_count - bullish_count) * 10)
            
            factors[category] = {
                'score': category_score,
                'bullish_count': bullish_count,
                'bearish_count': bearish_count
            }
            total_score += (category_score - 50) * 0.1
        
        total_score = max(0, min(100, total_score))
        
        return {
            'total_score': round(total_score),
            'factors': factors,
            'timestamp': pd.Timestamp.now().isoformat()
        }
    
    def analyze_with_macro(self, df: pd.DataFrame, code: str) -> TrendAnalysisResult:
        """
        带宏观因素的黄金分析
        
        Args:
            df: 包含 OHLCV 数据的 DataFrame
            code: 黄金代码
            
        Returns:
            TrendAnalysisResult 分析结果
        """
        # 1. 执行基础技术分析
        result = self.analyze(df, code)
        
        # 2. 获取宏观新闻
        macro_news_score = 50
        try:
            if self.search_service and self.search_service.is_available:
                logger.info(f"搜索黄金宏观因素新闻")
                macro_news = self.search_service.search_gold_macro_news(max_results=3)
                
                if macro_news:
                    # 分析新闻宏观因素
                    news_analysis = self._analyze_macro_factors(macro_news)
                    macro_news_score = news_analysis['total_score']
                    result.macro_news = macro_news
                    logger.info(f"新闻宏观因素分析完成，总评分: {macro_news_score}")
                else:
                    logger.info("未获取到宏观新闻数据")
            else:
                logger.info("搜索服务不可用，跳过新闻宏观因素分析")
        except Exception as e:
            logger.warning(f"获取宏观新闻失败: {e}")
        
        # 3. 获取结构化宏观数据
        macro_data_score = 50
        try:
            logger.info(f"获取黄金宏观数据")
            macro_data = self.macro_analyzer.get_macro_score()
            
            if macro_data:
                macro_data_score = macro_data['total_score']
                result.macro_score = macro_data_score
                result.macro_factors = macro_data['factors']
                result.macro_summary = macro_data['summary']
                result.macro_timestamp = macro_data['timestamp']
                logger.info(f"结构化宏观数据分析完成，总评分: {macro_data_score}")
            else:
                logger.info("未获取到结构化宏观数据")
        except Exception as e:
            logger.warning(f"获取结构化宏观数据失败: {e}")
        
        # 4. 计算综合宏观评分
        # 新闻评分权重 30%，结构化数据评分权重 70%
        total_macro_score = int(macro_news_score * 0.3 + macro_data_score * 0.7)
        total_macro_score = max(0, min(100, total_macro_score))
        
        # 保存原始技术评分和各项宏观评分（用于报告展示）
        original_technical_score = result.signal_score  # 保存技术评分
        result.technical_score = original_technical_score  # 技术评分（调整前）
        result.macro_news_score = macro_news_score  # 新闻评分
        result.macro_data_score = macro_data_score  # 数据评分
        result.total_macro_score = total_macro_score  # 综合宏观评分
        
        # 5. 调整综合评分
        # 技术评分权重 60%，宏观评分权重 40%
        result.signal_score = int(original_technical_score * 0.6 + total_macro_score * 0.4)
        result.signal_score = max(0, min(100, result.signal_score))
        
        logger.info(f"技术评分: {original_technical_score}, 新闻评分: {macro_news_score}, "
                   f"数据评分: {macro_data_score}, 综合宏观评分: {total_macro_score}, "
                   f"最终信号评分: {result.signal_score}")
        
        return result
    
    def format_analysis(self, result: TrendAnalysisResult) -> str:
        """
        格式化黄金分析结果为文本
        
        Args:
            result: 分析结果

        Returns:
            格式化的分析文本
        """
        lines = [
            f"=== {result.code} 黄金趋势分析 ===",
            f"",
            f"📊 趋势判断: {result.trend_status.value}",
            f"   均线排列: {result.ma_alignment}",
            f"   趋势强度: {result.trend_strength}/100",
            f"",
            f"📈 均线数据:",
            f"   现价: {result.current_price:.2f}",
            f"   MA5:  {result.ma5:.2f} (乖离 {result.bias_ma5:+.2f}%)",
            f"   MA10: {result.ma10:.2f} (乖离 {result.bias_ma10:+.2f}%)",
            f"   MA20: {result.ma20:.2f} (乖离 {result.bias_ma20:+.2f}%)",
            f"",
            f"📊 量能分析: {result.volume_status.value}",
            f"   量比(vs5日): {result.volume_ratio_5d:.2f}",
            f"   量能趋势: {result.volume_trend}",
            f"",
            f"📈 MACD指标: {result.macd_status.value}",
            f"   DIF: {result.macd_dif:.4f}",
            f"   DEA: {result.macd_dea:.4f}",
            f"   MACD: {result.macd_bar:.4f}",
            f"   信号: {result.macd_signal}",
            f"",
            f"📊 RSI指标: {result.rsi_status.value}",
            f"   RSI(6): {result.rsi_6:.1f}",
            f"   RSI(12): {result.rsi_12:.1f}",
            f"   RSI(24): {result.rsi_24:.1f}",
            f"   信号: {result.rsi_signal}",
            f"",
            f"🎯 操作建议: {result.buy_signal.value}",
            f"   综合评分: {result.signal_score}/100",
        ]

        if result.signal_reasons:
            lines.append(f"")
            lines.append(f"✅ 买入理由:")
            for reason in result.signal_reasons:
                lines.append(f"   {reason}")

        if result.risk_factors:
            lines.append(f"")
            lines.append(f"⚠️ 风险因素:")
            for risk in result.risk_factors:
                lines.append(f"   {risk}")

        # 添加黄金特有的分析提示
        lines.append(f"")
        lines.append(f"💡 黄金市场提示:")
        lines.append(f"   - 黄金作为避险资产，在市场不确定性增加时往往表现强势")
        lines.append(f"   - 黄金价格受全球宏观经济、地缘政治等因素影响较大")
        lines.append(f"   - 黄金趋势一旦形成，往往持续时间较长")

        # 添加宏观因素分析
        if hasattr(result, 'macro_score') and result.macro_score is not None:
            lines.append(f"")
            lines.append(f"🌍 宏观因素分析:")
            
            # 显示评分详情（如果有）
            if hasattr(result, 'technical_score'):
                lines.append(f"   评分详情:")
                lines.append(f"   - 技术评分: {result.technical_score}/100 (权重60%)")
                lines.append(f"   - 宏观评分: {result.total_macro_score}/100 (权重40%)")
                if hasattr(result, 'macro_news_score'):
                    lines.append(f"     - 新闻评分: {result.macro_news_score}/100 (权重30%)")
                if hasattr(result, 'macro_data_score'):
                    lines.append(f"     - 数据评分: {result.macro_data_score}/100 (权重70%)")
                lines.append(f"")
            
            lines.append(f"   综合评分: {result.macro_score}/100")
            
            if hasattr(result, 'macro_summary') and result.macro_summary:
                lines.append(f"   分析总结: {result.macro_summary}")
            
            if hasattr(result, 'macro_factors') and result.macro_factors:
                lines.append(f"   关键因素:")
                for factor_name, factor_data in result.macro_factors.items():
                    score = factor_data['score']
                    value = factor_data.get('value', 'N/A')
                    change = factor_data.get('change', '')
                    change_str = f" (变化{change}%)" if change else ""
                    emoji = "📈" if score > 60 else "📉" if score < 40 else "➡️"
                    lines.append(f"   {emoji} {factor_name}: {value}{change_str} ({score}/100)")
            
            if hasattr(result, 'macro_news') and result.macro_news:
                lines.append(f"")
                lines.append(f"📰 宏观新闻摘要:")
                news_count = 0
                for category, response in result.macro_news.items():
                    if response.success and response.results:
                        for i, news in enumerate(response.results[:1]):  # 每个类别只显示1条新闻
                            if news_count >= 3:
                                break
                            lines.append(f"   • {news.title[:80]}")
                            news_count += 1
                        if news_count >= 3:
                            break
            
            if hasattr(result, 'macro_timestamp'):
                lines.append(f"")
                lines.append(f"   🕒 数据时间: {result.macro_timestamp[:19]}")

        return "\n".join(lines)


def analyze_gold(df: pd.DataFrame, code: str, include_macro: bool = True) -> TrendAnalysisResult:
    """
    便捷函数：分析黄金数据
    
    Args:
        df: 包含 OHLCV 数据的 DataFrame
        code: 黄金代码
        include_macro: 是否包含宏观因素分析
        
    Returns:
        TrendAnalysisResult 分析结果
    """
    analyzer = GoldTrendAnalyzer()
    if include_macro:
        return analyzer.analyze_with_macro(df, code)
    else:
        return analyzer.analyze(df, code)


if __name__ == "__main__":
    # 测试代码
    logging.basicConfig(level=logging.INFO)
    
    # 模拟黄金数据测试
    import numpy as np
    
    dates = pd.date_range(start='2025-01-01', periods=60, freq='D')
    np.random.seed(42)
    
    # 模拟黄金价格数据（波动相对较小）
    base_price = 2000.0
    prices = [base_price]
    for i in range(59):
        change = np.random.randn() * 0.01 + 0.002  # 黄金波动相对较小
        prices.append(prices[-1] * (1 + change))
    
    df = pd.DataFrame({
        'date': dates,
        'open': prices,
        'high': [p * (1 + np.random.uniform(0, 0.01)) for p in prices],
        'low': [p * (1 - np.random.uniform(0, 0.01)) for p in prices],
        'close': prices,
        'volume': [np.random.randint(100000, 500000) for _ in prices],  # 黄金交易量特性
    })
    
    analyzer = GoldTrendAnalyzer()
    result = analyzer.analyze(df, 'GC=F')
    print(analyzer.format_analysis(result))
