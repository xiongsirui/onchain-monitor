#!/usr/bin/env python3
"""
多链监听示例

展示如何使用 MultiChainListener 同时监听 ETH、BSC、Solana 三条链
"""

from multichain_listener import MultiChainListener
import time


def example_single_chain():
    """
    示例 1: 单链监听 (ETH)
    """
    print("\n" + "="*80)
    print("示例 1: 单链监听 (以太坊)")
    print("="*80 + "\n")

    # 创建多链监听器
    listener = MultiChainListener(
        enable_filter=True,      # 启用币安代币过滤器
        proxy='127.0.0.1:7897'  # 使用代理（可选）
    )

    # 只添加 ETH 监听器
    # 免费 RPC: 可以使用 Alchemy, Infura, QuickNode 等
    listener.add_eth_listener(
        rpc_url='https://eth-mainnet.g.alchemy.com/v2/YOUR_API_KEY',
        proxy='127.0.0.1:7897'
    )

    # 启动监听（阻塞模式）
    listener.listeners['ETH'].listen(poll_interval=12)


def example_eth_bsc():
    """
    示例 2: ETH + BSC 双链监听
    """
    print("\n" + "="*80)
    print("示例 2: ETH + BSC 双链监听")
    print("="*80 + "\n")

    # 创建多链监听器
    listener = MultiChainListener(
        enable_filter=True,
        proxy='127.0.0.1:7897'
    )

    # 添加 ETH 监听器
    listener.add_eth_listener(
        rpc_url='https://eth-mainnet.g.alchemy.com/v2/YOUR_API_KEY',
        proxy='127.0.0.1:7897'
    )

    # 添加 BSC 监听器
    # BSC 免费 RPC: https://bsc-dataseed.binance.org/
    listener.add_bsc_listener(
        rpc_url='https://bsc-dataseed.binance.org/',
        proxy='127.0.0.1:7897'
    )

    # 启动所有链监听（多线程）
    listener.start_all(poll_intervals={
        'ETH': 12,  # 以太坊 12秒
        'BSC': 3,   # BSC 3秒
    })


def example_all_chains():
    """
    示例 3: ETH + BSC + Solana 三链监听
    """
    print("\n" + "="*80)
    print("示例 3: ETH + BSC + Solana 三链监听")
    print("="*80 + "\n")

    # 创建多链监听器
    listener = MultiChainListener(
        enable_filter=True,
        proxy='127.0.0.1:7897'
    )

    # 添加 ETH 监听器
    listener.add_eth_listener(
        rpc_url='https://eth-mainnet.g.alchemy.com/v2/YOUR_API_KEY',
        proxy='127.0.0.1:7897'
    )

    # 添加 BSC 监听器
    listener.add_bsc_listener(
        rpc_url='https://bsc-dataseed.binance.org/',
        proxy='127.0.0.1:7897'
    )

    # 添加 Solana 监听器
    # Solana 免费 RPC: https://api.mainnet-beta.solana.com
    listener.add_solana_listener(
        rpc_url='https://api.mainnet-beta.solana.com'
    )

    # 启动所有链监听（多线程）
    listener.start_all(poll_intervals={
        'ETH': 12,  # 以太坊 12秒
        'BSC': 3,   # BSC 3秒
        'SOL': 2,   # Solana 2秒
    })


