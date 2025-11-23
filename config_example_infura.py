#!/usr/bin/env python3
"""
配置文件示例 - 针对 Infura WebSocket 优化

使用说明:
1. 复制此文件为 config.py
2. 替换 YOUR_INFURA_API_KEY 为您的 Infura API Key
3. BSC 建议使用 HTTP 模式（更稳定）
"""

# ============================================================================
# 代理配置（如果需要）
# ============================================================================
PROXY = '127.0.0.1:7897'  # HTTP/SOCKS5 代理，如果不需要设为 None

# ============================================================================
# 是否启用币安代币过滤
# ============================================================================
ENABLE_FILTER = True  # 过滤已上架的 600+ 代币

# ============================================================================
# Ethereum 配置（推荐使用 Infura）
# ============================================================================
ETH_CONFIG = {
    # Infura HTTP 端点
    'rpc_url': 'https://mainnet.infura.io/v3/YOUR_INFURA_API_KEY',

    # Infura WebSocket 端点（推荐）
    'ws_url': 'wss://mainnet.infura.io/ws/v3/YOUR_INFURA_API_KEY',

    # 轮询间隔（秒）- WebSocket 模式下不使用
    'poll_interval': 12,
}

# ============================================================================
# BSC 配置（推荐使用 Binance 官方 HTTP）
# ============================================================================
BSC_CONFIG = {
    # Binance 官方免费 RPC（推荐）
    'rpc_url': 'https://bsc-dataseed.binance.org/',

    # WebSocket 端点（可选，留空使用 HTTP 轮询）
    # 选项 1: 不配置 WebSocket，使用稳定的 HTTP 轮询（推荐）
    'ws_url': None,

    # 选项 2: 使用 Ankr WebSocket（需要 API key）
    # 'ws_url': 'wss://rpc.ankr.com/bsc/ws/YOUR_ANKR_API_KEY',

    # 选项 3: 使用公共 WebSocket（不稳定）
    # 'ws_url': 'wss://bsc-ws-node.nariox.org:443',

    # 轮询间隔（秒）- BSC 出块时间 3 秒
    'poll_interval': 3,
}

# ============================================================================
# Solana 配置（可选）
# ============================================================================
SOLANA_CONFIG = {
    # Solana 官方免费 RPC
    'rpc_url': 'https://api.mainnet-beta.solana.com',

    # 轮询间隔（秒）- Solana 出块时间 < 1 秒
    'poll_interval': 2,
}

# ============================================================================
# 飞书通知配置
# ============================================================================
FEISHU_CONFIG = {
    # 是否启用飞书通知
    'enabled': True,

    # 飞书机器人 Webhook URL
    # 获取方式: 飞书群聊 -> 群设置 -> 群机器人 -> 添加机器人 -> 自定义机器人
    'webhook_url': 'https://open.feishu.cn/open-apis/bot/v2/hook/YOUR_FEISHU_TOKEN',

    # 注意: 飞书是国内服务，一般不需要代理
    # 如果配置了 PROXY，飞书通知会自动跳过代理
}

# ============================================================================
# 配置说明
# ============================================================================
"""
推荐配置组合:

【组合 1: 最稳定】（推荐）
- ETH: Infura WebSocket
- BSC: Binance HTTP 轮询
- 特点: ETH 实时性好，BSC 稳定可靠

【组合 2: 全 WebSocket】
- ETH: Infura WebSocket
- BSC: Ankr WebSocket（需注册）
- 特点: 实时性最好，需要配置多个 API key

【组合 3: 全 HTTP】
- ETH: Infura HTTP
- BSC: Binance HTTP
- 特点: 最简单，无 WebSocket 警告

延迟对比:
- WebSocket: < 1 秒实时推送
- HTTP 轮询 (ETH): 12 秒延迟
- HTTP 轮询 (BSC): 3 秒延迟

建议: BSC 使用 HTTP 轮询（3秒）已经足够快，无需 WebSocket
"""
