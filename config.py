#!/usr/bin/env python3
"""
项目统一配置文件

说明:
- 优先推荐使用 BSC + ETH，多链可选开启 Solana
- 飞书 Webhook 可以直接写在这里，或者通过环境变量 FEISHU_WEBHOOK_URL 提供
"""

import os

# ============================================================================
# RPC 节点配置
# ============================================================================

# Ethereum RPC 配置
ETH_CONFIG = {
    # HTTP RPC URL (必需)
    # 推荐使用 Alchemy/Infura/QuickNode 等主网节点
    # 替换下面的 YOUR_API_KEY 为你自己的 Key
    'rpc_url': os.getenv(
        'ETH_RPC_URL',
        'https://ethereum.publicnode.com',
    ),

    # WebSocket RPC URL (可选，配置后可启用 WebSocket 监听)
    'ws_url': os.getenv('ETH_WS_URL', 'wss://ethereum.publicnode.com'),

    # 轮询间隔（秒）
    'poll_interval': 12,
}


# BSC RPC 配置
BSC_CONFIG = {
    # HTTP RPC URL (必需)
    # 默认使用币安官方免费节点
    'rpc_url': os.getenv(
        'BSC_RPC_URL',
        'https://bsc-dataseed.binance.org/',
    ),

    # WebSocket RPC URL (可选)
    'ws_url': os.getenv('BSC_WS_URL', 'wss://bsc-ws-node.nariox.org'),

    # 轮询间隔（秒）
    'poll_interval': 3,
}


# Solana RPC 配置（可选）
SOLANA_CONFIG = {
    # HTTP RPC URL
    'rpc_url': os.getenv(
        'SOL_RPC_URL',
        'https://api.mainnet-beta.solana.com',
    ),

    # 轮询间隔（秒）
    'poll_interval': 2,
}


# ============================================================================
# 代理配置
# ============================================================================

# 代理服务器地址（如果需要）
# 支持格式:
#   - "127.0.0.1:7897"         (会在代码中自动补全 http://)
#   - "http://127.0.0.1:7897"
#   - "socks5://127.0.0.1:7891"
# 不需要代理时设为 None
PROXY = os.getenv('PROXY', None)


# ============================================================================
# 监听器 / 过滤器配置
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
# 飞书通知配置
# ============================================================================

# 如果你不想把 Webhook 写死在文件里，可以:
#   export FEISHU_WEBHOOK_URL='https://open.feishu.cn/open-apis/bot/v2/hook/XXXX'
_env_feishu_webhook = os.getenv('FEISHU_WEBHOOK_URL')

FEISHU_CONFIG = {
    # 是否启用飞书通知
    # 1. 如果设置了 FEISHU_WEBHOOK_URL 环境变量，会自动启用
    # 2. 否则，可以改成 True 并在下面填写 webhook_url
    'enabled': bool(_env_feishu_webhook),

    # 飞书 Webhook URL
    'webhook_url': _env_feishu_webhook
    or 'https://open.feishu.cn/open-apis/bot/v2/hook/YOUR_TOKEN',
}


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

# 多链监听持久化文件路径
PERSISTENCE_FILE = 'multichain_state.pkl'


# ============================================================================
# 使用说明（参考）
# ============================================================================

"""
使用方式示例:

from config import ETH_CONFIG, BSC_CONFIG, SOLANA_CONFIG, PROXY, ENABLE_FILTER, FEISHU_CONFIG
from multichain_listener import MultiChainListener

listener = MultiChainListener(
    enable_filter=ENABLE_FILTER,
    proxy=PROXY,
    feishu_webhook_url=FEISHU_CONFIG['webhook_url'] if FEISHU_CONFIG['enabled'] else None,
)

listener.add_eth_listener(rpc_url=ETH_CONFIG['rpc_url'], proxy=PROXY)
listener.add_bsc_listener(rpc_url=BSC_CONFIG['rpc_url'], proxy=PROXY)
"""
