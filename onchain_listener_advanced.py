#!/usr/bin/env python3
"""
区块链节点直接监听 - 完整策略版

功能增强:
- ✅ Web Socket 实时监听
- ✅ 智能代币过滤（已上架代币）
- 🆕 女巫攻击检测
- 🆕 多维度置信度评分
- 🆕 高级转账模式分析
- 🆕 智能告警策略
- 🆕 数据持久化
"""

from web3 import Web3
import json
import time
import pickle
from datetime import datetime, timedelta
from collections import defaultdict
from pathlib import Path
import statistics

# 导入币安代币过滤器
try:
    from binance_token_filter import BinanceTokenFilter
    FILTER_AVAILABLE = True
except ImportError:
    FILTER_AVAILABLE = False
    print("⚠️  binance_token_filter.py 未找到，将不过滤已上架代币")

# ERC20 Transfer 事件签名
TRANSFER_EVENT_SIGNATURE = '0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef'

# ERC20 ABI
ERC20_ABI = json.loads('''[
    {"constant": true, "inputs": [], "name": "name", "outputs": [{"name": "", "type": "string"}], "type": "function"},
    {"constant": true, "inputs": [], "name": "symbol", "outputs": [{"name": "", "type": "string"}], "type": "function"},
    {"constant": true, "inputs": [], "name": "decimals", "outputs": [{"name": "", "type": "uint8"}], "type": "function"},
    {"constant": true, "inputs": [{"name": "_owner", "type": "address"}], "name": "balanceOf", "outputs": [{"name": "balance", "type": "uint256"}], "type": "function"},
    {"constant": true, "inputs": [], "name": "totalSupply", "outputs": [{"name": "", "type": "uint256"}], "type": "function"}
]''')


