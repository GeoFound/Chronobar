# 中国期货专用平台网关协议 v1.2

## 1. 文档定位

本文档定义平台与交易所网关的标准接口契约、连接状态管理、重连策略和回调映射约束。
所有网关实现（CTP、OpenCTP、SimNow、模拟网关）必须遵守本协议，确保接口兼容性和可替换性。

## 2. 网关目标

1. 统一不同交易所网关的接口契约，屏蔽底层差异。
2. 提供标准化的连接管理、订阅、订单和查询接口。
3. 支持连接断开后的自动重连和状态恢复。
4. 确保回调事件的标准化映射和异常隔离。

### 2.1 网关适配器定位

Chronobar 中的 Gateway 不是某一个供应商 SDK 的同义词，而是平台稳定骨架上的适配器规范。

- CTP / OpenCTP / SimNow / 本地回放输入都应通过同一套骨架接口接入
- 用户可以根据自己的账户、环境和研究流程选择不同 Gateway 实现
- 平台负责统一对象语义、恢复策略、能力声明与替换边界
- 单个 Gateway 实现不应把自己的私有字段、私有线程模型或私有恢复方式上升为平台长期依赖

### 2.2 能力声明与降级规则

不同 Gateway 允许具备不同能力组合，但必须显式声明，而不能由上层猜测。

最小能力面至少包括：

- `market_data`
- `order_entry`
- `cancel_order`
- `account_query`
- `position_query`
- `order_query`
- `replay_input`
- `local_mock`

要求：

- 不支持的能力必须明确声明为不可用
- 上层模块、UI Bridge 与 AI 组件在调用前应先检查能力声明
- 不允许用静默失败或伪成功掩盖能力缺失
- 本地回放 Gateway、模拟 Gateway 和真实交易 Gateway 可以实现不同能力组合，但都必须遵守同一骨架协议

## 3. 连接状态枚举

```python
class GatewayStatus(str, Enum):
    DISCONNECTED = "disconnected"
    CONNECTING = "connecting"
    CONNECTED = "connected"
    AUTHENTICATED = "authenticated"
    DISCONNECTING = "disconnecting"
    ERROR = "error"

@dataclass(slots=True)
class GatewayCapabilities:
    market_data: bool = True
    order_entry: bool = False
    cancel_order: bool = False
    account_query: bool = False
    position_query: bool = False
    order_query: bool = False
    replay_input: bool = False
    local_mock: bool = False
```

## 4. BaseGateway 接口

### 4.1 核心接口

```python
from abc import ABC, abstractmethod
from enum import Enum
from typing import Callable, Optional
from dataclasses import dataclass

class BaseGateway(ABC):
    @abstractmethod
    def connect(self) -> None:
        """建立连接"""
        ...

    @abstractmethod
    def disconnect(self) -> None:
        """断开连接"""
        ...

    @abstractmethod
    def subscribe(self, instrument_ids: list[str]) -> None:
        """订阅行情"""
        ...

    @abstractmethod
    def unsubscribe(self, instrument_ids: list[str]) -> None:
        """取消订阅"""
        ...

    @abstractmethod
    def submit_order(self, order_request: OrderRequest) -> str:
        """提交订单，返回 order_id"""
        ...

    @abstractmethod
    def cancel_order(self, cancel_request: CancelRequest) -> bool:
        """撤销订单，返回是否成功"""
        ...

    @abstractmethod
    def query_account(self) -> Account:
        """查询账户信息"""
        ...

    @abstractmethod
    def query_position(self) -> list[Position]:
        """查询持仓信息"""
        ...

    @abstractmethod
    def get_status(self) -> GatewayStatus:
        """获取连接状态"""
        ...

    @abstractmethod
    def get_capabilities(self) -> GatewayCapabilities:
        """获取网关能力声明"""
        ...
```

### 4.2 回调接口

```python
class GatewayCallback(Protocol):
    def on_tick(self, tick: Tick) -> None:
        """行情回调"""
        ...

    def on_trade(self, trade: Trade) -> None:
        """成交回调"""
        ...

    def on_order(self, order: Order) -> None:
        """订单状态回调"""
        ...

    def on_position(self, position: Position) -> None:
        """持仓回调"""
        ...

    def on_account(self, account: Account) -> None:
        """账户回调"""
        ...

    def on_error(self, error: Exception) -> None:
        """错误回调"""
        ...

    def on_log(self, log: str) -> None:
        """日志回调"""
        ...
```

## 5. 重连策略

### 5.1 重连触发条件

