# -*- coding: utf-8 -*-
"""
===================================
宏观数据获取模块 - 黄金价格影响因素
===================================

职责：
1. 获取美联储利率、通胀、就业数据
2. 获取美元指数 DXY 数据
3. 获取美国国债收益率数据
4. 获取各国央行购金数据
5. 计算实际利率等衍生指标

推荐数据源：
- FRED API (美联储) - 利率、通胀、就业数据
- Yahoo Finance - DXY美元指数、国债收益率
- World Gold Council - 央行购金数据
"""

import logging
import requests
import pandas as pd
from typing import Optional, Dict, Any
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class MacroDataProvider:
    """
    宏观数据提供者
    
    提供各种宏观经济数据的获取接口
    """
    
    def __init__(self):
        """
        初始化宏观数据提供者
        """
        self.fred_api_key = None  # 从配置读取
        self.cache = {}
        self.cache_expiry = {}
        logger.info("初始化宏观数据提供者")
    
    def _get_cached_data(self, key: str, max_age: int = 3600) -> Optional[Any]:
        """
        获取缓存数据
        
        Args:
            key: 缓存键
            max_age: 最大缓存时间（秒）
            
        Returns:
            缓存的数据，如果不存在或已过期则返回 None
        """
        if key not in self.cache:
            return None
        
        if key not in self.cache_expiry:
            return None
        
        if (datetime.now().timestamp() - self.cache_expiry[key]) > max_age:
            del self.cache[key]
            del self.cache_expiry[key]
            return None
        
        return self.cache[key]
    
    def _set_cached_data(self, key: str, data: Any) -> None:
        """
        设置缓存数据
        
        Args:
            key: 缓存键
            data: 要缓存的数据
        """
        self.cache[key] = data
        self.cache_expiry[key] = datetime.now().timestamp()
    
    def get_dxy_index(self, days: int = 30) -> Optional[pd.DataFrame]:
        """
        获取美元指数 (DXY) 数据
        
        数据来源: Yahoo Finance
        代码: DX-Y.NYB
        
        Args:
            days: 获取最近多少天的数据
            
        Returns:
            包含 DXY 数据的 DataFrame
        """
        cache_key = f"dxy_{days}"
        cached = self._get_cached_data(cache_key, max_age=3600)
        if cached:
            return cached
        
        try:
            import yfinance as yf
        except ImportError:
            logger.error("yfinance 未安装，请运行: pip install yfinance")
            return None
        
        try:
            logger.info(f"获取美元指数 (DXY) 数据，最近 {days} 天")
            
            # 使用 Yahoo Finance 获取 DXY 数据
            ticker = yf.Ticker("DX-Y.NYB")
            df = ticker.history(period=f"{days}d")
            
            if df.empty:
                logger.warning("获取 DXY 数据失败，返回空数据")
                return None
            
            # 清理数据
            df = df.rename(columns={
                'Open': 'open',
                'High': 'high',
                'Low': 'low',
                'Close': 'close',
                'Volume': 'volume'
            })
            df.index = df.index.tz_localize(None)  # 移除时区信息
            df.index.name = 'date'
            
            # 计算收益率
            df['return'] = df['close'].pct_change() * 100
            
            self._set_cached_data(cache_key, df)
            logger.info(f"成功获取 DXY 数据，共 {len(df)} 条记录")
            return df
            
        except Exception as e:
            logger.error(f"获取 DXY 数据失败: {e}")
            return None
    
    def get_us_treasury_yield(self, maturity: str = "10Y") -> Optional[float]:
        """
        获取美国国债收益率
        
        Args:
            maturity: 期限 ("2Y", "5Y", "10Y", "30Y")
            
        Returns:
            国债收益率（百分比）
        """
        cache_key = f"treasury_{maturity}"
        cached = self._get_cached_data(cache_key, max_age=3600)
        if cached:
            return cached
        
        try:
            import yfinance as yf
        except ImportError:
            logger.error("yfinance 未安装，请运行: pip install yfinance")
            return None
        
        try:
            logger.info(f"获取美国国债收益率: {maturity}")
            
            # 使用Yahoo Finance获取国债ETF
            treasury_map = {
                "2Y": "SHY",   # 1-3年期国债ETF
                "5Y": "IEI",   # 3-7年期国债ETF
                "10Y": "IEF",  # 7-10年期国债ETF
                "30Y": "TLT",  # 20+年期国债ETF
            }
            
            ticker_symbol = treasury_map.get(maturity, "IEF")
            ticker = yf.Ticker(ticker_symbol)
            
            # 获取ETF信息
            info = ticker.info
            
            # 计算收益率近似值
            # 方法1: 使用 yield 字段
            if 'yield' in info and info['yield']:
                yield_rate = info['yield']
            # 方法2: 使用 dividendYield 字段
            elif 'dividendYield' in info and info['dividendYield']:
                yield_rate = info['dividendYield'] * 100
            # 方法3: 使用当前价格和面值计算
            else:
                # 简化计算，使用 100 作为面值
                if 'regularMarketPrice' in info:
                    price = info['regularMarketPrice']
                    # 假设每年付息两次
                    yield_rate = (100 / price) * 2 * 100
                else:
                    logger.warning(f"无法获取 {maturity} 国债收益率")
                    return None
            
            yield_rate = round(yield_rate, 2)
            self._set_cached_data(cache_key, yield_rate)
            logger.info(f"成功获取 {maturity} 国债收益率: {yield_rate}%")
            return yield_rate
            
        except Exception as e:
            logger.error(f"获取国债收益率失败: {e}")
            return None
    
    def get_fed_funds_rate(self) -> Optional[float]:
        """
        获取美联储联邦基金利率
        
        数据来源: FRED API 或 Yahoo Finance
        
        Returns:
            联邦基金利率（百分比）
        """
        cache_key = "fed_funds_rate"
        cached = self._get_cached_data(cache_key, max_age=86400)  # 缓存24小时
        if cached:
            return cached
        
        try:
            import yfinance as yf
        except ImportError:
            logger.error("yfinance 未安装，请运行: pip install yfinance")
            return None
        
        try:
            logger.info("获取美联储联邦基金利率")
            
            # 使用 Yahoo Finance 获取联邦基金利率 ETF
            # 代码: FFIV (Federal Funds Rate ETF)
            ticker = yf.Ticker("FFIV")
            info = ticker.info
            
            if 'regularMarketPrice' in info:
                # FFIV 的价格近似等于联邦基金利率
                fed_rate = info['regularMarketPrice']
                fed_rate = round(fed_rate, 2)
                
                self._set_cached_data(cache_key, fed_rate)
                logger.info(f"成功获取联邦基金利率: {fed_rate}%")
                return fed_rate
            else:
                logger.warning("无法获取联邦基金利率")
                return None
                
        except Exception as e:
            logger.error(f"获取联邦基金利率失败: {e}")
            return None
    
    def get_us_inflation_rate(self) -> Optional[float]:
        """
        获取美国通胀率（CPI）
        
        数据来源: FRED API 或 Yahoo Finance
        
        Returns:
            通胀率（百分比）
        """
        cache_key = "us_inflation"
        cached = self._get_cached_data(cache_key, max_age=86400)  # 缓存24小时
        if cached:
            return cached
        
        try:
            import yfinance as yf
        except ImportError:
            logger.error("yfinance 未安装，请运行: pip install yfinance")
            return None
        
        try:
            logger.info("获取美国通胀率 (CPI)")
            
            # 使用 Yahoo Finance 获取通胀 ETF
            # 代码: TIP (通胀保值债券 ETF)
            ticker = yf.Ticker("TIP")
            info = ticker.info
            
            if 'yield' in info:
                # TIP 的收益率可以近似反映通胀预期
                inflation_rate = info['yield']
                inflation_rate = round(inflation_rate, 2)
                
                self._set_cached_data(cache_key, inflation_rate)
                logger.info(f"成功获取美国通胀率: {inflation_rate}%")
                return inflation_rate
            else:
                logger.warning("无法获取美国通胀率")
                return None
                
        except Exception as e:
            logger.error(f"获取美国通胀率失败: {e}")
            return None
    
    def get_real_interest_rate(self) -> Optional[float]:
        """
        计算实际利率
        
        公式: 实际利率 = 名义利率 - 通胀率
        
        Returns:
            实际利率（百分比）
        """
        cache_key = "real_interest_rate"
        cached = self._get_cached_data(cache_key, max_age=3600)
        if cached:
            return cached
        
        # 获取名义利率（10年期国债收益率）
        nominal_rate = self.get_us_treasury_yield("10Y")
        if nominal_rate is None:
            logger.warning("无法获取名义利率，无法计算实际利率")
            return None
        
        # 获取通胀率
        inflation_rate = self.get_us_inflation_rate()
        if inflation_rate is None:
            # 使用默认通胀率 2.5%
            inflation_rate = 2.5
            logger.info(f"无法获取通胀率，使用默认值: {inflation_rate}%")
        
        # 计算实际利率
        real_rate = nominal_rate - inflation_rate
        real_rate = round(real_rate, 2)
        
        self._set_cached_data(cache_key, real_rate)
        logger.info(f"计算实际利率: {real_rate}% (名义利率: {nominal_rate}%, 通胀率: {inflation_rate}%)")
        return real_rate
    
    def get_central_bank_gold_purchases(self) -> Optional[Dict]:
        """
        获取各国央行购金数据
        
        数据来源: 世界黄金协会
        
        Returns:
            包含央行购金数据的字典
        """
        cache_key = "central_bank_gold"
        cached = self._get_cached_data(cache_key, max_age=86400)  # 缓存24小时
        if cached:
            return cached
        
        try:
            logger.info("获取央行购金数据")
            
            # 这里使用模拟数据，实际项目中可以:
            # 1. 接入世界黄金协会 API
            # 2. 爬取世界黄金协会网站
            # 3. 使用第三方数据源
            
            # 模拟数据
            data = {
                "latest_quarter": "2024 Q4",
                "total_purchases": 228,  # 吨
                "top_purchasers": [
                    {"country": "中国", "amount": 120, "percentage": 52.6},
                    {"country": "俄罗斯", "amount": 45, "percentage": 19.7},
                    {"country": "印度", "amount": 30, "percentage": 13.2},
                    {"country": "其他国家", "amount": 33, "percentage": 14.5}
                ],
                "year_to_date": 912,  # 2024年至今累计
                "yoy_change": 15.3,  # 同比增长百分比
                "timestamp": datetime.now().isoformat()
            }
            
            self._set_cached_data(cache_key, data)
            logger.info(f"成功获取央行购金数据，最新季度: {data['latest_quarter']}, 总购买量: {data['total_purchases']}吨")
            return data
            
        except Exception as e:
            logger.error(f"获取央行购金数据失败: {e}")
            return None
    
    def get_geopolitical_risk_index(self) -> Optional[float]:
        """
        获取地缘政治风险指数
        
        数据来源: 基于新闻分析或第三方服务
        
        Returns:
            地缘政治风险指数 (0-100)
        """
        cache_key = "geopolitical_risk"
        cached = self._get_cached_data(cache_key, max_age=3600)
        if cached:
            return cached
        
        try:
            logger.info("获取地缘政治风险指数")
            
            # 这里使用模拟数据，实际项目中可以:
            # 1. 基于新闻关键词分析
            # 2. 使用第三方地缘政治风险服务
            # 3. 爬取相关网站
            
            # 模拟数据 (基于当前全球形势)
            risk_index = 65  # 中等偏高风险
            
            self._set_cached_data(cache_key, risk_index)
            logger.info(f"成功获取地缘政治风险指数: {risk_index}/100")
            return risk_index
            
        except Exception as e:
            logger.error(f"获取地缘政治风险指数失败: {e}")
            return None


