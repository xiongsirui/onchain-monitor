# 问题排查指南

## ✅ 已修复的问题

### 1. 代理格式自动规范化

现在支持简化的代理格式，程序会自动添加协议前缀：

```python
# 所有格式都支持：
PROXY = "127.0.0.1:7897"              # ✅ 自动转换为 http://127.0.0.1:7897
PROXY = "http://127.0.0.1:7897"       # ✅ 完整格式
PROXY = "socks5://127.0.0.1:7891"     # ✅ SOCKS5
PROXY = None                          # ✅ 不使用代理
```

## 🔍 当前运行环境检查清单

在运行 `python run.py` 之前，请检查：

### 1. Python 环境

```bash
# 检查 Python 版本（需要 Python 3.7+）
python --version

# 检查是否在 conda 环境中
conda info --envs

# 检查必需的包是否已安装
python -c "import web3; import requests; print('✅ 依赖已安装')"
```

如果报错 `ModuleNotFoundError`，请安装：

```bash
# 使用 conda（推荐）
conda install -c conda-forge web3 requests

# 或使用 pip（如果 conda 不行）
pip install web3 requests
```

### 2. 代理检查

```bash
# 测试代理是否工作
curl -x http://127.0.0.1:7897 https://www.google.com

# 如果成功，应该返回 Google 首页 HTML
# 如果失败，检查：
#   1. 代理软件是否正在运行
#   2. 端口号是否正确（7897）
#   3. 防火墙是否阻止
```

### 3. RPC 节点检查

```bash
# 直接测试 RPC 节点（通过代理）
curl -x http://127.0.0.1:7897 https://eth.llmamarpc.com \
  -X POST \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","method":"eth_blockNumber","params":[],"id":1}'

# 预期输出（类似）:
# {"jsonrpc":"2.0","id":1,"result":"0x145a3f0"}
```

如果失败：
- 检查代理是否正在运行
- 尝试其他 RPC 节点（见下方列表）

## 🌐 备用 RPC 节点

如果 `https://eth.llmamarpc.com` 无法访问，尝试以下节点：

```python
# 1. LlamaNodes（免费，无需注册）
RPC_URL = "https://eth.llamarpc.com"

# 2. Ankr（免费，无需注册）
RPC_URL = "https://rpc.ankr.com/eth"

# 3. Cloudflare（免费，无需注册）
RPC_URL = "https://cloudflare-eth.com"

# 4. Alchemy（需要注册，免费额度大）
RPC_URL = "https://eth-mainnet.g.alchemy.com/v2/YOUR_API_KEY"

# 5. Infura（需要注册）
RPC_URL = "https://mainnet.infura.io/v3/YOUR_API_KEY"
```

## 🐛 常见错误排查

### 错误 1: `ModuleNotFoundError: No module named 'web3'`

**原因**: 依赖未安装

**解决方案**:
```bash
# 方案 1: conda（推荐）
conda install -c conda-forge web3 requests

# 方案 2: pip
pip install web3 requests

# 方案 3: 使用代理安装（如果网络问题）
pip install --proxy http://127.0.0.1:7897 web3 requests
```

### 错误 2: `❌ RPC 节点连接失败`

**可能原因**:

1. **代理未运行**
   ```bash
   # 检查代理进程
   ps aux | grep clash  # 或 v2ray/shadowsocks

   # 启动代理软件
   ```

2. **代理端口错误**
   - 检查代理软件显示的端口
   - 修改 `run.py` 第 32 行

3. **RPC 节点不可用**
   - 尝试备用 RPC 节点
   - 检查网络连接

4. **防火墙阻止**
   ```bash
   # 临时关闭防火墙测试
   sudo ufw disable  # Ubuntu
   ```

### 错误 3: `Connection timeout` / `Read timed out`

**原因**: 网络延迟高或代理不稳定

**解决方案**:
- 切换代理节点（选择延迟低的）
- 增加超时时间（修改代码中的 `timeout` 参数）
- 尝试备用 RPC 节点

### 错误 4: `Proxy error`

**可能原因**:

1. **代理格式错误**
   ```python
   # ❌ 错误
   PROXY = "127.0.0.1 7897"      # 多余空格
   PROXY = "localhost:7897"      # 使用 127.0.0.1 更可靠

   # ✅ 正确
   PROXY = "127.0.0.1:7897"
   PROXY = "http://127.0.0.1:7897"
   ```

