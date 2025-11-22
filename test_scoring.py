#!/usr/bin/env python3
"""
测试新的评分逻辑 - 验证项目方打新场景
"""

from multichain_listener import AdvancedTokenAnalyzer

# 创建分析器
analyzer = AdvancedTokenAnalyzer()

print("="*80)
print("测试新的评分逻辑 - 项目方打新场景")
print("="*80)

# 场景1: 项目方大额单发送者转账（应该高分）
print("\n【场景1: 项目方大额单发送者转账】")
transfers_1 = [
    {'from': '0xProjectTeam...', 'value': 5_000_000 * 10**18, 'timestamp': 1700000000},  # 500万代币
    {'from': '0xProjectTeam...', 'value': 3_000_000 * 10**18, 'timestamp': 1700000300},  # 300万代币，5分钟后
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

# 场景2: 小额女巫攻击（应该低分）
print("\n" + "="*80)
print("【场景2: 小额女巫攻击（5个地址，相同金额，30秒内）】")
transfers_2 = [
    {'from': '0xSybil1...', 'value': 100 * 10**18, 'timestamp': 1700000000},
    {'from': '0xSybil2...', 'value': 100 * 10**18, 'timestamp': 1700000010},
    {'from': '0xSybil3...', 'value': 100 * 10**18, 'timestamp': 1700000020},
    {'from': '0xSybil4...', 'value': 100 * 10**18, 'timestamp': 1700000025},
    {'from': '0xSybil5...', 'value': 100 * 10**18, 'timestamp': 1700000030},
]
senders_2 = {'0xSybil1...', '0xSybil2...', '0xSybil3...', '0xSybil4...', '0xSybil5...'}
token_info_2 = {'symbol': 'SCAMCOIN', 'decimals': 18}

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

# 场景3: 用户自然充值（多发送者，金额分散，应该高分）
print("\n" + "="*80)
print("【场景3: 用户自然充值（3个用户，不同金额，跨度2小时）】")
transfers_3 = [
    {'from': '0xUserA...', 'value': 1_000 * 10**18, 'timestamp': 1700000000},
    {'from': '0xUserB...', 'value': 500 * 10**18, 'timestamp': 1700003600},   # 1小时后
    {'from': '0xUserC...', 'value': 2_000 * 10**18, 'timestamp': 1700007200},  # 2小时后
]
senders_3 = {'0xUserA...', '0xUserB...', '0xUserC...'}
token_info_3 = {'symbol': 'GOODCOIN', 'decimals': 18}

analysis_3 = analyzer.analyze_transfers(transfers_3, senders_3, token_info_3)
print(f"置信度: {analysis_3['confidence']:.2%}")
print(f"风险等级: {analysis_3['risk_level']}")
print(f"建议: {analysis_3['recommendation']}")
print(f"发现的模式:")
for pattern in analysis_3['patterns']:
    print(f"  ✅ {pattern}")
if analysis_3['warnings']:
    print(f"警告:")
    for warning in analysis_3['warnings']:
        print(f"  ⚠️  {warning}")

print("\n" + "="*80)
print("测试完成！")
print("="*80)
