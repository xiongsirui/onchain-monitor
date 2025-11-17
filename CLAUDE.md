# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a blockchain on-chain deposit detector for identifying new cryptocurrency listings on Binance before official announcements. It monitors Binance's known wallet addresses across multiple blockchain networks to detect when new tokens are deposited, which historically precedes exchange listings by hours to days.

**Language**: Python 3
**Primary Files**:
- [multichain_listener.py](multichain_listener.py) - Multi-chain listener (ETH + BSC + Solana) 🆕⭐ **RECOMMENDED**
- [binance_token_filter.py](binance_token_filter.py) - Filter for already-listed Binance tokens
- [feishu_notifier.py](feishu_notifier.py) - Feishu (Lark) notification integration
- [run_multichain.py](run_multichain.py) - Multi-chain runtime entrypoint (ETH + BSC + optional Solana)
- [run_bsc.py](run_bsc.py) - BSC-only quick start script
- [run_feishu.py](run_feishu.py) - BSC with Feishu notifications

## Running the Code

### Method 1: Multi-Chain Listener (Recommended) 🆕⭐

This is the **recommended approach** that supports ETH, BSC, and Solana chains simultaneously with unified monitoring and filtering.

```bash
# Install dependencies
pip install -r requirements.txt

# Run the multi-chain listener
python3 run_multichain.py

# Or use directly in code
python3
>>> from multichain_listener import MultiChainListener
>>>
>>> # Create multi-chain listener
>>> listener = MultiChainListener(enable_filter=True, proxy='127.0.0.1:7897')
>>>
>>> # Add Ethereum listener
>>> listener.add_eth_listener(
...     rpc_url='https://eth-mainnet.g.alchemy.com/v2/YOUR_KEY',
...     proxy='127.0.0.1:7897'
... )
>>>
>>> # Add BSC listener
>>> listener.add_bsc_listener(
...     rpc_url='https://bsc-dataseed.binance.org/',
...     proxy='127.0.0.1:7897'
... )
>>>
>>> # Add Solana listener (optional, development in progress)
>>> listener.add_solana_listener(
...     rpc_url='https://api.mainnet-beta.solana.com'
... )
>>>
>>> # Start all chains (multi-threaded)
>>> listener.start_all()
>>>
>>> # OR start single chain
>>> listener.listeners['ETH'].listen(poll_interval=12)
>>> listener.listeners['BSC'].listen(poll_interval=3)
```

**Advantages of multi-chain listener**:
- ✅ Unified monitoring across ETH, BSC, and Solana
- ✅ Sub-second to 12-second latency depending on chain
- ✅ No API rate limiting
- ✅ Automatic filtering of 600+ already-listed Binance tokens
- ✅ Advanced sybil attack detection
- ✅ Multi-dimensional confidence scoring
- ✅ Smart alert strategy
- ✅ Multi-threaded for parallel monitoring

**Supported Chains**:
- **Ethereum (ETH)**: 12-second block time, comprehensive wallet coverage
- **BSC (Binance Smart Chain)**: 3-second block time, fastest detection ⚡
- **Solana**: Sub-second finality, development in progress

## Architecture

### Dependencies

```bash
# Install all dependencies
pip install -r requirements.txt

# Or manually
pip install web3>=6.0.0 requests>=2.28.0 solana>=0.30.0 solders>=0.18.0
```

**Note**: Solana dependencies (`solana` and `solders`) are only required if you plan to monitor the Solana chain. For ETH and BSC only, you can skip these.

## Architecture

### Core Detection Strategy

The system uses a multi-chain real-time listener approach:

**Multi-Chain Real-time Listener** ([multichain_listener.py](multichain_listener.py)) 🆕⭐
- Unified architecture for ETH, BSC, and Solana
- Direct blockchain node connection via Web3.py (EVM) and Solana RPC
- HTTP polling for reliable monitoring
- Multi-threaded parallel chain monitoring
- Shared token analyzer and filter
- Feishu notification integration