2. **代理认证问题**
   ```python
   # 如果代理需要认证
   PROXY = "http://username:password@127.0.0.1:7897"
   ```

### 错误 5: `Binance API 连接失败`

**原因**: 代理未正确传递给 BinanceTokenFilter

**检查**:
- 确认输出中有 `🔄 BinanceTokenFilter 使用代理: ...`
- 检查代理软件日志是否有 `api.binance.com` 请求

**解决方案**:
- 已修复，代理会自动传递
- 如果还是失败，手动禁用过滤器：
  ```python
  ENABLE_FILTER = False  # 临时禁用
  ```

## 🧪 测试脚本

创建一个测试脚本 `test_connection.py`：

```python
#!/usr/bin/env python3
"""连接测试脚本"""

print("=" * 60)
print("1. 测试 Python 环境")
print("=" * 60)

try:
    from web3 import Web3
    import requests
    print("✅ 依赖包已安装")
except ImportError as e:
    print(f"❌ 缺少依赖: {e}")
    print("请运行: conda install -c conda-forge web3 requests")
    exit(1)

print("\n" + "=" * 60)
print("2. 测试代理连接")
print("=" * 60)

PROXY = "http://127.0.0.1:7897"

try:
    response = requests.get(
        "https://www.google.com",
        proxies={'http': PROXY, 'https': PROXY},
        timeout=5
    )
    print(f"✅ 代理工作正常: {PROXY}")
except Exception as e:
    print(f"❌ 代理连接失败: {e}")
    print("请检查:")
    print("  1. 代理软件是否运行")
    print("  2. 端口号是否正确")

print("\n" + "=" * 60)
print("3. 测试 RPC 节点连接")
print("=" * 60)

RPC_URL = "https://eth.llmamarpc.com"

try:
    w3 = Web3(Web3.HTTPProvider(
        RPC_URL,
        request_kwargs={'proxies': {'http': PROXY, 'https': PROXY}}
    ))

    if w3.is_connected():
        block = w3.eth.block_number
        print(f"✅ RPC 节点连接成功")
        print(f"   当前区块: {block}")
    else:
        print("❌ RPC 节点无法连接")
except Exception as e:
    print(f"❌ RPC 连接失败: {e}")

print("\n" + "=" * 60)
print("4. 测试 Binance API")
print("=" * 60)

try:
    session = requests.Session()
    session.proxies = {'http': PROXY, 'https': PROXY}

    response = session.get(
        "https://api.binance.com/api/v3/exchangeInfo",
        timeout=10
    )
    data = response.json()
    print(f"✅ Binance API 连接成功")
    print(f"   交易对数量: {len(data['symbols'])}")
except Exception as e:
    print(f"❌ Binance API 失败: {e}")

print("\n" + "=" * 60)
print("测试完成！")
print("=" * 60)
```

运行测试：

```bash
python test_connection.py
```

## 📞 获取帮助

如果以上方法都无法解决问题，请提供以下信息：

1. **Python 版本**: `python --version`
2. **环境类型**: conda / venv / system
3. **操作系统**: Linux / macOS / Windows
4. **代理软件**: Clash / V2Ray / Shadowsocks
5. **完整错误信息**: 运行 `python run.py` 的完整输出

## 🎯 快速解决路径

```
问题: RPC 连接失败
  ↓
检查 1: 代理是否运行？
  └─ 否 → 启动代理软件
  └─ 是 → 继续
      ↓
检查 2: curl 测试代理
  └─ 失败 → 检查代理配置
  └─ 成功 → 继续
      ↓
检查 3: 依赖是否安装？
  └─ 否 → conda install web3 requests
  └─ 是 → 继续
      ↓
检查 4: 运行 test_connection.py
  └─ 找出具体失败环节
      ↓
检查 5: 尝试备用 RPC 节点
  └─ 修改 run.py 中的 RPC_URL
```

---

**大多数问题都是以下三种之一**:
1. ✅ 依赖未安装 → `conda install web3 requests`
2. ✅ 代理未运行 → 启动代理软件
3. ✅ RPC 节点不可用 → 换备用节点

现在应该可以正常运行了！🎉
