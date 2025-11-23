#!/usr/bin/env python3
"""
WebSocket 完整配置向导

帮助您配置 ETH + BSC 的 WebSocket 监听
"""

import os
import sys

print("""
╔════════════════════════════════════════════════════════════════════════════╗
║                   WebSocket 完整配置向导                                    ║
╚════════════════════════════════════════════════════════════════════════════╝
""")

print("【步骤 1/3】获取必要的 API Keys")
print("="*80)

print("""
需要注册以下服务获取 API Keys:

1️⃣  Infura (用于 Ethereum WebSocket)
   ┌─────────────────────────────────────────────────────────────────────┐
   │ 注册地址: https://infura.io/                                        │
   │ 费用: 免费（每月 100,000 请求）                                     │
   │ 步骤:                                                                │
   │   1. 注册账号                                                        │
   │   2. 创建新项目 (Create New Key)                                    │
   │   3. 选择 Ethereum Mainnet                                          │
   │   4. 复制 Project ID (API Key)                                      │
   │                                                                      │
   │ 获取的 URL 格式:                                                     │
   │   HTTP:  https://mainnet.infura.io/v3/YOUR_API_KEY                 │
   │   WS:    wss://mainnet.infura.io/ws/v3/YOUR_API_KEY                │
   └─────────────────────────────────────────────────────────────────────┘

2️⃣  Ankr (用于 BSC WebSocket)
   ┌─────────────────────────────────────────────────────────────────────┐
   │ 注册地址: https://www.ankr.com/rpc/                                 │
   │ 费用: 免费（每月 500M 请求单位）                                    │
   │ 步骤:                                                                │
   │   1. 注册账号                                                        │
   │   2. 进入 Dashboard                                                 │
   │   3. 创建 Endpoint → 选择 BNB Smart Chain                           │
   │   4. 复制 WebSocket URL                                             │
   │                                                                      │
   │ 获取的 URL 格式:                                                     │
   │   HTTP:  https://rpc.ankr.com/bsc/YOUR_API_KEY                     │
   │   WS:    wss://rpc.ankr.com/bsc/ws/YOUR_API_KEY                    │
   └─────────────────────────────────────────────────────────────────────┘

""")

# 检查是否已有 API keys
infura_key = os.getenv('INFURA_API_KEY')
ankr_key = os.getenv('ANKR_API_KEY')

if infura_key:
    print(f"✅ 检测到 INFURA_API_KEY: {infura_key[:8]}...")
else:
    print("⚠️  未检测到 INFURA_API_KEY 环境变量")

if ankr_key:
    print(f"✅ 检测到 ANKR_API_KEY: {ankr_key[:8]}...")
else:
    print("⚠️  未检测到 ANKR_API_KEY 环境变量")

print("\n" + "="*80)
print("【步骤 2/3】创建配置文件")
print("="*80)

config_content = """#!/usr/bin/env python3
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
"""

print("""
我将为您创建 config.py 配置文件。

配置内容:
  ✅ ETH: Infura WebSocket (实时推送)
  ✅ BSC: Ankr WebSocket (实时推送)
  ✅ 代理: 127.0.0.1:7897
  ✅ 飞书通知: 已启用

是否创建配置文件? (y/n): """)

choice = input().strip().lower()

if choice == 'y':
    with open('/Users/victoryx/onchain-monitor/config.py', 'w', encoding='utf-8') as f:
        f.write(config_content)

    print("""
✅ 配置文件已创建: config.py

⚠️  重要: 请立即编辑 config.py，替换以下内容:
   1. YOUR_INFURA_API_KEY  → 您的 Infura Project ID
   2. YOUR_ANKR_API_KEY    → 您的 Ankr API Key
   3. YOUR_FEISHU_TOKEN    → 您的飞书 Webhook Token (如果使用)

编辑命令:
   vim config.py
   # 或
   nano config.py
""")

print("\n" + "="*80)
print("【步骤 3/3】升级 Web3.py 到最新版本")
print("="*80)

print("""
为了获得最佳的 WebSocket 体验，建议升级到 Web3.py v7+

当前版本检测:
""")

try:
    import web3
    current_version = web3.__version__
    print(f"   Web3.py 版本: {current_version}")

    # 检查版本
    major_version = int(current_version.split('.')[0])
    if major_version >= 7:
        print(f"   ✅ 版本充足，支持最新 WebSocket API")
    else:
        print(f"   ⚠️  版本较旧，建议升级")
        print(f"\n   升级命令:")
        print(f"      pip install --upgrade web3>=7.7.0")
except ImportError:
    print("   ❌ Web3.py 未安装")
    print("   安装命令:")
    print("      pip install web3>=7.7.0")

print("\n" + "="*80)
print("【配置完成检查】")
print("="*80)

print("""
完成以上步骤后，您的系统将:

✅ Ethereum WebSocket 监听
   • 实时性: < 1 秒
   • 稳定性: ⭐⭐⭐⭐⭐
   • 提供商: Infura

✅ BSC WebSocket 监听
   • 实时性: < 1 秒
   • 稳定性: ⭐⭐⭐⭐⭐
   • 提供商: Ankr

✅ 所有检测功能
   • 单笔大额转账检测
   • 告警内容区分
   • 飞书通知

启动命令:
   python3 run_multichain.py

预期输出:
   ✅ [Ethereum] WebSocket 连接成功，使用 Web3.py v7+ 新版 API
   ✅ [BSC] WebSocket 连接成功，使用 Web3.py v7+ 新版 API

""")

print("="*80)
print("【快速测试】")
print("="*80)

print("""
如果您已经配置好 API Keys，可以运行快速测试:

测试脚本:
""")

test_script = """
# test_websocket.py
import asyncio
from web3 import AsyncWeb3
from web3.providers.persistent import WebSocketProvider

async def test_eth():
    try:
        ws_url = 'wss://mainnet.infura.io/ws/v3/YOUR_INFURA_API_KEY'
        w3 = AsyncWeb3(WebSocketProvider(ws_url))
        await w3.provider.connect()
        block = await w3.eth.block_number
        print(f'✅ ETH WebSocket 连接成功！区块高度: {block}')
        await w3.provider.disconnect()
    except Exception as e:
        print(f'❌ ETH WebSocket 连接失败: {e}')

async def test_bsc():
    try:
        ws_url = 'wss://rpc.ankr.com/bsc/ws/YOUR_ANKR_API_KEY'
        w3 = AsyncWeb3(WebSocketProvider(ws_url))
        await w3.provider.connect()
        block = await w3.eth.block_number
        print(f'✅ BSC WebSocket 连接成功！区块高度: {block}')
        await w3.provider.disconnect()
    except Exception as e:
        print(f'❌ BSC WebSocket 连接失败: {e}')

async def main():
    await test_eth()
    await test_bsc()

asyncio.run(main())
"""

print(test_script)

print("""
保存为 test_websocket.py 后运行:
   python3 test_websocket.py

""")

print("="*80)
print("【总结】")
print("="*80)

print("""
完整配置步骤:

1. 注册 Infura (https://infura.io/) 获取 ETH API Key ✅
2. 注册 Ankr (https://www.ankr.com/rpc/) 获取 BSC API Key ✅
3. 编辑 config.py，填入您的 API Keys ⚠️
4. (可选) 升级 Web3.py: pip install --upgrade web3>=7.7.0
5. 运行监听器: python3 run_multichain.py

需要帮助?
   • Infura 注册问题: https://docs.infura.io/
   • Ankr 注册问题: https://www.ankr.com/docs/
   • WebSocket 连接测试: python3 test_websocket.py

祝您配置顺利！🚀
""")
