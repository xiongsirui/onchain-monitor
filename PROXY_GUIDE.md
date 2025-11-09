# 代理配置指南

## 问题

如果你在国内或需要通过代理访问外网，可能会遇到以下错误：

```
❌ RPC 节点连接失败
```

## 解决方案

✅ 已支持 HTTP/SOCKS5 代理配置

## 配置方法

### 1. 编辑 run.py

找到第 27-29 行，配置你的代理：

```python
# 代理配置（如果需要）
# 格式: "http://127.0.0.1:7890" 或 "socks5://127.0.0.1:7891"
PROXY = "http://127.0.0.1:7897"  # 如果不需要代理，设为 None
```

### 2. 代理格式

支持以下格式：

```python
# HTTP 代理
PROXY = "http://127.0.0.1:7897"

# HTTPS 代理
PROXY = "https://127.0.0.1:7897"

# SOCKS5 代理（需要安装 pysocks: pip install pysocks）
PROXY = "socks5://127.0.0.1:7891"

# 不使用代理
PROXY = None
```

### 3. 常见代理软件配置

#### Clash
```python
PROXY = "http://127.0.0.1:7890"  # Clash 默认端口
```

#### V2Ray
```python
PROXY = "socks5://127.0.0.1:10808"  # V2Ray 默认 SOCKS5 端口
# 或
PROXY = "http://127.0.0.1:10809"   # V2Ray 默认 HTTP 端口
```

#### Shadowsocks
```python
PROXY = "socks5://127.0.0.1:1080"  # SS 默认端口
```

#### 自定义端口
```python
PROXY = "http://127.0.0.1:你的端口"  # 替换为你的实际端口
```

## 技术实现

### 1. Web3.py 代理支持

```python
# onchain_listener_advanced.py
if proxy:
    request_kwargs = {'proxies': {'http': proxy, 'https': proxy}}
    self.w3 = Web3(Web3.HTTPProvider(rpc_url, request_kwargs=request_kwargs))
```

### 2. Requests 代理支持

```python
# binance_token_filter.py
self.session = requests.Session()
if proxy:
    self.session.proxies = {
        'http': proxy,
        'https': proxy
    }
```

## 代理作用范围

配置代理后，以下所有网络请求都会通过代理：

✅ **RPC 节点连接**
- 连接 https://eth.llmamarpc.com
- 查询区块链数据
- 获取 Transfer 事件

✅ **Binance API**
- 获取已上架代币列表
- https://api.binance.com/api/v3/exchangeInfo

✅ **CoinGecko API**
- 获取合约地址映射
- https://api.coingecko.com/api/v3/coins/list

## 测试代理连接

### 1. 测试 RPC 连接

```bash
python3 run.py
```

如果看到：
```
🔄 使用代理: http://127.0.0.1:7897
✅ RPC 已连接: https://eth.llmamarpc.com
   当前区块: 12345678
```

说明代理配置成功！

### 2. 测试 Binance API

```bash
python3 -c "
from binance_token_filter import BinanceTokenFilter
f = BinanceTokenFilter(proxy='http://127.0.0.1:7897')
print(f.get_stats())
"
```

如果看到：
```
🔄 BinanceTokenFilter 使用代理: http://127.0.0.1:7897
📡 正在从币安 API 获取交易对列表...
   找到 628 个币安已上架代币
```

说明 API 请求成功！

## 常见问题

### Q1: 报错 "Connection refused"
**A**: 检查代理软件是否正在运行，端口是否正确

```bash
# 测试代理端口
curl -x http://127.0.0.1:7897 https://www.google.com
```

### Q2: 报错 "Proxy error"
**A**:
1. 确认代理协议正确（http/https/socks5）
2. 确认代理软件允许局域网连接
3. 检查防火墙设置

### Q3: SOCKS5 代理报错 "Missing dependencies"
**A**: 需要安装 pysocks

```bash
pip install pysocks
# 或
pip install requests[socks]
```

### Q4: 部分请求走代理，部分不走
**A**:
- Web3.py 和 requests 都已配置代理
- 确认 `run.py` 中 `PROXY` 参数正确传递
- 检查是否有系统环境变量覆盖（`HTTP_PROXY`, `HTTPS_PROXY`）

### Q5: 如何验证是否通过代理
**A**: 查看代理软件日志，应该能看到：
- `eth.llmamarpc.com` 的请求
- `api.binance.com` 的请求
- `api.coingecko.com` 的请求

## 性能影响

| 指标 | 无代理 | 使用代理 |
|------|--------|----------|
| RPC 延迟 | 50-100ms | 100-300ms |
| API 延迟 | 100-200ms | 200-500ms |
| 稳定性 | ✅ | ✅ |

**结论**: 使用代理会增加 100-300ms 延迟，对新币检测场景影响可忽略。

## 环境变量方式（高级）

如果不想修改代码，也可以设置环境变量：

```bash
# Linux/Mac
export HTTP_PROXY=http://127.0.0.1:7897
export HTTPS_PROXY=http://127.0.0.1:7897
python3 run.py

# Windows (PowerShell)
$env:HTTP_PROXY="http://127.0.0.1:7897"
$env:HTTPS_PROXY="http://127.0.0.1:7897"
python run.py
```

**注意**: 环境变量优先级低于代码配置，建议直接修改 `run.py`。

## 安全建议

⚠️ **代理安全**
- 只使用可信的代理服务器
- 不要使用不明来源的免费代理
- 定期检查代理软件更新
- 注意 API Key 不要通过不安全的代理传输

## 总结

✅ **已完成**
- Web3.py 代理支持
- Binance API 代理支持
- CoinGecko API 代理支持
- HTTP/HTTPS/SOCKS5 全协议支持

✅ **使用简单**
- 只需修改 `run.py` 一行配置
- 自动应用到所有网络请求
- 支持主流代理软件

现在可以在任何网络环境下运行程序了！🎉
