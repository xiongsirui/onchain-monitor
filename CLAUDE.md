# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a blockchain on-chain deposit detector for identifying new cryptocurrency listings on Binance before official announcements. It monitors Binance's known wallet addresses across multiple blockchain networks to detect when new tokens are deposited, which historically precedes exchange listings by hours to days.

**Language**: Python 3
**Primary Files**:
- [multichain_listener.py](multichain_listener.py) - Multi-chain listener (ETH + BSC + Solana) 🆕⭐ **RECOMMENDED**
- [onchain_listener_advanced.py](onchain_listener_advanced.py) - Advanced ETH listener with full strategy
- [binance_token_filter.py](binance_token_filter.py) - Filter for already-listed Binance tokens
- [onchain_new_coin_detector.py](onchain_new_coin_detector.py) - API-based polling detector with sybil protection
- [example_multichain.py](example_multichain.py) - Multi-chain usage examples 🆕
- [test_filter.py](test_filter.py) - Filter testing script

## Running the Code

### Method 1: Multi-Chain Listener (Recommended) 🆕⭐

This is the **recommended approach** that supports ETH, BSC, and Solana chains simultaneously with unified monitoring and filtering.

```bash
# Install dependencies
pip install -r requirements.txt

# Run the multi-chain example
python3 example_multichain.py

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

### Method 2: Single-Chain Advanced Listener (ETH Only)

For Ethereum-only monitoring with full strategy analysis.

```bash
# Run advanced ETH listener
python3
>>> from onchain_listener_advanced import BlockchainListener
>>> listener = BlockchainListener(
...     rpc_url='https://eth-mainnet.g.alchemy.com/v2/YOUR_KEY',
...     ws_url='wss://eth-mainnet.g.alchemy.com/v2/YOUR_KEY',
...     enable_filter=True,
...     proxy='127.0.0.1:7897'
... )
>>> listener.listen_with_websocket()  # Real-time mode
>>> # OR
>>> listener.listen_with_polling()     # HTTP polling mode
```

**Features**:
- Real-time ERC20 Transfer event monitoring
- Auto-reconnect on failure
- Automatic filtering of already-listed tokens
- Sybil attack detection
- Data persistence

### Method 3: API-based Polling (Legacy)

Uses Etherscan/BSCScan APIs to periodically check for new deposits.

```bash
# Run the detector
python3 onchain_new_coin_detector.py

# Or use in code
python3
>>> from onchain_new_coin_detector import OnChainDepositDetector
>>> detector = OnChainDepositDetector()
>>> detector.etherscan_api_key = 'YOUR_ETHERSCAN_API_KEY'
>>> detector.bscscan_api_key = 'YOUR_BSCSCAN_API_KEY'
>>> new_tokens = detector.monitor_binance_wallets('ETH')
>>> # OR
>>> detector.comprehensive_monitor(interval=60)
```

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

The system implements three complementary approaches:

**A. Multi-Chain Real-time Listener** ([multichain_listener.py](multichain_listener.py)) 🆕⭐
- Unified architecture for ETH, BSC, and Solana
- Direct blockchain node connection via Web3.py (EVM) and Solana RPC
- HTTP polling for reliable monitoring
- Multi-threaded parallel chain monitoring
- Shared token analyzer and filter

**B. Single-Chain Advanced Listener** ([onchain_listener_advanced.py](onchain_listener_advanced.py))
- Ethereum-focused monitoring
- Real-time ERC20 Transfer event monitoring
- HTTP polling mode (Web3.py v6+ compatible)
- Data persistence with state recovery

**C. API-based Historical Analysis** ([onchain_new_coin_detector.py](onchain_new_coin_detector.py))
- Etherscan/BSCScan API integration
- Sybil attack detection and validation
- Comprehensive fraud filtering
- Legacy support

All approaches:
1. **Wallet Monitoring**: Track known Binance hot/cold wallets across multiple chains
2. **Transaction Analysis**: Detect new token contracts from transfer events
3. **Validation**: Filter false positives and fraudulent signals

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

#### BlockchainListener Class ([onchain_listener_advanced.py](onchain_listener_advanced.py))

Advanced single-chain (Ethereum) monitoring system with full strategy.

**Core Methods**:
- `__init__(rpc_url, ws_url, enable_filter, persistence_file, proxy)`: Initialize with persistence and proxy support
- `get_token_info(contract_address)`: Fetch ERC20 token metadata with caching
- `decode_transfer_log(log)`: Parse raw Transfer event logs
- `listen_with_websocket(callback)`: Real-time monitoring (uses HTTP polling in v6+)
- `listen_with_polling(from_block, poll_interval, callback)`: HTTP polling mode
- `process_transfer(transfer_data)`: Complete strategy analysis pipeline
- `_display_analysis(analysis, token_info)`: Rich analysis display
- `_check_alert_conditions(contract, buffer, analysis, token_info)`: Smart alert logic
- `_save_state()` / `_load_state()`: State persistence

**Event Detection Flow**:
```
Web3 WebSocket → Transfer Events → decode_transfer_log()
                                         ↓
                                  Filter by Binance wallets
                                         ↓
                                  get_token_info() → Cache
                                         ↓
                        is_listed_on_binance()? ← BinanceTokenFilter
                                    ↙         ↘
                            YES (listed)    NO (new!)
                                ↓               ↓
                         ⏭️ Skip/Log    🚨 Alert & Aggregate
                                                ↓
                                  new_tokens_buffer (is_new=True)
                                                ↓
                                  process_transfer() → Callback