**Core workflow**:
1. **Wallet Monitoring**: Track known Binance hot/cold wallets across multiple chains
2. **Transaction Analysis**: Detect new token contracts from transfer events
3. **Validation**: Filter false positives and fraudulent signals
4. **Notification**: Send alerts via Feishu when new tokens detected

### Key Components

#### BinanceTokenFilter Class ([binance_token_filter.py](binance_token_filter.py))

Smart filter for identifying already-listed Binance tokens.

**Core Methods**:
- `__init__(cache_file, cache_hours)`: Initialize with local cache file (default 24h validity)
- `update_token_list()`: Fetch latest token list from Binance API and CoinGecko
- `_fetch_binance_symbols()`: Get all trading pairs from Binance exchange API
- `_fetch_contract_addresses(symbols)`: Map symbols to contract addresses via CoinGecko
- `is_listed_on_binance(contract_address)`: Check if contract is already listed → (bool, info)
- `is_symbol_listed(symbol)`: Check if symbol is already listed → bool
- `get_stats()`: Return filter statistics (total tokens, mappings, last update)

**Data Sources**:
1. **Binance API** (`/api/v3/exchangeInfo`): Get all trading pairs and base assets (600+ tokens)
2. **CoinGecko API** (`/coins/list?include_platform=true`): Map symbols to contract addresses (ETH + BSC)

**Cache Management**:
- Saves to `binance_tokens_cache.json` (JSON format)
- Auto-refresh when cache expires (configurable, default 24h)
- Fast in-memory lookups after initial load (O(1) hash table)

**Performance**:
- Initial load: ~30-60 seconds (depends on CoinGecko response time)
- Subsequent queries: < 1ms (memory lookup)
- Cache file size: ~200-500KB

**Data Structure**:
```python
{
    'tokens': {
        'BTC': {'symbol': 'BTC', 'name': 'Bitcoin', 'eth_contract': '0x...', ...},
        'ETH': {...},
        ...
    },
    'contract_map': {
        '0xdac17f958d2ee523a2206206994597c13d831ec7': 'USDT',  # lowercase
        '0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48': 'USDC',
        ...
    },
    'last_update': '2025-10-29T12:00:00',
    'total_count': 600
}
```

#### MultiChainListener Class ([multichain_listener.py](multichain_listener.py)) 🆕

**Multi-chain unified monitoring system** supporting ETH, BSC, and Solana.

**Core Architecture**:
- `BaseChainListener`: Abstract base class for all chain listeners
- `EVMChainListener`: EVM-compatible chains (Ethereum, BSC)
- `SolanaChainListener`: Solana-specific implementation
- `AdvancedTokenAnalyzer`: Shared analyzer for all chains
- `MultiChainListener`: Orchestrator for multi-chain monitoring

**Key Methods**:
- `add_eth_listener(rpc_url, ws_url, proxy)`: Add Ethereum chain listener
- `add_bsc_listener(rpc_url, ws_url, proxy)`: Add BSC chain listener
- `add_solana_listener(rpc_url)`: Add Solana chain listener
- `start_all(poll_intervals)`: Start all chains in parallel (multi-threaded)
- `get_summary_report()`: Generate cross-chain summary report

**Binance Wallet Coverage**:
- **Ethereum**: 8 hot wallets monitored
- **BSC**: 4 hot wallets monitored (including cross-chain bridges)
- **Solana**: 2 hot wallets monitored

**Multi-Chain Event Flow**:
```
[Thread 1: ETH] → EVMChainListener → BaseChainListener.process_transfer()
                                              ↓
[Thread 2: BSC] → EVMChainListener → BinanceTokenFilter (shared)
                                              ↓
[Thread 3: SOL] → SolanaChainListener → AdvancedTokenAnalyzer (shared)
                                              ↓
                                    Unified new_tokens_buffer
                                              ↓
                                    Cross-chain deduplication
```

