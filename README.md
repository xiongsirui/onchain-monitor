# 多链区块链监听器 - Binance 新币检测

> 实时监控 Binance 钱包地址，检测新代币转入（支持 ETH、BSC、Solana）

## 🚀 快速开始

### 方式 1: 一键启动（推荐新手）⚡

```bash
# 1. 安装依赖
pip install -r requirements.txt

# 2. 验证安装
python3 verify_installation.py

# 3. 启动 BSC 监听器（最简单，无需配置）
python3 run_bsc.py
```

这是最简单的方式，直接监听 BSC 链，无需任何配置！

### 方式 2: 多链启动脚本（ETH + BSC，支持 Solana）

```bash
# 运行多链监听脚本
python3 run_multichain.py
```

### 方式 3: 自定义配置

**1. 创建配置文件**:
```bash
cp config_template.py config.py
# 编辑 config.py 填写你的 RPC URL
```

**2. 在代码中使用配置**:
```python
from config import ETH_CONFIG, BSC_CONFIG, PROXY
from multichain_listener import MultiChainListener

listener = MultiChainListener(enable_filter=True, proxy=PROXY)
listener.add_bsc_listener(rpc_url=BSC_CONFIG['rpc_url'])
listener.listeners['BSC'].listen(poll_interval=BSC_CONFIG['poll_interval'])
```

---

## 🔧 配置 RPC 节点

