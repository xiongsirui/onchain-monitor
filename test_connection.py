#!/usr/bin/env python3
"""连接测试脚本 - 诊断所有网络连接问题"""

print("=" * 60)
print("币安新币监控系统 - 连接测试")
print("=" * 60)

print("\n1. 测试 Python 环境")
print("-" * 60)

try:
    from web3 import Web3
    import requests
    print("✅ 依赖包已安装 (web3, requests)")
except ImportError as e:
    print(f"❌ 缺少依赖: {e}")
    print("\n请运行:")
    print("  conda install -c conda-forge web3 requests")
    print("或:")
    print("  pip install web3 requests")
    exit(1)

print("\n2. 测试代理连接")
print("-" * 60)

PROXY = "http://127.0.0.1:7897"  # 修改为你的代理

try:
    response = requests.get(
        "https://www.google.com",
        proxies={'http': PROXY, 'https': PROXY},
        timeout=5
    )
    print(f"✅ 代理工作正常: {PROXY}")
    print(f"   响应状态: {response.status_code}")
except requests.exceptions.ProxyError:
    print(f"❌ 代理连接失败: {PROXY}")
    print("\n请检查:")
    print("  1. 代理软件是否正在运行")
    print("  2. 端口号是否正确 (127.0.0.1:7897)")
    print("  3. 防火墙是否阻止")
except Exception as e:
    print(f"❌ 网络错误: {e}")

print("\n3. 测试 RPC 节点连接")
print("-" * 60)

# 测试多个 RPC 节点
RPC_NODES = [
    ("LlamaRPC", "https://eth.llamarpc.com"),
    ("LlamaNodes", "https://eth.llmamarpc.com"),
    ("Ankr", "https://rpc.ankr.com/eth"),
    ("Cloudflare", "https://cloudflare-eth.com"),
]

rpc_success = False
for name, rpc_url in RPC_NODES:
    print(f"\n测试 {name}: {rpc_url}")
    try:
        w3 = Web3(Web3.HTTPProvider(
            rpc_url,
            request_kwargs={'proxies': {'http': PROXY, 'https': PROXY}, 'timeout': 10}
        ))

        if w3.is_connected():
            block = w3.eth.block_number
            print(f"  ✅ 连接成功！当前区块: {block:,}")
            rpc_success = True

            # 保存成功的 RPC URL
            print(f"\n💡 推荐使用此 RPC 节点:")
            print(f"    RPC_URL = \"{rpc_url}\"")
            break
        else:
            print(f"  ❌ 无法连接")
    except Exception as e:
        print(f"  ❌ 失败: {type(e).__name__}: {str(e)[:50]}")

if not rpc_success:
    print("\n⚠️  所有 RPC 节点均无法连接")
    print("\n可能原因:")
    print("  1. 代理未正常工作")
    print("  2. 网络防火墙阻止")
    print("  3. Web3.py 配置问题")
    print("\n建议:")
    print("  1. 检查代理软件状态")
    print("  2. 尝试: curl -x http://127.0.0.1:7897 https://eth.llamarpc.com")
    print("  3. 检查 conda 环境中 web3 版本: pip show web3")

print("\n4. 测试 Binance API")
print("-" * 60)

try:
    session = requests.Session()
    session.proxies = {'http': PROXY, 'https': PROXY}

    response = session.get(
        "https://api.binance.com/api/v3/exchangeInfo",
        timeout=10
    )
    data = response.json()
    print(f"✅ Binance API 连接成功")
    print(f"   交易对数量: {len(data['symbols'])}")
except Exception as e:
    print(f"❌ Binance API 失败: {e}")

print("\n5. 测试 CoinGecko API")
print("-" * 60)

try:
    response = session.get(
        "https://api.coingecko.com/api/v3/ping",
        timeout=10
    )
    print(f"✅ CoinGecko API 连接成功")
    print(f"   响应: {response.json()}")
except Exception as e:
    print(f"❌ CoinGecko API 失败: {e}")

print("\n" + "=" * 60)
print("测试完成！")
print("=" * 60)

print("\n建议:")
print("  - 如果所有测试通过 ✅ → 运行: python run.py")
print("  - 如果代理失败 ❌ → 检查代理软件")
print("  - 如果 RPC 失败 ❌ → 尝试备用 RPC 节点")
print("  - 如果 API 失败 ❌ → 可临时禁用过滤器")