**Chain-Specific Features**:

| Chain | Block Time | Poll Interval | Detection Speed | Status |
|-------|-----------|---------------|-----------------|--------|
| Ethereum | 12s | 12s | Medium | ✅ Production |
| BSC | 3s | 3s | Fast ⚡ | ✅ Production |
| Solana | <1s | 2s | Very Fast | ✅ Production |

**Shared Components**:
- Single `BinanceTokenFilter` instance across all chains
- Single `AdvancedTokenAnalyzer` for consistent scoring
- Thread-safe buffer management
- Unified alert system

#### FeishuNotifier Class ([feishu_notifier.py](feishu_notifier.py))

**Feishu (Lark) messaging integration** for real-time notifications.

**Core Methods**:
- `__init__(webhook_url)`: Initialize with Feishu webhook URL
- `send_new_token_alert(token_data, chain)`: Send token detection alert
- `send_message(title, content, color)`: Send custom message card
- `test_connection()`: Verify webhook connectivity

**Features**:
- Rich message cards with token details
- Color-coded alerts (red for warnings, green for success)
- Chain-specific formatting
- Error handling and retry logic

### Known Limitations

**multichain_listener.py**:
1. **No Cross-Chain Deduplication**: Same token on different chains treated as separate tokens
2. **Memory-only Storage**: Token buffers are per-listener, not persisted across restarts
3. **Thread Safety**: Buffer access not fully thread-safe (use locks for production)
4. **No Historical Backfill**: Only captures events from start time forward
5. **Solana Token Metadata**: Currently uses simplified token info (symbol/name based on mint address), requires Metaplex integration for full metadata

**binance_token_filter.py**:
1. **API Dependencies**: Requires Binance API and CoinGecko (both free but may have rate limits)
2. **Coverage Gaps**: Some tokens may not have contract addresses in CoinGecko database
3. **24h Cache**: Updates daily, may miss tokens listed in past 24h
4. **ETH/BSC Only**: Currently only maps Ethereum and BSC contracts (Solana needs manual addition)

**feishu_notifier.py**:
1. **No Retry Queue**: Failed notifications are logged but not retried
2. **Rate Limiting**: No built-in rate limiting for high-frequency alerts
3. **Single Webhook**: Only supports one webhook URL at a time

**All Components**:
- No database persistence (recommend PostgreSQL/MongoDB for production)
- Single-threaded per chain (could parallelize wallet queries within chain)
- No dynamic wallet discovery (relies on hardcoded wallet lists)

### Output Format

Token detection results include:
- Contract address
- Symbol and name
- Chain information (ETH, BSC, or Solana)
- Transaction count and unique senders
- Confidence score (with visual bar chart)
- Validation report with warnings
- Sybil attack patterns if detected
- Recommendation (high/medium/low confidence)
- Real-time notifications via Feishu

## Security Considerations

This code is designed for **authorized security research and market analysis only**. Key points:

1. **Public Data Only**: Uses public blockchain explorers and APIs
2. **No Trading Logic**: Detection only - does not execute trades
3. **Sybil Protection**: Built-in fraud detection to avoid manipulation
4. **Secure Configuration**: Use environment variables for sensitive data (API keys, webhooks)

**Do not** use this for:
- Acting on insider information
- Market manipulation
- Violating exchange terms of service
- Regulatory violations

## Testing Approach

Use the provided testing utilities:

1. **verify_installation.py**: Verify all dependencies are installed correctly
2. **test_feishu.py**: Test Feishu webhook integration
3. **Manual Testing**: Test against historical Binance listings to validate detection accuracy

Example test pattern:
```python
# Test multi-chain listener
from multichain_listener import MultiChainListener

listener = MultiChainListener(enable_filter=True)
listener.add_bsc_listener(rpc_url='https://bsc-dataseed.binance.org/')
# Monitor for a few blocks to verify detection
```
