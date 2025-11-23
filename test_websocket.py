#!/usr/bin/env python3
"""
WebSocket 连接测试脚本

用于测试 Infura (ETH) 和 Ankr (BSC) 的 WebSocket 连接
"""

import asyncio
from web3 import AsyncWeb3
from web3.providers.persistent import WebSocketProvider

# 从 config.py 读取配置
try:
    from config import ETH_CONFIG, BSC_CONFIG

    eth_ws_url = ETH_CONFIG.get('ws_url')
    bsc_ws_url = BSC_CONFIG.get('ws_url')
except ImportError:
    print("❌ 未找到 config.py，请先运行 setup_websocket.py 创建配置文件")
    exit(1)

async def test_connection(name, ws_url, proxy=None):
    """测试 WebSocket 连接"""
    print(f"\n{'='*80}")
    print(f"测试 {name} WebSocket 连接")
    print(f"{'='*80}")
    print(f"URL: {ws_url}")

    if not ws_url or 'YOUR_' in ws_url:
        print(f"⚠️  {name} WebSocket URL 未配置或包含占位符")
        print(f"   请编辑 config.py，替换 YOUR_API_KEY")
        return False

    try:
        # 创建 WebSocket 提供者
        provider = WebSocketProvider(ws_url)
        w3 = AsyncWeb3(provider)

        print(f"⏳ 正在连接...")
        await w3.provider.connect()
        print(f"✅ WebSocket 连接成功！")

        # 测试基本查询
        print(f"⏳ 测试区块查询...")
        block_number = await w3.eth.block_number
        print(f"✅ 当前区块高度: {block_number}")

        # 测试链 ID
        chain_id = await w3.eth.chain_id
        chain_names = {
            1: 'Ethereum Mainnet',
            56: 'BSC Mainnet',
        }
        chain_name = chain_names.get(chain_id, f'Chain {chain_id}')
        print(f"✅ 链 ID: {chain_id} ({chain_name})")

        # 断开连接
        await w3.provider.disconnect()
        print(f"✅ {name} WebSocket 测试通过！")
        return True

    except Exception as e:
        print(f"❌ {name} WebSocket 连接失败: {e}")
        print(f"\n常见问题:")
        print(f"   1. API Key 是否正确?")
        print(f"   2. 网络连接是否正常?")
        print(f"   3. 是否需要代理?")
        return False

async def main():
    print("""
╔════════════════════════════════════════════════════════════════════════════╗
║                    WebSocket 连接测试                                       ║
╚════════════════════════════════════════════════════════════════════════════╝
""")

    # 测试 ETH
    eth_success = await test_connection('Ethereum', eth_ws_url)

    # 测试 BSC
    bsc_success = await test_connection('BSC', bsc_ws_url)

    # 总结
    print(f"\n{'='*80}")
    print(f"测试结果总结")
    print(f"{'='*80}")

    if eth_success and bsc_success:
        print(f"✅ 所有连接测试通过！")
        print(f"\n下一步:")
        print(f"   运行监听器: python3 run_multichain.py")
        print(f"\n预期输出:")
        print(f"   ✅ [Ethereum] WebSocket 连接成功，使用 Web3.py v7+ 新版 API")
        print(f"   ✅ [BSC] WebSocket 连接成功，使用 Web3.py v7+ 新版 API")
    else:
        print(f"⚠️  部分连接测试失败")
        print(f"\n建议:")
        if not eth_success:
            print(f"   • 检查 Infura API Key 是否正确")
            print(f"   • 确认 config.py 中 ETH_CONFIG['ws_url'] 已正确配置")
        if not bsc_success:
            print(f"   • 检查 Ankr API Key 是否正确")
            print(f"   • 确认 config.py 中 BSC_CONFIG['ws_url'] 已正确配置")
        print(f"\n失败的连接会自动回退到 HTTP 轮询模式，不影响功能")

    print(f"{'='*80}\n")

if __name__ == '__main__':
    asyncio.run(main())