```

**Buffer Structure**:
- `new_tokens_buffer`: Dict[contract_address] → {transfers: [], senders: set(), first_seen: datetime, is_new: bool, binance_symbol: str}
- Automatically aggregates all transfers by token contract
- Tracks unique senders for validation
- Records first detection timestamp
- **New**: `is_new` flag distinguishes unlisted vs already-listed tokens
- **New**: `binance_symbol` stores matched symbol for listed tokens

**Statistics Tracking**:
- `stats['total_transfers']`: Total transfer events captured
- `stats['filtered_tokens']`: Number of already-listed tokens filtered out
- `stats['new_tokens']`: Number of genuinely new (unlisted) tokens detected

**Connection Management**:
- Dual connection: HTTP (reliable queries) + WebSocket (real-time events)
- Auto-reconnect on WebSocket failure
- Graceful degradation to HTTP polling if WebSocket unavailable

#### OnChainDepositDetector Class ([onchain_new_coin_detector.py](onchain_new_coin_detector.py))

Main detector class with several functional modules:

**Wallet Address Lists** (lines 38-79)
- `binance_hot_wallets`: Dictionary of known Binance hot wallet addresses by chain
- `binance_cold_wallets`: Dictionary of cold storage addresses
- Addresses are validated and updated as of October 2024

**Sybil Attack Detection** (lines 88-366)
- `sybil_protection`: Configuration parameters for filtering fraudulent signals
- `get_address_info()`: Retrieves wallet metadata (balance, age, transaction count)
- `check_address_legitimacy()`: Validates individual sender addresses
- `detect_sybil_patterns()`: Identifies coordinated attack patterns (same timestamps, amounts, sequential nonces)
- `analyze_sender_network()`: Analyzes relationships between sender addresses
- `validate_token_transfers()`: Comprehensive validation combining all checks

**Detection Methods**:

1. **Method 1: Hot Wallet Monitoring** (lines 368-550)
   - `get_erc20_transfers_to_address()`: Fetches token transfers via Etherscan API
   - `analyze_new_tokens()`: Aggregates transfers by token contract and validates legitimacy
   - `monitor_binance_wallets()`: Main monitoring loop for wallet activity

2. **Method 2: Factory Contract Monitoring** (lines 552-575)
   - `get_recent_token_creations()`: Monitors DEX factory contracts (Uniswap, PancakeSwap)
   - Placeholder for Web3.py implementation

3. **Method 3: Dune Analytics** (lines 577-593)
   - `query_dune_analytics()`: Interface for Dune Analytics SQL queries
   - Placeholder for API integration

4. **Method 4: Large Transfer Detection** (lines 595-621)
   - `detect_large_transfers()`: Tracks high-value token movements to Binance
   - Useful for detecting market maker preparation

5. **Method 5: Testnet Monitoring** (lines 623-639)
   - `monitor_testnet_activity()`: Tracks Binance activity on test networks
   - Can signal upcoming mainnet listings

6. **Method 6: Telegram Alerts** (lines 641-665)
   - `setup_telegram_alerts()`: Real-time notifications via Telegram bot

**Continuous Monitoring** (lines 667-707)
- `comprehensive_monitor()`: Main loop combining all detection methods
- Configurable interval between checks

### Data Flow

```
External APIs (Etherscan/BSCScan)
    ↓
get_erc20_transfers_to_address()
    ↓
