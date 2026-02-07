# GitHub Actions 黄金分析配置指南

本指南介绍如何在 GitHub Actions 中配置和运行黄金分析功能，使您的股票分析系统能够同时分析黄金相关资产。

## 📋 配置要求

### 1. 核心代码修改

系统已经内置了黄金分析功能，主要修改包括：

- **`src/gold_analyzer.py`** - 黄金趋势分析器，针对黄金特性优化
- **`src/core/pipeline.py`** - 分析流水线，支持自动识别黄金相关资产

### 2. GitHub Actions 配置

在 GitHub 仓库的 **Settings > Secrets and variables > Actions** 中配置以下参数：

| 配置项 | 类型 | 说明 | 示例值 |
|-------|------|------|--------|
| **STOCK_LIST** | 变量/密钥 | 自选股列表，包含黄金相关代码 | `600519,Au9999,GC=F,GLD` |
| **GEMINI_API_KEY** | 密钥 | Gemini AI API Key（用于综合分析） | - |
| **TAVILY_API_KEYS** | 密钥 | Tavily 搜索 API（用于新闻搜索） | - |
| **BOCHA_API_KEYS** | 密钥 | 博查搜索 API（用于中文搜索） | - |

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
git add src/gold_analyzer.py src/core/pipeline.py .github/workflows/daily_analysis.yml

# 提交更改
git commit -m "添加黄金分析功能"

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
6. **报告生成** - 生成包含所有资产的综合分析报告
7. **结果推送** - 推送到配置的通知渠道

## 🔧 高级配置

### 1. 调整分析参数

可以在 `src/gold_analyzer.py` 中调整黄金分析的参数：

```python
# 黄金特有的交易参数配置
BIAS_THRESHOLD = 3.0        # 乖离率阈值（%）
VOLUME_SHRINK_RATIO = 0.7   # 缩量判断阈值
VOLUME_HEAVY_RATIO = 1.8    # 放量判断阈值
```

### 2. 添加更多黄金相关资产

在 `src/core/pipeline.py` 中可以添加更多黄金相关资产的识别：

```python
if code in ['Au9999', 'GC=F', 'GLD', 'GOLD', 'NEM'] or 'gold' in code.lower():
    # 使用黄金分析器
    trend_result = self.gold_trend_analyzer.analyze(df, code)
```

### 3. 配置通知渠道

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
│   ├── gold_analyzer.py          # 黄金趋势分析器
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

### Q: 如何添加新的黄金相关资产？

**A:** 在 `src/core/pipeline.py` 中修改资产识别逻辑，添加新的黄金相关代码。

### Q: GitHub Actions 运行失败怎么办？

**A:** 检查以下几点：
- 确保所有必要的 API Key 已正确配置
- 确保 `STOCK_LIST` 格式正确，无多余空格
- 查看 GitHub Actions 日志，了解具体错误信息

## 🎯 总结

通过本指南的配置，您的股票分析系统将能够：

- ✅ 自动识别和分析黄金相关资产
- ✅ 为黄金资产提供专业的分析建议
- ✅ 在 GitHub Actions 中定期执行黄金分析
- ✅ 生成包含黄金和股票的综合分析报告

祝您投资顺利！
