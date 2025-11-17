#!/usr/bin/env python3
"""
多链监听启动脚本（生产可用）

专注 ETH + BSC，可选开启 Solana，方便直接用于实际运行。

配置优先级:
1. 如存在 config.py，则优先从中读取 RPC / 代理 / 飞书配置
2. 否则，从环境变量读取 ETH_RPC_URL / BSC_RPC_URL / SOL_RPC_URL / PROXY / FEISHU_WEBHOOK_URL
"""

import os

from multichain_listener import MultiChainListener

try:
    from config import (
        ETH_CONFIG,
        BSC_CONFIG,
        SOLANA_CONFIG,
        PROXY as CONFIG_PROXY,
        ENABLE_FILTER,
        FEISHU_CONFIG,
    )

    HAS_CONFIG = True
except ImportError:
    HAS_CONFIG = False
    CONFIG_PROXY = None
    ENABLE_FILTER = True
    FEISHU_CONFIG = {}
def main():
    print("""
╔════════════════════════════════════════════════════════════════════════════╗
║                      多链监听启动（ETH + BSC + 可选 Solana）              ║
╚════════════════════════════════════════════════════════════════════════════╝

免费 RPC 节点:
- Ethereum: https://eth-mainnet.g.alchemy.com/v2/YOUR_API_KEY (Alchemy)
- BSC: https://bsc-dataseed.binance.org/ (Binance 官方)
- Solana: https://api.mainnet-beta.solana.com (Solana 官方)
    """)

    # 1) 优先使用 config.py 中的配置
    if HAS_CONFIG:
        ETH_RPC_URL = ETH_CONFIG['rpc_url']
        ETH_WS_URL = ETH_CONFIG.get('ws_url')
        BSC_RPC_URL = BSC_CONFIG['rpc_url']
        BSC_WS_URL = BSC_CONFIG.get('ws_url')
        SOL_RPC_URL = SOLANA_CONFIG['rpc_url']
        PROXY = CONFIG_PROXY
        enable_filter = ENABLE_FILTER

        feishu_webhook_url = None
        if FEISHU_CONFIG.get('enabled') and FEISHU_CONFIG.get('webhook_url'):
            feishu_webhook_url = FEISHU_CONFIG['webhook_url']
    else:
        # 2) 退回到环境变量配置
        ETH_RPC_URL = os.getenv('ETH_RPC_URL', 'https://eth-mainnet.g.alchemy.com/v2/YOUR_API_KEY')
        ETH_WS_URL = os.getenv('ETH_WS_URL')
        BSC_RPC_URL = os.getenv('BSC_RPC_URL', 'https://bsc-dataseed.binance.org/')
        BSC_WS_URL = os.getenv('BSC_WS_URL')
        SOL_RPC_URL = os.getenv('SOL_RPC_URL', 'https://api.mainnet-beta.solana.com')
        PROXY = os.getenv('PROXY', None)  # 例如 "127.0.0.1:7897"
        enable_filter = True
        feishu_webhook_url = os.getenv('FEISHU_WEBHOOK_URL')

    listener = MultiChainListener(
        enable_filter=enable_filter,
        proxy=PROXY,
        feishu_webhook_url=feishu_webhook_url,
    )

    # 添加 ETH + BSC 监听器
    listener.add_eth_listener(
        rpc_url=ETH_RPC_URL,
        ws_url=ETH_WS_URL,
        proxy=PROXY,
        use_websocket=bool(ETH_WS_URL),
    )
    listener.add_bsc_listener(
        rpc_url=BSC_RPC_URL,
        ws_url=BSC_WS_URL,
        proxy=PROXY,
        use_websocket=bool(BSC_WS_URL),
    )

    # 询问是否启用 Solana
    use_solana = input("是否同时启用 Solana 监听？(y/N): ").strip().lower()
    if use_solana == 'y':
        listener.add_solana_listener(
            rpc_url=SOL_RPC_URL
        )
        print("✅ 已启用 Solana 监听")
    else:
        print("ℹ️ 已跳过 Solana，只监听 ETH + BSC")

    # 启动所有链监听（多线程）
    listener.start_all()


if __name__ == '__main__':
    main()
