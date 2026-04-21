# 中国期货专用平台数据协议 v1.2

## 1. 文档定位

本文档定义平台内部统一数据对象，用于接口层、规则层、计算层、存储层、展示层和插件层之间的数据交换。
所有核心对象必须具备稳定字段、明确语义、可序列化能力和版本兼容策略。

## 2. 设计原则

1. 所有核心对象必须强类型化。
2. 所有对象必须可序列化、可回放、可日志化。
3. 所有时间相关字段必须区分自然日与交易日。
4. 所有计算只消费标准对象，不直接消费交易所私有原始字段。
5. 原始字段允许保留在 `extra` 或 `raw` 扩展区，但不得形成跨模块依赖。
6. 面向前端传输的结构必须由标准对象映射而来，不得单独发明第二套业务语义。

## 3. 通用约束

- 默认时区：Asia/Shanghai。
- 时间字段：使用带时区的 datetime。
- 金额字段：默认 float，后续可升级 Decimal。
- 成交量字段：默认 float。
- 所有对象必须包含 `gateway_name`。
- 所有对象可选包含 `extra: dict[str, Any]`。
- 所有对象禁止删除已有核心字段而不经过 major 升级。

## 4. 基础对象

### 4.1 Tick

```text
Tick:
  gateway_name: str
  exchange: str
  symbol: str
  instrument_id: str
  datetime: datetime
  trading_date: date
  calendar_date: date
  session_type: enum[morning, afternoon, night]
  last_price: float
  volume: float
  turnover: float
  open_interest: float
  bid_price_1: float
  ask_price_1: float
  bid_volume_1: float
  ask_volume_1: float
  extra: dict | null
```

### 4.2 Bar

```text
Bar:
  gateway_name: str
  exchange: str
  symbol: str
  instrument_id: str
  interval: enum[tick, 1s, 1m, 3m, 5m, 15m, 30m, 60m, 1d]
  datetime: datetime
  calendar_date: date
  trading_date: date
  session_type: enum[morning, afternoon, night]
  session_id: str
  segment_seq: int
  open: float
  high: float
  low: float
  close: float
  volume: float
  turnover: float
  open_interest: float
  extra: dict | null
```

### 4.3 Instrument

```text
Instrument:
  exchange: str
  product_id: str
  instrument_id: str
  name: str
  price_tick: float
  contract_multiplier: float
  volume_multiple: float
  session_template_id: str
  timezone: str
  is_active: bool
  listed_date: date | null
  expire_date: date | null
  extra: dict | null
```

### 4.4 SessionContext

```text
SessionContext:
  session_id: str
  exchange: str
  product_id: str
  session_type: enum[morning, afternoon, night]
  calendar_date: date
  trading_date: date
  start_time: time
  end_time: time
  is_cross_day: bool
  template_id: str
```

## 5. 数据对象行为约束

### 5.1 唯一性

- Tick 唯一性建议键：`gateway_name + instrument_id + datetime`
- Bar 唯一性建议键：`instrument_id + interval + datetime`
- SessionContext 唯一性建议键：`session_id`

### 5.2 序列化

所有对象必须支持：
- Python 对象实例
- JSON 可序列化 dict
- 数据库存储映射
- 回放文件写入与恢复

### 5.3 兼容策略

- 新增非必填字段：minor 升级
- 新增必填字段：minor 升级，但必须提供默认值或迁移规则
- 删除字段或改变字段语义：major 升级

## 6. 前端映射约束

- 前端展示对象必须由标准对象投影生成。
- 前端字段命名可以更贴近交互，但不得改变业务语义。
- 任何图表、面板、工作区组件不得直接消费网关私有原始字段。
- 回放模式与实时模式必须复用同一套展示映射逻辑。

## 7. Python 参考定义

