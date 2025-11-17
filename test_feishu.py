#!/usr/bin/env python3
"""
飞书通知测试脚本

快速测试飞书通知功能是否正常工作
"""

import sys
import os


def test_feishu():
    """测试飞书通知"""
    print("="*80)
    print("飞书通知功能测试")
    print("="*80)
    print()

    # 检查 Webhook URL (从环境变量或 config.py 读取)
    webhook_url = os.environ.get('FEISHU_WEBHOOK_URL')

    # 尝试从配置文件读取
    if not webhook_url:
        try:
            import config
            webhook_url = config.webhook_url
        except (ImportError, AttributeError):
            pass

    if not webhook_url:
        print("❌ 未找到飞书 Webhook URL")
        print()
        print("请先设置环境变量:")
        print("  export FEISHU_WEBHOOK_URL='https://open.feishu.cn/open-apis/bot/v2/hook/YOUR_TOKEN'")
        print()
        print("获取 Webhook URL 步骤:")
        print("  1. 打开飞书群组")
        print("  2. 点击右上角 [...] → 群设置")
        print("  3. 群机器人 → 添加机器人 → 自定义机器人")
        print("  4. 复制 Webhook 地址")
        print()
        return False

    print(f"✅ Webhook URL 已设置")
    print(f"   {webhook_url[:50]}...")
    print()

    # 导入模块
    try:
        from feishu_notifier import FeishuNotifier
        print("✅ 飞书通知模块加载成功")
    except ImportError as e:
        print(f"❌ 飞书通知模块加载失败: {e}")
        print()
        print("请确保 feishu_notifier.py 文件存在")
        return False

    print()
    print("-"*80)
    print("测试 1: 发送简单测试消息")
    print("-"*80)
    print()

    # 创建通知器
    try:
        notifier = FeishuNotifier(webhook_url)
        print("✅ 飞书通知器创建成功")
    except Exception as e:
        print(f"❌ 飞书通知器创建失败: {e}")
        return False

    # 发送测试消息
    print("📤 正在发送测试消息...")
    success = notifier.send_test_message()

    if success:
        print("✅ 测试消息发送成功！")
        print("   请检查飞书群是否收到消息")
    else:
        print("❌ 测试消息发送失败")
        print()
        print("可能的原因:")
        print("  1. Webhook URL 不正确")
        print("  2. 网络连接问题")
        print("  3. 飞书机器人被禁用")
        return False

    print()
    print("-"*80)
    print("测试 2: 发送模拟告警消息")
    print("-"*80)
    print()

    # 模拟告警数据
    token_info = {
        'symbol': 'TEST',
        'name': 'Test Token',
        'decimals': 18
    }

    buffer = {
        'transfers': [{'value': 1000000}] * 5,
        'senders': {'0xabc123', '0xdef456', '0x789xyz'}
    }

    analysis = {
        'confidence': 0.85,
        'risk_level': 'low',
        'patterns': [
            '发现 5 笔转账',
            '3 个独立发送者',
            '所有转账在 2.5 小时内完成'
        ],
        'warnings': [],
        'recommendation': '🟢 强烈建议: 高置信度信号，多维度验证通过，建议重点关注'
    }

    print("📤 正在发送模拟 HIGH 级别告警...")
    success = notifier.send_token_alert(
        level='HIGH',
        chain='BSC',
        contract='0x1234567890abcdef1234567890abcdef12345678',
        token_info=token_info,
        buffer=buffer,
        analysis=analysis
    )

    if success:
        print("✅ 模拟告警发送成功！")
        print("   请检查飞书群是否收到告警卡片")
    else:
        print("❌ 模拟告警发送失败")
        return False

    print()
    print("="*80)
    print("🎉 所有测试通过！")
    print("="*80)
    print()
    print("下一步:")
    print("  运行 python3 run_feishu.py 启动实时监控")
    print()

    return True


if __name__ == '__main__':
    success = test_feishu()
    sys.exit(0 if success else 1)
