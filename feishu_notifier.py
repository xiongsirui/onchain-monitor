#!/usr/bin/env python3
"""
飞书机器人告警通知模块

功能:
- 支持飞书 Webhook 机器人
- 富文本卡片消息
- 告警级别颜色标识
- 重试机制
"""

import requests
import time
import json
from typing import Dict, Optional, List
from datetime import datetime


class FeishuNotifier:
    """飞书机器人通知器"""

    def __init__(self, webhook_url: str, proxy: Optional[str] = None):
        """
        初始化飞书通知器

        参数:
            webhook_url: 飞书机器人 Webhook URL
            proxy: 可选的代理服务器
        """
        self.webhook_url = webhook_url
        self.proxy = proxy
        self.session = requests.Session()

        if proxy:
            self.session.proxies = {
                'http': proxy if proxy.startswith('http') else f'http://{proxy}',
                'https': proxy if proxy.startswith('http') else f'http://{proxy}'
            }

    def send_token_alert(self, level: str, chain: str, contract: str,
                        token_info: Dict, buffer: Dict, analysis: Dict) -> bool:
        """
        发送新代币告警

        参数:
            level: 告警级别 (HIGH/MEDIUM)
            chain: 链名称 (ETH/BSC/SOL)
            contract: 合约地址
            token_info: 代币信息
            buffer: 转账缓冲区数据
            analysis: 分析结果

        返回:
            bool: 发送是否成功
        """
        # 构造富文本卡片消息
        card = self._build_alert_card(level, chain, contract, token_info, buffer, analysis)

        payload = {
            "msg_type": "interactive",
            "card": card
        }

        return self._send_message(payload)

    def _build_alert_card(self, level: str, chain: str, contract: str,
                          token_info: Dict, buffer: Dict, analysis: Dict) -> Dict:
        """构造告警卡片"""

        # 颜色映射
        color_map = {
            'HIGH': 'red',      # 红色 - 高优先级
            'MEDIUM': 'orange', # 橙色 - 中等优先级
            'LOW': 'blue'       # 蓝色 - 低优先级
        }
        color = color_map.get(level, 'grey')

        # 告警图标
        icon_map = {
            'HIGH': '🚨🚨🚨',
            'MEDIUM': '⚡',
            'LOW': 'ℹ️'
        }
        icon = icon_map.get(level, '📢')

        # 置信度评分
        confidence = analysis['confidence']
        confidence_bar = '█' * int(confidence * 10) + '▒' * (10 - int(confidence * 10))

        # 风险等级标签
        risk_labels = {
            'low': '🟢 低风险',
            'medium': '🟡 中等风险',
            'high': '🔴 高风险'
        }
        risk_label = risk_labels.get(analysis['risk_level'], analysis['risk_level'])

        # 构造卡片
        card = {
            "config": {
                "wide_screen_mode": True
            },
            "header": {
                "template": color,
                "title": {
                    "content": f"{icon} [{chain}] {level} 级别新代币告警",
                    "tag": "plain_text"
                }
            },
            "elements": [
                # 代币基本信息
                {
                    "tag": "div",
                    "fields": [
                        {
                            "is_short": True,
                            "text": {
                                "tag": "lark_md",
                                "content": f"**代币符号**\n{token_info.get('symbol', 'UNKNOWN')}"
                            }
                        },
                        {
                            "is_short": True,
                            "text": {
                                "tag": "lark_md",
                                "content": f"**代币名称**\n{token_info.get('name', 'Unknown Token')}"
                            }
                        },
                        {
                            "is_short": False,
                            "text": {
                                "tag": "lark_md",
                                "content": f"**合约地址**\n`{contract}`"
                            }
                        }
                    ]
                },
                # 分隔线
                {
                    "tag": "hr"
                },
                # 分析数据
                {
                    "tag": "div",
                    "fields": [
                        {
                            "is_short": True,
                            "text": {
                                "tag": "lark_md",
                                "content": f"**转账笔数**\n{len(buffer['transfers'])} 笔"
                            }
                        },
                        {
                            "is_short": True,
                            "text": {
                                "tag": "lark_md",
                                "content": f"**发送者数**\n{len(buffer['senders'])} 个"
                            }
                        },
                        {
                            "is_short": True,
                            "text": {
                                "tag": "lark_md",
                                "content": f"**置信度评分**\n{confidence:.1%} {confidence_bar}"
                            }
                        },
                        {
                            "is_short": True,
                            "text": {
                                "tag": "lark_md",
                                "content": f"**风险等级**\n{risk_label}"
                            }
                        }
                    ]
                },
                # 分隔线
                {
                    "tag": "hr"
                },
                # 分析结果
                {
                    "tag": "div",
                    "text": {
                        "tag": "lark_md",
                        "content": f"**📊 分析结果**\n{analysis['recommendation']}"
                    }
                }
            ]
        }

        # 添加发现的模式
        if analysis.get('patterns'):
            patterns_text = "\n".join([f"• {p}" for p in analysis['patterns'][:3]])
            card['elements'].append({
                "tag": "div",
                "text": {
                    "tag": "lark_md",
                    "content": f"**✅ 发现模式**\n{patterns_text}"
                }
            })

        # 添加警告信息
        if analysis.get('warnings'):
            warnings_text = "\n".join([f"• {w}" for w in analysis['warnings'][:3]])
            card['elements'].append({
                "tag": "div",
                "text": {
                    "tag": "lark_md",
                    "content": f"**⚠️ 警告信息**\n{warnings_text}"
                }
            })

        # 添加区块浏览器链接
        explorer_url = self._get_explorer_url(chain, contract)
        if explorer_url:
            card['elements'].extend([
                {
                    "tag": "hr"
                },
                {
                    "tag": "action",
                    "actions": [
                        {
                            "tag": "button",
                            "text": {
                                "tag": "plain_text",
                                "content": "查看合约详情"
                            },
                            "type": "default",
                            "url": explorer_url
                        }
                    ]
                }
            ])

        # 添加时间戳
        card['elements'].append({
            "tag": "note",
            "elements": [
                {
                    "tag": "plain_text",
                    "content": f"检测时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                }
            ]
        })

        return card

    def _get_explorer_url(self, chain: str, contract: str) -> Optional[str]:
        """获取区块浏览器URL"""
        explorers = {
            'ETH': f'https://etherscan.io/token/{contract}',
            'Ethereum': f'https://etherscan.io/token/{contract}',
            'BSC': f'https://bscscan.com/token/{contract}',
            'SOL': f'https://solscan.io/token/{contract}',
            'Solana': f'https://solscan.io/token/{contract}'
        }
        return explorers.get(chain)

    def _send_message(self, payload: Dict, retry: int = 3) -> bool:
        """
        发送消息到飞书

        参数:
            payload: 消息内容
            retry: 重试次数

        返回:
            bool: 是否发送成功
        """
        for attempt in range(retry):
            try:
                response = self.session.post(
                    self.webhook_url,
                    json=payload,
                    timeout=10
                )

                result = response.json()

                if result.get('code') == 0 or result.get('StatusCode') == 0:
                    print(f"✅ 飞书通知发送成功")
                    return True
                else:
                    error_msg = result.get('msg') or result.get('StatusMessage', 'Unknown error')
                    print(f"⚠️  飞书通知发送失败: {error_msg}")

                    if attempt < retry - 1:
                        time.sleep(1)
                        continue
                    return False

            except requests.exceptions.RequestException as e:
                print(f"⚠️  飞书通知网络错误 (尝试 {attempt + 1}/{retry}): {e}")
                if attempt < retry - 1:
                    time.sleep(2)
                    continue
                return False
            except Exception as e:
                print(f"❌ 飞书通知发送异常: {e}")
                return False

        return False

    def send_test_message(self) -> bool:
        """发送测试消息"""
        payload = {
            "msg_type": "interactive",
            "card": {
                "header": {
                    "template": "blue",
                    "title": {
                        "content": "🧪 飞书通知测试",
                        "tag": "plain_text"
                    }
                },
                "elements": [
                    {
                        "tag": "div",
                        "text": {
                            "tag": "lark_md",
                            "content": "**多链区块链监听器**\n飞书通知功能测试成功！✅"
                        }
                    },
                    {
                        "tag": "note",
                        "elements": [
                            {
                                "tag": "plain_text",
                                "content": f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                            }
                        ]
                    }
                ]
            }
        }

        return self._send_message(payload)


def test_feishu_notifier():
    """测试飞书通知功能"""
    print("飞书通知器测试")
    print("=" * 60)

    # 从环境变量或配置文件读取 Webhook URL
    import os
    webhook_url = os.environ.get('FEISHU_WEBHOOK_URL')

    if not webhook_url:
        print("❌ 请设置环境变量 FEISHU_WEBHOOK_URL")
        print("   export FEISHU_WEBHOOK_URL='https://open.feishu.cn/open-apis/bot/v2/hook/YOUR_TOKEN'")
        return

    # 创建通知器
    notifier = FeishuNotifier(webhook_url)

    # 发送测试消息
    print("\n📤 发送测试消息...")
    success = notifier.send_test_message()

    if success:
        print("✅ 测试成功！")

        # 模拟告警数据
        print("\n📤 发送模拟告警...")
        token_info = {
            'symbol': 'TEST',
            'name': 'Test Token',
            'decimals': 18
        }

        buffer = {
            'transfers': [{'value': 1000000}] * 5,
            'senders': {'0xabc', '0xdef', '0x123'}
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

        notifier.send_token_alert(
            level='HIGH',
            chain='BSC',
            contract='0x1234567890abcdef1234567890abcdef12345678',
            token_info=token_info,
            buffer=buffer,
            analysis=analysis
        )
    else:
        print("❌ 测试失败")


if __name__ == '__main__':
    test_feishu_notifier()
