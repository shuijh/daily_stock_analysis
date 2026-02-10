# GitHub Actions 黄金分析配置指南

本指南介绍如何在 GitHub Actions 中配置和运行黄金分析功能，使您的股票分析系统能够同时分析黄金相关资产。

## 📋 配置要求

### 1. 核心代码修改

系统已经内置了黄金分析功能，主要修改包括：

- **`src/gold_analyzer.py`** - 黄金趋势分析器，针对黄金特性优化
- **`src/macro_data_provider.py`** - 宏观数据获取模块，获取美元指数、利率等宏观数据
- **`src/ai_macro_analyzer.py`** - AI驱动的宏观分析模块，使用大语言模型分析宏观影响
- **`src/search_service.py`** - 搜索服务，支持黄金宏观因素新闻搜索
- **`src/core/pipeline.py`** - 分析流水线，支持自动识别黄金相关资产

### 2. GitHub Actions 配置

在 GitHub 仓库的 **Settings > Secrets and variables > Actions** 中配置以下参数：

#### 基础配置

| 配置项 | 类型 | 说明 | 示例值 |
|-------|------|------|--------|
| **STOCK_LIST** | 变量/密钥 | 自选股列表，包含黄金相关代码 | `600519,Au9999,GC=F,GLD` |

#### AI 模型配置（二选一）