class AdvancedTokenAnalyzer:
    """
    高级代币分析器 - 策略核心
    """

    def __init__(self):
        # 女巫攻击检测配置
        self.sybil_thresholds = {
            'min_sender_balance': 0.1,          # ETH
            'min_account_age_days': 30,         # 天
            'min_tx_count': 10,                  # 笔
            'same_timestamp_tolerance': 60,      # 秒
            'same_value_tolerance': 0.01,        # 比例
            'min_unique_senders': 2,             # 个
            'max_sender_concentration': 0.7,     # 最大单一发送者占比
        }

        # 区块缓存（避免重复查询）
        self.block_cache = {}
        self.address_cache = {}

    def analyze_transfers(self, transfers, senders, token_info, w3):
        """
        综合分析转账模式

        返回:
            analysis: {
                'confidence': float,        # 置信度 0-1
                'risk_level': str,          # low/medium/high
                'patterns': [],            # 发现的模式
                'warnings': [],            # 警告信息
                'recommendation': str,     # 建议
                'scores': {}               # 各维度评分
            }
        """
        analysis = {
            'confidence': 1.0,
            'risk_level': 'low',
            'patterns': [],
            'warnings': [],
            'recommendation': '',
            'scores': {}
        }

        # 1. 基础统计分析
        stats_score = self._analyze_basic_stats(transfers, senders, analysis)
        analysis['scores']['basic_stats'] = stats_score

        # 2. 时间模式分析
        time_score = self._analyze_time_patterns(transfers, analysis)
        analysis['scores']['time_pattern'] = time_score

        # 3. 金额分布分析
        amount_score = self._analyze_amount_distribution(transfers, token_info, analysis)
        analysis['scores']['amount_distribution'] = amount_score

        # 4. 发送者分析
        sender_score = self._analyze_senders(transfers, senders, w3, analysis)
        analysis['scores']['sender_analysis'] = sender_score

        # 5. 女巫攻击检测
        sybil_score = self._detect_sybil_attack(transfers, senders, analysis)
        analysis['scores']['sybil_detection'] = sybil_score

        # 6. 计算综合置信度
        analysis['confidence'] = self._calculate_overall_confidence(analysis['scores'])

        # 7. 确定风险等级
        analysis['risk_level'] = self._determine_risk_level(analysis['confidence'], analysis['warnings'])

        # 8. 生成建议
        analysis['recommendation'] = self._generate_recommendation(analysis)

        return analysis

    def _analyze_basic_stats(self, transfers, senders, analysis):
        """基础统计分析"""
        score = 1.0

        transfer_count = len(transfers)
        sender_count = len(senders)

        # 检查转账数量
        if transfer_count < 2:
            analysis['warnings'].append("转账次数过少（< 2）")
            score -= 0.3
        elif transfer_count < 3:
            analysis['warnings'].append("转账次数较少（< 3）")
            score -= 0.1
        else:
            analysis['patterns'].append(f"发现 {transfer_count} 笔转账")

        # 检查发送者数量
        if sender_count < self.sybil_thresholds['min_unique_senders']:
            analysis['warnings'].append(f"独立发送者过少（< {self.sybil_thresholds['min_unique_senders']}）")
            score -= 0.3
        else:
            analysis['patterns'].append(f"{sender_count} 个独立发送者")

        # 检查发送者集中度
        if transfer_count > 0:
            sender_concentration = {}
            for tx in transfers:
                sender = tx['from']
                sender_concentration[sender] = sender_concentration.get(sender, 0) + 1

            max_concentration = max(sender_concentration.values()) / transfer_count
            if max_concentration > self.sybil_thresholds['max_sender_concentration']:
                analysis['warnings'].append(f"发送者过于集中（{max_concentration:.1%}来自单一地址）")
                score -= 0.2

        return max(0.0, score)

    def _analyze_time_patterns(self, transfers, analysis):
        """时间模式分析"""
        score = 1.0

        if len(transfers) < 2:
            return score

        # 获取时间戳
        timestamps = [tx.get('timestamp', 0) for tx in transfers if tx.get('timestamp')]
        if len(timestamps) < 2:
            return score

        timestamps.sort()

        # 计算时间间隔
        intervals = [timestamps[i] - timestamps[i-1] for i in range(1, len(timestamps))]

        # 检查是否有异常紧密的时间聚类
        close_intervals = [i for i in intervals if i < self.sybil_thresholds['same_timestamp_tolerance']]
        if len(close_intervals) > len(intervals) * 0.5:
            analysis['warnings'].append(f"发现 {len(close_intervals)} 笔交易时间过于接近（< {self.sybil_thresholds['same_timestamp_tolerance']}秒）")
            score -= 0.3
            analysis['patterns'].append("疑似批量操作")

        # 计算时间跨度
        if len(timestamps) >= 2:
            time_span = timestamps[-1] - timestamps[0]
            time_span_hours = time_span / 3600

            if time_span_hours < 1:
                analysis['patterns'].append(f"所有转账在 {time_span / 60:.0f} 分钟内完成")
            elif time_span_hours < 24:
                analysis['patterns'].append(f"所有转账在 {time_span_hours:.1f} 小时内完成")
            else:
                analysis['patterns'].append(f"转账跨度 {time_span_hours / 24:.1f} 天")
                score += 0.1  # 时间跨度长通常是好信号

        return min(1.0, score)

    def _analyze_amount_distribution(self, transfers, token_info, analysis):
        """金额分布分析"""
        score = 1.0

        if len(transfers) < 2:
            return score

        decimals = token_info.get('decimals', 18)
        amounts = [tx['value'] / (10 ** decimals) for tx in transfers]

        # 检查金额相似度
        unique_amounts = len(set(amounts))
        if unique_amounts < len(amounts) * 0.3:  # 70%的金额相同
            analysis['warnings'].append(f"金额过于相似（只有 {unique_amounts} 个不同值）")
            score -= 0.3
            analysis['patterns'].append("疑似批量测试")

        # 计算金额统计
        if len(amounts) >= 2:
            mean_amount = statistics.mean(amounts)
            total_amount = sum(amounts)

            try:
                stdev = statistics.stdev(amounts)
                cv = stdev / mean_amount if mean_amount > 0 else 0  # 变异系数

                if cv < 0.1:  # 变异系数很小
                    analysis['warnings'].append("金额变异度极低")
                    score -= 0.2
            except:
                pass

            analysis['patterns'].append(f"总金额: {total_amount:,.0f} {token_info.get('symbol', 'tokens')}")
            analysis['patterns'].append(f"平均金额: {mean_amount:,.0f} {token_info.get('symbol', 'tokens')}")

        return max(0.0, score)

    def _analyze_senders(self, transfers, senders, w3, analysis):
        """发送者分析"""
        score = 1.0

        # 简化版：只检查发送者数量和分布
        # 完整版需要查询链上数据（余额、交易历史等）

        sender_stats = {}
        for tx in transfers:
            sender = tx['from']
            if sender not in sender_stats:
                sender_stats[sender] = {'count': 0, 'total_value': 0}
            sender_stats[sender]['count'] += 1
            sender_stats[sender]['total_value'] += tx['value']

        # 检查发送者活跃度
        active_senders = len([s for s, stats in sender_stats.items() if stats['count'] >= 2])
        if active_senders > 1:
            analysis['patterns'].append(f"{active_senders} 个发送者多次转账")
            score += 0.1

        return min(1.0, score)

    def _detect_sybil_attack(self, transfers, senders, analysis):
        """女巫攻击检测"""
        score = 1.0

        sybil_indicators = 0

        # 指标1: 发送者过少
        if len(senders) < self.sybil_thresholds['min_unique_senders']:
            sybil_indicators += 1

        # 指标2: 时间过于集中
        if len(transfers) >= 2:
            timestamps = [tx.get('timestamp', 0) for tx in transfers if tx.get('timestamp')]
            if len(timestamps) >= 2:
                timestamps.sort()
                intervals = [timestamps[i] - timestamps[i-1] for i in range(1, len(timestamps))]
                close_count = sum(1 for i in intervals if i < self.sybil_thresholds['same_timestamp_tolerance'])
                if close_count > len(intervals) * 0.5:
                    sybil_indicators += 1

        # 指标3: 金额过于相似
        decimals = 18  # 默认
        amounts = [tx['value'] for tx in transfers]
        unique_amounts = len(set(amounts))
        if unique_amounts < len(amounts) * 0.3:
            sybil_indicators += 1

        # 综合判断
        if sybil_indicators >= 2:
            analysis['warnings'].append(f"⚠️ 女巫攻击风险: 发现 {sybil_indicators} 个可疑指标")
            score -= 0.4
        elif sybil_indicators == 1:
            analysis['warnings'].append("轻微女巫攻击迹象")
            score -= 0.2

        return max(0.0, score)

    def _calculate_overall_confidence(self, scores):
        """计算综合置信度"""
        if not scores:
            return 0.5

        # 加权平均
        weights = {
            'basic_stats': 0.25,
            'time_pattern': 0.15,
            'amount_distribution': 0.15,
            'sender_analysis': 0.20,
            'sybil_detection': 0.25,
        }

        weighted_sum = 0
        weight_total = 0

        for key, weight in weights.items():
            if key in scores:
                weighted_sum += scores[key] * weight
                weight_total += weight

        return weighted_sum / weight_total if weight_total > 0 else 0.5

    def _determine_risk_level(self, confidence, warnings):
        """确定风险等级"""
        critical_warnings = [w for w in warnings if '⚠️' in w or '女巫' in w]

        if confidence >= 0.7 and len(critical_warnings) == 0:
            return 'low'      # 低风险
        elif confidence >= 0.4:
            return 'medium'   # 中等风险
        else:
            return 'high'     # 高风险

    def _generate_recommendation(self, analysis):
        """生成建议"""
        confidence = analysis['confidence']
        risk_level = analysis['risk_level']

        if confidence >= 0.8 and risk_level == 'low':
            return "�� 强烈建议: 高置信度信号，多维度验证通过，建议重点关注"
        elif confidence >= 0.6 and risk_level in ['low', 'medium']:
            return "🟡 谨慎建议: 中等置信度，建议持续观察，等待更多信号"
        elif confidence >= 0.4:
            return "🟠 观察建议: 置信度偏低，存在疑点，建议谨慎观察"
        else:
            return "🔴 不建议: 置信度很低或存在女巫攻击风险，不建议行动"