- 连接断开（网络异常、服务器断开）
- 认证失败
- 心跳超时

### 5.2 重连策略

```python
class ReconnectPolicy:
    max_retries: int = 5
    initial_delay: float = 1.0  # 秒
    max_delay: float = 60.0  # 秒
    backoff_factor: float = 2.0
```

重连逻辑：
1. 首次重连延迟 initial_delay 秒
2. 每次失败后延迟时间乘以 backoff_factor
3. 延迟时间不超过 max_delay
4. 重试次数不超过 max_retries
5. 超过最大重试次数后进入 ERROR 状态

### 5.3 状态恢复

重连成功后必须恢复：
- 所有订阅的合约
- 所有未完成订单的状态查询
- 账户和持仓信息的重新查询

## 6. 回调映射约束

### 6.1 必须映射的字段

所有回调对象必须包含以下标准字段：
- gateway_name: str
- trading_date: date
- session_type: SessionType

### 6.2 禁止行为

- 禁止在回调中直接修改核心状态
- 禁止在回调中阻塞主线程
- 禁止在回调中抛出未捕获异常
- 禁止在回调中直接访问数据库

### 6.3 异常隔离

单个回调异常不得影响其他回调：
- 回调异常必须转化为 ERROR 事件
- 回调异常必须记录日志
- 回调异常不得中断网关运行

## 7. 配置协议

### 7.1 网关配置示例

```json
{
  "gateway_name": "openctp",
  "gateway_type": "ctp",
  "broker_id": "9999",
  "investor_id": "user001",
  "password": "<your_password>",
  "td_address": "tcp://180.168.146.187:10101",
  "md_address": "tcp://180.168.146.187:10131",
  "app_id": "simnow_client_test",
  "auth_code": "0000000000000000",
  "reconnect_policy": {
    "max_retries": 5,
    "initial_delay": 1.0,
    "max_delay": 60.0,
    "backoff_factor": 2.0
  }
}
```

### 7.2 配置字段说明

- gateway_name: 网关唯一标识
- gateway_type: 网关类型（ctp、openctp、sim、mock）
- broker_id: 期货公司 ID
- investor_id: 投资者账号
- password: 密码（禁止写入配置文件，运行时从环境变量注入）
- td_address: 交易服务器地址
- md_address: 行情服务器地址
- app_id: 应用 ID（CTP 6.3+）
- auth_code: 认证码（CTP 6.3+）
- reconnect_policy: 重连策略配置

**密码管理策略：**
- 禁止将明文密码写入配置文件
- 运行时通过环境变量注入（如 `GATEWAY_PASSWORD_<gateway_name>`）
- 配置文件中的 password 字段仅作为占位符或引用环境变量名

### 7.3 连接资产边界

- 网关配置、地址映射、能力声明与恢复策略属于用户连接资产的一部分
- 凭据、认证码与口令不属于可公开导出的普通配置样例
- AI 可以辅助生成连接配置候选产物和能力说明，但不得静默读取、持久化或外送凭据

## 8. 网关实现要求

### 8.1 必须实现的方法

所有网关实现必须实现 BaseGateway 的所有抽象方法。

### 8.2 线程安全

- 网关内部必须保证线程安全
- 回调必须在主线程或事件线程中执行
- 禁止在回调中直接修改网关内部状态

### 8.3 能力声明与降级

- 所有网关实现必须提供能力声明对象
- 上层若调用未声明支持的能力，应返回明确错误或拒绝结果
- 不允许把“当前未实现”伪装为“调用成功但无结果”
- Gateway 的能力缺口必须允许 UI、策略宿主和 AI 助手显示降级路径

### 8.4 资源清理

- disconnect 必须释放所有资源
- 订阅必须在 disconnect 时取消
- 回调必须在 disconnect 时清除

## 9. Python 参考实现

