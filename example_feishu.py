#!/usr/bin/env python3
"""
飞书通知示例 - 集成飞书机器人告警

使用方法:
1. 在飞书群组中创建自定义机器人
2. 获取 Webhook URL
3. 运行此脚本
"""

import os
from multichain_listener import MultiChainListener


def main():
    print("""
╔════════════════════════════════════════════════════════════════════════════╗
║              多链区块链监听器 - 飞书通知示例                              ║
╚════════════════════════════════════════════════════════════════════════════╝
""")

    # ========== 配置区域 ==========

    # 飞书 Webhook URL
    # 方式 1: 直接在代码中设置
    FEISHU_WEBHOOK_URL = None  # 替换为你的飞书 Webhook URL

    # 方式 2: 从环境变量读取（更安全）
    if not FEISHU_WEBHOOK_URL:
        FEISHU_WEBHOOK_URL = os.environ.get('FEISHU_WEBHOOK_URL')

    if not FEISHU_WEBHOOK_URL:
        print("❌ 请设置飞书 Webhook URL")
        print("\n方式 1: 在代码中设置")
        print("   FEISHU_WEBHOOK_URL = 'https://open.feishu.cn/open-apis/bot/v2/hook/YOUR_TOKEN'\n")
        print("方式 2: 设置环境变量")
        print("   export FEISHU_WEBHOOK_URL='https://open.feishu.cn/open-apis/bot/v2/hook/YOUR_TOKEN'\n")
        print("获取 Webhook URL 步骤:")
        print("   1. 打开飞书群组")
        print("   2. 点击右上角 [...] → 群设置")
        print("   3. 群机器人 → 添加机器人 → 自定义机器人")
        print("   4. 复制 Webhook 地址\n")
        return

    # RPC 配置
    BSC_RPC = "https://bsc-dataseed.binance.org/"  # BSC 免费 RPC

    # 代理配置（可选）
    PROXY = None  # 例如: "127.0.0.1:7897"

    # ==============================

    print("⏳ 初始化多链监听器（带飞书通知）...\n")

    # 创建监听器，传入飞书 Webhook URL
    listener = MultiChainListener(
        enable_filter=True,
        proxy=PROXY,
        feishu_webhook_url=FEISHU_WEBHOOK_URL  # 启用飞书通知
    )

    # 添加 BSC 监听器（最快，3秒出块）
    print("🔗 添加 BSC 链监听器...\n")
    listener.add_bsc_listener(rpc_url=BSC_RPC, proxy=PROXY)

    # 可选：添加更多链
    # listener.add_eth_listener(rpc_url='YOUR_ETH_RPC', proxy=PROXY)
    # listener.add_solana_listener(rpc_url='https://api.mainnet-beta.solana.com')

    print("="*80)
    print("🎉 监听器已启动！")
    print("="*80)
    print("✅ BSC 链监听已开启")
    print("✅ 币安代币过滤器已启用")
    print("✅ 飞书通知已启用")
    print("="*80)
    print("\n📱 当检测到新代币时，将自动发送飞书通知！\n")
    print("💡 提示: 按 Ctrl+C 停止监听\n")

    try:
        # 启动监听
        listener.listeners['BSC'].listen(poll_interval=3)

    except KeyboardInterrupt:
        print("\n\n" + "="*80)
        print("⏹️  监听已停止")
        print("="*80)

        # 显示统计报告
        try:
            report = listener.get_summary_report()
            print(report)
        except:
            pass

        print("\n✅ 程序已安全退出")


if __name__ == '__main__':
    main()
