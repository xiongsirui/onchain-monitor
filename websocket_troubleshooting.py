#!/usr/bin/env python3
"""
快速配置向导 - 消除 WebSocket 警告

根据您看到的警告信息，选择对应的解决方案。
"""

print("""
╔════════════════════════════════════════════════════════════════════════════╗
║                      WebSocket 警告解决方案向导                            ║
╚════════════════════════════════════════════════════════════════════════════╝

您遇到的警告:
1. ⚠️  [Ethereum] 使用旧版 subscribe API
2. ⚠️  [BSC] WebSocket 监听失败，回退到 HTTP 轮询模式

""")

print("="*80)
print("解决方案分析")
print("="*80)

print("""
警告 1: [Ethereum] 使用旧版 subscribe API
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ 状态: Ethereum WebSocket 正常工作
📊 影响: 无影响，只是 API 版本提示
🔧 原因: 系统使用 Web3.py v6 兼容模式
💡 建议:
   - 可以忽略（功能完全正常）
   - 或升级到 Web3.py v7（可选）

解决方法（可选）:
   pip install --upgrade web3>=7.7.0

警告 2: [BSC] WebSocket 监听失败，回退到 HTTP 轮询模式
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ 状态: BSC HTTP 轮询正常工作（3秒间隔）
📊 影响: 延迟 3 秒（完全够用）
🔧 原因: Infura BSC WebSocket 端点不可用
💡 建议:
   - **推荐**: 继续使用 HTTP 轮询（最稳定）
   - 或配置其他 WebSocket 端点（见下方）

""")

print("="*80)
print("推荐配置（消除所有警告）")
print("="*80)

print("""
【方案 1: 最简单】⭐ 推荐
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
使用 HTTP 轮询模式，无需任何 WebSocket 配置

优点:
  ✅ 无警告
  ✅ 最稳定
  ✅ 无需额外配置
  ✅ BSC 3秒延迟已经很快

配置:
  # config.py 或环境变量
  ETH_RPC_URL = 'https://mainnet.infura.io/v3/YOUR_API_KEY'
  ETH_WS_URL = None  # 不配置 WebSocket

  BSC_RPC_URL = 'https://bsc-dataseed.binance.org/'
  BSC_WS_URL = None  # 不配置 WebSocket


【方案 2: ETH WebSocket + BSC HTTP】⭐⭐ 平衡
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
ETH 使用 Infura WebSocket，BSC 使用 HTTP 轮询

优点:
  ✅ ETH 实时性好（< 1秒）
  ✅ BSC 稳定可靠（3秒）
  ✅ 只有一个信息提示（v6 兼容模式）

配置:
  ETH_RPC_URL = 'https://mainnet.infura.io/v3/YOUR_API_KEY'
  ETH_WS_URL = 'wss://mainnet.infura.io/ws/v3/YOUR_API_KEY'

  BSC_RPC_URL = 'https://bsc-dataseed.binance.org/'
  BSC_WS_URL = None  # 不配置 WebSocket


【方案 3: 全 WebSocket】
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
ETH 和 BSC 都使用 WebSocket

优点:
  ✅ 实时性最好
  ✅ 无警告（升级 Web3.py 后）

缺点:
  ❌ 需要注册 Ankr 获取 BSC WebSocket
  ❌ 配置复杂

配置:
  1. 注册 Ankr: https://www.ankr.com/rpc/
  2. 获取 API key
  3. 配置:
     ETH_WS_URL = 'wss://mainnet.infura.io/ws/v3/YOUR_INFURA_KEY'
     BSC_WS_URL = 'wss://rpc.ankr.com/bsc/ws/YOUR_ANKR_KEY'
  4. 升级 Web3.py:
     pip install --upgrade web3>=7.7.0

""")

print("="*80)
print("快速操作")
print("="*80)

import os

current_config = f"""
当前运行环境检测:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
ETH_RPC_URL  = {os.getenv('ETH_RPC_URL', '未设置')}
ETH_WS_URL   = {os.getenv('ETH_WS_URL', '未设置')}
BSC_RPC_URL  = {os.getenv('BSC_RPC_URL', '未设置')}
BSC_WS_URL   = {os.getenv('BSC_WS_URL', '未设置')}

建议操作:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
1. 复制 config_example_infura.py 为 config.py
   cp config_example_infura.py config.py

2. 编辑 config.py，替换 YOUR_INFURA_API_KEY

3. BSC 保持 ws_url = None（使用 HTTP 轮询）

4. 重启监听器
   python3 run_multichain.py

这样配置后:
  ✅ ETH WebSocket 正常（只有 v6 兼容提示，不影响使用）
  ✅ BSC HTTP 轮询（3秒，无警告）
  ✅ 所有功能完全正常
"""

print(current_config)

print("""
╔════════════════════════════════════════════════════════════════════════════╗
║                         总结                                                ║
╚════════════════════════════════════════════════════════════════════════════╝

这两个警告都不影响功能:
  ✅ ETH WebSocket 正常工作（只是使用 v6 兼容模式）
  ✅ BSC HTTP 轮询正常工作（3秒延迟完全够用）
  ✅ 所有新功能（单笔大额检测、告警区分）都正常

如果您不在意这些提示信息，可以直接使用，完全不影响检测效果！

如果想消除提示:
  • 最简单: BSC 保持 HTTP，ETH 也改为 HTTP（方案 1）
  • 推荐: BSC 保持 HTTP，ETH 使用 WebSocket（方案 2）✅

""")
