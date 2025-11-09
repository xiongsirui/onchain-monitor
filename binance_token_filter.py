#!/usr/bin/env python3
"""
币安已上架代币过滤器

功能：
1. 从币安 API 获取已上架代币列表
2. 缓存代币列表到本地文件
3. 提供合约地址查询接口
4. 自动更新（可配置）
"""

import requests
import json
import time
from datetime import datetime, timedelta
from pathlib import Path


class BinanceTokenFilter:
    """
    币安代币过滤器
    """

    def __init__(self, cache_file='binance_tokens_cache.json', cache_hours=24, proxy=None):
        """
        初始化过滤器

        参数:
            cache_file: 缓存文件路径
            cache_hours: 缓存有效期（小时）
            proxy: 代理服务器 (例如: "http://127.0.0.1:7897" 或 "127.0.0.1:7897")
        """
        self.cache_file = Path(cache_file)
        self.cache_hours = cache_hours
        self.tokens = {}  # symbol -> info
        self.contract_map = {}  # contract_address -> symbol
        self.last_update = None

        # 规范化代理格式
        if proxy:
            # 如果代理格式不含协议前缀，自动添加 http://
            if not proxy.startswith(('http://', 'https://', 'socks5://', 'socks4://')):
                proxy = f'http://{proxy}'

        self.proxy = proxy

        # 配置 requests 代理
        self.session = requests.Session()
        if proxy:
            self.session.proxies = {
                'http': proxy,
                'https': proxy
            }
            print(f"🔄 BinanceTokenFilter 使用代理: {proxy}")

        # 加载缓存
        self._load_cache()

    def _load_cache(self):
        """
        从缓存文件加载数据
        """
        if not self.cache_file.exists():
            print("⚠️  缓存文件不存在，将从币安 API 获取数据")
            self.update_token_list()
            return

        try:
            with open(self.cache_file, 'r', encoding='utf-8') as f:
                data = json.load(f)

            self.tokens = data.get('tokens', {})
            self.contract_map = data.get('contract_map', {})
            self.last_update = datetime.fromisoformat(data.get('last_update', '2000-01-01'))

            print(f"✅ 已加载缓存: {len(self.tokens)} 个代币")
            print(f"   最后更新: {self.last_update.strftime('%Y-%m-%d %H:%M:%S')}")

            # 检查是否需要更新
            if datetime.now() - self.last_update > timedelta(hours=self.cache_hours):
                print(f"⚠️  缓存已过期（超过 {self.cache_hours} 小时），开始更新...")
                self.update_token_list()

        except Exception as e:
            print(f"❌ 加载缓存失败: {e}")
            self.update_token_list()

    def _save_cache(self):
        """
        保存数据到缓存文件
        """
        try:
            data = {
                'tokens': self.tokens,
                'contract_map': self.contract_map,
                'last_update': datetime.now().isoformat(),
                'total_count': len(self.tokens)
            }

            with open(self.cache_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)

            print(f"✅ 缓存已保存: {self.cache_file}")

        except Exception as e:
            print(f"❌ 保存缓存失败: {e}")

    def update_token_list(self):
        """
        从币安 API 更新代币列表

        使用多个数据源:
        1. 币安现货交易对列表
        2. CoinGecko API（补充合约地址）
        """
        print(f"\n{'='*80}")
        print("🔄 更新币安代币列表")
        print(f"{'='*80}\n")

        # 步骤 1: 获取币安交易对
        binance_symbols = self._fetch_binance_symbols()

        # 步骤 2: 获取合约地址（从 CoinGecko）
        self._fetch_contract_addresses(binance_symbols)

        # 步骤 3: 保存缓存
        self.last_update = datetime.now()
        self._save_cache()

        print(f"\n✅ 更新完成:")
        print(f"   总代币数: {len(self.tokens)}")
        print(f"   已映射合约: {len(self.contract_map)}")

    def _fetch_binance_symbols(self):
        """
        从币安 API 获取交易对列表

        返回:
            代币 symbol 集合
        """
        print("📡 正在从币安 API 获取交易对列表...")

        try:
            # 币安现货交易对信息
            url = "https://api.binance.com/api/v3/exchangeInfo"
            response = self.session.get(url, timeout=10)
            data = response.json()

            symbols = set()
            for pair in data['symbols']:
                if pair['status'] == 'TRADING':
                    # 只要基础代币（例如 BTCUSDT 中的 BTC）
                    base_asset = pair['baseAsset']
                    symbols.add(base_asset)

            print(f"   找到 {len(symbols)} 个币安已上架代币")
            self.tokens = {symbol: {'symbol': symbol, 'source': 'binance'} for symbol in symbols}

            return symbols

        except Exception as e:
            print(f"❌ 获取币安交易对失败: {e}")
            return set()

    def _fetch_contract_addresses(self, symbols):
        """
        从 CoinGecko 获取合约地址

        参数:
            symbols: 代币 symbol 集合
        """
        print(f"\n📡 正在从 CoinGecko 获取合约地址...")
        print("   （这可能需要几分钟，请耐心等待...）\n")

        # CoinGecko API（免费，无需 API key）
        url = "https://api.coingecko.com/api/v3/coins/list"
        params = {
            'include_platform': 'true'
        }

        try:
            response = self.session.get(url, params=params, timeout=30)
            coins = response.json()

            mapped_count = 0
            for coin in coins:
                symbol = coin.get('symbol', '').upper()

                # 只处理币安已上架的代币
                if symbol not in symbols:
                    continue

                # 提取平台信息
                platforms = coin.get('platforms', {})

                # 提取 Ethereum 合约地址
                eth_contract = platforms.get('ethereum', '').strip()
                if eth_contract and eth_contract != '':
                    # 转换为标准格式
                    eth_contract = eth_contract.lower()
                    if eth_contract.startswith('0x') and len(eth_contract) == 42:
                        self.contract_map[eth_contract] = symbol
                        self.tokens[symbol]['eth_contract'] = eth_contract
                        mapped_count += 1

                # 提取 BSC 合约地址
                bsc_contract = platforms.get('binance-smart-chain', '').strip()
                if bsc_contract and bsc_contract != '':
                    bsc_contract = bsc_contract.lower()
                    if bsc_contract.startswith('0x') and len(bsc_contract) == 42:
                        self.contract_map[bsc_contract] = symbol
                        self.tokens[symbol]['bsc_contract'] = bsc_contract

                # 添加其他信息
                self.tokens[symbol].update({
                    'name': coin.get('name', ''),
                    'coingecko_id': coin.get('id', '')
                })

                # 显示进度
                if mapped_count % 50 == 0:
                    print(f"   已处理 {mapped_count} 个代币...")

            print(f"\n   成功映射 {mapped_count} 个 Ethereum 合约地址")

        except Exception as e:
            print(f"❌ 获取 CoinGecko 数据失败: {e}")
            print("   将只使用币安交易对列表（无合约地址过滤）")

    def is_listed_on_binance(self, contract_address):
        """
        检查合约地址是否已在币安上架

        参数:
            contract_address: 合约地址

        返回:
            (is_listed, token_info)
        """
        # 标准化地址
        contract_address = contract_address.lower().strip()

        if contract_address in self.contract_map:
            symbol = self.contract_map[contract_address]
            return True, self.tokens.get(symbol)

        return False, None

    def is_symbol_listed(self, symbol):
        """
        检查代币符号是否已在币安上架

        参数:
            symbol: 代币符号（如 BTC, ETH）

        返回:
            bool
        """
        return symbol.upper() in self.tokens

    def get_token_info(self, contract_address):
        """
        获取代币详细信息

        参数:
            contract_address: 合约地址

        返回:
            代币信息字典，如果未上架返回 None
        """
        is_listed, info = self.is_listed_on_binance(contract_address)
        return info if is_listed else None

    def get_stats(self):
        """
        获取统计信息

        返回:
            统计信息字典
        """
        eth_contracts = sum(1 for t in self.tokens.values() if 'eth_contract' in t)
        bsc_contracts = sum(1 for t in self.tokens.values() if 'bsc_contract' in t)

        return {
            'total_tokens': len(self.tokens),
            'eth_contracts': eth_contracts,
            'bsc_contracts': bsc_contracts,
            'last_update': self.last_update.isoformat() if self.last_update else None,
            'cache_file': str(self.cache_file)
        }

    def print_stats(self):
        """
        打印统计信息
        """
        stats = self.get_stats()

        print(f"\n{'='*80}")
        print("📊 币安代币过滤器统计")
        print(f"{'='*80}")
        print(f"  总代币数: {stats['total_tokens']}")
        print(f"  Ethereum 合约: {stats['eth_contracts']}")
        print(f"  BSC 合约: {stats['bsc_contracts']}")
        print(f"  最后更新: {stats['last_update']}")
        print(f"  缓存文件: {stats['cache_file']}")
        print(f"{'='*80}\n")


