# 项目结构说明

## 📁 核心文件（必需）

### 1. 监听器核心
| 文件 | 大小 | 说明 |
|------|------|------|
| [multichain_listener.py](multichain_listener.py) | 36K | **多链统一监听器**（推荐）- 支持 ETH、BSC、Solana |
| [binance_token_filter.py](binance_token_filter.py) | 12K | **代币过滤器** - 过滤已上架代币 |
| [onchain_listener_advanced.py](onchain_listener_advanced.py) | 35K | ETH 单链高级监听器（可选） |

### 2. 启动脚本
| 文件 | 大小 | 说明 |
|------|------|------|
| [run_bsc.py](run_bsc.py) | 5.5K | **BSC 一键启动**（最简单）⭐ |
| [example_multichain.py](example_multichain.py) | 7.6K | 多链示例（6个完整示例） |
| [run.py](run.py) | 4.6K | ETH 单链启动（可选） |

### 3. 配置和工具
| 文件 | 大小 | 说明 |
|------|------|------|
| [config_template.py](config_template.py) | 4.5K | 配置文件模板 |
| [verify_installation.py](verify_installation.py) | 7.0K | 安装验证脚本 |

### 4. 文档
| 文件 | 大小 | 说明 |
|------|------|------|
| [README.md](README.md) | 11K | **项目主文档** - 完整功能说明 |
| [QUICKSTART.md](QUICKSTART.md) | 5.9K | **快速上手指南** - 5分钟开始 |
| [CLAUDE.md](CLAUDE.md) | 19K | 开发者详细文档 - 架构和 API |

---

## 🎯 推荐使用方式

### 新手用户（最简单）
```bash
python3 run_bsc.py
```
- ✅ 无需配置
- ✅ 免费 RPC
- ✅ 3秒出块，最快

### 进阶用户（多链监控）
```bash
python3 example_multichain.py
```
- ✅ ETH + BSC 双链
- ✅ 多线程并行
- ✅ 统一管理

### 开发者（自定义）
```python
from multichain_listener import MultiChainListener

listener = MultiChainListener(enable_filter=True)
listener.add_bsc_listener('https://bsc-dataseed.binance.org/')
listener.listeners['BSC'].listen(poll_interval=3)
```

---

## 🗑️ 已删除的文件（不再需要）

以下文件已被删除，功能已被其他文件覆盖：

| 删除的文件 | 替代方案 |
|----------|---------|
| `test_connection.py` | → `verify_installation.py` |
| `test_fxs_filter.py` | → 临时测试文件，不再需要 |
| `README_old.md` | → `README.md` |
| `FXS_ANALYSIS.md` | → 过时文档，已删除 |
| `FXS_FIX_SUMMARY.md` | → 过时文档，已删除 |
| `PROJECT_OVERVIEW.md` | → `README.md` + `CLAUDE.md` |
| `PROXY_GUIDE.md` | → `README.md` 中的代理配置章节 |
| `TROUBLESHOOTING.md` | → `README.md` 中的常见问题章节 |
| `WALLET_UPDATE.md` | → 已过时 |
| `WEBSOCKET_FIX.md` | → 已过时 |

---

## 📦 数据文件（自动生成）

以下文件会在运行时自动生成，不需要手动创建：

| 文件 | 说明 |
|------|------|
| `binance_tokens_cache.json` | 币安代币缓存（24h有效） |
| `listener_state.pkl` | ETH 监听器状态持久化 |
| `multichain_state.pkl` | 多链监听器状态持久化 |

---

## 📊 项目统计

- **Python 文件**: 8 个（总计 ~112K）
- **文档文件**: 3 个（总计 ~36K）
- **总代码行数**: ~1,900 行

---

## ✨ 优化成果

### 删除前
- Python 文件: 10 个
- 文档文件: 10 个
- 冗余/过时文件: 多个

### 删除后
- Python 文件: 8 个（精简）
- 文档文件: 3 个（整合）
- 结构清晰，易于维护 ✅

---

## 🎉 结论

项目结构已优化完成！

- ✅ 删除了 10 个冗余/过时文件
- ✅ 保留了 11 个核心文件
- ✅ 文档整合为 3 个主要文档
- ✅ 代码结构清晰，易于维护

**立即开始使用**: `python3 run_bsc.py`
