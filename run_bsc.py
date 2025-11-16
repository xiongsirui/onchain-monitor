#!/usr/bin/env python3
"""
BSC 快速启动脚本

这是最简单的启动方式，直接监听 BSC 链
优势：
- BSC 出块速度快（3秒）
- 币安官方 RPC 免费且稳定
- 无需 API Key
"""

from multichain_listener import MultiChainListener
import sys

def main():
    print("""
╔════════════════════════════════════════════════════════════════════════════╗
║                    BSC 链新币监听器 - 快速启动                            ║
╚════════════════════════════════════════════════════════════════════════════╝

优势：
✅ BSC 出块速度快（3秒），检测速度快 ⚡
✅ 币安官方 RPC 免费且稳定
✅ 更多新代币首先在 BSC 测试
✅ 无需 API Key

配置：
- RPC: https://bsc-dataseed.binance.org/ (币安官方)
- 监控钱包: 4 个 Binance BSC 热钱包
- 轮询间隔: 3 秒
- 过滤器: 启用（自动过滤 600+ 已上架代币）

════════════════════════════════════════════════════════════════════════════
    """)

    # 询问是否需要代理
    use_proxy = input("是否需要使用代理？(y/n, 默认 n): ").strip().lower()
    proxy = None

    if use_proxy == 'y':
        proxy = input("请输入代理地址 (例如: 127.0.0.1:7897): ").strip()
        if not proxy:
            proxy = '127.0.0.1:7897'
            print(f"使用默认代理: {proxy}")

    print("\n开始初始化监听器...\n")

    try:
        # 创建多链监听器
        listener = MultiChainListener(
            enable_filter=True,
            proxy=proxy
        )

        # 添加 BSC 监听器
        listener.add_bsc_listener(
            rpc_url='https://bsc-dataseed.binance.org/',
            proxy=proxy
        )

        print("\n" + "="*80)
        print("🚀 BSC 监听器已启动！")
        print("="*80)
        print()
        print("说明:")
        print("  • 程序将持续监听 BSC 链上的新代币充值")
        print("  • 检测到高置信度新代币时会发出告警")
        print("  • 按 Ctrl+C 可以停止监听并查看统计报告")
        print()
        print("="*80 + "\n")

        # 启动监听
        listener.listeners['BSC'].listen(poll_interval=3)

    except KeyboardInterrupt:
        print("\n\n⏹️  监听已停止")
        print("\n正在生成统计报告...\n")

        # 显示统计报告
        if 'BSC' in listener.listeners:
            bsc_listener = listener.listeners['BSC']
            stats = bsc_listener.stats

            print("="*80)
            print("📊 BSC 监听统计报告")
            print("="*80)
            print(f"总转账事件: {stats['total_transfers']}")
            print(f"已过滤代币: {stats['filtered_tokens']} (币安已上架)")
            print(f"新发现代币: {stats['new_tokens']} ⭐")
            print(f"高置信度代币: {stats['high_confidence_tokens']} 🔥")

            # 显示新代币列表
            new_tokens = [(c, b) for c, b in bsc_listener.new_tokens_buffer.items()
                         if b.get('is_new', True)]

            if new_tokens:
                print(f"\n{'─'*80}")
                print(f"🚨 未上架新代币详细列表 - {len(new_tokens)} 个")
                print(f"{'─'*80}\n")

                # 按置信度排序
                new_tokens.sort(
                    key=lambda x: x[1].get('analysis', {}).get('confidence', 0),
                    reverse=True
                )

                for contract, buffer in new_tokens[:10]:  # 最多显示 10 个
                    token_info = bsc_listener.known_tokens.get(contract, {})
                    symbol = token_info.get('symbol', 'UNKNOWN')
                    name = token_info.get('name', 'Unknown Token')
                    analysis = buffer.get('analysis')

                    print(f"🪙 {symbol} ({name})")
                    print(f"   合约: {contract}")
                    print(f"   转账数: {len(buffer['transfers'])} 笔")
                    print(f"   发送者: {len(buffer['senders'])} 个")

                    if analysis:
                        confidence = analysis['confidence']
                        confidence_bar = "█" * int(confidence * 10)
                        print(f"   置信度: {confidence_bar} {confidence:.2%}")
                        print(f"   风险等级: {analysis['risk_level'].upper()}")
                        print(f"   {analysis['recommendation']}")
                    else:
                        print(f"   状态: 等待更多数据...")
                    print()
            else:
                print("\n📭 暂无未上架新代币检测")

            print("="*80)

        print("\n✅ 程序已安全退出\n")
        sys.exit(0)

    except Exception as e:
        print(f"\n❌ 错误: {e}")
        print("\n常见问题排查:")
        print("  1. 检查网络连接是否正常")
        print("  2. 如果在国内，尝试使用代理")
        print("  3. 确认已安装所有依赖: pip install -r requirements.txt")
        print()
        sys.exit(1)


if __name__ == '__main__':
    main()
