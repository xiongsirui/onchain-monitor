#!/usr/bin/env python3
'''
WebSocket 完整配置 - ETH + BSC

使用说明:
1. 替换 YOUR_INFURA_API_KEY 为您的 Infura API Key
2. 替换 YOUR_ANKR_API_KEY 为您的 Ankr API Key
3. 保存此文件为 config.py
'''

# ============================================================================
# 代理配置
# ============================================================================
PROXY = '127.0.0.1:7897'  # 如果不需要代理，设为 None

# ============================================================================
# 是否启用币安代币过滤
# ============================================================================
ENABLE_FILTER = True

# ============================================================================
# Ethereum 配置 (Infura WebSocket)
# ============================================================================
ETH_CONFIG = {
    # Infura HTTP RPC
    'rpc_url': 'https://mainnet.infura.io/v3/YOUR_INFURA_API_KEY',

    # Infura WebSocket ⭐
    'ws_url': 'wss://mainnet.infura.io/ws/v3/YOUR_INFURA_API_KEY',

    # 轮询间隔（WebSocket 模式下不使用）
    'poll_interval': 12,
}

# ============================================================================
# BSC 配置 (Ankr WebSocket)
# ============================================================================
BSC_CONFIG = {
    # Ankr HTTP RPC
    'rpc_url': 'https://rpc.ankr.com/bsc/YOUR_ANKR_API_KEY',

    # Ankr WebSocket ⭐
    'ws_url': 'wss://rpc.ankr.com/bsc/ws/YOUR_ANKR_API_KEY',

    # 轮询间隔（WebSocket 模式下不使用）
    'poll_interval': 3,
}

# ============================================================================
# Solana 配置（可选）
# ============================================================================
SOLANA_CONFIG = {
    'rpc_url': 'https://api.mainnet-beta.solana.com',
    'poll_interval': 2,
}

# ============================================================================
# 飞书通知配置
# ============================================================================
FEISHU_CONFIG = {
    'enabled': True,
    'webhook_url': 'https://open.feishu.cn/open-apis/bot/v2/hook/YOUR_FEISHU_TOKEN',
}