**免费 RPC 节点推荐**:
- **Ethereum**: [Alchemy](https://alchemy.com/) (需注册获取 API Key)
- **BSC**: https://bsc-dataseed.binance.org/ (无需 API Key)
- **Solana**: https://api.mainnet-beta.solana.com (无需 API Key)

**修改示例代码中的 RPC URL**:
```python
listener.add_eth_listener(
    rpc_url='https://eth-mainnet.g.alchemy.com/v2/YOUR_API_KEY',
    proxy='127.0.0.1:7897'  # 可选：如果需要代理
)
```

---

## ⭐ 推荐配置

**最佳实践**：优先监听 BSC 链
- BSC 出块速度快（3秒），检测速度快 ⚡
- 币安官方 RPC 免费且稳定
- 更多新代币首先在 BSC 测试

```python
from multichain_listener import MultiChainListener

listener = MultiChainListener(enable_filter=True, proxy='127.0.0.1:7897')
listener.add_bsc_listener(rpc_url='https://bsc-dataseed.binance.org/')
listener.listeners['BSC'].listen(poll_interval=3)
```

---

## 📊 功能特性

✅ **多链支持**: 同时监听 ETH、BSC、Solana
✅ **智能过滤**: 自动过滤 600+ 已上架代币
✅ **女巫攻击检测**: 识别虚假信号
✅ **置信度评分**: 多维度评估新代币可信度
✅ **智能告警**: 高置信度代币自动告警
✅ **飞书通知**: 实时推送告警到飞书群聊 🆕
✅ **多线程监控**: 并行监听多条链

---

## 📁 项目结构

| 文件 | 说明 | 推荐度 |
|------|------|--------|
| [run_bsc.py](run_bsc.py) | **BSC 一键启动脚本** 🆕 | ⭐⭐⭐⭐⭐ |
| [run_feishu.py](run_feishu.py) | **飞书通知启动脚本** 🆕 | ⭐⭐⭐⭐⭐ |
| [verify_installation.py](verify_installation.py) | **安装验证脚本** 🆕 | ⭐⭐⭐⭐⭐ |
| [multichain_listener.py](multichain_listener.py) | 多链统一监听器（ETH+BSC+Solana） | ⭐⭐⭐⭐⭐ |
| [feishu_notifier.py](feishu_notifier.py) | 飞书机器人通知器 🆕 | ⭐⭐⭐⭐⭐ |
| [run_multichain.py](run_multichain.py) | 多链监听启动脚本 | ⭐⭐⭐⭐⭐ |
| [config_template.py](config_template.py) | 配置文件模板 🆕 | ⭐⭐⭐⭐ |
| [binance_token_filter.py](binance_token_filter.py) | 币安代币过滤器 | ⭐⭐⭐⭐ |
| [FEISHU_GUIDE.md](FEISHU_GUIDE.md) | 飞书通知配置指南 🆕 | 📖 |
| [CLAUDE.md](CLAUDE.md) | 开发者详细文档 | 📖 |

**推荐使用**:
- 🆕 **新手**: 直接运行 `python3 run_bsc.py`
- 🆕 **飞书通知**: 使用 `python3 run_feishu.py` 启用飞书告警
- **进阶**: 使用 `python3 run_multichain.py` 进行多链监听

---

## 🔧 使用示例

### 示例 1: 监听单条链 (BSC)

```python
from multichain_listener import MultiChainListener

listener = MultiChainListener(enable_filter=True)
listener.add_bsc_listener(rpc_url='https://bsc-dataseed.binance.org/')
listener.listeners['BSC'].listen(poll_interval=3)
```

### 示例 2: 监听多条链 (ETH + BSC)

```python
from multichain_listener import MultiChainListener

listener = MultiChainListener(enable_filter=True)
listener.add_eth_listener(rpc_url='https://eth-mainnet.g.alchemy.com/v2/YOUR_KEY')
listener.add_bsc_listener(rpc_url='https://bsc-dataseed.binance.org/')
listener.start_all()  # 多线程并行监听
```

### 示例 3: 使用回调函数

```python
def on_new_token(transfer_data, tokens_buffer):
    contract = transfer_data['contract']
    buffer = tokens_buffer[contract]

    if buffer.get('analysis'):
        confidence = buffer['analysis']['confidence']
        if confidence >= 0.8:
            print(f"🚨 高置信度新代币: {contract}")
            # TODO: 发送 Telegram 通知

listener = MultiChainListener(enable_filter=True)
listener.add_bsc_listener(rpc_url='https://bsc-dataseed.binance.org/')
listener.listeners['BSC'].listen(poll_interval=3, callback=on_new_token)
```

---

## 📱 飞书通知

将新代币告警自动推送到飞书群聊！

### 快速开始

```bash
# 1. 设置飞书 Webhook URL
export FEISHU_WEBHOOK_URL='https://open.feishu.cn/open-apis/bot/v2/hook/YOUR_TOKEN'

# 2. 运行飞书通知示例
python3 run_feishu.py
```

### 代码集成

```python
from multichain_listener import MultiChainListener

# 创建监听器（传入飞书 Webhook URL）
listener = MultiChainListener(
    enable_filter=True,
    proxy='127.0.0.1:7897',
    feishu_webhook_url='https://open.feishu.cn/open-apis/bot/v2/hook/YOUR_TOKEN'
)

# 添加监听链
listener.add_bsc_listener(rpc_url='https://bsc-dataseed.binance.org/')
listener.listeners['BSC'].listen(poll_interval=3)
```

### 功能特性

- ✅ **富文本卡片消息** - 结构化展示告警信息
- ✅ **颜色标识** - 红色/橙色/蓝色区分告警级别
- ✅ **详细分析** - 置信度、风险等级、发现模式
- ✅ **一键跳转** - 直接访问区块浏览器
- ✅ **自动重试** - 网络故障时自动重试

**详细配置**: 查看 [FEISHU_GUIDE.md](FEISHU_GUIDE.md)

---

## 🌐 代理配置

如果网络访问受限，可以配置代理:

```python
listener = MultiChainListener(
    enable_filter=True,
    proxy='127.0.0.1:7897'  # HTTP/SOCKS5 代理
)

listener.add_eth_listener(
    rpc_url='https://eth-mainnet.g.alchemy.com/v2/YOUR_KEY',
    proxy='127.0.0.1:7897'
)
```

---

## 📈 监控的钱包地址

### Ethereum (8 个热钱包)
- 0x28C6c06298d514Db089934071355E5743bf21d60 (Binance 14)
- 0x21a31Ee1afC51d94C2eFcCAa2092aD1028285549 (Binance 15)
- 0xF977814e90dA44bFA03b6295A0616a897441aceC (Binance 8)
- ... 等

### BSC (4 个热钱包)
- 0x8894E0a0c962CB723c1976a4421c95949bE2D4E3 (Binance BSC Hot)
- 0x28C6c06298d514Db089934071355E5743bf21d60 (Binance 14)
- ... 等

### Solana (2 个热钱包)
- FWWqD7mGFWzGbUB14TXLxESJ5GSKboMvCHvmh6xEjHfQ
- 5tzFkiKscXHK5ZXCGbXZxdw7gTjjD1mBwuoFbhUvuAi9

---

## 🔍 工作原理

### 多链监控流程

```
[Thread 1: ETH] → ETH RPC 节点 → Transfer 事件 (12s 间隔)
                        ↓
[Thread 2: BSC] → BSC RPC 节点 → Transfer 事件 (3s 间隔) ⚡
                        ↓
[Thread 3: SOL] → SOL RPC 节点 → Transfer 指令 (2s 间隔)
                        ↓
                  过滤 Binance 钱包
                        ↓
              BinanceTokenFilter (共享)
                ↙           ↘
         已上架 → 跳过    未上架 → 分析
                              ↓
                   AdvancedTokenAnalyzer (共享)
                              ↓
              5 维度评分 + 女巫检测
                              ↓
                  置信度 ≥ 80% → 🚨 HIGH 告警
                  置信度 ≥ 60% → ⚡ MEDIUM 告警
```

### 5 维度分析

| 维度 | 权重 | 检测内容 |
|------|------|----------|
| 基础统计 | 30% | 转账次数、发送者数量、集中度 |
| 时间模式 | 20% | 时间分布、间隔分析 |
| 金额分布 | 20% | 金额相似度、变异系数 |
| 女巫检测 | 30% | 协同攻击模式识别 |

---

## 📊 输出示例

### 正常检测

```
🚨🚨🚨 [BSC] 发现未上架新代币! 🚨🚨🚨
   代币: NEWCOIN (New Coin Token)
   合约: 0x1234567890abcdef1234567890abcdef12345678
   ✅ 未在币安上架 - 可能是即将上线的新币!
   📥 充值: 100000.0000 NEWCOIN
   发送者: 0xabcd1234...5678efgh
   时间: 2024-11-09 10:30:45

   📊 执行完整策略分析...

   ─────────────────────────────────────────────────────────
   🔍 策略分析结果:
   ─────────────────────────────────────────────────────────
   置信度: 85% ████████▓▓
   风险等级: LOW

   ✅ 发现模式:
      • 发现 5 笔转账
      • 3 个独立发送者
      • 所有转账在 2.5 小时内完成

   💡 🟢 强烈建议: 高置信度信号，多维度验证通过，建议重点关注
   ─────────────────────────────────────────────────────────

🚨🚨🚨 [BSC] HIGH 级别告警! 🚨🚨🚨
   代币: NEWCOIN (New Coin Token)
   合约: 0x1234567890abcdef1234567890abcdef12345678
   转账数: 5 笔
   发送者: 3 个
   置信度: 85%
   🟢 强烈建议: 高置信度信号，多维度验证通过，建议重点关注
   立即行动建议: 深入调查此代币！
```

---

## 🛠️ 高级配置

### 调整轮询间隔

```python
listener.start_all(poll_intervals={
    'ETH': 12,  # 以太坊 12 秒
    'BSC': 3,   # BSC 3 秒（推荐）
    'SOL': 2,   # Solana 2 秒
})
```

### 自定义告警阈值

修改 `multichain_listener.py` 中的 `BaseChainListener._check_alert_conditions()`:

```python
# 更严格的 HIGH 级别
if confidence >= 0.9 and transfer_count >= 5 and sender_count >= 3:
    should_alert = True
    alert_level = 'HIGH'
```

---

## 🔀 链对比

| 链 | 出块速度 | 轮询间隔 | 检测速度 | RPC 成本 | 状态 |
|------|----------|----------|----------|---------|------|
| **Ethereum** | 12秒 | 12秒 | 中等 | 免费额度 | ✅ 生产 |
| **BSC** | 3秒 | 3秒 | 快速 ⚡ | 完全免费 | ✅ 生产 |
| **Solana** | <1秒 | 2秒 | 极快 | 完全免费 | ✅ 生产 |

**推荐**: BSC 链最快且完全免费！

---

## ⚠️ 注意事项

1. **合法合规**: 仅用于市场研究,不提供投资建议
2. **风险提示**: 新代币检测不保证准确性，可能存在误报
3. **不执行交易**: 本工具仅监控检测，不自动执行任何交易
4. **网络要求**: 需要稳定的网络连接和 RPC 节点访问权限

---

## 📚 详细文档

查看 [CLAUDE.md](CLAUDE.md) 获取完整的架构说明和 API 文档。

---

## 🔄 更新日志

### v2.1 (2024-11) 🆕
- 🆕 新增飞书通知功能 (`feishu_notifier.py`)
- ✅ 富文本卡片消息，支持颜色标识
- ✅ 自动推送告警到飞书群聊
- ✅ 一键跳转区块浏览器

### v2.0 (2024-11)
- 🆕 新增多链统一监听器 (`multichain_listener.py`)
- ✅ 支持 ETH + BSC + Solana 实时监听
- ✅ 统一的代币过滤器和分析器
- ✅ 多线程并行监听
- ✅ 跨链监控能力

### v1.0 (2024-10)
- ✅ 单链 ETH 监听器
- ✅ 币安代币过滤器
- ✅ 女巫攻击检测
- ✅ 数据持久化

---

## 📧 问题反馈

如有问题或建议，请提交 Issue。

---

## 📜 许可证

本项目仅供学习研究使用，请遵守相关法律法规。

---

**祝你好运！🚀**