def main():
    """
    测试函数
    """
    print("""
╔════════════════════════════════════════════════════════════════════════════╗
║                      币安已上架代币过滤器                                  ║
╚════════════════════════════════════════════════════════════════════════════╝

功能：
1. 从币安 API 获取所有已上架代币
2. 从 CoinGecko 获取对应的合约地址
3. 提供快速查询接口
4. 自动缓存，定期更新

使用方法：
    filter = BinanceTokenFilter()

    # 检查合约地址
    is_listed, info = filter.is_listed_on_binance('0x...')

    # 检查代币符号
    is_listed = filter.is_symbol_listed('BTC')

    # 强制更新
    filter.update_token_list()

    """)

    # 创建过滤器
    filter = BinanceTokenFilter()

    # 显示统计
    filter.print_stats()

    # 测试几个合约地址
    print("\n🧪 测试合约地址查询:\n")

    test_contracts = [
        ('0xdac17f958d2ee523a2206206994597c13d831ec7', 'USDT'),  # 已上架
        ('0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48', 'USDC'),  # 已上架
        ('0x1234567890123456789012345678901234567890', '未知'),  # 未上架
    ]

    for contract, expected in test_contracts:
        is_listed, info = filter.is_listed_on_binance(contract)
        status = "✅ 已上架" if is_listed else "🆕 未上架"
        symbol = info['symbol'] if info else 'N/A'
        print(f"   {contract[:10]}...{contract[-8:]}: {status} ({symbol})")

    print()


if __name__ == '__main__':
    main()
