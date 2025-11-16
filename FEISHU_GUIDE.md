# 飞书通知配置指南

> 将新代币告警自动发送到飞书群聊

## 🎯 功能特性

- ✅ **富文本卡片消息** - 结构化展示告警信息
- ✅ **颜色标识** - 红色/橙色/蓝色区分告警级别
- ✅ **详细分析** - 置信度、风险等级、发现模式、警告信息
- ✅ **一键跳转** - 直接访问区块浏览器查看合约详情
- ✅ **自动重试** - 网络故障时自动重试发送

## 📱 快速开始

### 步骤 1: 创建飞书机器人 (2 分钟)

1. 打开飞书群组
2. 点击右上角 **[...]** → **群设置**
3. 点击 **群机器人** → **添加机器人** → **自定义机器人**
4. 设置机器人名称（例如：新币监控）
5. 复制 **Webhook 地址**

   ```
   https://open.feishu.cn/open-apis/bot/v2/hook/xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
   ```

### 步骤 2: 配置 Webhook URL (1 分钟)

#### 方式 A: 使用环境变量（推荐）

```bash
# Linux/macOS
export FEISHU_WEBHOOK_URL='https://open.feishu.cn/open-apis/bot/v2/hook/YOUR_TOKEN'

# Windows PowerShell
$env:FEISHU_WEBHOOK_URL='https://open.feishu.cn/open-apis/bot/v2/hook/YOUR_TOKEN'

# 验证
echo $FEISHU_WEBHOOK_URL
```

#### 方式 B: 使用配置文件

编辑 `config.py`：

```python
FEISHU_CONFIG = {
    'enabled': True,
    'webhook_url': 'https://open.feishu.cn/open-apis/bot/v2/hook/YOUR_TOKEN',
}
```

### 步骤 3: 运行监听器

#### 快速测试（推荐）

```bash
# 运行飞书通知示例
python3 example_feishu.py
```

**预期输出**:
```
📱 初始化飞书通知器...
📤 发送测试消息...
✅ 飞书通知发送成功
✅ 飞书通知器已启用

🎉 监听器已启动！
✅ BSC 链监听已开启
✅ 币安代币过滤器已启用
✅ 飞书通知已启用
```

#### 代码集成

```python
from multichain_listener import MultiChainListener

# 创建监听器（传入飞书 Webhook URL）
listener = MultiChainListener(
    enable_filter=True,
    proxy='127.0.0.1:7897',  # 可选
    feishu_webhook_url='https://open.feishu.cn/open-apis/bot/v2/hook/YOUR_TOKEN'
)

# 添加监听链
listener.add_bsc_listener(rpc_url='https://bsc-dataseed.binance.org/')

# 启动监听
listener.listeners['BSC'].listen(poll_interval=3)
```

---

## 📊 消息示例

### HIGH 级别告警（红色）

<div style="background: #fee; border-left: 4px solid red; padding: 12px;">

**🚨🚨🚨 [BSC] HIGH 级别新代币告警**

**代币符号**
NEWCOIN

**代币名称**
New Coin Token

**合约地址**
`0x1234567890abcdef1234567890abcdef12345678`

---

**转账笔数**
5 笔

**发送者数**
3 个

**置信度评分**
85% ████████▒▒

**风险等级**
🟢 低风险

---

**📊 分析结果**
🟢 强烈建议: 高置信度信号，多维度验证通过，建议重点关注

**✅ 发现模式**
• 发现 5 笔转账
• 3 个独立发送者
• 所有转账在 2.5 小时内完成

**[查看合约详情]** → BSCScan

检测时间: 2024-11-10 15:30:45

</div>

### MEDIUM 级别告警（橙色）

<div style="background: #fff3e0; border-left: 4px solid orange; padding: 12px;">

**⚡ [ETH] MEDIUM 级别新代币告警**

**代币符号**
TEST

**代币名称**
Test Token

**合约地址**
`0xabcdefabcdefabcdefabcdefabcdefabcdefabcd`

---