```python
from dataclasses import dataclass, field
from datetime import datetime, date, time
from enum import Enum
from typing import Any

class SessionType(str, Enum):
    MORNING = "morning"
    AFTERNOON = "afternoon"
    NIGHT = "night"

class Interval(str, Enum):
    TICK = "tick"
    S1 = "1s"
    M1 = "1m"
    M3 = "3m"
    M5 = "5m"
    M15 = "15m"
    M30 = "30m"
    H1 = "60m"
    D1 = "1d"

@dataclass(slots=True)
class Tick:
    gateway_name: str
    exchange: str
    symbol: str
    instrument_id: str
    datetime: datetime
    trading_date: date
    calendar_date: date
    session_type: SessionType
    last_price: float
    volume: float
    turnover: float
    open_interest: float
    bid_price_1: float
    ask_price_1: float
    bid_volume_1: float
    ask_volume_1: float
    extra: dict[str, Any] | None = field(default=None)

@dataclass(slots=True)
class Bar:
    gateway_name: str
    exchange: str
    symbol: str
    instrument_id: str
    interval: Interval
    datetime: datetime
    calendar_date: date
    trading_date: date
    session_type: SessionType
    session_id: str
    segment_seq: int
    open: float
    high: float
    low: float
    close: float
    volume: float
    turnover: float
    open_interest: float
    extra: dict[str, Any] | None = field(default=None)

class CancelReasonCode(str, Enum):
    TIMEOUT = "timeout"
    REJECTED_BY_USER = "rejected_by_user"
    REJECTED_BY_RISK = "rejected_by_risk"
    REJECTED_BY_EXCHANGE = "rejected_by_exchange"
    CONNECTION_LOST = "connection_lost"
    OTHER = "other"

@dataclass(slots=True)
class Order:
    order_id: str
    gateway_name: str
    exchange: str
    symbol: str
    instrument_id: str
    order_type: str
    direction: str
    offset: str
    price: float
    volume: float
    traded_volume: float
    status: str
    datetime: datetime
    trading_date: date
    session_type: SessionType
    gateway_order_id: str | None = None
    error_message: str | None = None
    cancellation_reason: str | None = None
    cancel_reason_code: CancelReasonCode | None = None
    extra: dict[str, Any] | None = None

@dataclass(slots=True)
class Trade:
    trade_id: str
    order_id: str
    gateway_name: str
    exchange: str
    symbol: str
    instrument_id: str
    direction: str
    offset: str
    price: float
    volume: float
    datetime: datetime
    trading_date: date
    session_type: SessionType
    gateway_trade_id: str | None = None
    commission: float | None = None
    extra: dict[str, Any] | None = None

@dataclass(slots=True)
class Position:
    gateway_name: str
    exchange: str
    symbol: str
    instrument_id: str
    direction: str
    volume: float
    available_volume: float
    avg_price: float
    open_price: float
    unrealized_pnl: float
    realized_pnl: float
    margin: float
    datetime: datetime
    trading_date: date
    extra: dict[str, Any] | None = None

@dataclass(slots=True)
class Account:
    gateway_name: str
    account_id: str
    balance: float
    available: float
    margin: float
    frozen_margin: float
    commission: float
    position_profit: float
    close_profit: float
    datetime: datetime
    trading_date: date
    extra: dict[str, Any] | None = None

@dataclass(slots=True)
class OrderRequest:
    gateway_name: str
    exchange: str
    symbol: str
    instrument_id: str
    order_type: str
    direction: str
    offset: str
    price: float
    volume: float
    time_in_force: str | None = None
    stop_price: float | None = None
    reference: str | None = None
    extra: dict[str, Any] | None = None

@dataclass(slots=True)
class CancelRequest:
    gateway_name: str
    order_id: str
    gateway_order_id: str | None = None
    reference: str | None = None
    extra: dict[str, Any] | None = None
```

## 8. 交易执行数据协议

### 8.1 Order