```python
from abc import ABC, abstractmethod
from enum import Enum
from typing import Callable, Optional
from dataclasses import dataclass

class GatewayStatus(str, Enum):
    DISCONNECTED = "disconnected"
    CONNECTING = "connecting"
    CONNECTED = "connected"
    AUTHENTICATED = "authenticated"
    DISCONNECTING = "disconnecting"
    ERROR = "error"

@dataclass(slots=True)
class ReconnectPolicy:
    max_retries: int = 5
    initial_delay: float = 1.0
    max_delay: float = 60.0
    backoff_factor: float = 2.0

@dataclass(slots=True)
class GatewayCapabilities:
    market_data: bool = True
    order_entry: bool = False
    cancel_order: bool = False
    account_query: bool = False
    position_query: bool = False
    order_query: bool = False
    replay_input: bool = False
    local_mock: bool = False

class BaseGateway(ABC):
    def __init__(self, gateway_name: str):
        self.gateway_name = gateway_name
        self._status = GatewayStatus.DISCONNECTED
        self._capabilities = GatewayCapabilities()
        self._callback: Optional[GatewayCallback] = None
        self._reconnect_policy = ReconnectPolicy()
        self._event_emitter: Optional[Callable[[str, dict], None]] = None

    def set_callback(self, callback: GatewayCallback) -> None:
        """设置回调接口"""
        self._callback = callback

    def set_reconnect_policy(self, policy: ReconnectPolicy) -> None:
        """设置重连策略"""
        self._reconnect_policy = policy

    def set_event_emitter(self, emitter: Callable[[str, dict], None]) -> None:
        """设置事件发射器（用于向 EventEngine 发送 PLUGIN_ERROR 等事件）"""
        self._event_emitter = emitter

    @abstractmethod
    def connect(self) -> None:
        """建立连接"""
        ...

    @abstractmethod
    def disconnect(self) -> None:
        """断开连接"""
        ...

    @abstractmethod
    def subscribe(self, instrument_ids: list[str]) -> None:
        """订阅行情"""
        ...

    @abstractmethod
    def unsubscribe(self, instrument_ids: list[str]) -> None:
        """取消订阅"""
        ...

    @abstractmethod
    def submit_order(self, order_request: OrderRequest) -> str:
        """提交订单，返回 order_id"""
        ...

    @abstractmethod
    def cancel_order(self, cancel_request: CancelRequest) -> bool:
        """撤销订单，返回是否成功"""
        ...

    @abstractmethod
    def query_account(self) -> Account:
        """查询账户信息"""
        ...

    @abstractmethod
    def query_position(self) -> list[Position]:
        """查询持仓信息"""
        ...

    @abstractmethod
    def query_orders(self) -> list[Order]:
        """查询委托信息"""
        ...

    def get_status(self) -> GatewayStatus:
        """获取连接状态"""
        return self._status

    def get_capabilities(self) -> GatewayCapabilities:
        """获取网关能力声明"""
        return self._capabilities

    def _emit_tick(self, tick: Tick) -> None:
        """发送行情回调"""
        if self._callback:
            try:
                self._callback.on_tick(tick)
            except Exception as e:
                self._on_callback_error("on_tick", e)

    def _emit_trade(self, trade: Trade) -> None:
        """发送成交回调"""
        if self._callback:
            try:
                self._callback.on_trade(trade)
            except Exception as e:
                self._on_callback_error("on_trade", e)

    def _emit_order(self, order: Order) -> None:
        """发送订单回调"""
        if self._callback:
            try:
                self._callback.on_order(order)
            except Exception as e:
                self._on_callback_error("on_order", e)

    def _emit_position(self, position: Position) -> None:
        """发送持仓回调"""
        if self._callback:
            try:
                self._callback.on_position(position)
            except Exception as e:
                self._on_callback_error("on_position", e)

    def _emit_account(self, account: Account) -> None:
        """发送账户回调"""
        if self._callback:
            try:
                self._callback.on_account(account)
            except Exception as e:
                self._on_callback_error("on_account", e)

    def _emit_error(self, error: Exception) -> None:
        """发送错误回调"""
        if self._callback:
            try:
                self._callback.on_error(error)
            except Exception as e:
                # 错误回调本身出错，向 EventEngine 发送 PLUGIN_ERROR 事件
                self._emit_plugin_error("error_callback", e)

    def _on_callback_error(self, method: str, error: Exception) -> None:
        """回调异常处理"""
        # 向 EventEngine 发送 PLUGIN_ERROR 事件，保持与 event_protocol.md 一致
        self._emit_plugin_error(method, error)
        self._emit_error(error)

    def _emit_plugin_error(self, source: str, error: Exception) -> None:
        """向 EventEngine 发送 PLUGIN_ERROR 事件"""
        if self._event_emitter:
            try:
                self._event_emitter("PLUGIN_ERROR", {
                    "source": f"gateway_{self.gateway_name}.{source}",
                    "error_type": type(error).__name__,
                    "error_message": str(error),
                    "gateway_name": self.gateway_name
                })
            except Exception as e:
                # 事件发射失败时的兜底日志
                print(f"Failed to emit PLUGIN_ERROR: {e}")
```
