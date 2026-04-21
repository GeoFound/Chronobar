# 中国期货专用平台网关协议 v1.2

## 1. 文档定位

本文档定义平台与交易所网关的标准接口契约、连接状态管理、重连策略和回调映射约束。
所有网关实现（CTP、OpenCTP、SimNow、模拟网关）必须遵守本协议，确保接口兼容性和可替换性。

## 2. 网关目标

1. 统一不同交易所网关的接口契约，屏蔽底层差异。
2. 提供标准化的连接管理、订阅、订单和查询接口。
3. 支持连接断开后的自动重连和状态恢复。
4. 确保回调事件的标准化映射和异常隔离。

## 3. 连接状态枚举

```python
class GatewayStatus(str, Enum):
    DISCONNECTED = "disconnected"
    CONNECTING = "connecting"
    CONNECTED = "connected"
    AUTHENTICATED = "authenticated"
    DISCONNECTING = "disconnecting"
    ERROR = "error"
```

## 4. BaseGateway 接口

### 4.1 核心接口

```python
from abc import ABC, abstractmethod
from enum import Enum
from typing import Callable, Optional

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
    def query_orders(self) -> list[Order]:
        """查询委托信息"""
        ...

    @abstractmethod
    def get_status(self) -> GatewayStatus:
        """获取连接状态"""
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
  "password": "password",
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
- password: 密码
- td_address: 交易服务器地址
- md_address: 行情服务器地址
- app_id: 应用 ID（CTP 6.3+）
- auth_code: 认证码（CTP 6.3+）
- reconnect_policy: 重连策略配置

## 8. 网关实现要求

### 8.1 必须实现的方法

所有网关实现必须实现 BaseGateway 的所有抽象方法。

### 8.2 线程安全

- 网关内部必须保证线程安全
- 回调必须在主线程或事件线程中执行
- 禁止在回调中直接修改网关内部状态

### 8.3 资源清理

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

class BaseGateway(ABC):
    def __init__(self, gateway_name: str):
        self.gateway_name = gateway_name
        self._status = GatewayStatus.DISCONNECTED
        self._callback: Optional[GatewayCallback] = None
        self._reconnect_policy = ReconnectPolicy()

    def set_callback(self, callback: GatewayCallback) -> None:
        """设置回调接口"""
        self._callback = callback

    def set_reconnect_policy(self, policy: ReconnectPolicy) -> None:
        """设置重连策略"""
        self._reconnect_policy = policy

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
                # 错误回调本身出错，只能记录日志
                print(f"Error in error callback: {e}")

    def _on_callback_error(self, method: str, error: Exception) -> None:
        """回调异常处理"""
        print(f"Callback error in {method}: {error}")
        self._emit_error(error)
```
