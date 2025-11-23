#!/usr/bin/env python3
"""
快速测试 WebSocket 连接修复
"""

import asyncio
from web3 import AsyncWeb3
from web3.providers.persistent import WebSocketProvider

async def test_infura():
    """测试 Infura WebSocket 连接"""
    try:
        # 替换为您的 Infura API Key
        ws_url = 'wss://mainnet.infura.io/ws/v3/a5c953a20c9b46d2b620c84b3eafe726'

        print("="*80)
        print("测试 Infura WebSocket 连接")
        print("="*80)
        print(f"URL: {ws_url}\n")

        # 创建 Provider
        print("⏳ 创建 WebSocket Provider...")
        ws_provider = WebSocketProvider(ws_url)
        w3 = AsyncWeb3(ws_provider)
        print("✅ WebSocket Provider 已创建\n")

        # 建立连接
        print("⏳ 正在建立连接...")
        await w3.provider.connect()
        print("✅ WebSocket 连接已建立\n")

        # 测试查询
        print("⏳ 测试区块查询...")
        block = await w3.eth.block_number
        print(f"✅ 当前区块高度: {block}\n")

        # 断开连接
        print("⏳ 断开连接...")
        await w3.provider.disconnect()
        print("✅ 连接已断开\n")

        print("="*80)
        print("✅ Infura WebSocket 测试通过！")
        print("="*80)
        return True

    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_ankr():
    """测试 Ankr BSC WebSocket 连接"""
    try:
        # 需要替换为您的 Ankr API Key
        ws_url = 'wss://rpc.ankr.com/bsc/ws/YOUR_ANKR_API_KEY'

        print("\n" + "="*80)
        print("测试 Ankr BSC WebSocket 连接")
        print("="*80)
        print(f"URL: {ws_url}\n")

        if 'YOUR_' in ws_url:
            print("⚠️  请先配置 Ankr API Key")
            return False

        # 创建 Provider
        print("⏳ 创建 WebSocket Provider...")
        ws_provider = WebSocketProvider(ws_url)
        w3 = AsyncWeb3(ws_provider)
        print("✅ WebSocket Provider 已创建\n")

        # 建立连接
        print("⏳ 正在建立连接...")
        await w3.provider.connect()
        print("✅ WebSocket 连接已建立\n")

        # 测试查询
        print("⏳ 测试区块查询...")
        block = await w3.eth.block_number
        print(f"✅ 当前区块高度: {block}\n")

        # 断开连接
        print("⏳ 断开连接...")
        await w3.provider.disconnect()
        print("✅ 连接已断开\n")

        print("="*80)
        print("✅ Ankr BSC WebSocket 测试通过！")
        print("="*80)
        return True

    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    print("""
╔════════════════════════════════════════════════════════════════════════════╗
║                  WebSocket 连接修复验证                                     ║
╚════════════════════════════════════════════════════════════════════════════╝
""")

    # 测试 Infura
    infura_ok = await test_infura()

    # 测试 Ankr (可选)
    # ankr_ok = await test_ankr()

    print("\n" + "="*80)
    print("测试总结")
    print("="*80)
    if infura_ok:
        print("✅ 修复成功！WebSocket 连接正常")
        print("\n下一步:")
        print("   1. 编辑 config.py，填入您的 API Keys")
        print("   2. 运行: python3 run_multichain.py")
    else:
        print("⚠️  连接仍有问题，请检查:")
        print("   1. API Key 是否正确")
        print("   2. 网络连接是否正常")
        print("   3. 是否需要代理")

if __name__ == '__main__':
    asyncio.run(main())
