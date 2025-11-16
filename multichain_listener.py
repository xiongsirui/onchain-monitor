#!/usr/bin/env python3
"""
多链区块链监听器 - 支持 ETH、BSC、Solana

功能:
- ✅ 以太坊链 (Ethereum) 监听
- ✅ BSC链 (Binance Smart Chain) 监听
- ✅ Solana链监听
- ✅ 统一的代币过滤器
- ✅ 女巫攻击检测
- ✅ 多维度置信度评分
- ✅ 智能告警策略
"""

from web3 import Web3
import json
import time
import pickle
from datetime import datetime, timedelta
from pathlib import Path
import statistics
from typing import Any, Callable, Dict, List, Optional, Set
from abc import ABC, abstractmethod

# 导入币安代币过滤器
try:
    from binance_token_filter import BinanceTokenFilter
    FILTER_AVAILABLE = True
except ImportError:
    FILTER_AVAILABLE = False
    print("⚠️  binance_token_filter.py 未找到，将不过滤已上架代币")

# 导入飞书通知器
try:
    from feishu_notifier import FeishuNotifier
    FEISHU_AVAILABLE = True
except ImportError:
    FEISHU_AVAILABLE = False
    print("⚠️  feishu_notifier.py 未找到，将不发送飞书通知")

# ERC20/BEP20 Transfer 事件签名
TRANSFER_EVENT_SIGNATURE = '0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef'

# ERC20/BEP20 ABI
TOKEN_ABI = json.loads('''[
    {"constant": true, "inputs": [], "name": "name", "outputs": [{"name": "", "type": "string"}], "type": "function"},
    {"constant": true, "inputs": [], "name": "symbol", "outputs": [{"name": "", "type": "string"}], "type": "function"},
    {"constant": true, "inputs": [], "name": "decimals", "outputs": [{"name": "", "type": "uint8"}], "type": "function"},
    {"constant": true, "inputs": [{"name": "_owner", "type": "address"}], "name": "balanceOf", "outputs": [{"name": "balance", "type": "uint256"}], "type": "function"},
    {"constant": true, "inputs": [], "name": "totalSupply", "outputs": [{"name": "", "type": "uint256"}], "type": "function"}
]''')


class ChainConfig:
    """链配置"""
    def __init__(self, name: str, rpc_url: str, ws_url: Optional[str] = None):
        self.name = name
        self.rpc_url = rpc_url
        self.ws_url = ws_url