**转账笔数**
7 笔

**发送者数**
2 个

**置信度评分**
65% ██████▒▒▒▒

**风险等级**
🟡 中等风险

---

**📊 分析结果**
🟡 谨慎建议: 中等置信度，建议持续观察，等待更多信号

**⚠️ 警告信息**
• 发送者过少（< 3）
• 金额过于相似（只有 2 个不同值）

**[查看合约详情]** → Etherscan

检测时间: 2024-11-10 15:35:20

</div>

---

## 🔧 高级配置

### 自定义告警级别

修改 `multichain_listener.py` 的 `_check_alert_conditions()` 方法：

```python
# 更严格的 HIGH 级别
if confidence >= 0.9 and transfer_count >= 5 and sender_count >= 3:
    should_alert = True
    alert_level = 'HIGH'

# 新增 CRITICAL 级别
elif confidence >= 0.95 and transfer_count >= 10:
    should_alert = True
    alert_level = 'CRITICAL'
```

### 添加自定义字段

修改 `feishu_notifier.py` 的 `_build_alert_card()` 方法：

```python
# 添加总供应量信息
card['elements'].append({
    "tag": "div",
    "text": {
        "tag": "lark_md",
        "content": f"**总供应量**\n{token_info.get('total_supply', 'N/A')}"
    }
})
```

### 代理配置

如果飞书 API 访问受限，可以配置代理：

```python
listener = MultiChainListener(
    enable_filter=True,
    proxy='127.0.0.1:7897',  # 将同时用于 RPC 和飞书 API
    feishu_webhook_url='YOUR_WEBHOOK_URL'
)
```

---

## ❓ 常见问题

### Q1: 飞书通知发送失败

**错误信息**: `⚠️ 飞书通知发送失败: connection timeout`

**解决方案**:
1. 检查 Webhook URL 是否正确
2. 检查网络连接
3. 如果在国内，尝试使用代理
4. 检查飞书群机器人是否被禁用

### Q2: 收到测试消息但没有告警

**原因**: 没有检测到新代币或代币不满足告警条件

**解决方案**:
1. 等待一段时间（可能需要几小时）
2. 降低告警阈值（编辑 `_check_alert_conditions`）
3. 查看控制台输出，确认检测到转账事件

### Q3: 如何禁用测试消息

编辑 `multichain_listener.py` 的 `MultiChainListener.__init__()` 方法，注释掉测试消息部分：

```python
# 不发送测试消息
# if self.feishu_notifier.send_test_message():
#     print("✅ 飞书通知器已启用\n")
self.feishu_notifier = FeishuNotifier(feishu_webhook_url, proxy=proxy)
print("✅ 飞书通知器已启用\n")
```

### Q4: 如何测试飞书通知

运行独立测试脚本：

```bash
# 设置环境变量
export FEISHU_WEBHOOK_URL='YOUR_WEBHOOK_URL'

# 运行测试
python3 -c "from feishu_notifier import test_feishu_notifier; test_feishu_notifier()"
```

或使用 Python 交互式：

```python
from feishu_notifier import FeishuNotifier

notifier = FeishuNotifier('YOUR_WEBHOOK_URL')
notifier.send_test_message()
```

---

## 📚 相关文档

- [飞书机器人开发文档](https://open.feishu.cn/document/ukTMukTMukTM/ucTM5YjL3ETO24yNxkjN)
- [README.md](README.md) - 项目主文档
- [QUICKSTART.md](QUICKSTART.md) - 快速上手指南
- [config_template.py](config_template.py) - 配置文件模板

---

## 🎉 成功案例

使用飞书通知后，您将获得：

- ⚡ **实时告警** - 新代币检测后立即通知
- 📱 **移动友好** - 手机飞书 App 随时查看
- 👥 **团队协作** - 群组成员同步接收告警
- 📊 **结构化信息** - 清晰的卡片展示
- 🔗 **快速响应** - 一键跳转区块浏览器

**开始使用**: `python3 example_feishu.py` 🚀
