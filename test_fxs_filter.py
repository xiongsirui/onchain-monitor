#!/usr/bin/env python3
"""测试 FXS 代币过滤"""

from binance_token_filter import BinanceTokenFilter

# FXS 合约地址
FXS_CONTRACT = "0x3432B6A60D23Ca0dFCa7761B7ab56459D9C964D0"

print("=" * 60)
print("FXS (Frax Share) 过滤测试")
print("=" * 60)

# 初始化过滤器
print("\n1. 初始化币安过滤器...")
proxy = "127.0.0.1:7897"  # 使用代理
filter = BinanceTokenFilter(proxy=proxy)

print("\n2. 检查 FXS 是否在币安上架...")
is_listed, info = filter.is_listed_on_binance(FXS_CONTRACT)

print(f"\n结果:")
print(f"  合约地址: {FXS_CONTRACT}")
print(f"  是否上架: {is_listed}")
print(f"  币安信息: {info}")

print("\n3. 检查 FXS 符号是否在币安...")
is_symbol_listed = filter.is_symbol_listed("FXS")
print(f"  FXS 符号是否上架: {is_symbol_listed}")

print("\n4. 获取过滤器统计...")
stats = filter.get_stats()
print(f"  总代币数: {stats['total_tokens']}")
print(f"  合约映射数: {stats['total_contracts']}")
print(f"  最后更新: {stats['last_update']}")

print("\n5. 手动搜索 FXS...")
if hasattr(filter, 'tokens') and 'FXS' in filter.tokens:
    fxs_info = filter.tokens['FXS']
    print(f"  找到 FXS: {fxs_info}")
else:
    print(f"  ❌ 未找到 FXS 在代币列表中")

print("\n6. 检查合约映射...")
contract_lower = FXS_CONTRACT.lower()
if hasattr(filter, 'contract_map') and contract_lower in filter.contract_map:
    symbol = filter.contract_map[contract_lower]
    print(f"  ✅ 合约 {FXS_CONTRACT} 映射到符号: {symbol}")
else:
    print(f"  ❌ 合约 {FXS_CONTRACT} 不在映射表中")

print("\n" + "=" * 60)
print("结论:")
if is_listed:
    print("✅ FXS 已在币安上架，过滤器工作正常")
    print("   问题可能在于:")
    print("   1. 过滤器未被正确初始化")
    print("   2. 过滤器在监听器中被禁用")
else:
    print("❌ 过滤器未识别 FXS 为已上架代币")
    print("   可能原因:")
    print("   1. CoinGecko 未收录 FXS 的以太坊合约地址")
    print("   2. FXS 符号在币安是不同的（如 FXSUSDT vs FXS）")
    print("   3. 缓存数据过期或损坏")
    print("\n   建议:")
    print("   - 删除 binance_tokens_cache.json 强制刷新")
    print("   - 检查 CoinGecko API 返回的 FXS 数据")
print("=" * 60)
