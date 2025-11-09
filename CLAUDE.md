# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a blockchain on-chain deposit detector for identifying new cryptocurrency listings on Binance before official announcements. It monitors Binance's known wallet addresses across multiple blockchain networks to detect when new tokens are deposited, which historically precedes exchange listings by hours to days.

**Language**: Python 3
**Primary Files**:
- [onchain_listener.py](onchain_listener.py) - Real-time blockchain node listener (recommended) ⭐
- [binance_token_filter.py](binance_token_filter.py) - Filter for already-listed Binance tokens 🆕
- [onchain_new_coin_detector.py](onchain_new_coin_detector.py) - API-based polling detector with sybil protection
- [example_listener.py](example_listener.py) - Usage examples
- [test_filter.py](test_filter.py) - Filter testing script 🆕

## Running the Code

### Method 1: Real-time Blockchain Listener with Smart Filtering (Recommended)

This method uses Web3.py to directly connect to blockchain nodes for real-time event monitoring, combined with intelligent filtering to ignore already-listed tokens. It's faster, more reliable, and has no API rate limits.

```bash
# Install dependencies
pip install -r requirements.txt

# Run the example
python3 example_listener.py

# Or use directly in code
python3
>>> from onchain_listener import BlockchainListener
>>> listener = BlockchainListener(
...     rpc_url='https://eth-mainnet.g.alchemy.com/v2/YOUR_KEY',
...     ws_url='wss://eth-mainnet.g.alchemy.com/v2/YOUR_KEY'
... )
>>> listener.listen_with_websocket()  # Real-time WebSocket mode
>>> # OR
>>> listener.listen_with_polling()     # HTTP polling mode (backup)
```

**Advantages of blockchain listener with filter**:
- Sub-second latency with WebSocket
- No API rate limiting
- Complete event data
- Auto-reconnect on failure
- Automatic filtering of 600+ already-listed Binance tokens
- Local caching (24h validity) for fast lookups

### Method 2: API-based Polling (Legacy)

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
pip install web3>=6.0.0 requests>=2.28.0
```

## Architecture

### Core Detection Strategy

The system implements two complementary approaches:

**A. Real-time Event Listening** ([onchain_listener.py](onchain_listener.py))
- Direct blockchain node connection via Web3.py
- WebSocket streaming for sub-second latency
- HTTP polling fallback mode
- Real-time ERC20 Transfer event monitoring

**B. API-based Historical Analysis** ([onchain_new_coin_detector.py](onchain_new_coin_detector.py))
- Etherscan/BSCScan API integration
- Sybil attack detection and validation
- Comprehensive fraud filtering
- Multi-chain support

Both approaches:
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

#### BlockchainListener Class ([onchain_listener.py](onchain_listener.py))

Real-time blockchain event monitoring system.

**Core Methods**:
- `__init__(rpc_url, ws_url, enable_filter)`: Initialize Web3 connections + optional filter (HTTP for queries, WebSocket for events)
- `get_token_info(contract_address)`: Fetch ERC20 token metadata (name, symbol, decimals) with caching
- `decode_transfer_log(log)`: Parse raw Transfer event logs into structured data
- `listen_with_websocket(callback)`: Real-time event streaming via WebSocket (recommended)
- `listen_with_polling(from_block, poll_interval, callback)`: HTTP-based block polling (fallback)
- `process_transfer(transfer_data)`: Handle detected transfers, **filter already-listed tokens**, aggregate by token, trigger alerts

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

**onchain_listener.py**:
1. **Single Chain**: Currently only monitors Ethereum mainnet (easy to extend to BSC/Polygon)
2. **Basic Filtering Only**: Uses BinanceTokenFilter but no sybil attack detection (consider integrating with detector's validation)
3. **Memory-only Storage**: Token buffer lost on restart
4. **No Historical Backfill**: Only captures events from start time forward

**binance_token_filter.py**:
1. **API Dependencies**: Requires Binance API and CoinGecko (both free but may have rate limits)
2. **Coverage Gaps**: Some tokens may not have contract addresses in CoinGecko database
3. **24h Cache**: Updates daily, may miss tokens listed in past 24h
4. **ETH/BSC Only**: Currently only maps Ethereum and BSC contracts (Polygon/Arbitrum need manual addition)

**onchain_new_coin_detector.py**:
1. **Incomplete Implementations**: Methods 2-5 are placeholders requiring Web3.py, Dune API, or additional infrastructure
2. **Block Range**: Currently queries all historical blocks (line 502) - should be optimized to recent blocks in production
3. **Network Analysis**: `analyze_sender_network()` is a stub (lines 281-308)
4. **No Persistent Storage**: Detected tokens tracked only in memory via `known_tokens` set

**Both**:
- No database persistence
- No Telegram/Discord integration in listener
- Single-threaded (could parallelize multi-chain monitoring)

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