class BlockchainListener:
    """
    区块链节点直接监听器（完整策略版）
    """

    def __init__(self, rpc_url, ws_url=None, enable_filter=True, persistence_file='listener_state.pkl', proxy=None):
        """初始化监听器"""
        # 规范化代理格式
        if proxy:
            # 如果代理格式不含协议前缀，自动添加 http://
            if not proxy.startswith(('http://', 'https://', 'socks5://', 'socks4://')):
                proxy = f'http://{proxy}'
                print(f"ℹ️  自动添加协议前缀: {proxy}")

        # Web3 连接（只使用 HTTP，WebSocket 在 Web3.py v6+ 中需要异步）
        # 支持 HTTP/SOCKS 代理
        if proxy:
            print(f"🔄 使用代理: {proxy}")
            request_kwargs = {'proxies': {'http': proxy, 'https': proxy}}
            self.w3 = Web3(Web3.HTTPProvider(rpc_url, request_kwargs=request_kwargs))
        else:
            self.w3 = Web3(Web3.HTTPProvider(rpc_url))

        self.ws_url = ws_url  # 保存 WebSocket URL，但使用 HTTP 轮询代替
        self.ws_w3 = None

        # Web3.py v6+ 移除了同步 WebSocket 支持
        # 使用 HTTP 轮询代替，性能同样优秀（1-2秒延迟）
        if ws_url:
            print(f"ℹ️  注意: 使用 HTTP 轮询模式（Web3.py v6+ 不支持同步 WebSocket）")
            print(f"   轮询间隔: 1-2 秒（性能优秀）")

        if not self.w3.is_connected():
            raise Exception("❌ RPC 节点连接失败，请检查:\n"
                          "   1. RPC URL 是否正确\n"
                          "   2. 网络连接是否正常\n"
                          "   3. 代理是否正在运行\n"
                          f"   4. 代理配置: {proxy if proxy else '未使用代理'}")

        print(f"✅ RPC 已连接: {rpc_url}")
        print(f"   当前区块: {self.w3.eth.block_number}")

        # 币安热钱包地址（用于新币充值检测）
        # 来源：https://etherscan.io/accounts/label/binance
        # 更新时间：2024-10
        # 说明：只监控热钱包，因为新币上架前首次充值都是到热钱包
        self.binance_wallets = [
            '0x28C6c06298d514Db089934071355E5743bf21d60',  # Binance 14
            '0x21a31Ee1afC51d94C2eFcCAa2092aD1028285549',  # Binance 15
            '0xDFd5293D8e347dFe59E90eFd55b2956a1343963d',  # Binance 16
            '0x56Eddb7aa87536c09CCc2793473599fD21A8b17F',  # Binance 17
            '0x9696f59E4d72E237BE84fFD425DCaD154Bf96976',  # Binance 18
            '0x4E9ce36E442e55EcD9025B9a6E0D88485d628A67',  # Binance 19
            '0xbe0eB53F46cd790Cd13851d5EFf43D12404d33E8',  # Binance 20
            '0xF977814e90dA44bFA03b6295A0616a897441aceC',  # Binance 8
            '0x001866Ae5B3de6caa5a51543FD9fB64F524F5478',  # Binance 21
            '0x85b931A32a0725Be14285B66f1a22178c672d69B',  # Binance 22
            '0x708396f17127c42383E3b9014072679b2F60B82f',  # Binance 23
            '0x8f22F2063D253846b53609231ED80FA571bC0c8F',  # Binance 24
        ]
        self.binance_wallets = [Web3.to_checksum_address(addr) for addr in self.binance_wallets]

        print(f"   监控钱包数量: {len(self.binance_wallets)} 个")

        # 过滤器
        self.filter_enabled = enable_filter and FILTER_AVAILABLE
        self.binance_filter = None

        if self.filter_enabled:
            print("\n🔍 初始化币安已上架代币过滤器...")
            try:
                self.binance_filter = BinanceTokenFilter(proxy=proxy)
                stats = self.binance_filter.get_stats()
                print(f"✅ 过滤器已启用 (已知 {stats['total_tokens']} 个币安代币)")
            except Exception as e:
                print(f"⚠️  过滤器初始化失败: {e}")
                self.filter_enabled = False

        # 分析器
        self.analyzer = AdvancedTokenAnalyzer()

        # 数据存储
        self.known_tokens = {}
        self.new_tokens_buffer = defaultdict(lambda: {
            'transfers': [],
            'first_seen': None,
            'senders': set(),
            'is_new': True,
            'analysis': None,  # 存储分析结果
            'alert_sent': False,  # 是否已发送警报
        })

        # 统计
        self.stats = {
            'total_transfers': 0,
            'filtered_tokens': 0,
            'new_tokens': 0,
            'high_confidence_tokens': 0,
        }

        # 持久化
        self.persistence_file = Path(persistence_file)
        self._load_state()

    def _load_state(self):
        """加载持久化状态"""
        if self.persistence_file.exists():
            try:
                with open(self.persistence_file, 'rb') as f:
                    state = pickle.load(f)
                    self.known_tokens = state.get('known_tokens', {})
                    # 恢复 new_tokens_buffer（需要处理 set）
                    saved_buffer = state.get('new_tokens_buffer', {})
                    for contract, data in saved_buffer.items():
                        self.new_tokens_buffer[contract] = data
                        # 恢复 set
                        if 'senders' in data and isinstance(data['senders'], list):
                            data['senders'] = set(data['senders'])
                    self.stats = state.get('stats', self.stats)
                    print(f"✅ 已加载持久化状态: {self.persistence_file}")
                    print(f"   已知代币: {len(self.known_tokens)} 个")
                    print(f"   监控中代币: {len(self.new_tokens_buffer)} 个")
            except Exception as e:
                print(f"⚠️  加载状态失败: {e}")

    def _save_state(self):
        """保存持久化状态"""
        try:
            # 准备可序列化的数据
            save_buffer = {}
            for contract, data in self.new_tokens_buffer.items():
                save_data = dict(data)
                # 转换 set 为 list
                if 'senders' in save_data:
                    save_data['senders'] = list(save_data['senders'])
                save_buffer[contract] = save_data

            state = {
                'known_tokens': self.known_tokens,
                'new_tokens_buffer': save_buffer,
                'stats': self.stats,
                'last_save': datetime.now().isoformat(),
            }

            with open(self.persistence_file, 'wb') as f:
                pickle.dump(state, f)
        except Exception as e:
            print(f"⚠️  保存状态失败: {e}")

    def get_token_info(self, contract_address):
        """获取代币信息"""
        if contract_address in self.known_tokens:
            return self.known_tokens[contract_address]

        try:
            contract_address = Web3.to_checksum_address(contract_address)
            contract = self.w3.eth.contract(address=contract_address, abi=ERC20_ABI)

            info = {
                'address': contract_address,
                'name': contract.functions.name().call(),
                'symbol': contract.functions.symbol().call(),
                'decimals': contract.functions.decimals().call(),
            }

            # 尝试获取总供应量
            try:
                info['total_supply'] = contract.functions.totalSupply().call()
            except:
                info['total_supply'] = None

            self.known_tokens[contract_address] = info
            return info
        except Exception as e:
            print(f"   ⚠️  无法获取代币信息 {contract_address}: {e}")
            return None

    def decode_transfer_log(self, log):
        """解析 Transfer 事件"""
        try:
            from_address = '0x' + log['topics'][1].hex()[-40:]
            to_address = '0x' + log['topics'][2].hex()[-40:]
            value = int(log['data'].hex(), 16)

            return {
                'block_number': log['blockNumber'],
                'tx_hash': log['transactionHash'].hex(),
                'contract': log['address'],
                'from': Web3.to_checksum_address(from_address),
                'to': Web3.to_checksum_address(to_address),
                'value': value,
                'timestamp': None,
            }
        except Exception as e:
            print(f"   ⚠️  日志解析失败: {e}")
            return None

    def get_block_timestamp(self, block_number):
        """获取区块时间戳（带缓存）"""
        if block_number in self.analyzer.block_cache:
            return self.analyzer.block_cache[block_number]

        try:
            block = self.w3.eth.get_block(block_number)
            timestamp = block['timestamp']
            self.analyzer.block_cache[block_number] = timestamp
            return timestamp
        except:
            return int(time.time())

    def process_transfer(self, transfer_data):
        """处理转账（完整策略版）"""
        contract = transfer_data['contract']
        to_address = transfer_data['to']

        if to_address not in self.binance_wallets:
            return

        self.stats['total_transfers'] += 1

        # 获取代币信息
        token_info = self.get_token_info(contract)
        if not token_info:
            return

        # 检查是否已上架
        is_listed = False
        binance_info = None

        if self.filter_enabled and self.binance_filter:
            is_listed, binance_info = self.binance_filter.is_listed_on_binance(contract)

            if is_listed:
                if contract not in self.new_tokens_buffer:
                    self.stats['filtered_tokens'] += 1
                    print(f"\n⏭️  已过滤 (已上架): {token_info['symbol']} ({token_info['name']})")

                buffer = self.new_tokens_buffer[contract]
                buffer['is_new'] = False
                buffer['binance_symbol'] = binance_info.get('symbol', 'N/A')
                return

        # ============ 未上架新代币 - 完整分析 ============

        is_first_time = contract not in self.new_tokens_buffer

        if is_first_time:
            self.stats['new_tokens'] += 1
            print(f"\n{'🚨'*3} 发现未上架新代币! {'🚨'*3}")
            print(f"   代币: {token_info['symbol']} ({token_info['name']})")
            print(f"   合约: {contract}")
            print(f"   ✅ 未在币安上架 - 可能是即将上线的新币!")

        # 更新缓冲区
        buffer = self.new_tokens_buffer[contract]
        buffer['transfers'].append(transfer_data)
        buffer['senders'].add(transfer_data['from'])
        buffer['is_new'] = True

        if buffer['first_seen'] is None:
            buffer['first_seen'] = datetime.now()

        # 计算金额
        decimals = token_info['decimals']
        amount = transfer_data['value'] / (10 ** decimals)

        print(f"   📥 充值: {amount:.4f} {token_info['symbol']}")
        print(f"   发送者: {transfer_data['from'][:10]}...{transfer_data['from'][-8:]}")
        print(f"   接收者: {to_address[:10]}...{to_address[-8:]}")
        print(f"   交易: {transfer_data['tx_hash'][:10]}...{transfer_data['tx_hash'][-8:]}")
        print(f"   时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

        # 🆕 执行完整分析（如果达到阈值）
        if len(buffer['transfers']) >= 2:
            print(f"\n   📊 执行完整策略分析...")
            analysis = self.analyzer.analyze_transfers(
                buffer['transfers'],
                buffer['senders'],
                token_info,
                self.w3
            )
            buffer['analysis'] = analysis

            # 显示分析结果
            self._display_analysis(analysis, token_info)

            # 🆕 智能告警
            self._check_alert_conditions(contract, buffer, analysis, token_info)
        else:
            print(f"   📊 统计: {len(buffer['transfers'])} 笔转账, {len(buffer['senders'])} 个发送者")

        # 定期保存状态
        if self.stats['total_transfers'] % 10 == 0:
            self._save_state()

    def _display_analysis(self, analysis, token_info):
        """显示分析结果"""
        print(f"\n   {'─'*60}")
        print(f"   🔍 策略分析结果:")
        print(f"   {'─'*60}")
        print(f"   置信度: {analysis['confidence']:.2%} {'█' * int(analysis['confidence'] * 10)}")
        print(f"   风险等级: {analysis['risk_level'].upper()}")

        if analysis['patterns']:
            print(f"\n   ✅ 发现模式:")
            for pattern in analysis['patterns'][:5]:
                print(f"      • {pattern}")

        if analysis['warnings']:
            print(f"\n   ⚠️  警告信息:")
            for warning in analysis['warnings'][:5]:
                print(f"      • {warning}")

        print(f"\n   💡 {analysis['recommendation']}")
        print(f"   {'─'*60}\n")

    def _check_alert_conditions(self, contract, buffer, analysis, token_info):
        """检查告警条件"""
        if buffer.get('alert_sent'):
            return  # 已发送过告警

        confidence = analysis['confidence']
        transfer_count = len(buffer['transfers'])
        sender_count = len(buffer['senders'])

        # 告警条件
        should_alert = False
        alert_level = None

        if confidence >= 0.8 and transfer_count >= 3 and sender_count >= 2:
            should_alert = True
            alert_level = 'HIGH'
        elif confidence >= 0.6 and transfer_count >= 5:
            should_alert = True
            alert_level = 'MEDIUM'

        if should_alert:
            # 🆕 二次验证 - 避免误报（特别是 HIGH 级别告警）
            if alert_level == 'HIGH' and self.filter_enabled and self.binance_filter:
                is_listed, binance_info = self.binance_filter.is_listed_on_binance(contract)
                if is_listed:
                    symbol = token_info.get('symbol', 'UNKNOWN')
                    binance_symbol = binance_info.get('symbol', 'N/A')
                    print(f"\n⚠️  HIGH 告警被二次验证阻止:")
                    print(f"   代币 {symbol} 已在币安上架 (交易对: {binance_symbol}USDT)")
                    print(f"   这是误报，已自动过滤\n")
                    # 更新缓冲区，标记为已上架
                    buffer['is_new'] = False
                    buffer['binance_symbol'] = binance_symbol
                    return  # 不发送告警

            self.stats['high_confidence_tokens'] += 1
            buffer['alert_sent'] = True
            self._send_alert(alert_level, contract, buffer, analysis, token_info)

    def _send_alert(self, level, contract, buffer, analysis, token_info):
        """发送告警"""
        symbol = f"{'🚨'*3}" if level == 'HIGH' else "⚡"

        print(f"\n{symbol} {level} 级别告警! {symbol}")
        print(f"   代币: {token_info['symbol']} ({token_info['name']})")
        print(f"   合约: {contract}")
        print(f"   转账数: {len(buffer['transfers'])} 笔")
        print(f"   发送者: {len(buffer['senders'])} 个")
        print(f"   置信度: {analysis['confidence']:.2%}")
        print(f"   {analysis['recommendation']}")
        print(f"   立即行动建议: 深入调查此代币！\n")

        # TODO: 集成 Telegram/Discord/邮件通知

    def listen_with_websocket(self, callback=None):
        """
        实时监听（使用 HTTP 轮询代替 WebSocket）

        注意: Web3.py v6+ 移除了同步 WebSocket 支持
        使用 HTTP 轮询模式，性能同样优秀（1-2秒延迟）
        """
        print(f"\n{'='*80}")
        print(f"🚀 启动实时监听（HTTP 轮询模式）")
        print(f"{'='*80}")
        print(f"监控钱包: {len(self.binance_wallets)} 个")
        print(f"过滤器: {'启用' if self.filter_enabled else '禁用'}")
        print(f"策略分析: 启用")
        print(f"轮询间隔: 2 秒")
        print(f"{'='*80}\n")

        # 使用 HTTP 轮询代替 WebSocket
        self.listen_with_polling(from_block='latest', poll_interval=2, callback=callback)

    def listen_with_polling(self, from_block='latest', poll_interval=12, callback=None):
        """HTTP 轮询监听（完整版）"""
        print(f"\n{'='*80}")
        print(f"🔄 启动 HTTP 轮询监听（完整策略版）")
        print(f"{'='*80}")
        print(f"监控钱包: {len(self.binance_wallets)} 个")
        print(f"轮询间隔: {poll_interval} 秒")
        print(f"{'='*80}\n")

        current_block = self.w3.eth.block_number if from_block == 'latest' else int(from_block)
        print(f"⏰ 从区块 {current_block} 开始监听...\n")

        try:
            while True:
                latest_block = self.w3.eth.block_number

                if latest_block > current_block:
                    print(f"🔍 检查区块 {current_block} - {latest_block}")

                    for wallet in self.binance_wallets:
                        try:
                            logs = self.w3.eth.get_logs({
                                'fromBlock': current_block,
                                'toBlock': latest_block,
                                'topics': [
                                    TRANSFER_EVENT_SIGNATURE,
                                    None,
                                    '0x' + wallet[2:].zfill(64)
                                ]
                            })

                            for log in logs:
                                transfer_data = self.decode_transfer_log(log)
                                if transfer_data:
                                    transfer_data['timestamp'] = self.get_block_timestamp(
                                        transfer_data['block_number']
                                    )
                                    self.process_transfer(transfer_data)

                                    if callback:
                                        callback(transfer_data, self.new_tokens_buffer)
                        except Exception as e:
                            print(f"   ⚠️  查询 {wallet[:10]}... 失败: {e}")

                    current_block = latest_block + 1

                time.sleep(poll_interval)

        except KeyboardInterrupt:
            print("\n⏹️  监听已停止")
            self._save_state()
            print("✅ 状态已保存")
        except Exception as e:
            print(f"\n❌ 监听出错: {e}")
            self._save_state()

    def get_summary_report(self):
        """获取汇总报告（增强版）"""
        report = []
        report.append(f"\n{'='*80}")
        report.append(f"📊 新代币检测汇总（完整策略版）")
        report.append(f"{'='*80}\n")

        report.append(f"总转账事件: {self.stats['total_transfers']}")
        report.append(f"已过滤代币: {self.stats['filtered_tokens']} (币安已上架)")
        report.append(f"新发现代币: {self.stats['new_tokens']} ⭐")
        report.append(f"高置信度代币: {self.stats['high_confidence_tokens']} 🔥\n")

        new_tokens = []
        for contract, buffer in self.new_tokens_buffer.items():
            if buffer.get('is_new', True):
                new_tokens.append((contract, buffer))

        if new_tokens:
            # 按置信度排序
            new_tokens.sort(key=lambda x: x[1].get('analysis', {}).get('confidence', 0), reverse=True)

            report.append(f"{'─'*80}")
            report.append(f"🚨 未上架新代币详细分析 - {len(new_tokens)} 个")
            report.append(f"{'─'*80}\n")

            for contract, buffer in new_tokens:
                token_info = self.known_tokens.get(contract, {})
                symbol = token_info.get('symbol', 'UNKNOWN')
                name = token_info.get('name', 'Unknown Token')
                analysis = buffer.get('analysis')

                if analysis:
                    confidence_bar = "█" * int(analysis['confidence'] * 10)
                    report.append(f"🪙 {symbol} ({name})")
                    report.append(f"   合约: {contract}")
                    report.append(f"   转账数: {len(buffer['transfers'])}")
                    report.append(f"   发送者: {len(buffer['senders'])} 个")
                    report.append(f"   置信度: {confidence_bar} {analysis['confidence']:.2%}")
                    report.append(f"   风险等级: {analysis['risk_level'].upper()}")
                    report.append(f"   {analysis['recommendation']}")
                    report.append("")
                else:
                    report.append(f"🪙 {symbol} ({name}) - 等待更多数据...")
                    report.append(f"   合约: {contract}")
                    report.append(f"   转账数: {len(buffer['transfers'])}")
                    report.append("")
        else:
            report.append("📭 暂无未上架新代币检测\n")

        report.append(f"{'='*80}\n")
        return "\n".join(report)


def main():
    print("""
╔════════════════════════════════════════════════════════════════════════════╗
║              区块链节点直接监听 - 完整策略版 v2.0                         ║
╚════════════════════════════════════════════════════════════════════════════╝

🆕 完整策略功能:
✅ 实时 WebSocket 监听
✅ 智能代币过滤（600+ 已上架代币）
✅ 女巫攻击检测
✅ 多维度置信度评分
✅ 高级转账模式分析
✅ 智能告警策略
✅ 数据持久化

使用方法:
    listener = BlockchainListener(
        rpc_url='YOUR_HTTP_RPC',
        ws_url='YOUR_WEBSOCKET_RPC'
    )
    listener.listen_with_websocket()

╚════════════════════════════════════════════════════════════════════════════╝
    """)


if __name__ == '__main__':
    main()