| 配置项 | 类型 | 说明 | 必填 |
|-------|------|------|------|
| **GEMINI_API_KEY** | 密钥 | [Google AI Studio](https://aistudio.google.com/app/apikey) 获取免费 Key | ✅ 推荐 |
| **OPENAI_API_KEY** | 密钥 | OpenAI 兼容 API Key（支持 DeepSeek、通义千问等） | 可选 |
| **OPENAI_BASE_URL** | 密钥 | OpenAI 兼容 API 地址（如 `https://api.deepseek.com/v1`） | 可选 |
| **OPENAI_MODEL** | 变量 | 模型名称（如 `deepseek-chat`） | 可选 |

> **注：** `GEMINI_API_KEY` 和 `OPENAI_API_KEY` 至少配置一个

#### 新闻搜索配置

| 配置项 | 类型 | 说明 | 示例值 |
|-------|------|------|--------|
| **TAVILY_API_KEYS** | 密钥 | Tavily 搜索 API（用于新闻搜索） | - |
| **BOCHA_API_KEYS** | 密钥 | 博查搜索 API（用于中文搜索） | - |

#### 技术栈与数据来源

| 类型 | 支持 |
|------|------|
| **AI 模型** | Gemini（免费）、OpenAI 兼容、DeepSeek、通义千问、Claude、Ollama |
| **行情数据** | AkShare、Tushare、Pytdx、Baostock、YFinance |
| **新闻搜索** | Tavily、SerpAPI、Bocha |

## 🚀 配置步骤

### 步骤 1：修改 GitHub Actions 工作流文件

编辑 `.github/workflows/daily_analysis.yml` 文件，确保以下配置正确：

```yaml
# ==========================================
# 自选股配置
# ==========================================
STOCK_LIST: ${{ vars.STOCK_LIST || secrets.STOCK_LIST || '600519,Au9999,GC=F' }}
```

### 步骤 2：在 GitHub 仓库中添加配置

1. 进入 GitHub 仓库页面
2. 点击 **Settings** > **Secrets and variables** > **Actions**
3. 点击 **New repository variable** 或 **New repository secret**
4. 添加 `STOCK_LIST` 变量，包含您的自选股和黄金代码

### 步骤 3：推送代码到 GitHub

```bash
# 检查状态
git status

# 添加新文件
git add src/gold_analyzer.py src/macro_data_provider.py src/ai_macro_analyzer.py src/core/pipeline.py .github/workflows/daily_analysis.yml

# 提交更改
git commit -m "添加黄金分析功能（含技术分析、宏观数据、AI分析）"

# 推送至 GitHub
git push origin main
```

## 💡 黄金代码说明

系统支持以下黄金相关代码：

| 代码 | 名称 | 类型 | 说明 |
|------|------|------|------|
| **Au9999** | 黄金现货 | 国内黄金 | 上海黄金交易所黄金现货合约 |
| **GC=F** | 黄金期货 | 国际黄金 | COMEX 黄金期货主力合约 |
| **GLD** | SPDR Gold Shares | 黄金ETF | 全球最大的黄金ETF |
| **GOLD** | Barrick Gold | 金矿股 | 全球最大的金矿公司之一 |
| **NEM** | Newmont Corporation | 金矿股 | 全球领先的金矿公司 |

## 🔧 技术实现细节

### 分析器自动选择机制

系统会根据代码自动选择合适的分析器：

```python
# 根据代码选择合适的分析器
if code in ['Au9999', 'GC=F', 'GLD'] or 'gold' in code.lower():
    # 使用黄金分析器
    trend_result = self.gold_trend_analyzer.analyze(df, code)
else:
    # 使用股票分析器
    trend_result = self.stock_trend_analyzer.analyze(df, code)
```

### 黄金分析器优化参数

黄金分析器针对黄金特性进行了以下优化：

| 参数 | 股票默认值 | 黄金优化值 | 说明 |
|------|-----------|-----------|------|
| **乖离率阈值** | 5.0% | 3.0% | 黄金价格波动相对较小 |
| **放量判断阈值** | 1.5 | 1.8 | 黄金交易量特性不同 |
| **缩量判断阈值** | 0.7 | 0.7 | 保持不变 |

## 📊 分析结果示例

### 黄金现货 (Au9999) 分析结果

```
=== Au9999 黄金趋势分析 ===

📊 趋势判断: 弱势空头
   均线排列: 弱势空头，MA5<MA10 但 MA10≥MA20
   趋势强度: 40/100

📈 均线数据:
   现价: 1083.40
   MA5:  1091.41 (乖离 -0.73%)
   MA10: 1133.76 (乖离 -4.44%)
   MA20: 1093.76 (乖离 -0.95%)

📊 量能分析: 缩量回调
   量比(vs5日): 0.26
   量能趋势: 缩量回调，洗盘特征明显（黄金，好）

📈 MACD指标: 多头
   DIF: 28.5346
   DEA: 35.4737
   MACD: -13.8781
   信号: ✓ 多头排列，持续上涨

📊 RSI指标: 中性
   RSI(6): 29.0
   RSI(12): 49.6
   RSI(24): 56.8
   信号:  RSI中性(49.6)，震荡整理中

🎯 操作建议: 持有
   综合评分: 56/100

✅ 买入理由:
   ✅ 价格略低于MA5(-0.7%)，回踩买点
   ✅ 缩量回调，主力洗盘
   ✓ 多头排列，持续上涨
    RSI中性(49.6)，震荡整理中

💡 黄金市场提示:
   - 黄金作为避险资产，在市场不确定性增加时往往表现强势
   - 黄金价格受全球宏观经济、地缘政治等因素影响较大
   - 黄金趋势一旦形成，往往持续时间较长
```

### 黄金期货 (GC=F) 分析结果

```
=== GC=F 黄金趋势分析 ===

📊 趋势判断: 弱势空头
   均线排列: 弱势空头，MA5<MA10 但 MA10≥MA20
   趋势强度: 40/100

📈 均线数据:
   现价: 4878.70
   MA5:  4887.44 (乖离 -0.18%)
   MA10: 4978.34 (乖离 -2.00%)
   MA20: 4789.43 (乖离 +1.86%)

📊 量能分析: 量能正常
   量比(vs5日): 1.77
   量能趋势: 量能正常（黄金）

📈 MACD指标: 多头
   DIF: 135.1039
   DEA: 157.1273
   MACD: -44.0469
   信号: ✓ 多头排列，持续上涨

📊 RSI指标: 中性
   RSI(6): 41.9
   RSI(12): 58.4
   RSI(24): 61.4
   信号:  RSI中性(58.4)，震荡整理中

🎯 操作建议: 持有
   综合评分: 51/100

✅ 买入理由:
   ✅ 价格略低于MA5(-0.2%)，回踩买点
   ✓ 多头排列，持续上涨

💡 黄金市场提示:
   - 黄金作为避险资产，在市场不确定性增加时往往表现强势
   - 黄金价格受全球宏观经济、地缘政治等因素影响较大
   - 黄金趋势一旦形成，往往持续时间较长
```

## 🚀 运行流程

当 GitHub Actions 执行时：

1. **代码获取** - 从 GitHub 仓库获取最新代码
2. **环境设置** - 配置 Python 环境和依赖项
3. **数据获取** - 获取 `STOCK_LIST` 中所有资产的数据
4. **资产识别** - 自动识别黄金相关资产和股票
5. **分析执行** - 对不同类型资产使用相应的分析器
   - 黄金资产：技术分析 + 宏观数据分析 + AI综合分析
   - 股票资产：技术分析
6. **报告生成** - 生成包含所有资产的综合分析报告
7. **结果推送** - 推送到配置的通知渠道

## 🌍 宏观因素分析

系统通过三阶段改进计划，实现了全面的黄金宏观因素分析：

### Phase 1: 新闻宏观因素搜索

系统通过搜索服务获取最新的黄金宏观因素新闻：

- **美联储政策** - 利率决策、货币政策声明
- **美元指数** - DXY走势对黄金的影响
- **通胀数据** - CPI、PPI等通胀指标
- **地缘政治** - 国际局势、避险情绪
- **央行购金** - 各国央行黄金储备变化

### Phase 2: 结构化宏观数据分析

系统自动获取并分析以下宏观数据：

| 数据类型 | 数据源 | 更新频率 | 影响方向 |
|---------|--------|---------|---------|
| **美元指数(DXY)** | Yahoo Finance | 1小时缓存 | 负相关 |
| **实际利率** | FRED API | 24小时缓存 | 负相关 |
| **通胀预期** | FRED API | 24小时缓存 | 正相关 |
| **VIX波动率** | Yahoo Finance | 1小时缓存 | 正相关 |
| **央行购金** | World Gold Council | 月度 | 正相关 |
| **地缘政治风险** | 新闻分析 | 实时 | 正相关 |

**宏观评分计算**：
- 各因素评分范围：0-100分
- 综合宏观评分 = 各因素评分的加权平均
- 技术评分权重 60%，宏观评分权重 40%

### Phase 3: AI驱动的宏观分析

系统使用大语言模型（Gemini/OpenAI）进行智能分析：

**AI分析流程**：
1. 整合技术分析结果
2. 整合结构化宏观数据
3. 整合宏观新闻信息
4. 生成综合分析报告

**AI分析输出**：
- 当前宏观环境对黄金的整体影响
- 关键驱动因素分析（2-3个最重要因素）
- 短期（1-2周）价格走势预判
- 投资建议（仓位、入场时机、止损策略）
- 风险提示

### 宏观分析结果示例

```
=== 黄金宏观因素分析 ===

📊 综合宏观评分: 65/100 (偏多)

📈 关键宏观因素:
   美元指数: 103.5 (+0.2%) → 利空黄金 (评分: 40)
   实际利率: 1.8% → 中性 (评分: 50)
   通胀预期: 3.2% → 利好黄金 (评分: 70)
   VIX指数: 18.5 → 中性 (评分: 55)
   央行购金: 2024年Q1增加290吨 → 利好黄金 (评分: 80)
   地缘风险: 中东局势紧张 → 利好黄金 (评分: 75)

🤖 AI宏观分析:
   当前宏观环境整体偏多黄金。虽然美元指数保持强势对黄金构成
   一定压力，但通胀数据支撑和地缘政治风险上升为黄金提供了
   有力支撑。各国央行持续增持黄金储备，显示长期看好黄金。
   
   短期预判: 黄金可能在当前区间震荡整理，等待美联储政策明朗化
   
   投资建议: 维持适度仓位，可在回调至关键支撑位时加仓
   
   风险提示: 需关注美联储利率决议和美元指数走势

💡 宏观因素总结: 通胀支撑 + 地缘避险 - 美元压制 = 中性偏多
```

## 🔧 高级配置

### 1. 调整分析参数

可以在 `src/gold_analyzer.py` 中调整黄金分析的参数：

```python
# 黄金特有的交易参数配置
BIAS_THRESHOLD = 3.0        # 乖离率阈值（%）
VOLUME_SHRINK_RATIO = 0.7   # 缩量判断阈值
VOLUME_HEAVY_RATIO = 1.8    # 放量判断阈值
```

### 2. 调整宏观数据权重

可以在 `src/gold_analyzer.py` 中调整宏观因素权重：

```python
# 在 analyze_with_macro 方法中
# 新闻评分权重 30%，结构化数据评分权重 70%
total_macro_score = int(macro_news_score * 0.3 + macro_data_score * 0.7)

# 技术评分权重 60%，宏观评分权重 40%
result.signal_score = int(result.signal_score * 0.6 + total_macro_score * 0.4)
```

### 3. 配置AI分析模型

可以在 `src/ai_macro_analyzer.py` 中选择不同的AI模型：

#### 方案一：使用 Gemini（推荐，免费）

```python
from src.ai_macro_analyzer import GeminiAnalyzer, AIGoldMacroAnalyzer

# 从环境变量读取 API Key
import os
api_key = os.getenv('GEMINI_API_KEY')

analyzer = GeminiAnalyzer(api_key=api_key)
ai_gold_analyzer = AIGoldMacroAnalyzer(analyzer)
```

**GitHub Actions 配置：**
- 添加 Secret: `GEMINI_API_KEY` = 你的 Gemini API Key
- 获取地址: [Google AI Studio](https://aistudio.google.com/app/apikey)

#### 方案二：使用 OpenAI 兼容模型

```python
from src.ai_macro_analyzer import OpenAIAnalyzer, AIGoldMacroAnalyzer

import os
api_key = os.getenv('OPENAI_API_KEY')
base_url = os.getenv('OPENAI_BASE_URL')  # 可选，用于兼容其他服务商
model = os.getenv('OPENAI_MODEL', 'gpt-3.5-turbo')  # 可选，默认模型

analyzer = OpenAIAnalyzer(
    api_key=api_key,
    base_url=base_url,
    model=model
)
ai_gold_analyzer = AIGoldMacroAnalyzer(analyzer)
```

**GitHub Actions 配置：**

| 服务商 | OPENAI_API_KEY | OPENAI_BASE_URL | OPENAI_MODEL |
|--------|---------------|-----------------|--------------|
| **OpenAI** | sk-... | 不设置 | gpt-3.5-turbo / gpt-4 |
| **DeepSeek** | sk-... | `https://api.deepseek.com/v1` | deepseek-chat |
| **通义千问** | sk-... | `https://dashscope.aliyuncs.com/compatible-mode/v1` | qwen-turbo |
| **其他** | 对应Key | 服务商提供的base_url | 对应模型名 |

#### 方案三：使用其他AI模型（需扩展）

系统支持通过扩展 `BaseAIAnalyzer` 类来集成其他AI模型：

```python
from src.ai_macro_analyzer import BaseAIAnalyzer

class ClaudeAnalyzer(BaseAIAnalyzer):
    def __init__(self, api_key):
        super().__init__()
        self.api_key = api_key
        # 初始化 Claude 客户端
    
    def generate_response(self, prompt: str) -> str:
        # 调用 Claude API
        pass

# 使用
analyzer = ClaudeAnalyzer(api_key="your-claude-api-key")
ai_gold_analyzer = AIGoldMacroAnalyzer(analyzer)
```

### 4. 配置宏观数据缓存

可以在 `src/macro_data_provider.py` 中调整缓存时间：

```python
# 获取美元指数（缓存1小时）
dxy_data = self._get_cached_data(cache_key, max_age=3600)

# 获取通胀数据（缓存24小时）
inflation_data = self._get_cached_data(cache_key, max_age=86400)
```

### 5. 添加更多黄金相关资产

在 `src/core/pipeline.py` 中可以添加更多黄金相关资产的识别：

```python
if code in ['Au9999', 'GC=F', 'GLD', 'GOLD', 'NEM'] or 'gold' in code.lower():
    # 使用黄金分析器
    trend_result = self.gold_trend_analyzer.analyze(df, code)
```

### 6. 配置通知渠道

可以在 GitHub Actions 中配置多种通知渠道：

- **企业微信** - `WECHAT_WEBHOOK_URL`
- **飞书** - `FEISHU_WEBHOOK_URL`
- **Telegram** - `TELEGRAM_BOT_TOKEN` 和 `TELEGRAM_CHAT_ID`
- **Discord** - `DISCORD_WEBHOOK_URL`

## 📁 目录结构

```
daily_stock_analysis/
├── .github/
│   └── workflows/
│       └── daily_analysis.yml    # GitHub Actions 工作流
├── src/
│   ├── gold_analyzer.py          # 黄金趋势分析器（含宏观分析集成）
│   ├── macro_data_provider.py    # 宏观数据获取模块
│   ├── ai_macro_analyzer.py      # AI驱动的宏观分析模块
│   ├── search_service.py         # 搜索服务（支持黄金宏观新闻）
│   └── core/
│       └── pipeline.py           # 分析流水线
├── docs/
│   └── GitHub Actions 黄金分析配置指南.md  # 本指南
└── requirements.txt              # 依赖项
```

## 💡 常见问题

### Q: 为什么黄金分析结果与股票分析结果格式不同？

**A:** 黄金分析器针对黄金特性进行了优化，包括：
- 调整了乖离率阈值（从 5% 改为 3%）
- 调整了量能判断阈值（从 1.5 改为 1.8）
- 添加了黄金特有的市场提示
- 集成了宏观因素分析（美元指数、利率、通胀等）
- 集成了AI驱动的智能分析

### Q: 宏观数据是如何获取和更新的？

**A:** 系统通过以下方式获取宏观数据：
- **实时数据**（Yahoo Finance）：美元指数、VIX、国债收益率，缓存1小时
- **每日数据**（FRED API）：实际利率、通胀预期，缓存24小时
- **新闻数据**（搜索服务）：宏观新闻，实时获取
- **月度数据**（World Gold Council）：央行购金数据，缓存30天

系统会自动管理缓存，确保数据新鲜度同时避免频繁API调用。

### Q: AI分析需要额外配置吗？

**A:** AI分析是可选功能，需要配置以下API Key之一：
- **Gemini API Key** - 推荐，响应速度快，免费额度充足
- **OpenAI API Key** - 备选，分析质量高但成本较高

如果没有配置AI API Key，系统仍会进行技术分析和宏观数据分析，只是不会生成AI综合分析报告。

### Q: 如何添加新的黄金相关资产？

**A:** 在 `src/core/pipeline.py` 中修改资产识别逻辑，添加新的黄金相关代码。

### Q: GitHub Actions 运行失败怎么办？

**A:** 检查以下几点：
- 确保所有必要的 API Key 已正确配置
- 确保 `STOCK_LIST` 格式正确，无多余空格
- 查看 GitHub Actions 日志，了解具体错误信息
- 检查宏观数据API是否可用（FRED、Yahoo Finance等）
- 如果使用AI分析，确保AI API Key有效且有足够额度

## 🎯 总结

通过本指南的配置，您的股票分析系统将能够：

- ✅ 自动识别和分析黄金相关资产
- ✅ 为黄金资产提供专业的技术分析
- ✅ 获取和分析宏观因素数据（美元指数、利率、通胀等）
- ✅ 搜索和分析宏观新闻
- ✅ 使用AI生成智能分析报告
- ✅ 在 GitHub Actions 中定期执行黄金分析
- ✅ 生成包含黄金和股票的综合分析报告

**三阶段改进计划已完成**：
1. ✅ Phase 1: 扩展搜索服务，添加黄金宏观因素搜索
2. ✅ Phase 2: 创建宏观数据获取模块，集成宏观分析
3. ✅ Phase 3: 创建AI驱动的宏观分析模块，集成到分析流水线

祝您投资顺利！