analyze_new_tokens()
    ↓
validate_token_transfers() → Sybil Detection
    ↓
monitor_binance_wallets() → Results with confidence scores
    ↓
comprehensive_monitor() → Optional Telegram alerts
```

### Validation Pipeline

Each detected token goes through:
1. Basic aggregation (transaction count, unique senders)
2. Address legitimacy checks (balance, age, activity)
3. Pattern detection (timestamp clustering, amount similarity, nonce sequences)
4. Network analysis (sender relationships)
5. Confidence scoring (0.0-1.0 range)
6. Final filtering (only tokens with confidence > 0.3 or is_valid=True)

## Important Implementation Details

### API Rate Limiting

- Built-in 0.2 second delays between API calls (line 548)
- Etherscan/BSCScan free tier: 5 requests/second
- Consider implementing exponential backoff for production use

### Token Validation Thresholds

Defined in `sybil_protection` dict (lines 88-100):
- Minimum sender balance: 0.1 ETH
- Minimum account age: 30 days
- Minimum transaction count: 10 txs
- Minimum unique senders: 3 addresses
- Confidence threshold: 0.5 for validity

These can be tuned based on false positive/negative rates in production.

### Known Limitations

**multichain_listener.py**:
1. **No Cross-Chain Deduplication**: Same token on different chains treated as separate tokens
2. **Memory-only Storage**: Token buffers are per-listener, not persisted across restarts
3. **Thread Safety**: Buffer access not fully thread-safe (use locks for production)
4. **No Historical Backfill**: Only captures events from start time forward
5. **Solana Token Metadata**: Currently uses simplified token info (symbol/name based on mint address), requires Metaplex integration for full metadata

**onchain_listener_advanced.py**:
1. **Single Chain**: Currently only monitors Ethereum mainnet
2. **Basic Filtering Only**: Uses BinanceTokenFilter but integrated sybil detection
3. **Memory-only Storage**: Token buffer lost on restart (uses pickle for state)
4. **No Historical Backfill**: Only captures events from start time forward

**binance_token_filter.py**:
1. **API Dependencies**: Requires Binance API and CoinGecko (both free but may have rate limits)
2. **Coverage Gaps**: Some tokens may not have contract addresses in CoinGecko database
3. **24h Cache**: Updates daily, may miss tokens listed in past 24h
4. **ETH/BSC Only**: Currently only maps Ethereum and BSC contracts (Solana needs manual addition)

**onchain_new_coin_detector.py**:
1. **Incomplete Implementations**: Methods 2-5 are placeholders requiring Web3.py, Dune API, or additional infrastructure
2. **Block Range**: Currently queries all historical blocks - should be optimized to recent blocks in production
3. **Network Analysis**: `analyze_sender_network()` is a stub
4. **No Persistent Storage**: Detected tokens tracked only in memory via `known_tokens` set

**All**:
- No database persistence (recommend PostgreSQL/MongoDB for production)
- No Telegram/Discord integration (webhook support recommended)
- Single-threaded per chain (could parallelize wallet queries within chain)
- No dynamic wallet discovery (relies on hardcoded wallet lists)

### Output Format

Token detection results include:
- Contract address
- Symbol and name
- Transaction count and unique senders
- Confidence score (with visual bar chart)
- Validation report with warnings
- Sybil attack patterns if detected
- Recommendation (high/medium/low confidence)

## Security Considerations

This code is designed for **authorized security research and market analysis only**. Key points:

1. **Public Data Only**: Uses public blockchain explorers and APIs
2. **No Trading Logic**: Detection only - does not execute trades
3. **Risk Warnings**: Comprehensive risk disclosure in usage guide (lines 892-908)
4. **Sybil Protection**: Built-in fraud detection to avoid manipulation

**Do not** use this for:
- Acting on insider information
- Market manipulation
- Violating exchange terms of service
- Regulatory violations

## Testing Approach

No formal tests exist yet. To validate changes:

1. **Mock API Responses**: Test with sample transaction data
2. **Sybil Detection**: Create test cases with coordinated wallets
3. **Known Token Dataset**: Test against historical Binance listings
4. **Rate Limiting**: Verify API call throttling works correctly

Example test pattern:
```python
# Create detector with mock data
detector = OnChainDepositDetector()
test_transactions = [...]  # Load fixture
new_tokens = detector.analyze_new_tokens(test_transactions)
assert len(new_tokens) > 0
assert all(token['confidence'] >= 0.3 for token in new_tokens)
```
