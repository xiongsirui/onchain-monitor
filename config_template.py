#!/usr/bin/env python3
"""
配置文件模板

将此文件复制为 config.py 并填写你的 RPC URL
"""

# ============================================================================
# RPC 节点配置
# ============================================================================

# Ethereum RPC 配置
ETH_CONFIG = {
    # HTTP RPC URL (必需)
    'rpc_url': 'https://eth-mainnet.g.alchemy.com/v2/YOUR_API_KEY',

    # WebSocket RPC URL (可选，Web3.py v6+ 不再支持同步 WebSocket)
    'ws_url': None,

    # 轮询间隔（秒）
    'poll_interval': 12,
}

# BSC RPC 配置
BSC_CONFIG = {
    # HTTP RPC URL (必需)
    # 免费 RPC: https://bsc-dataseed.binance.org/
    'rpc_url': 'https://bsc-dataseed.binance.org/',

    # WebSocket RPC URL (可选)
    'ws_url': None,

    # 轮询间隔（秒）
    'poll_interval': 3,
}

# Solana RPC 配置
SOLANA_CONFIG = {
    # HTTP RPC URL (必需)
    # 免费 RPC: https://api.mainnet-beta.solana.com
    'rpc_url': 'https://api.mainnet-beta.solana.com',

    # 轮询间隔（秒）
    'poll_interval': 2,
}

# ============================================================================
# 代理配置
# ============================================================================

# 代理服务器地址（如果需要）
# 格式: 'http://host:port' 或 'host:port'
# 留空表示不使用代理
PROXY = None  # 例如: '127.0.0.1:7897'

# ============================================================================
# 监听器配置
# ============================================================================

# 是否启用币安代币过滤器
# True: 自动过滤 600+ 已上架代币
# False: 显示所有代币（包括已上架）
ENABLE_FILTER = True

# 缓存文件路径
CACHE_FILE = 'binance_tokens_cache.json'

# 缓存有效期（小时）
CACHE_HOURS = 24

# ============================================================================
# 告警配置
# ============================================================================

# HIGH 级别告警阈值
HIGH_ALERT_THRESHOLD = {
    'confidence': 0.8,      # 置信度 ≥ 80%
    'transfer_count': 3,    # 转账数 ≥ 3 笔
    'sender_count': 2,      # 发送者 ≥ 2 个
}

# MEDIUM 级别告警阈值
MEDIUM_ALERT_THRESHOLD = {
    'confidence': 0.6,      # 置信度 ≥ 60%
    'transfer_count': 5,    # 转账数 ≥ 5 笔
}

# ============================================================================
# 飞书通知配置（推荐）
# ============================================================================

FEISHU_CONFIG = {
    'enabled': False,  # 是否启用飞书通知
    'webhook_url': 'https://open.feishu.cn/open-apis/bot/v2/hook/YOUR_TOKEN',
}

# 获取飞书 Webhook URL 步骤:
# 1. 打开飞书群组
# 2. 点击右上角 [...] → 群设置
# 3. 群机器人 → 添加机器人 → 自定义机器人
# 4. 设置机器人名称和描述
# 5. 复制 Webhook 地址

# ============================================================================
# Telegram 通知配置（可选）
# ============================================================================

TELEGRAM_CONFIG = {
    'enabled': False,           # 是否启用 Telegram 通知
    'bot_token': 'YOUR_BOT_TOKEN',
    'chat_id': 'YOUR_CHAT_ID',
}

# ============================================================================
# 其他配置
# ============================================================================

# 是否启用详细日志
VERBOSE = True

# 持久化文件路径
PERSISTENCE_FILE = 'multichain_state.pkl'


# ============================================================================
# 免费 RPC 节点推荐
# ============================================================================

"""
Ethereum:
- Alchemy: https://www.alchemy.com/ (需注册，每月 100M CU 免费额度)
  格式: https://eth-mainnet.g.alchemy.com/v2/YOUR_API_KEY

- Infura: https://infura.io/ (需注册，每天 100k 请求)
  格式: https://mainnet.infura.io/v3/YOUR_API_KEY

- QuickNode: https://www.quicknode.com/ (需注册)

BSC:
- Binance 官方: https://bsc-dataseed.binance.org/ (完全免费，无需注册)
- Binance 备用:
  - https://bsc-dataseed1.binance.org/
  - https://bsc-dataseed2.binance.org/
  - https://bsc-dataseed3.binance.org/

Solana:
- Solana 官方: https://api.mainnet-beta.solana.com (完全免费)
- Helius: https://www.helius.dev/ (需注册，免费额度充足)
"""

# ============================================================================
# 使用说明
# ============================================================================

"""
1. 复制此文件为 config.py:
   cp config_template.py config.py

2. 编辑 config.py，填写你的 RPC URL

3. 在代码中导入配置:
   from config import ETH_CONFIG, BSC_CONFIG, PROXY

4. 使用配置:
   listener.add_eth_listener(
       rpc_url=ETH_CONFIG['rpc_url'],
       proxy=PROXY
   )

推荐配置:
- 如果只需要快速监听，使用 BSC（免费且快速）
- 如果需要全面监听，使用 ETH + BSC
- Solana 功能开发中，不推荐使用
"""
