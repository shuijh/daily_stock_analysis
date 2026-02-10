# -*- coding: utf-8 -*-
"""
===================================
AI驱动的黄金宏观分析模块
===================================

职责：
1. 利用大语言模型分析宏观因素对黄金的影响
2. 整合技术分析、宏观数据和新闻信息
3. 生成智能化的黄金投资分析报告
4. 提供短期价格走势预判和投资建议

支持的AI模型：
- Gemini API
- OpenAI API
- 本地大语言模型
"""

import logging
import json
from typing import Optional, Dict, Any, List
from datetime import datetime

logger = logging.getLogger(__name__)


class BaseAIAnalyzer:
    """
    AI分析器基类
    """
    
    def __init__(self):
        """
        初始化AI分析器
        """
        logger.info("初始化AI分析器")
    
    def generate_response(self, prompt: str) -> str:
        """
        生成AI响应
        
        Args:
            prompt: 提示词
            
        Returns:
            AI生成的响应
        """
        raise NotImplementedError("子类必须实现generate_response方法")


class GeminiAnalyzer(BaseAIAnalyzer):
    """
    Gemini AI分析器
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        初始化Gemini分析器
        
        Args:
            api_key: Gemini API Key
        """
        super().__init__()
        self.api_key = api_key
        self.client = None
        
        if api_key:
            self._initialize_client()
    
    def _initialize_client(self):
        """
        初始化Gemini客户端
        """
        try:
            import google.generativeai as genai
            genai.configure(api_key=self.api_key)
            self.client = genai.GenerativeModel('gemini-1.5-flash')
            logger.info("Gemini客户端初始化成功")
        except ImportError:
            logger.error("google-generativeai 未安装，请运行: pip install google-generativeai")
        except Exception as e:
            logger.error(f"Gemini客户端初始化失败: {e}")
    
    def generate_response(self, prompt: str) -> str:
        """
        使用Gemini生成响应
        
        Args:
            prompt: 提示词
            
        Returns:
            AI生成的响应
        """
        if not self.client:
            logger.warning("Gemini客户端未初始化，返回默认响应")
            return "AI分析暂时不可用，请检查API配置"
        
        try:
            logger.info("使用Gemini生成分析响应")
            response = self.client.generate_content(prompt)
            return response.text
        except Exception as e:
            logger.error(f"Gemini生成响应失败: {e}")
            return f"AI分析失败: {str(e)}"


class OpenAIAnalyzer(BaseAIAnalyzer):
    """
    OpenAI AI分析器
    """
    
    def __init__(self, api_key: Optional[str] = None, model: str = "gpt-3.5-turbo"):
        """
        初始化OpenAI分析器
        
        Args:
            api_key: OpenAI API Key
            model: 使用的模型
        """
        super().__init__()
        self.api_key = api_key
        self.model = model
    
    def generate_response(self, prompt: str) -> str:
        """
        使用OpenAI生成响应
        
        Args:
            prompt: 提示词
            
        Returns:
            AI生成的响应
        """
        if not self.api_key:
            logger.warning("OpenAI API Key未配置，返回默认响应")
            return "AI分析暂时不可用，请检查API配置"
        
        try:
            import openai
            openai.api_key = self.api_key
            
            logger.info(f"使用OpenAI {self.model}生成分析响应")
            response = openai.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "你是一位专业的黄金投资分析师，擅长分析宏观经济因素对黄金价格的影响。"},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=1000
            )
            
            return response.choices[0].message.content
        except ImportError:
            logger.error("openai 未安装，请运行: pip install openai")
            return "AI分析暂时不可用，请安装openai库"
        except Exception as e:
            logger.error(f"OpenAI生成响应失败: {e}")
            return f"AI分析失败: {str(e)}"


