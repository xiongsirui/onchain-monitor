#!/usr/bin/env python3
"""
安装验证脚本

检查所有依赖是否正确安装，并测试基本功能
"""

import sys
import importlib

def check_python_version():
    """检查 Python 版本"""
    print("1. 检查 Python 版本...")
    version = sys.version_info
    if version.major >= 3 and version.minor >= 8:
        print(f"   ✅ Python {version.major}.{version.minor}.{version.micro}")
        return True
    else:
        print(f"   ❌ Python 版本过低: {version.major}.{version.minor}.{version.micro}")
        print(f"      需要 Python 3.8 或更高版本")
        return False


def check_dependencies():
    """检查依赖包"""
    print("\n2. 检查依赖包...")

    required_packages = {
        'web3': 'Web3',
        'requests': 'requests',
        'solana': 'solana (可选，仅 Solana 链需要)',
        'solders': 'solders (可选，仅 Solana 链需要)',
    }

    all_ok = True
    optional_missing = []

    for package, display_name in required_packages.items():
        try:
            mod = importlib.import_module(package)
            version = getattr(mod, '__version__', 'unknown')
            print(f"   ✅ {display_name}: {version}")
        except ImportError:
            if package in ['solana', 'solders']:
                print(f"   ⚠️  {display_name}: 未安装 (可选)")
                optional_missing.append(package)
            else:
                print(f"   ❌ {display_name}: 未安装")
                all_ok = False

    if optional_missing:
        print(f"\n   ℹ️  提示: {', '.join(optional_missing)} 是可选依赖")
        print(f"      如果不需要监听 Solana 链，可以忽略")
        print(f"      如需安装: pip install {' '.join(optional_missing)}")

    return all_ok


def check_files():
    """检查必要文件"""
    print("\n3. 检查项目文件...")

    required_files = [
        'multichain_listener.py',
        'binance_token_filter.py',
        'run_multichain.py',
        'run_bsc.py',
        'requirements.txt',
    ]

    import os
    all_ok = True

    for filename in required_files:
        if os.path.exists(filename):
            print(f"   ✅ {filename}")
        else:
            print(f"   ❌ {filename} 缺失")
            all_ok = False

    return all_ok


def test_basic_functionality():
    """测试基本功能"""
    print("\n4. 测试基本功能...")

    try:
        # 测试导入
        print("   测试导入模块...")
        from multichain_listener import MultiChainListener
        from binance_token_filter import BinanceTokenFilter
        print("   ✅ 模块导入成功")

        # 测试币安过滤器（不连接网络）
        print("   测试币安过滤器...")
        try:
            filter = BinanceTokenFilter(cache_file='test_cache.json')
            print(f"   ✅ 币安过滤器初始化成功")
            # 删除测试缓存
            import os
            if os.path.exists('test_cache.json'):
                os.remove('test_cache.json')
        except Exception as e:
            print(f"   ⚠️  币安过滤器测试失败: {e}")
            print(f"      (这可能是网络问题，不影响基本功能)")

        return True

    except Exception as e:
        print(f"   ❌ 功能测试失败: {e}")
        return False


def test_network():
    """测试网络连接"""
    print("\n5. 测试网络连接...")

    try:
        import requests

        # 测试 BSC RPC
        print("   测试 BSC RPC 连接...")
        try:
            response = requests.get('https://bsc-dataseed.binance.org/', timeout=5)
            print("   ✅ BSC RPC 连接正常")
        except Exception as e:
            print(f"   ❌ BSC RPC 连接失败: {e}")
            print(f"      建议: 检查网络连接或使用代理")
            return False

        # 测试 Binance API
        print("   测试 Binance API 连接...")
        try:
            response = requests.get('https://api.binance.com/api/v3/ping', timeout=5)
            if response.status_code == 200:
                print("   ✅ Binance API 连接正常")
            else:
                print(f"   ⚠️  Binance API 返回状态码: {response.status_code}")
        except Exception as e:
            print(f"   ⚠️  Binance API 连接失败: {e}")
            print(f"      (这不影响监听，但会影响代币过滤功能)")

        # 测试 CoinGecko API
        print("   测试 CoinGecko API 连接...")
        try:
            response = requests.get('https://api.coingecko.com/api/v3/ping', timeout=5)
            if response.status_code == 200:
                print("   ✅ CoinGecko API 连接正常")
            else:
                print(f"   ⚠️  CoinGecko API 返回状态码: {response.status_code}")
        except Exception as e:
            print(f"   ⚠️  CoinGecko API 连接失败: {e}")
            print(f"      (这不影响监听，但会影响代币过滤功能)")

        return True

    except Exception as e:
        print(f"   ❌ 网络测试失败: {e}")
        return False


def main():
    print("""
╔════════════════════════════════════════════════════════════════════════════╗
║                      安装验证脚本                                          ║
╚════════════════════════════════════════════════════════════════════════════╝
""")

    results = []

    # 1. Python 版本
    results.append(("Python 版本", check_python_version()))

    # 2. 依赖包
    results.append(("依赖包", check_dependencies()))

    # 3. 项目文件
    results.append(("项目文件", check_files()))

    # 4. 基本功能
    results.append(("基本功能", test_basic_functionality()))

    # 5. 网络连接
    results.append(("网络连接", test_network()))

    # 汇总
    print("\n" + "="*80)
    print("📊 验证结果汇总")
    print("="*80)

    all_passed = True
    for name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{name:20s}: {status}")
        if not result:
            all_passed = False

    print("="*80)

    if all_passed:
        print("\n🎉 恭喜！所有检查都通过了！")
        print("\n下一步:")
        print("  • 运行 BSC 监听器: python3 run_bsc.py")
        print("  • 运行多链监听: python3 run_multichain.py")
        print("  • 查看文档: 阅读 README.md 和 CLAUDE.md")
    else:
        print("\n⚠️  部分检查未通过，请根据上述提示修复问题")
        print("\n常见解决方案:")
        print("  • 安装依赖: pip install -r requirements.txt")
        print("  • 检查网络: 如果在国内，可能需要使用代理")
        print("  • 检查 Python 版本: python3 --version")

    print()


if __name__ == '__main__':
    main()
