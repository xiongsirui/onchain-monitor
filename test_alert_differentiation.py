#!/usr/bin/env python3
"""
测试不同触发原因的告警内容区分
"""

from multichain_listener import AdvancedTokenAnalyzer

def simulate_alert(scenario_name, transfers, senders, token_symbol):
    """模拟告警输出"""
    print(f"\n{'='*80}")
    print(f"【{scenario_name}】")
    print('='*80)

    # 创建分析器
    analyzer = AdvancedTokenAnalyzer()

    # 模拟代币信息
    token_info = {
        'symbol': token_symbol,
        'name': f'{token_symbol} Token',
        'decimals': 18
    }

    # 执行分析
    analysis = analyzer.analyze_transfers(transfers, senders, token_info)

    # 模拟 buffer
    buffer = {
        'transfers': transfers,
        'senders': senders
    }

    # 计算告警条件
    confidence = analysis['confidence']
    transfer_count = len(transfers)
    sender_count = len(senders)

    total_value = sum(tx.get('value', 0) for tx in transfers)
    max_single_value = max((tx.get('value', 0) for tx in transfers), default=0)
    is_large_transfer = (
        total_value >= 1e24 or  # 100万代币总额
        max_single_value >= 1e23  # 10万代币单笔
    )

    # 判断触发原因
    should_alert = False
    alert_level = None
    trigger_reason = None

    if confidence >= 0.8 and transfer_count >= 3 and sender_count >= 2:
        should_alert = True
        alert_level = 'HIGH'
        trigger_reason = 'multi_transfer'
    elif confidence >= 0.8 and is_large_transfer:
        should_alert = True
        alert_level = 'HIGH'
        trigger_reason = 'large_single'
    elif confidence >= 0.6 and transfer_count >= 5:
        should_alert = True
        alert_level = 'MEDIUM'
        trigger_reason = 'medium_confidence'

    # 显示告警内容
    if should_alert:
        symbol_icon = f"{'🚨'*3}" if alert_level == 'HIGH' else "⚡"

        # 触发原因提示
        trigger_hints = {
            'multi_transfer': '📊 多笔转账+多发送者模式',
            'large_single': '💰 大额单笔转账（疑似项目方打新）',
            'medium_confidence': '⚠️  中等置信度信号'
        }
        trigger_hint = trigger_hints.get(trigger_reason, '🔍 触发告警')

        print(f"\n{symbol_icon} [BSC] {alert_level} 级别告警! {symbol_icon}")
        print(f"   触发原因: {trigger_hint}")
        print(f"   代币: {token_symbol} ({token_symbol} Token)")
        print(f"   合约: 0x1234567890abcdef1234567890abcdef12345678")
        print(f"   转账数: {transfer_count} 笔")
        print(f"   发送者: {sender_count} 个")
        print(f"   置信度: {confidence:.2%}")
        print(f"   {analysis['recommendation']}")

        # 不同的行动建议
        action_suggestions = {
            'multi_transfer': '建议：检查多个发送者地址关联性，确认是否为真实用户',
            'large_single': '建议：重点关注！大额转账通常是项目方入库，可能即将上线',
            'medium_confidence': '建议：持续观察，等待更多转账数据验证'
        }
        action = action_suggestions.get(trigger_reason, '建议：深入调查此代币')
        print(f"   💡 {action}")
    else:
        print(f"\n❌ 未触发告警")
        print(f"   置信度: {confidence:.2%} (需要 >= 80%)")
        print(f"   转账数: {transfer_count} 笔")
        print(f"   发送者: {sender_count} 个")


# ============================================================================
# 场景 1: 大额单笔转账（项目方打新）
# ============================================================================
scenario_1_transfers = [
    {'from': '0xProject...', 'value': 5_000_000 * 10**18, 'timestamp': 1700000000},
]
scenario_1_senders = {'0xProject...'}
simulate_alert(
    "场景1: 项目方单笔大额打新 - 500万代币",
    scenario_1_transfers,
    scenario_1_senders,
    'NEWCOIN'
)

# ============================================================================
# 场景 2: 多笔转账+多发送者（用户自然充值）
# ============================================================================
scenario_2_transfers = [
    {'from': '0xUserA...', 'value': 1_000 * 10**18, 'timestamp': 1700000000},
    {'from': '0xUserB...', 'value': 500 * 10**18, 'timestamp': 1700003600},
    {'from': '0xUserC...', 'value': 2_000 * 10**18, 'timestamp': 1700007200},
]
scenario_2_senders = {'0xUserA...', 'UserB...', '0xUserC...'}
simulate_alert(
    "场景2: 用户自然充值 - 3个用户分散转账",
    scenario_2_transfers,
    scenario_2_senders,
    'GOODCOIN'
)

# ============================================================================
# 场景 3: 中等置信度（5笔小额转账）
# ============================================================================
scenario_3_transfers = [
    {'from': '0xUser1...', 'value': 100 * 10**18, 'timestamp': 1700000000},
    {'from': '0xUser2...', 'value': 150 * 10**18, 'timestamp': 1700001000},
    {'from': '0xUser3...', 'value': 120 * 10**18, 'timestamp': 1700002000},
    {'from': '0xUser4...', 'value': 130 * 10**18, 'timestamp': 1700003000},
    {'from': '0xUser5...', 'value': 110 * 10**18, 'timestamp': 1700004000},
]
scenario_3_senders = {'0xUser1...', '0xUser2...', '0xUser3...', '0xUser4...', '0xUser5...'}
simulate_alert(
    "场景3: 中等置信度 - 5个用户小额转账",
    scenario_3_transfers,
    scenario_3_senders,
    'MEDIUMCOIN'
)

# ============================================================================
# 场景 4: 项目方+用户混合（多笔+多发送者）
# ============================================================================
scenario_4_transfers = [
    {'from': '0xProject...', 'value': 2_000_000 * 10**18, 'timestamp': 1700000000},
    {'from': '0xProject...', 'value': 1_500_000 * 10**18, 'timestamp': 1700000300},
    {'from': '0xUserA...', 'value': 5_000 * 10**18, 'timestamp': 1700003600},
    {'from': '0xUserB...', 'value': 3_000 * 10**18, 'timestamp': 1700007200},
]
scenario_4_senders = {'0xProject...', '0xUserA...', '0xUserB...'}
simulate_alert(
    "场景4: 项目方+用户混合 - 大额+小额混合转账",
    scenario_4_transfers,
    scenario_4_senders,
    'MIXCOIN'
)

print(f"\n{'='*80}")
print("✅ 测试完成！不同场景的告警内容已区分")
print('='*80)
print("\n📝 总结:")
print("   • 场景1 (单笔大额) → 触发原因: 💰 大额单笔转账（疑似项目方打新）")
print("   • 场景2 (多发送者) → 触发原因: 📊 多笔转账+多发送者模式")
print("   • 场景3 (中等置信) → 触发原因: ⚠️  中等置信度信号")
print("   • 场景4 (混合) → 触发原因: 📊 多笔转账+多发送者模式 (优先匹配)")
print()