class AdvancedTokenAnalyzer:
    """
    高级代币分析器 - 策略核心
    """

    def __init__(self):
        # 女巫攻击检测配置
        self.sybil_thresholds = {
            'min_sender_balance': 0.1,          # ETH/BNB
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

    def analyze_transfers(self, transfers, senders, token_info):
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

        # 4. 女巫攻击检测
        sybil_score = self._detect_sybil_attack(transfers, senders, analysis)
        analysis['scores']['sybil_detection'] = sybil_score

        # 5. 计算综合置信度
        analysis['confidence'] = self._calculate_overall_confidence(analysis['scores'])

        # 6. 确定风险等级
        analysis['risk_level'] = self._determine_risk_level(analysis['confidence'], analysis['warnings'])

        # 7. 生成建议
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
            'basic_stats': 0.30,
            'time_pattern': 0.20,
            'amount_distribution': 0.20,
            'sybil_detection': 0.30,
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
            return "🟢 强烈建议: 高置信度信号，多维度验证通过，建议重点关注"
        elif confidence >= 0.6 and risk_level in ['low', 'medium']:
            return "🟡 谨慎建议: 中等置信度，建议持续观察，等待更多信号"
        elif confidence >= 0.4:
            return "🟠 观察建议: 置信度偏低，存在疑点，建议谨慎观察"
        else:
            return "🔴 不建议: 置信度很低或存在女巫攻击风险，不建议行动"


class BaseChainListener(ABC):
    """链监听器基类"""

    def __init__(self, chain_name: str, binance_wallets: List[str],
                 analyzer: AdvancedTokenAnalyzer,
                 binance_filter: Optional[BinanceTokenFilter] = None,
                 feishu_notifier: Optional['FeishuNotifier'] = None):
        self.chain_name = chain_name
        self.binance_wallets = binance_wallets
        self.analyzer = analyzer
        self.binance_filter = binance_filter
        self.feishu_notifier = feishu_notifier

        # 数据存储
        self.known_tokens: Dict[str, Dict[str, Any]] = {}
        self.new_tokens_buffer: Dict[str, Dict[str, Any]] = {}

        # 统计
        self.stats = {
            'total_transfers': 0,
            'filtered_tokens': 0,
            'new_tokens': 0,
            'high_confidence_tokens': 0,
        }

    @abstractmethod
    def get_token_info(self, contract_address: str) -> Optional[Dict]:
        """获取代币信息"""
        pass

    @abstractmethod
    def listen(self, callback=None):
        """开始监听"""
        pass

    def process_transfer(self, transfer_data):
        """处理转账（通用逻辑）"""
        contract = transfer_data.get('contract')
        to_address = transfer_data.get('to')

        if not contract or not to_address or not self._is_monitored_wallet(to_address):
            return

        self.stats['total_transfers'] += 1

        # 获取代币信息
        token_info = self.get_token_info(contract)
        if not token_info:
            return

        # 已上架代币直接过滤
        if self._handle_listed_token(contract, token_info):
            return

        buffer_existed = contract in self.new_tokens_buffer
        buffer = self._get_token_buffer(contract)
        is_first_time = not buffer_existed

        if is_first_time:
            self._mark_new_token_detected(buffer, contract, token_info)

        # 更新缓冲区
        self._record_transfer(buffer, transfer_data)
        self._print_transfer_event(token_info, transfer_data, to_address)

        if self._should_run_analysis(buffer):
            self._run_full_analysis(contract, buffer, token_info)
        else:
            self._print_basic_stats(buffer)

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
            # 二次验证 - 避免误报
            if alert_level == 'HIGH' and self.binance_filter:
                is_listed, binance_info = self.binance_filter.is_listed_on_binance(contract)
                if is_listed:
                    symbol = token_info.get('symbol', 'UNKNOWN')
                    binance_symbol = binance_info.get('symbol', 'N/A')
                    print(f"\n⚠️  [{self.chain_name}] HIGH 告警被二次验证阻止:")
                    print(f"   代币 {symbol} 已在币安上架 (交易对: {binance_symbol}USDT)")
                    print(f"   这是误报，已自动过滤\n")
                    buffer['is_new'] = False
                    buffer['binance_symbol'] = binance_symbol
                    return

            self.stats['high_confidence_tokens'] += 1
            buffer['alert_sent'] = True
            self._send_alert(alert_level, contract, buffer, analysis, token_info)

    def _send_alert(self, level, contract, buffer, analysis, token_info):
        """发送告警"""
        symbol = f"{'🚨'*3}" if level == 'HIGH' else "⚡"

        print(f"\n{symbol} [{self.chain_name}] {level} 级别告警! {symbol}")
        print(f"   代币: {token_info['symbol']} ({token_info['name']})")
        print(f"   合约: {contract}")
        print(f"   转账数: {len(buffer['transfers'])} 笔")
        print(f"   发送者: {len(buffer['senders'])} 个")
        print(f"   置信度: {analysis['confidence']:.2%}")
        print(f"   {analysis['recommendation']}")
        print(f"   立即行动建议: 深入调查此代币！\n")

        # 发送飞书通知
        if self.feishu_notifier:
            try:
                self.feishu_notifier.send_token_alert(
                    level=level,
                    chain=self.chain_name,
                    contract=contract,
                    token_info=token_info,
                    buffer=buffer,
                    analysis=analysis
                )
            except Exception as e:
                print(f"   ⚠️  飞书通知发送失败: {e}")

    def _is_monitored_wallet(self, to_address: str) -> bool:
        """判断转入地址是否属于监控钱包"""
        return to_address in self.binance_wallets

    def _get_token_buffer(self, contract: str) -> Dict[str, Any]:
        """获取或创建代币缓冲区"""
        if contract not in self.new_tokens_buffer:
            self.new_tokens_buffer[contract] = self._create_token_buffer()
        return self.new_tokens_buffer[contract]

    def _create_token_buffer(self) -> Dict[str, Any]:
        """默认缓冲区结构"""
        return {
            'transfers': [],
            'first_seen': None,
            'senders': set(),
            'is_new': True,
            'analysis': None,
            'alert_sent': False,
            'chain': self.chain_name,
            'binance_symbol': None,
        }

    def _handle_listed_token(self, contract: str, token_info: Dict[str, Any]) -> bool:
        """检测并处理币安已上架代币"""
        if not self.binance_filter:
            return False

        is_listed, binance_info = self.binance_filter.is_listed_on_binance(contract)
        if not is_listed:
            return False

        buffer_was_known = contract in self.new_tokens_buffer
        buffer = self._get_token_buffer(contract)
        buffer['is_new'] = False
        buffer['binance_symbol'] = binance_info.get('symbol', 'N/A')

        if not buffer_was_known:
            self.stats['filtered_tokens'] += 1
            print(f"\n⏭️  [{self.chain_name}] 已过滤 (已上架): {token_info['symbol']} ({token_info['name']})")

        return True

    def _mark_new_token_detected(self, buffer: Dict[str, Any], contract: str, token_info: Dict[str, Any]):
        """首次发现未上架代币时的处理"""
        buffer['first_seen'] = datetime.now()
        buffer['is_new'] = True
        self.stats['new_tokens'] += 1

        print(f"\n{'🚨'*3} [{self.chain_name}] 发现未上架新代币! {'🚨'*3}")
        print(f"   代币: {token_info['symbol']} ({token_info['name']})")
        print(f"   合约: {contract}")
        print("   ✅ 未在币安上架 - 可能是即将上线的新币!")

    def _record_transfer(self, buffer: Dict[str, Any], transfer_data: Dict[str, Any]):
        """缓存转账数据"""
        buffer['transfers'].append(transfer_data)
        sender = transfer_data.get('from')
        if sender:
            buffer['senders'].add(sender)

    def _print_transfer_event(self, token_info: Dict[str, Any], transfer_data: Dict[str, Any], to_address: str):
        """格式化打印单笔充值事件"""
        decimals = token_info.get('decimals', 18)
        divisor = 10 ** decimals if decimals else 1
        amount = transfer_data['value'] / divisor
        sender = transfer_data.get('from', 'Unknown')
        tx_hash = transfer_data.get('tx_hash', 'N/A')

        print(f"   📥 充值: {amount:.4f} {token_info['symbol']}")
        print(f"   发送者: {self._shorten(sender)}")
        print(f"   接收者: {self._shorten(to_address)}")
        print(f"   交易: {self._shorten(tx_hash)}")
        print(f"   时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    def _should_run_analysis(self, buffer: Dict[str, Any]) -> bool:
        """分析阈值控制"""
        return len(buffer['transfers']) >= 2

    def _run_full_analysis(self, contract: str, buffer: Dict[str, Any], token_info: Dict[str, Any]):
        """执行策略分析并触发告警"""
        print("\n   📊 执行完整策略分析...")
        analysis = self.analyzer.analyze_transfers(
            buffer['transfers'],
            buffer['senders'],
            token_info
        )
        buffer['analysis'] = analysis

        self._display_analysis(analysis, token_info)
        self._check_alert_conditions(contract, buffer, analysis, token_info)

    def _print_basic_stats(self, buffer: Dict[str, Any]):
        """打印基础统计信息"""
        print(f"   📊 统计: {len(buffer['transfers'])} 笔转账, {len(buffer['senders'])} 个发送者")

    @staticmethod
    def _shorten(value: str, prefix: int = 10, suffix: int = 8) -> str:
        """截断长字符串，便于阅读"""
        if value is None:
            return "N/A"

        value = str(value)
        if len(value) <= prefix + suffix:
            return value
        return f"{value[:prefix]}...{value[-suffix:]}"


class EVMChainListener(BaseChainListener):
    """EVM兼容链监听器 (支持 Ethereum, BSC)"""

    def __init__(self, chain_name: str, rpc_url: str, ws_url: Optional[str],
                 binance_wallets: List[str], analyzer: AdvancedTokenAnalyzer,
                 binance_filter: Optional[BinanceTokenFilter] = None,
                 feishu_notifier: Optional['FeishuNotifier'] = None,
                 proxy: Optional[str] = None):
        super().__init__(chain_name, binance_wallets, analyzer, binance_filter, feishu_notifier)

        # Web3 连接
        if proxy:
            print(f"🔄 [{chain_name}] 使用代理: {proxy}")
            request_kwargs = {'proxies': {'http': proxy, 'https': proxy}}
            self.w3 = Web3(Web3.HTTPProvider(rpc_url, request_kwargs=request_kwargs))
        else:
            self.w3 = Web3(Web3.HTTPProvider(rpc_url))

        if not self.w3.is_connected():
            raise Exception(f"❌ [{chain_name}] RPC 节点连接失败")

        print(f"✅ [{chain_name}] RPC 已连接: {rpc_url}")
        print(f"   当前区块: {self.w3.eth.block_number}")

        self.binance_wallets = [Web3.to_checksum_address(addr) for addr in binance_wallets]

    def get_token_info(self, contract_address: str) -> Optional[Dict]:
        """获取ERC20/BEP20代币信息"""
        if contract_address in self.known_tokens:
            return self.known_tokens[contract_address]

        try:
            contract_address = Web3.to_checksum_address(contract_address)
            contract = self.w3.eth.contract(address=contract_address, abi=TOKEN_ABI)

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
            print(f"   ⚠️  [{self.chain_name}] 无法获取代币信息 {contract_address}: {e}")
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
            print(f"   ⚠️  [{self.chain_name}] 日志解析失败: {e}")
            return None

    def get_block_timestamp(self, block_number):
        """获取区块时间戳"""
        try:
            block = self.w3.eth.get_block(block_number)
            return block['timestamp']
        except:
            return int(time.time())

    def listen(self, from_block='latest', poll_interval=12, callback=None):
        """HTTP 轮询监听"""
        print(f"\n{'='*80}")
        print(f"🔄 [{self.chain_name}] 启动 HTTP 轮询监听")
        print(f"{'='*80}")
        print(f"监控钱包: {len(self.binance_wallets)} 个")
        print(f"轮询间隔: {poll_interval} 秒")
        print(f"{'='*80}\n")

        current_block = self.w3.eth.block_number if from_block == 'latest' else int(from_block)
        print(f"⏰ [{self.chain_name}] 从区块 {current_block} 开始监听...\n")

        try:
            while True:
                latest_block = self.w3.eth.block_number

                if latest_block > current_block:
                    self._process_block_range(current_block, latest_block, callback)
                    current_block = latest_block + 1

                time.sleep(poll_interval)

        except KeyboardInterrupt:
            print(f"\n⏹️  [{self.chain_name}] 监听已停止")

    def _process_block_range(self, start_block: int, end_block: int, callback=None):
        """按区块范围处理所有监控钱包"""
        print(f"🔍 [{self.chain_name}] 检查区块 {start_block} - {end_block}")

        for wallet in self.binance_wallets:
            self._process_wallet_logs(wallet, start_block, end_block, callback)

    def _process_wallet_logs(self, wallet: str, start_block: int, end_block: int, callback=None):
        """拉取并处理指定钱包在区块范围内的 Transfer 日志"""
        try:
            logs = self.w3.eth.get_logs({
                'fromBlock': start_block,
                'toBlock': end_block,
                'topics': [
                    TRANSFER_EVENT_SIGNATURE,
                    None,
                    '0x' + wallet[2:].zfill(64)
                ]
            })
        except Exception as e:
            print(f"   ⚠️  [{self.chain_name}] 查询 {wallet[:10]}... 失败: {e}")
            return

        for log in logs:
            transfer_data = self.decode_transfer_log(log)
            if not transfer_data:
                continue

            transfer_data['timestamp'] = self.get_block_timestamp(
                transfer_data['block_number']
            )
            self.process_transfer(transfer_data)

            if callback:
                callback(transfer_data, self.new_tokens_buffer)


class SolanaChainListener(BaseChainListener):
    """Solana链监听器"""

    def __init__(self, rpc_url: str, binance_wallets: List[str],
                 analyzer: AdvancedTokenAnalyzer,
                 binance_filter: Optional[BinanceTokenFilter] = None,
                 feishu_notifier: Optional['FeishuNotifier'] = None):
        super().__init__("Solana", binance_wallets, analyzer, binance_filter, feishu_notifier)

        try:
            from solders.pubkey import Pubkey
            from solders.signature import Signature
            from solana.rpc.api import Client
            self.Pubkey = Pubkey
            self.Signature = Signature
            self.client = Client(rpc_url)
            print(f"✅ [Solana] RPC 已连接: {rpc_url}")
        except ImportError:
            raise Exception("❌ [Solana] 请安装 Solana 依赖: pip install solana solders")
        except Exception as e:
            raise Exception(f"❌ [Solana] RPC 连接失败: {e}")

    def get_token_info(self, mint_address: str) -> Optional[Dict]:
        """获取SPL代币信息"""
        if mint_address in self.known_tokens:
            return self.known_tokens[mint_address]

        try:
            from solders.pubkey import Pubkey

            # 尝试获取代币账户信息
            mint_pubkey = Pubkey.from_string(mint_address)

            # 获取代币供应量和小数位
            response = self.client.get_token_supply(mint_pubkey)

            decimals = 9  # 默认值
            if response.value:
                decimals = response.value.decimals

            # TODO: 可以通过 Metaplex 获取代币元数据（名称、符号）
            # 这里使用简化版本
            info = {
                'address': mint_address,
                'name': f'Token-{mint_address[:8]}',
                'symbol': f'TK-{mint_address[:4]}',
                'decimals': decimals,
            }

            self.known_tokens[mint_address] = info
            return info
        except Exception as e:
            print(f"   ⚠️  [Solana] 无法获取代币信息 {mint_address}: {e}")
            # 返回默认信息
            info = {
                'address': mint_address,
                'name': 'Unknown Token',
                'symbol': 'UNKNOWN',
                'decimals': 9,
            }
            self.known_tokens[mint_address] = info
            return info

    def listen(self, poll_interval: int = 2, callback: Optional[Callable] = None):
        """Solana 监听（解析 SPL Token Transfer）"""
        print(f"\n{'='*80}")
        print(f"🔄 [Solana] 启动监听")
        print(f"{'='*80}")
        print(f"监控钱包: {len(self.binance_wallets)} 个")
        print(f"轮询间隔: {poll_interval} 秒")
        print(f"{'='*80}\n")

        last_signatures: Dict[str, Optional[str]] = {wallet: None for wallet in self.binance_wallets}

        print(f"✅ [Solana] 开始监听 SPL Token 转账...\n")

        try:
            while True:
                self._poll_wallets(last_signatures, callback)
                time.sleep(poll_interval)
        except KeyboardInterrupt:
            print(f"\n⏹️  [Solana] 监听已停止")

    def _poll_wallets(self, last_signatures: Dict[str, Optional[str]], callback: Optional[Callable]):
        """轮询所有监控钱包"""
        for wallet_address in self.binance_wallets:
            self._process_wallet_transactions(wallet_address, last_signatures, callback)

    def _process_wallet_transactions(self, wallet_address: str,
                                     last_signatures: Dict[str, Optional[str]],
                                     callback: Optional[Callable]):
        """处理指定钱包的最新交易"""
        try:
            wallet_pubkey = self.Pubkey.from_string(wallet_address)
            signatures = self._fetch_recent_signatures(wallet_pubkey)
        except Exception as e:
            print(f"   ⚠️  [Solana] 查询钱包 {wallet_address[:8]}... 失败: {e}")
            return

        if not signatures:
            return

        signatures.reverse()  # 旧 -> 新
        for sig_info in signatures:
            sig_str = str(sig_info.signature)

            if last_signatures.get(wallet_address) == sig_str:
                break  # 后续都是已处理的

            self._handle_signature(sig_str, wallet_address, callback)

        last_signatures[wallet_address] = str(signatures[-1].signature)

    def _fetch_recent_signatures(self, wallet_pubkey, limit: int = 10):
        """获取钱包近期签名"""
        response = self.client.get_signatures_for_address(wallet_pubkey, limit=limit)
        return response.value or []

    def _handle_signature(self, signature_str: str, wallet_address: str, callback: Optional[Callable]):
        """获取交易并解析"""
        try:
            tx_response = self.client.get_transaction(
                self.Signature.from_string(signature_str),
                max_supported_transaction_version=0
            )
        except Exception as e:
            print(f"   ⚠️  [Solana] 获取交易 {signature_str[:8]}... 失败: {e}")
            return

        if not tx_response.value:
            return

        try:
            self._parse_solana_transaction(
                tx_response.value,
                wallet_address,
                signature_str,
                callback
            )
        except Exception as e:
            print(f"   ⚠️  [Solana] 解析交易 {signature_str[:8]}... 失败: {e}")

    def _parse_solana_transaction(self, transaction, wallet_address, signature, callback=None):
        """解析 Solana 交易，提取 SPL Token Transfer"""
        meta = transaction.transaction.meta if transaction and transaction.transaction else None
        if not meta:
            return

        balance_changes = self._extract_balance_changes(meta, wallet_address)
        if not balance_changes:
            return

        timestamp = getattr(transaction, 'block_time', None) or int(time.time())

        for mint, change in balance_changes.items():
            transfer_data = self._build_transfer_payload(
                slot=transaction.slot,
                signature=signature,
                mint=mint,
                wallet_address=wallet_address,
                change=change,
                timestamp=timestamp
            )

            self.process_transfer(transfer_data)

            if callback:
                callback(transfer_data, self.new_tokens_buffer)

    def _extract_balance_changes(self, meta, wallet_address: str) -> Dict[str, int]:
        """提取指定钱包的 SPL Token 余额新增"""
        post_token_balances = meta.post_token_balances or []
        pre_token_balances = meta.pre_token_balances or []

        balance_changes: Dict[str, int] = {}
        for post_balance in post_token_balances:
            owner = str(post_balance.owner) if post_balance.owner else None
            if owner != wallet_address:
                continue

            amount_after = int(post_balance.ui_token_amount.amount)
            amount_before = self._find_previous_amount(pre_token_balances, post_balance.account_index)
            change = amount_after - amount_before

            if change > 0:
                mint = str(post_balance.mint)
                balance_changes[mint] = change

        return balance_changes

    @staticmethod
    def _find_previous_amount(pre_balances, account_index: int) -> int:
        """匹配前置余额"""
        for pre_balance in pre_balances or []:
            if pre_balance.account_index == account_index:
                return int(pre_balance.ui_token_amount.amount)
        return 0

    @staticmethod
    def _build_transfer_payload(slot: int, signature: str, mint: str,
                                wallet_address: str, change: int, timestamp: int) -> Dict[str, Any]:
        """构造标准化转账结构"""
        return {
            'block_number': slot,
            'tx_hash': signature,
            'contract': mint,  # Solana mint address
            'from': 'Unknown',
            'to': wallet_address,
            'value': change,
            'timestamp': timestamp,
        }


class MultiChainListener:
    """多链统一监听器"""

    def __init__(self, enable_filter=True, proxy=None, persistence_file='multichain_state.pkl',
                 feishu_webhook_url: Optional[str] = None):
        """
        初始化多链监听器

        参数:
            enable_filter: 是否启用币安代币过滤器
            proxy: 代理服务器 (例如: "http://127.0.0.1:7897")
            persistence_file: 持久化文件路径
            feishu_webhook_url: 飞书机器人 Webhook URL (可选)
        """
        print(f"\n{'='*80}")
        print("🚀 多链区块链监听器初始化")
        print(f"{'='*80}\n")

        # 规范化代理格式
        if proxy and not proxy.startswith(('http://', 'https://', 'socks5://', 'socks4://')):
            proxy = f'http://{proxy}'

        self.proxy = proxy

        # 初始化过滤器
        self.filter_enabled = enable_filter and FILTER_AVAILABLE
        self.binance_filter = None

        if self.filter_enabled:
            print("🔍 初始化币安已上架代币过滤器...")
            try:
                self.binance_filter = BinanceTokenFilter(proxy=proxy)
                stats = self.binance_filter.get_stats()
                print(f"✅ 过滤器已启用 (已知 {stats['total_tokens']} 个币安代币)\n")
            except Exception as e:
                print(f"⚠️  过滤器初始化失败: {e}\n")
                self.filter_enabled = False

        # 初始化飞书通知器
        self.feishu_notifier = None
        if feishu_webhook_url and FEISHU_AVAILABLE:
            print("📱 初始化飞书通知器...")
            try:
                self.feishu_notifier = FeishuNotifier(feishu_webhook_url, proxy=proxy)
                # 发送测试消息
                if self.feishu_notifier.send_test_message():
                    print("✅ 飞书通知器已启用\n")
                else:
                    print("⚠️  飞书通知器测试失败，将禁用通知\n")
                    self.feishu_notifier = None
            except Exception as e:
                print(f"⚠️  飞书通知器初始化失败: {e}\n")
                self.feishu_notifier = None
        elif feishu_webhook_url and not FEISHU_AVAILABLE:
            print("⚠️  feishu_notifier.py 未找到，无法启用飞书通知\n")

        # 初始化分析器
        self.analyzer = AdvancedTokenAnalyzer()

        # 链监听器
        self.listeners: Dict[str, BaseChainListener] = {}

        # 持久化
        self.persistence_file = Path(persistence_file)

    def add_eth_listener(self, rpc_url: str, ws_url: Optional[str] = None, proxy: Optional[str] = None):
        """添加以太坊监听器"""
        binance_wallets = [
            '0x28C6c06298d514Db089934071355E5743bf21d60',  # Binance 14
            '0x21a31Ee1afC51d94C2eFcCAa2092aD1028285549',  # Binance 15
            '0xDFd5293D8e347dFe59E90eFd55b2956a1343963d',  # Binance 16
            '0x56Eddb7aa87536c09CCc2793473599fD21A8b17F',  # Binance 17
            '0x9696f59E4d72E237BE84fFD425DCaD154Bf96976',  # Binance 18
            '0x4E9ce36E442e55EcD9025B9a6E0D88485d628A67',  # Binance 19
            '0xbe0eB53F46cd790Cd13851d5EFf43D12404d33E8',  # Binance 20
            '0xF977814e90dA44bFA03b6295A0616a897441aceC',  # Binance 8
        ]

        listener = EVMChainListener(
            chain_name="Ethereum",
            rpc_url=rpc_url,
            ws_url=ws_url,
            binance_wallets=binance_wallets,
            analyzer=self.analyzer,
            binance_filter=self.binance_filter,
            feishu_notifier=self.feishu_notifier,
            proxy=proxy or self.proxy
        )
        self.listeners['ETH'] = listener
        return listener

    def add_bsc_listener(self, rpc_url: str, ws_url: Optional[str] = None, proxy: Optional[str] = None):
        """添加BSC监听器"""
        binance_wallets = [
            '0x8894E0a0c962CB723c1976a4421c95949bE2D4E3',  # Binance BSC Hot Wallet
            '0x28C6c06298d514Db089934071355E5743bf21d60',  # Binance 14
            '0xdccf3b77da55107280bd850ea519df3705d1a75a',  # Binance BSC Wallet
            '0x0eD7e52944161450477ee417DE9Cd3a859b14fD0',  # Binance BSC Wallet
        ]

        listener = EVMChainListener(
            chain_name="BSC",
            rpc_url=rpc_url,
            ws_url=ws_url,
            binance_wallets=binance_wallets,
            analyzer=self.analyzer,
            binance_filter=self.binance_filter,
            feishu_notifier=self.feishu_notifier,
            proxy=proxy or self.proxy
        )
        self.listeners['BSC'] = listener
        return listener

    def add_solana_listener(self, rpc_url: str):
        """添加Solana监听器"""
        binance_wallets = [
            'FWWqD7mGFWzGbUB14TXLxESJ5GSKboMvCHvmh6xEjHfQ',  # Binance Solana Hot Wallet
            '5tzFkiKscXHK5ZXCGbXZxdw7gTjjD1mBwuoFbhUvuAi9',  # Binance Solana Hot Wallet 2
        ]

        listener = SolanaChainListener(
            rpc_url=rpc_url,
            binance_wallets=binance_wallets,
            analyzer=self.analyzer,
            binance_filter=self.binance_filter,
            feishu_notifier=self.feishu_notifier
        )
        self.listeners['SOL'] = listener
        return listener

    def start_all(self, poll_intervals: Optional[Dict[str, int]] = None):
        """启动所有链监听（多线程）"""
        import threading

        if poll_intervals is None:
            poll_intervals = {
                'ETH': 12,   # 以太坊 12秒出块
                'BSC': 3,    # BSC 3秒出块
                'SOL': 2,    # Solana 亚秒级出块，但轮询间隔2秒
            }

        threads = []
        for chain, listener in self.listeners.items():
            interval = poll_intervals.get(chain, 12)
            thread = threading.Thread(
                target=listener.listen,
                kwargs={'poll_interval': interval},
                daemon=True,
                name=f"{chain}-Listener"
            )
            thread.start()
            threads.append(thread)
            print(f"✅ {chain} 监听线程已启动")

        print(f"\n{'='*80}")
        print(f"🎉 所有链监听器已启动!")
        print(f"{'='*80}\n")

        try:
            for thread in threads:
                thread.join()
        except KeyboardInterrupt:
            print("\n⏹️  所有监听器已停止")

    def get_summary_report(self):
        """获取所有链的汇总报告"""
        report = []
        report.append(f"\n{'='*80}")
        report.append(f"📊 多链新代币检测汇总")
        report.append(f"{'='*80}\n")

        for chain, listener in self.listeners.items():
            report.append(f"\n🔗 {chain} 链:")
            report.append(f"   总转账事件: {listener.stats['total_transfers']}")
            report.append(f"   已过滤代币: {listener.stats['filtered_tokens']}")
            report.append(f"   新发现代币: {listener.stats['new_tokens']} ⭐")
            report.append(f"   高置信度代币: {listener.stats['high_confidence_tokens']} 🔥")

            # 列出新代币
            new_tokens = [(c, b) for c, b in listener.new_tokens_buffer.items() if b.get('is_new', True)]
            if new_tokens:
                report.append(f"\n   未上架新代币:")
                for contract, buffer in new_tokens[:5]:  # 最多显示5个
                    token_info = listener.known_tokens.get(contract, {})
                    symbol = token_info.get('symbol', 'UNKNOWN')
                    analysis = buffer.get('analysis')
                    if analysis:
                        confidence = analysis['confidence']
                        report.append(f"      • {symbol}: {confidence:.2%} 置信度")
                    else:
                        report.append(f"      • {symbol}: 等待更多数据...")

        report.append(f"\n{'='*80}\n")
        return "\n".join(report)


def main():
    print("""
╔════════════════════════════════════════════════════════════════════════════╗
║              多链区块链监听器 - ETH + BSC + Solana                        ║
╚════════════════════════════════════════════════════════════════════════════╝

功能:
✅ 以太坊链 (Ethereum) 实时监听
✅ BSC链 (Binance Smart Chain) 实时监听
✅ Solana链实时监听
✅ 统一的币安代币过滤器
✅ 女巫攻击检测
✅ 多维度置信度评分
✅ 智能告警策略

使用方法:
    listener = MultiChainListener(enable_filter=True, proxy='127.0.0.1:7897')
    listener.add_eth_listener(rpc_url='YOUR_ETH_RPC', proxy='127.0.0.1:7897')
    listener.add_bsc_listener(rpc_url='YOUR_BSC_RPC', proxy='127.0.0.1:7897')
    listener.start_all()

╚════════════════════════════════════════════════════════════════════════════╝
    """)


if __name__ == '__main__':
    main()