```text
Order:
  order_id: str
  gateway_name: str
  exchange: str
  symbol: str
  instrument_id: str
  order_type: enum[limit, market, stop, stop_limit, iceberg, conditional]
  direction: enum[long, short]
  offset: enum[open, close, close_today, close_yesterday]
  price: float
  volume: float
  traded_volume: float
  status: enum[submitting, submitted, accepted, rejected, partial_filled, filled, cancelled, cancelling]
  datetime: datetime
  trading_date: date
  session_type: enum[morning, afternoon, night]
  gateway_order_id: str | null
  error_message: str | null
  cancellation_reason: str | null
  cancel_reason_code: enum[timeout, rejected_by_user, rejected_by_risk, rejected_by_exchange, connection_lost, other] | null
  extra: dict | null
```

### 8.1.1 CancelReasonCode 枚举

```text
CancelReasonCode:
  timeout: 撤单超时
  rejected_by_user: 用户主动撤单
  rejected_by_risk: 风控拦截撤单
  rejected_by_exchange: 交易所拒绝撤单
  connection_lost: 连接丢失
  other: 其他原因
```

### 8.2 Trade

```text
Trade:
  trade_id: str
  order_id: str
  gateway_name: str
  exchange: str
  symbol: str
  instrument_id: str
  direction: enum[long, short]
  offset: enum[open, close, close_today, close_yesterday]
  price: float
  volume: float
  datetime: datetime
  trading_date: date
  session_type: enum[morning, afternoon, night]
  gateway_trade_id: str | null
  commission: float | null
  extra: dict | null
```

### 8.3 Position

```text
Position:
  gateway_name: str
  exchange: str
  symbol: str
  instrument_id: str
  direction: enum[long, short]
  volume: float
  available_volume: float
  avg_price: float
  open_price: float
  unrealized_pnl: float
  realized_pnl: float
  margin: float
  datetime: datetime
  trading_date: date
  extra: dict | null
```

### 8.4 Account

```text
Account:
  gateway_name: str
  account_id: str
  balance: float
  available: float
  margin: float
  frozen_margin: float
  commission: float
  position_profit: float
  close_profit: float
  datetime: datetime
  trading_date: date
  extra: dict | null
```

### 8.5 OrderRequest

```text
OrderRequest:
  gateway_name: str
  exchange: str
  symbol: str
  instrument_id: str
  order_type: enum[limit, market, stop, stop_limit]
  direction: enum[long, short]
  offset: enum[open, close, close_today, close_yesterday]
  price: float
  volume: float
  time_in_force: enum[GTC, IOC, FOK, GTD] | null
  stop_price: float | null
  reference: str | null
  extra: dict | null
```

### 8.6 CancelRequest

```text
CancelRequest:
  gateway_name: str
  order_id: str
  gateway_order_id: str | null
  reference: str | null
  extra: dict | null
```

### 8.7 RiskCheckResult

```text
RiskCheckResult:
  passed: bool
  check_type: enum[position_limit, order_limit, margin_check, price_band, frozen_check, custom]
  block_reason: str | null
  block_code: str | null
  check_time: datetime
  context: dict | null
```

### 8.8 交易数据行为约束

- Order 唯一性建议键：`gateway_name + order_id`
- Trade 唯一性建议键：`gateway_name + trade_id`
- Position 唯一性建议键：`gateway_name + instrument_id + direction`
- Account 唯一性建议键：`gateway_name + account_id`
- 所有交易对象必须支持实时与回放模式下的状态重建
- Order 状态转换必须符合交易所规则，不允许非法跳转
- Trade 必须关联到有效的 Order
- Position 更新必须由 Trade 触发或由系统初始化
- Account 更新必须由 Trade、Commission、Deposit、Withdraw 触发

## 9. 最低测试要求

- Tick 序列化/反序列化测试。
- Bar 唯一键测试。
- trading_date 与 calendar_date 分离测试。
- 夜盘 Tick 转 SessionContext 映射测试。
- 全量重算与增量更新一致性测试。
- 标准对象到前端投影结构一致性测试。
- Order 状态转换合法性测试。
- Trade 与 Order 关联性测试。
- Position 增量更新测试。
- Account 资金流水平衡测试。
- RiskCheckResult 拦截逻辑测试。