def example_with_callback():
    """
    示例 4: 使用回调函数处理新代币
    """
    print("\n" + "="*80)
    print("示例 4: 使用回调函数处理新代币")
    print("="*80 + "\n")

    # 定义回调函数
    def on_new_token(transfer_data, tokens_buffer):
        """
        当检测到新代币时调用

        参数:
            transfer_data: 转账数据
            tokens_buffer: 所有已检测代币的缓冲区
        """
        contract = transfer_data['contract']
        buffer = tokens_buffer[contract]

        # 只处理新代币（未上架）
        if not buffer.get('is_new', True):
            return

        # 获取分析结果
        analysis = buffer.get('analysis')
        if analysis:
            confidence = analysis['confidence']

            # 高置信度告警
            if confidence >= 0.8:
                print(f"\n🚨 高置信度新代币! 置信度: {confidence:.2%}")
                print(f"   合约: {contract}")
                # TODO: 发送 Telegram 消息
                # TODO: 发送邮件通知
                # TODO: 记录到数据库

    # 创建监听器
    listener = MultiChainListener(enable_filter=True, proxy='127.0.0.1:7897')
    listener.add_eth_listener(
        rpc_url='https://eth-mainnet.g.alchemy.com/v2/YOUR_API_KEY',
        proxy='127.0.0.1:7897'
    )

    # 启动监听（带回调）
    listener.listeners['ETH'].listen(
        poll_interval=12,
        callback=on_new_token
    )


def example_periodic_report():
    """
    示例 5: 定期生成汇总报告
    """
    print("\n" + "="*80)
    print("示例 5: 定期生成汇总报告")
    print("="*80 + "\n")

    # 创建监听器
    listener = MultiChainListener(enable_filter=True, proxy='127.0.0.1:7897')
    listener.add_eth_listener(
        rpc_url='https://eth-mainnet.g.alchemy.com/v2/YOUR_API_KEY',
        proxy='127.0.0.1:7897'
    )
    listener.add_bsc_listener(
        rpc_url='https://bsc-dataseed.binance.org/',
        proxy='127.0.0.1:7897'
    )

    # 在后台启动监听
    import threading
    thread = threading.Thread(target=listener.start_all, daemon=True)
    thread.start()

    # 定期生成报告
    try:
        while True:
            time.sleep(300)  # 每 5 分钟
            report = listener.get_summary_report()
            print(report)

            # TODO: 保存报告到文件
            # TODO: 发送报告到 Telegram/邮件

    except KeyboardInterrupt:
        print("\n⏹️  已停止")


def example_bsc_only():
    """
    示例 6: 只监听 BSC 链
    """
    print("\n" + "="*80)
    print("示例 6: 只监听 BSC 链")
    print("="*80 + "\n")

    # 创建多链监听器
    listener = MultiChainListener(
        enable_filter=True,
        proxy='127.0.0.1:7897'
    )

    # 只添加 BSC 监听器
    # BSC 出块速度快（3秒），更容易捕获新代币
    listener.add_bsc_listener(
        rpc_url='https://bsc-dataseed.binance.org/',
        proxy='127.0.0.1:7897'
    )

    # 启动监听
    listener.listeners['BSC'].listen(poll_interval=3)


def main():
    print("""
╔════════════════════════════════════════════════════════════════════════════╗
║                      多链监听示例                                          ║
╚════════════════════════════════════════════════════════════════════════════╝

请选择示例:

1. 单链监听 (ETH)
2. ETH + BSC 双链监听 ⭐ 推荐
3. ETH + BSC + Solana 三链监听
4. 使用回调函数处理新代币
5. 定期生成汇总报告
6. 只监听 BSC 链 ⚡ 快速

注意事项:
- 需要配置 RPC 节点 URL (Alchemy, Infura, QuickNode 等)
- 如果网络受限，需要配置代理
- BSC 链出块速度快，推荐优先监听
- Solana 监听功能开发中

免费 RPC 节点:
- Ethereum: https://eth-mainnet.g.alchemy.com/v2/YOUR_API_KEY (Alchemy)
- BSC: https://bsc-dataseed.binance.org/ (Binance 官方)
- Solana: https://api.mainnet-beta.solana.com (Solana 官方)

╚════════════════════════════════════════════════════════════════════════════╝
    """)

    choice = input("请输入示例编号 (1-6): ").strip()

    if choice == '1':
        example_single_chain()
    elif choice == '2':
        example_eth_bsc()
    elif choice == '3':
        example_all_chains()
    elif choice == '4':
        example_with_callback()
    elif choice == '5':
        example_periodic_report()
    elif choice == '6':
        example_bsc_only()
    else:
        print("无效选择！")


if __name__ == '__main__':
    main()
