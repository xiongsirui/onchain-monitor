#!/usr/bin/env python3
"""
测试单笔大额转账告警 - 验证项目方单笔打新场景
"""

from multichain_listener import AdvancedTokenAnalyzer

# 创建分析器
analyzer = AdvancedTokenAnalyzer()

print("="*80)
print("测试单笔大额转账告警 - 项目方单笔打新场景")
print("="*80)

# 场景1: 项目方单笔大额转账（10万代币）
print("\n【场景1: 项目方单笔大额转账 - 10万代币】")
transfers_1 = [
    {'from': '0xProjectTeam...', 'value': 100_000 * 10**18, 'timestamp': 1700000000},  # 10万代币
]
senders_1 = {'0xProjectTeam...'}
token_info_1 = {'symbol': 'NEWCOIN', 'decimals': 18}

analysis_1 = analyzer.analyze_transfers(transfers_1, senders_1, token_info_1)
print(f"置信度: {analysis_1['confidence']:.2%}")
print(f"风险等级: {analysis_1['risk_level']}")
print(f"建议: {analysis_1['recommendation']}")
print(f"发现的模式:")
for pattern in analysis_1['patterns']:
    print(f"  ✅ {pattern}")
if analysis_1['warnings']:
    print(f"警告:")
    for warning in analysis_1['warnings']:
        print(f"  ⚠️  {warning}")

# 检查告警条件
confidence = analysis_1['confidence']
transfer_count = len(transfers_1)
sender_count = len(senders_1)
max_single_value = max((tx.get('value', 0) for tx in transfers_1), default=0)
is_large_transfer = max_single_value >= 1e23

print(f"\n📊 告警条件检查:")
print(f"   置信度: {confidence:.2%} (需要 >= 80%)")
print(f"   转账数: {transfer_count} 笔")
print(f"   发送者: {sender_count} 个")
print(f"   是否大额: {'✅ 是' if is_large_transfer else '❌ 否'} (单笔 >= 10万代币)")

# 判断是否触发告警
should_alert_high = False
if confidence >= 0.8 and transfer_count >= 3 and sender_count >= 2:
    should_alert_high = True
    print(f"\n✅ 触发 HIGH 告警 (原有逻辑)")
elif confidence >= 0.8 and is_large_transfer:
    should_alert_high = True
    print(f"\n✅ 触发 HIGH 告警 (大额单笔逻辑)")
else:
    print(f"\n❌ 未触发告警")

if should_alert_high:
    print(f"   🚨🚨🚨 HIGH 级别告警!")
    print(f"   代币: NEWCOIN")
    print(f"   转账数: {transfer_count} 笔")
    print(f"   发送者: {sender_count} 个")
    print(f"   置信度: {confidence:.2%}")
    print(f"   立即行动建议: 深入调查此代币！")

# 场景2: 项目方超大额单笔转账（500万代币）
print("\n" + "="*80)
print("【场景2: 项目方超大额单笔转账 - 500万代币】")
transfers_2 = [
    {'from': '0xProjectTeam...', 'value': 5_000_000 * 10**18, 'timestamp': 1700000000},  # 500万代币
]
senders_2 = {'0xProjectTeam...'}
token_info_2 = {'symbol': 'MEGACOIN', 'decimals': 18}

analysis_2 = analyzer.analyze_transfers(transfers_2, senders_2, token_info_2)
print(f"置信度: {analysis_2['confidence']:.2%}")
print(f"风险等级: {analysis_2['risk_level']}")
print(f"建议: {analysis_2['recommendation']}")
print(f"发现的模式:")
for pattern in analysis_2['patterns']:
    print(f"  ✅ {pattern}")
if analysis_2['warnings']:
    print(f"警告:")
    for warning in analysis_2['warnings']:
        print(f"  ⚠️  {warning}")

confidence_2 = analysis_2['confidence']
max_single_value_2 = max((tx.get('value', 0) for tx in transfers_2), default=0)
is_large_transfer_2 = max_single_value_2 >= 1e23

print(f"\n📊 告警条件检查:")
print(f"   置信度: {confidence_2:.2%} (需要 >= 80%)")
print(f"   转账数: {len(transfers_2)} 笔")
print(f"   发送者: {len(senders_2)} 个")
print(f"   是否大额: {'✅ 是' if is_large_transfer_2 else '❌ 否'} (单笔 >= 10万代币)")

if confidence_2 >= 0.8 and is_large_transfer_2:
    print(f"\n✅ 触发 HIGH 告警 (大额单笔逻辑)")
    print(f"   🚨🚨🚨 HIGH 级别告警!")
    print(f"   代币: MEGACOIN")
    print(f"   转账数: {len(transfers_2)} 笔")
    print(f"   发送者: {len(senders_2)} 个")
    print(f"   置信度: {confidence_2:.2%}")
    print(f"   立即行动建议: 深入调查此代币！")
else:
    print(f"\n❌ 未触发告警")

# 场景3: 小额单笔转账（不应该触发告警）
print("\n" + "="*80)
print("【场景3: 小额单笔转账 - 100代币 (不应触发)】")
transfers_3 = [
    {'from': '0xUser...', 'value': 100 * 10**18, 'timestamp': 1700000000},  # 100代币
]
senders_3 = {'0xUser...'}
token_info_3 = {'symbol': 'SMALLCOIN', 'decimals': 18}

analysis_3 = analyzer.analyze_transfers(transfers_3, senders_3, token_info_3)
print(f"置信度: {analysis_3['confidence']:.2%}")
print(f"风险等级: {analysis_3['risk_level']}")

confidence_3 = analysis_3['confidence']
max_single_value_3 = max((tx.get('value', 0) for tx in transfers_3), default=0)
is_large_transfer_3 = max_single_value_3 >= 1e23

print(f"\n📊 告警条件检查:")
print(f"   置信度: {confidence_3:.2%} (需要 >= 80%)")
print(f"   转账数: {len(transfers_3)} 笔")
print(f"   发送者: {len(senders_3)} 个")
print(f"   是否大额: {'✅ 是' if is_large_transfer_3 else '❌ 否'} (单笔 >= 10万代币)")

if confidence_3 >= 0.8 and is_large_transfer_3:
    print(f"\n✅ 触发 HIGH 告警 (大额单笔逻辑)")
else:
    print(f"\n✅ 正确：未触发告警（小额转账不应触发）")

print("\n" + "="*80)
print("测试完成！")
print("="*80)