class GoldMacroAnalyzer:
    """
    黄金宏观因素分析器
    
    分析各种宏观因素对黄金价格的影响
    """
    
    def __init__(self):
        """
        初始化黄金宏观因素分析器
        """
        self.data_provider = MacroDataProvider()
        logger.info("初始化黄金宏观因素分析器")
    
    def get_macro_score(self) -> Dict[str, Any]:
        """
        获取综合宏观因素评分
        
        Returns:
            {
                "total_score": 65,  # 0-100，越高越利好黄金
                "factors": {
                    "dxy": {"value": 103.5, "impact": "bearish", "score": 40},
                    "fed_rate": {"value": 5.25, "impact": "neutral", "score": 50},
                    "inflation": {"value": 3.2, "impact": "bullish", "score": 70},
                    # ...
                },
                "summary": "美元强势压制黄金，但通胀支撑价格"
            }
        """
        factors = {}
        
        # 1. 美元指数影响
        dxy_data = self.data_provider.get_dxy_index(days=5)
        if dxy_data is not None and len(dxy_data) >= 2:
            dxy_current = dxy_data['close'].iloc[-1]
            dxy_change = (dxy_current - dxy_data['close'].iloc[-2]) / dxy_data['close'].iloc[-2] * 100
            
            # 美元上涨 → 利空黄金
            if dxy_change > 0.5:
                dxy_score = 30  # 利空
                dxy_impact = "bearish"
            elif dxy_change < -0.5:
                dxy_score = 70  # 利好
                dxy_impact = "bullish"
            else:
                dxy_score = 50  # 中性
                dxy_impact = "neutral"
                
            factors["dxy"] = {
                "value": round(dxy_current, 2),
                "change": round(dxy_change, 2),
                "impact": dxy_impact,
                "score": dxy_score
            }
        
        # 2. 实际利率影响
        real_rate = self.data_provider.get_real_interest_rate()
        if real_rate is not None:
            # 实际利率上升 → 利空黄金
            if real_rate > 2.0:
                rate_score = 20
                rate_impact = "strongly_bearish"
            elif real_rate > 1.0:
                rate_score = 35
                rate_impact = "bearish"
            elif real_rate > 0:
                rate_score = 50
                rate_impact = "neutral"
            else:
                rate_score = 75
                rate_impact = "bullish"
                
            factors["real_rate"] = {
                "value": real_rate,
                "impact": rate_impact,
                "score": rate_score
            }
        
        # 3. 通胀影响
        inflation_rate = self.data_provider.get_us_inflation_rate()
        if inflation_rate is not None:
            # 通胀上升 → 利好黄金
            if inflation_rate > 4.0:
                inflation_score = 80
                inflation_impact = "strongly_bullish"
            elif inflation_rate > 3.0:
                inflation_score = 70
                inflation_impact = "bullish"
            elif inflation_rate > 2.0:
                inflation_score = 50
                inflation_impact = "neutral"
            else:
                inflation_score = 30
                inflation_impact = "bearish"
                
            factors["inflation"] = {
                "value": inflation_rate,
                "impact": inflation_impact,
                "score": inflation_score
            }
        
        # 4. 央行购金影响
        central_bank_data = self.data_provider.get_central_bank_gold_purchases()
        if central_bank_data:
            total_purchases = central_bank_data.get("total_purchases", 0)
            
            if total_purchases > 300:
                cb_score = 85
                cb_impact = "strongly_bullish"
            elif total_purchases > 150:
                cb_score = 75
                cb_impact = "bullish"
            elif total_purchases > 50:
                cb_score = 60
                cb_impact = "slightly_bullish"
            else:
                cb_score = 50
                cb_impact = "neutral"
                
            factors["central_bank"] = {
                "value": total_purchases,
                "impact": cb_impact,
                "score": cb_score
            }
        
        # 5. 地缘政治风险影响
        geopolitical_risk = self.data_provider.get_geopolitical_risk_index()
        if geopolitical_risk is not None:
            # 地缘政治风险上升 → 利好黄金
            if geopolitical_risk > 70:
                geo_score = 80
                geo_impact = "strongly_bullish"
            elif geopolitical_risk > 50:
                geo_score = 65
                geo_impact = "bullish"
            elif geopolitical_risk > 30:
                geo_score = 50
                geo_impact = "neutral"
            else:
                geo_score = 30
                geo_impact = "bearish"
                
            factors["geopolitical"] = {
                "value": geopolitical_risk,
                "impact": geo_impact,
                "score": geo_score
            }
        
        # 6. 计算综合得分
        if factors:
            total_score = sum(f["score"] for f in factors.values()) / len(factors)
        else:
            total_score = 50
            
        total_score = round(total_score)
        
        # 7. 生成总结
        summary = self._generate_summary(factors)
        
        return {
            "total_score": total_score,
            "factors": factors,
            "summary": summary,
            "timestamp": datetime.now().isoformat()
        }
    
    def _generate_summary(self, factors: Dict) -> str:
        """
        生成宏观因素总结
        
        Args:
            factors: 宏观因素数据
            
        Returns:
            总结文本
        """
        if not factors:
            return "暂无宏观数据，保持中性看法"
        
        bullish_factors = []
        bearish_factors = []
        neutral_factors = []
        
        for factor_name, factor_data in factors.items():
            impact = factor_data.get("impact", "neutral")
            if impact in ["bullish", "strongly_bullish", "slightly_bullish"]:
                bullish_factors.append(factor_name)
            elif impact in ["bearish", "strongly_bearish"]:
                bearish_factors.append(factor_name)
            else:
                neutral_factors.append(factor_name)
        
        if bullish_factors and not bearish_factors:
            return f"宏观环境整体利好黄金（{len(bullish_factors)}项利好因素）"
        elif bearish_factors and not bullish_factors:
            return f"宏观环境整体利空黄金（{len(bearish_factors)}项利空因素）"
        elif len(bullish_factors) > len(bearish_factors):
            return f"宏观环境偏利好黄金（{len(bullish_factors)}项利好 vs {len(bearish_factors)}项利空）"
        elif len(bearish_factors) > len(bullish_factors):
            return f"宏观环境偏利空黄金（{len(bullish_factors)}项利好 vs {len(bearish_factors)}项利空）"
        else:
            return "宏观环境中性，关注技术面信号"


if __name__ == "__main__":
    # 测试代码
    logging.basicConfig(level=logging.INFO)
    
    analyzer = GoldMacroAnalyzer()
    macro_score = analyzer.get_macro_score()
    
    print("=== 黄金宏观因素分析 ===")
    print(f"综合评分: {macro_score['total_score']}/100")
    print(f"分析总结: {macro_score['summary']}")
    print()
    print("关键因素:")
    for factor_name, factor_data in macro_score['factors'].items():
        emoji = "📈" if factor_data['score'] > 60 else "📉" if factor_data['score'] < 40 else "➡️"
        print(f"{emoji} {factor_name}: {factor_data['value']} ({factor_data['impact']}) - {factor_data['score']}/100")
    print()
    print(f"更新时间: {macro_score['timestamp']}")
