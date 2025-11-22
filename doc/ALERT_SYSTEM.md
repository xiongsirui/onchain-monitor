# 📢 项目方打新消息发送机制

> 详细说明当检测到项目方打新时，系统如何自动发送告警消息

---

## 📋 目录

1. [消息发送流程](#消息发送流程)
2. [触发条件](#触发条件)
3. [消息内容](#消息内容)
4. [飞书通知配置](#飞书通知配置)
5. [消息示例](#消息示例)

---

## 🔄 消息发送流程

### 完整流程图

```
区块链事件
    ↓
检测到代币转账
    ↓
代币过滤 (BinanceTokenFilter)
    ↓
【未上架】→ 加入缓冲区
    ↓
累积转账数据
    ↓
触发分析条件 (≥3笔 或 ≥2发送者 或 1小时)
    ↓
四维度评分 (AdvancedTokenAnalyzer)
    ↓
【置信度 ≥ 80% + 转账 ≥ 3 + 发送者 ≥ 2】
    ↓
🚨 HIGH 级别告警
    ↓
┌─────────────┬─────────────┐
│             │             │
控制台输出    飞书通知      其他通知
                          (Telegram/邮件等)
```

---

## ✅ 触发条件

### HIGH 级别告警 (红色)

**满足以下任一条件组**:

#### 条件组 1: 多笔转账 (原有逻辑)
```python
✅ 置信度 >= 80%
✅ 转账笔数 >= 3 笔
✅ 独立发送者 >= 2 个
```

#### 条件组 2: 大额单笔转账 (项目方打新) 🆕
```python
✅ 置信度 >= 80%
✅ 单笔转账 >= 10万代币 (或总额 >= 100万代币)
```

**项目方打新场景示例**:

```python
# 场景 1: 单笔大额转账 (现在会触发告警!) 🆕
transfers = [
    {'from': '0xProject...', 'value': 5_000_000 * 10**18},  # 500万代币
]
置信度 = 100% ✅
转账数 = 1 笔
单笔金额 = 500万 ✅ (>= 10万)
→ 🚨 触发 HIGH 告警！(大额单笔逻辑)

# 场景 2: 多笔大额转账 (也会触发)
transfers = [
    {'from': '0xProject...', 'value': 5_000_000 * 10**18},  # 500万代币
    {'from': '0xProject...', 'value': 3_000_000 * 10**18},  # 300万代币
]
置信度 = 100% ✅
转账数 = 2 笔
单笔金额 = 500万 ✅ (>= 10万)
→ 🚨 触发 HIGH 告警！(大额单笔逻辑)

# 场景 3: 项目方 + 用户充值 (原有逻辑)
transfers = [
    {'from': '0xProject...', 'value': 5_000_000 * 10**18},  # 项目方
    {'from': '0xProject...', 'value': 3_000_000 * 10**18},  # 项目方
    {'from': '0xUser...', 'value': 1_000 * 10**18},         # 用户
]
置信度 = 100% ✅
转账数 = 3 笔 ✅
发送者 = 2 个 ✅
→ 🚨 触发 HIGH 告警！(多笔转账逻辑)
```

**代码位置**: [multichain_listener.py:518-528](../multichain_listener.py#L518-L528)

---

### MEDIUM 级别告警 (橙色)

**必须同时满足**:

```python
✅ 置信度 >= 60%
✅ 转账笔数 >= 5 笔
```

---

## 📨 消息内容

### 1. 控制台输出

```bash
🚨🚨🚨 [BSC] HIGH 级别告警! 🚨🚨🚨
   代币: NEWCOIN (New Coin Token)
   合约: 0x1234567890abcdef1234567890abcdef12345678
   转账数: 5 笔
   发送者: 3 个
   置信度: 100%
   🟢 强烈建议: 高置信度信号，多维度验证通过，建议重点关注
   立即行动建议: 深入调查此代币！
```

**代码位置**: [multichain_listener.py:526-537](../multichain_listener.py#L526-L537)

---

### 2. 飞书富文本卡片

#### 卡片结构

```
┌───────────────────────────────────────────┐
│ 🚨🚨🚨 [BSC] HIGH 级别新代币告警           │ ← 红色标题
├───────────────────────────────────────────┤
│ 代币符号: NEWCOIN                          │
│ 代币名称: New Coin Token                   │
│ 合约地址: 0x1234567890...                  │
├───────────────────────────────────────────┤
│ 转账笔数: 5 笔                             │
│ 发送者数: 3 个                             │
│ 置信度评分: 100% ██████████               │
│ 风险等级: 🟢 低风险                        │
├───────────────────────────────────────────┤
│ 📊 分析结果                                │
│ 🟢 强烈建议: 高置信度信号，建议重点关注    │
├───────────────────────────────────────────┤
│ ✅ 发现模式                                │
│ • ⭐ 大额转账（可能是项目方入库）          │
│ • 💎 单一发送者大额转账（项目方入库模式）  │
│ • ✅ 大额转账检测通过（加 30% 置信度）    │
├───────────────────────────────────────────┤
│ ⚠️ 警告信息                               │
│ (无)                                       │
├───────────────────────────────────────────┤
│ [查看合约详情] ← 按钮，跳转 BscScan        │
├───────────────────────────────────────────┤
│ 检测时间: 2024-11-23 15:30:45             │
└───────────────────────────────────────────┘
```

#### 颜色编码

| 告警级别 | 颜色 | 说明 |
|---------|------|------|
| HIGH | 🔴 红色 | 高置信度，建议立即关注 |
| MEDIUM | 🟠 橙色 | 中等置信度，持续观察 |
| LOW | 🔵 蓝色 | 低优先级，仅供参考 |

**代码位置**: [feishu_notifier.py:71-252](../feishu_notifier.py#L71-L252)

---

## 🛠️ 飞书通知配置

### 方式 1: 环境变量 (推荐)

```bash
# 设置飞书 Webhook URL
export FEISHU_WEBHOOK_URL='https://open.feishu.cn/open-apis/bot/v2/hook/YOUR_TOKEN'

# 运行监听器
python3 run_multichain.py
```

---

### 方式 2: 配置文件

编辑 `config.py`:

```python
FEISHU_CONFIG = {
    'enabled': True,
    'webhook_url': 'https://open.feishu.cn/open-apis/bot/v2/hook/YOUR_TOKEN',
}
```

---

### 方式 3: 代码中直接配置

```python
from multichain_listener import MultiChainListener

listener = MultiChainListener(
    enable_filter=True,
    proxy='127.0.0.1:7897',
    feishu_webhook_url='https://open.feishu.cn/open-apis/bot/v2/hook/YOUR_TOKEN'
)
```

---

## 📝 获取飞书 Webhook URL

### 步骤 1: 创建飞书机器人

1. 打开飞书，进入需要接收告警的群聊
2. 点击群设置 → 群机器人 → 添加机器人
3. 选择"自定义机器人"
4. 设置机器人名称（如"币安新币监测"）
5. 复制生成的 Webhook URL

**URL 格式**:
```
https://open.feishu.cn/open-apis/bot/v2/hook/xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
```

---

### 步骤 2: 测试飞书通知

```bash
# 方法 1: 使用测试脚本
export FEISHU_WEBHOOK_URL='https://open.feishu.cn/open-apis/bot/v2/hook/YOUR_TOKEN'
python3 feishu_notifier.py

# 方法 2: 使用 curl 测试
curl -X POST 'https://open.feishu.cn/open-apis/bot/v2/hook/YOUR_TOKEN' \
  -H 'Content-Type: application/json' \
  -d '{
    "msg_type": "text",
    "content": {
      "text": "测试消息"
    }
  }'
```

---

## 📱 消息示例

### 示例 1: 项目方大额打新 (HIGH)

```
🚨🚨🚨 [BSC] HIGH 级别新代币告警

代币符号: NEWCOIN
代币名称: New Coin Token
合约地址: 0x1234567890abcdef1234567890abcdef12345678

转账笔数: 3 笔
发送者数: 2 个
置信度评分: 100% ██████████
风险等级: 🟢 低风险

📊 分析结果
🟢 强烈建议: 高置信度信号，多维度验证通过，建议重点关注

✅ 发现模式
• ⭐ 大额转账（可能是项目方入库）
• 💎 单一发送者大额转账（项目方入库模式）
• ✅ 大额转账检测通过（加 30% 置信度）

[查看合约详情] → https://bscscan.com/token/0x1234...

检测时间: 2024-11-23 15:30:45
```

---

### 示例 2: 用户自然充值 (HIGH)

```
🚨🚨🚨 [ETH] HIGH 级别新代币告警

代币符号: GOODCOIN
代币名称: Good Coin
合约地址: 0xabcdef1234567890abcdef1234567890abcdef12

转账笔数: 5 笔
发送者数: 3 个
置信度评分: 100% ██████████
风险等级: 🟢 低风险

📊 分析结果
🟢 强烈建议: 高置信度信号，多维度验证通过，建议重点关注

✅ 发现模式
• 发现 5 笔转账
• 3 个独立发送者
• 所有转账在 2.0 小时内完成

[查看合约详情] → https://etherscan.io/token/0xabcd...

检测时间: 2024-11-23 16:15:20
```

---

### 示例 3: 可疑女巫攻击 (MEDIUM)

```
⚡ [BSC] MEDIUM 级别新代币告警

代币符号: SCAMCOIN
代币名称: Scam Coin
合约地址: 0x9876543210fedcba9876543210fedcba98765432

转账笔数: 5 笔
发送者数: 5 个
置信度评分: 72% ███████▒▒▒
风险等级: 🟡 中等风险

📊 分析结果
🟡 谨慎建议: 中等置信度，建议持续观察，等待更多信号

✅ 发现模式
• 发现 5 笔转账
• 5 个独立发送者
• 疑似批量操作
• ⚠️ 发现小额重复转账模式

⚠️ 警告信息
• 发现 4 笔交易时间过于接近（< 60秒）
• 金额过于相似（只有 1 个不同值）
• ⚠️ 女巫攻击风险: 发现 2 个可疑指标

[查看合约详情] → https://bscscan.com/token/0x9876...

检测时间: 2024-11-23 16:45:10
```

---

## 🔧 高级配置

### 自定义告警条件

如果你想调整告警触发条件，编辑 [multichain_listener.py:447-453](../multichain_listener.py#L447-L453):

```python
# 更严格的 HIGH 级别
if confidence >= 0.9 and transfer_count >= 5 and sender_count >= 3:
    should_alert = True
    alert_level = 'HIGH'

# 更宽松的 MEDIUM 级别
elif confidence >= 0.5 and transfer_count >= 3:
    should_alert = True
    alert_level = 'MEDIUM'
```

---

### 添加其他通知方式

#### 示例: 添加 Telegram 通知

```python
# 在 multichain_listener.py 的 _send_alert 方法中添加

def _send_alert(self, level, contract, buffer, analysis, token_info):
    """发送告警"""
    # ... 现有代码 ...

    # 发送 Telegram 通知
    if self.telegram_notifier:
        try:
            self.telegram_notifier.send_alert(
                level=level,
                chain=self.chain_name,
                contract=contract,
                token_info=token_info,
                analysis=analysis
            )
        except Exception as e:
            print(f"   ⚠️  Telegram 通知发送失败: {e}")
```

---

## 🚨 告警防误报机制

### 二次验证

对于 **HIGH 级别告警**，系统会二次查询 Binance API 确认代币未上架：

```python
if alert_level == 'HIGH' and self.binance_filter:
    is_listed, binance_info = self.binance_filter.is_listed_on_binance(contract)
    if is_listed:
        # 取消告警，防止误报
        print(f"\n⚠️  [{self.chain_name}] HIGH 告警被二次验证阻止:")
        print(f"   代币 {symbol} 已在币安上架 (交易对: {binance_symbol}USDT)")
        return  # 不发送告警
```

**代码位置**: [multichain_listener.py:456-462](../multichain_listener.py#L456-L462)

---

### 防止重复告警

每个代币只会发送一次告警：

```python
buffer['alert_sent'] = True  # 标记已发送
```

即使后续有更多转账，也不会重复发送。

---

## 🔍 消息调试

### 查看控制台输出

```bash
# 运行监听器并查看实时输出
python3 run_multichain.py

# 或使用 nohup 后台运行并保存日志
nohup python3 run_multichain.py > monitor.log 2>&1 &

# 查看日志
tail -f monitor.log
```

---

### 测试飞书通知

```bash
# 发送测试消息
export FEISHU_WEBHOOK_URL='你的Webhook URL'
python3 feishu_notifier.py

# 应该看到输出
✅ 飞书通知发送成功
```

---

## 📊 数据流程总结

```
┌─────────────────────────────────────────────┐
│ 1. 区块链监听 (每 3-12 秒)                   │
│    - ETH: 12 秒轮询                          │
│    - BSC: 3 秒轮询                           │
└────────────────┬────────────────────────────┘
                 │
┌────────────────▼────────────────────────────┐
│ 2. 代币过滤 (BinanceTokenFilter)            │
│    - 查询 441 个已上架代币                   │
│    - 过滤已知代币                            │
└────────────────┬────────────────────────────┘
                 │
┌────────────────▼────────────────────────────┐
│ 3. 转账数据缓冲                              │
│    - 累积每个新代币的转账记录                │
│    - 记录发送者、金额、时间戳                │
└────────────────┬────────────────────────────┘
                 │
┌────────────────▼────────────────────────────┐
│ 4. 触发分析 (≥3笔 或 ≥2发送者)              │
│    - 基础统计分析 (30%)                      │
│    - 时间模式分析 (20%)                      │
│    - 金额分布分析 (20%)                      │
│    - 女巫攻击检测 (30%)                      │
└────────────────┬────────────────────────────┘
                 │
┌────────────────▼────────────────────────────┐
│ 5. 计算置信度                                │
│    - 大额转账: 100%                          │
│    - 多发送者分散金额: 100%                  │
│    - 小额女巫: 72%                           │
└────────────────┬────────────────────────────┘
                 │
┌────────────────▼────────────────────────────┐
│ 6. 判断是否告警                              │
│    HIGH: 置信度≥80% + 转账≥3 + 发送者≥2     │
│    MEDIUM: 置信度≥60% + 转账≥5              │
└────────────────┬────────────────────────────┘
                 │
         ┌───────┴───────┐
         │               │
┌────────▼────┐  ┌───────▼──────┐
│ 控制台输出  │  │ 飞书通知     │
│ (实时显示)  │  │ (富文本卡片) │
└─────────────┘  └──────────────┘
```

---

## 📚 相关文档

- 检测逻辑详解: [DETECTION_LOGIC.md](DETECTION_LOGIC.md)
- 飞书通知代码: [feishu_notifier.py](../feishu_notifier.py)
- 主监听器代码: [multichain_listener.py](../multichain_listener.py)
- 项目配置: [config.py](../config.py)

---

## 🔄 更新日志

### v3.1 (2024-11-23) 🆕
- ✅ **修复单笔大额转账告警缺失**
  - 问题: 项目方单笔大额打新不触发告警
  - 原因: `_should_run_analysis` 要求 >= 2 笔转账
  - 解决: 单笔 >= 10万代币也触发分析
  - 新增 HIGH 告警条件: 置信度 >= 80% + 大额单笔
  - 代码: [multichain_listener.py:628-650](../multichain_listener.py#L628-L650)
  - 代码: [multichain_listener.py:518-528](../multichain_listener.py#L518-L528)

### v3.0 (2024-11-23)
- ✅ 优化项目方打新识别
- ✅ 大额转账自动豁免女巫检测
- ✅ 100% 置信度告警

### v2.1 (2024-11-22)
- ✅ 新增飞书富文本卡片
- ✅ 添加区块浏览器跳转链接
- ✅ 二次验证防误报机制

---

**最后更新**: 2024-11-23
**维护者**: Claude Code AI
