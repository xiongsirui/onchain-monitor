#!/usr/bin/env python3
"""
币安新币上架监控 - 生产环境运行脚本

用法:
1. 编辑下方 RPC 配置
2. 运行: python3 run.py
3. 按 Ctrl+C 停止
"""

from onchain_listener_advanced import BlockchainListener
import sys


def main():
    print("""
╔════════════════════════════════════════════════════════════════════════════╗
║              币安新币上架监控系统 - 实时区块链监听                        ║
╚════════════════════════════════════════════════════════════════════════════╝
    """)

    # ========== 配置区域 ==========
    # RPC 节点配置（免费，无需注册）
    # 如果主节点失败，会自动尝试备用节点
    RPC_NODES = [
        "https://eth.llamarpc.com",      # LlamaRPC（推荐）
        "https://eth.llmamarpc.com",     # LlamaNodes
        "https://rpc.ankr.com/eth",      # Ankr
        "https://cloudflare-eth.com",    # Cloudflare
    ]

    # 代理配置（如果需要）
    # 支持格式:
    #   - "127.0.0.1:7897"               (会自动添加 http://)
    #   - "http://127.0.0.1:7897"        (完整格式)
    #   - "socks5://127.0.0.1:7891"      (SOCKS5 代理)
    PROXY = "127.0.0.1:7897"  # 如果不需要代理，设为 None

    # 可选配置
    ENABLE_FILTER = True                    # 是否过滤已上架代币（推荐开启）
    PERSISTENCE_FILE = "listener_state.pkl" # 持久化文件路径
    # ==============================

    print("⏳ 正在初始化监听器...")
    print(f"   - 代理设置: {PROXY if PROXY else '不使用代理'}")
    print(f"   - 监听模式: HTTP 轮询（2秒间隔）")
    print(f"   - 币安过滤器: {'启用' if ENABLE_FILTER else '禁用'}")
    print(f"   - 持久化文件: {PERSISTENCE_FILE}")
    print()

    # 尝试连接 RPC 节点（自动故障转移）
    listener = None
    for i, rpc_url in enumerate(RPC_NODES, 1):
        print(f"📡 尝试连接 RPC 节点 [{i}/{len(RPC_NODES)}]: {rpc_url}")
        try:
            # 创建监听器
            listener = BlockchainListener(
                rpc_url=rpc_url,
                ws_url=None,  # Web3.py v6+ 不支持同步 WebSocket
                enable_filter=ENABLE_FILTER,
                persistence_file=PERSISTENCE_FILE,
                proxy=PROXY  # 传入代理配置
            )
            # 如果成功创建，跳出循环
            print(f"✅ 成功连接: {rpc_url}\n")
            break
        except Exception as e:
            print(f"❌ 连接失败: {str(e)[:60]}")
            if i < len(RPC_NODES):
                print(f"   尝试下一个节点...\n")
            else:
                print("\n❌ 所有 RPC 节点均无法连接")
                print("\n建议:")
                print("  1. 运行测试脚本: python test_connection.py")
                print("  2. 检查代理是否正常工作")
                print("  3. 检查网络连接")
                sys.exit(1)

    if not listener:
        print("❌ 初始化失败")
        sys.exit(1)

    try:

        print("\n✅ 初始化完成！\n")
        print("功能说明:")
        print("  - HTTP 轮询监听（2秒间隔，性能优秀）")
        print("  - 实时监听 Binance 钱包地址")
        print("  - 自动过滤已上架代币（600+ 代币）")
        print("  - 女巫攻击检测")
        print("  - 多维度置信度评分")
        print("  - 智能分级告警 (HIGH/MEDIUM)")
        print("  - 自动数据持久化")
        print()
        print("="*80)
        print("🚀 开始监听... (按 Ctrl+C 停止并查看统计报告)")
        print("="*80)
        print()

        # 启动监听（内部使用 HTTP 轮询）
        listener.listen_with_websocket()

    except KeyboardInterrupt:
        print("\n\n" + "="*80)
        print("⏹️  监听已停止")
        print("="*80)

        # 显示统计报告
        try:
            report = listener.generate_report()
            print(report)
        except:
            pass

        print("\n✅ 程序已安全退出")
        sys.exit(0)

    except Exception as e:
        print(f"\n❌ 错误: {e}")
        print("\n常见问题:")
        print("  1. 检查 RPC URL 是否正确")
        print("  2. 检查网络连接")
        print("  3. 检查 Alchemy API Key 配额")
        sys.exit(1)


if __name__ == '__main__':
    main()