class AIGoldMacroAnalyzer:
    """
    AI驱动的黄金宏观分析器
    """
    
    def __init__(self, analyzer: BaseAIAnalyzer):
        """
        初始化AI黄金宏观分析器
        
        Args:
            analyzer: AI分析器实例
        """
        self.analyzer = analyzer
        logger.info("初始化AI黄金宏观分析器")
    
    def analyze_macro_impact(
        self,
        technical_analysis: Dict[str, Any],
        macro_data: Dict[str, Any],
        macro_news: Dict[str, Any]
    ) -> str:
        """
        使用AI分析宏观因素对黄金的影响
        
        Args:
            technical_analysis: 技术分析结果
            macro_data: 宏观数据
            macro_news: 宏观新闻
            
        Returns:
            AI生成的宏观分析报告
        """
        # 构建提示词
        prompt = self._build_prompt(technical_analysis, macro_data, macro_news)
        
        # 生成AI响应
        return self.analyzer.generate_response(prompt)
    
    def _build_prompt(
        self,
        technical_analysis: Dict[str, Any],
        macro_data: Dict[str, Any],
        macro_news: Dict[str, Any]
    ) -> str:
        """
        构建AI分析提示词
        
        Args:
            technical_analysis: 技术分析结果
            macro_data: 宏观数据
            macro_news: 宏观新闻
            
        Returns:
            构建好的提示词
        """
        prompt_parts = []
        
        # 系统提示
        prompt_parts.append("""
你是一位专业的黄金投资分析师，擅长分析宏观经济因素对黄金价格的影响。
请基于以下数据，提供专业、客观的黄金投资分析：

""")
        
        # 技术分析数据
        if technical_analysis:
            prompt_parts.append("【技术分析数据】\n")
            prompt_parts.append(f"趋势判断: {technical_analysis.get('trend_status', 'N/A')}\n")
            prompt_parts.append(f"趋势强度: {technical_analysis.get('trend_strength', 'N/A')}/100\n")
            prompt_parts.append(f"均线排列: {technical_analysis.get('ma_alignment', 'N/A')}\n")
            prompt_parts.append(f"当前价格: {technical_analysis.get('current_price', 'N/A')}\n")
            prompt_parts.append(f"技术评分: {technical_analysis.get('signal_score', 'N/A')}/100\n")
            prompt_parts.append(f"操作建议: {technical_analysis.get('buy_signal', 'N/A')}\n")
            prompt_parts.append("\n")
        
        # 宏观数据
        if macro_data:
            prompt_parts.append("【宏观数据】\n")
            prompt_parts.append(f"宏观评分: {macro_data.get('total_score', 'N/A')}/100\n")
            prompt_parts.append(f"宏观总结: {macro_data.get('summary', 'N/A')}\n")
            
            factors = macro_data.get('factors', {})
            if factors:
                prompt_parts.append("关键宏观因素:\n")
                for factor_name, factor_data in factors.items():
                    value = factor_data.get('value', 'N/A')
                    impact = factor_data.get('impact', 'N/A')
                    score = factor_data.get('score', 'N/A')
                    prompt_parts.append(f"- {factor_name}: {value} ({impact}) - {score}/100\n")
            prompt_parts.append("\n")
        
        # 宏观新闻
        if macro_news:
            prompt_parts.append("【宏观新闻摘要】\n")
            news_count = 0
            for category, response in macro_news.items():
                if hasattr(response, 'results') and response.results:
                    for news in response.results[:1]:
                        if news_count >= 5:
                            break
                        prompt_parts.append(f"- {news.title}: {news.snippet[:100]}...\n")
                        news_count += 1
                    if news_count >= 5:
                        break
            prompt_parts.append("\n")
        
        # 分析要求
        prompt_parts.append("""
请提供以下分析：
1. 当前宏观环境对黄金的整体影响（利好/利空/中性）
2. 关键驱动因素分析（重点分析对黄金价格影响最大的2-3个因素）
3. 短期（1-2周）价格走势预判
4. 投资建议（仓位、入场时机、止损策略等）
5. 风险提示

要求：
- 使用中文回答
- 保持专业、客观的分析风格
- 基于提供的数据进行分析，不要编造信息
- 分析要具体，有数据支持
- 建议要实用，可操作性强
- 回答简洁明了，不要冗长
""")
        
        return "".join(prompt_parts)
    
    def generate_investment_report(
        self,
        technical_analysis: Dict[str, Any],
        macro_data: Dict[str, Any],
        macro_news: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        生成完整的投资分析报告
        
        Args:
            technical_analysis: 技术分析结果
            macro_data: 宏观数据
            macro_news: 宏观新闻
            
        Returns:
            包含分析报告的字典
        """
        try:
            logger.info("生成AI投资分析报告")
            
            # 获取AI分析
            ai_analysis = self.analyze_macro_impact(technical_analysis, macro_data, macro_news)
            
            # 构建报告
            report = {
                "technical": technical_analysis,
                "macro": macro_data,
                "ai_analysis": ai_analysis,
                "timestamp": datetime.now().isoformat(),
                "generated_by": "AI Gold Macro Analyzer"
            }
            
            logger.info("AI投资分析报告生成完成")
            return report
            
        except Exception as e:
            logger.error(f"生成投资报告失败: {e}")
            return {
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }


def get_ai_analyzer(api_provider: str = "gemini", api_key: Optional[str] = None) -> Optional[BaseAIAnalyzer]:
    """
    获取AI分析器实例
    
    Args:
        api_provider: API提供商 ("gemini" 或 "openai")
        api_key: API Key
        
    Returns:
        AI分析器实例
    """
    if api_provider == "gemini":
        return GeminiAnalyzer(api_key)
    elif api_provider == "openai":
        return OpenAIAnalyzer(api_key)
    else:
        logger.error(f"不支持的API提供商: {api_provider}")
        return None


if __name__ == "__main__":
    # 测试代码
    logging.basicConfig(level=logging.INFO)
    
    # 测试AI分析器
    # 注意：需要配置API Key
    # analyzer = GeminiAnalyzer(api_key="YOUR_API_KEY")
    # analyzer = OpenAIAnalyzer(api_key="YOUR_API_KEY")
    
    # 模拟数据
    technical_data = {
        "trend_status": "强势多头",
        "trend_strength": 85,
        "ma_alignment": "多头排列",
        "current_price": 2050.50,
        "signal_score": 80,
        "buy_signal": "买入"
    }
    
    macro_data = {
        "total_score": 75,
        "summary": "宏观环境整体利好黄金",
        "factors": {
            "dxy": {"value": 102.5, "change": -0.5, "impact": "bullish", "score": 70},
            "real_rate": {"value": -0.5, "impact": "bullish", "score": 80},
            "inflation": {"value": 3.5, "impact": "bullish", "score": 75},
            "central_bank": {"value": 228, "impact": "bullish", "score": 80},
            "geopolitical": {"value": 65, "impact": "bullish", "score": 70}
        }
    }
    
    # 模拟新闻数据
    class MockSearchResponse:
        def __init__(self, results):
            self.results = results
            self.success = True
    
    mock_news = {
        "美联储政策": MockSearchResponse([
            type('obj', (object,), {"title": "美联储暗示可能降息", "snippet": "美联储主席鲍威尔表示，如果通胀持续下降，可能会考虑降息"})
        ]),
        "地缘政治": MockSearchResponse([
            type('obj', (object,), {"title": "中东局势紧张", "snippet": "中东地区冲突加剧，市场避险情绪升温"})
        ])
    }
    
    # 测试分析
    # if analyzer:
    #     ai_macro_analyzer = AIGoldMacroAnalyzer(analyzer)
    #     report = ai_macro_analyzer.generate_investment_report(
    #         technical_data, macro_data, mock_news
    #     )
    #     print("=== AI黄金投资分析报告 ===")
    #     print(report["ai_analysis"])
    # else:
    #     print("请配置API Key后测试")
