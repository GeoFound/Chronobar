# 中国期货专用平台事件协议 v1.2

## 1. 文档定位

本文档定义平台内部统一事件模型、标准事件类型、事件路由规则、消费约束与桥接边界。
系统各模块默认通过事件总线协同，禁止以跨层随意直连作为默认通信方式。

## 2. 核心目标

1. 用统一事件模型承载所有可见状态变化。
2. 让接口层、规则层、计算层、展示层、插件层解耦。
3. 让实时运行与历史回放使用同一种事件协议。
4. 为日志排障和链路追踪提供最小必要信息。
5. 为 React 展示层提供稳定的实时订阅边界。

## 3. 事件封包模型

### 3.1 EventEnvelope

```text
EventEnvelope:
  event_id: str
  event_type: str
  source: str
  ts: datetime
  instrument_id: str | null
  session_id: str | null
  payload: object
  trace_id: str
  replayable: bool
  version: str
```

字段说明：
- `event_id`：事件唯一 ID
- `event_type`：标准事件类型
- `source`：事件来源模块，例如 `gateway.ctp_main` / `compute.bar_1m` / `plugin.ma_01`
- `ts`：事件创建时间
- `instrument_id`：相关合约，可为空
- `session_id`：相关时段，可为空
- `payload`：标准对象或标准序列化结构
- `trace_id`：同一条处理链路共享追踪 ID
- `replayable`：是否进入回放日志
- `version`：事件协议版本

## 4. 标准事件类型

```text
SYSTEM_START
SYSTEM_STOP

GATEWAY_STATUS_CHANGED

TICK
BAR
BAR_CLOSED

REPLAY_TICK
REPLAY_BAR

ORDER
ORDER_ACCEPTED
ORDER_REJECTED
ORDER_CANCELLED
ORDER_PARTIAL_FILLED
ORDER_FILLED

TRADE
TRADE_FILLED

POSITION
POSITION_UPDATED

ACCOUNT
ACCOUNT_UPDATED

RISK_BLOCKED
RISK_WARNING

TIMER_1S
TIMER_5S
TIMER_1M

SESSION_OPEN
SESSION_CLOSE
SESSION_SWITCH

ALERT
PLUGIN_ERROR
CONFIG_CHANGED

WORKSPACE_CHANGED
PANEL_CHANGED
SUBSCRIPTION_CHANGED
THEME_CHANGED
ACTIVE_INSTRUMENT_CHANGED

REPLAY_STARTED
REPLAY_FINISHED
REPLAY_PROGRESS
```

### 4.1 GATEWAY_STATUS_CHANGED 事件 payload

```text
{
  "gateway_name": str,
  "status": str,  // GatewayStatus enum: disconnected, connecting, connected, authenticated, disconnecting, error
  "previous_status": str | null,
  "error_message": str | null
}
```

## 5. 路由规则

### 5.1 事件 replayable 标注

以下表格定义了各类事件的 replayable 默认值：

| 事件类型 | replayable | 说明 |
|---------|-----------|------|
| SYSTEM_START | False | 系统启动事件不应在回放时重放 |
| SYSTEM_STOP | False | 系统停止事件不应在回放时重放 |
| GATEWAY_STATUS_CHANGED | False | 网关状态变化事件不应在回放时重放 |
| TICK | True | 行情事件可回放 |
| BAR | True | K线事件可回放 |
| BAR_CLOSED | True | K线闭合事件可回放 |
| REPLAY_TICK | True | 回放行情事件可回放 |
| REPLAY_BAR | True | 回放K线事件可回放 |
| ORDER | True | 订单事件可回放 |
| ORDER_ACCEPTED | True | 订单接受事件可回放 |
| ORDER_REJECTED | True | 订单拒绝事件可回放 |
| ORDER_CANCELLED | True | 订单撤消事件可回放 |
| ORDER_PARTIAL_FILLED | True | 订单部分成交事件可回放 |
| ORDER_FILLED | True | 订单完全成交事件可回放 |
| TRADE | True | 成交事件可回放 |
| TRADE_FILLED | True | 成交填充事件可回放 |
| POSITION | True | 持仓事件可回放 |
| POSITION_UPDATED | True | 持仓更新事件可回放 |
| ACCOUNT | True | 账户事件可回放 |
| ACCOUNT_UPDATED | True | 账户更新事件可回放 |
| RISK_BLOCKED | True | 风控拦截事件可回放 |
| RISK_WARNING | True | 风控警告事件可回放 |
| TIMER_1S | False | 定时器事件不应在回放时重放 |
| TIMER_5S | False | 定时器事件不应在回放时重放 |
| TIMER_1M | False | 定时器事件不应在回放时重放 |
| SESSION_OPEN | True | 时段开启事件可回放 |
| SESSION_CLOSE | True | 时段关闭事件可回放 |
| SESSION_SWITCH | True | 时段切换事件可回放 |
| ALERT | True | 告警事件可回放 |
| PLUGIN_ERROR | True | 插件错误事件可回放 |
| CONFIG_CHANGED | False | 配置变更事件不应在回放时重放 |
| WORKSPACE_CHANGED | False | 工作区变更事件不应在回放时重放 |
| PANEL_CHANGED | False | 面板变更事件不应在回放时重放 |
| SUBSCRIPTION_CHANGED | False | 订阅变更事件不应在回放时重放 |
| THEME_CHANGED | False | 主题变更事件不应在回放时重放 |
| ACTIVE_INSTRUMENT_CHANGED | False | 活跃合约变更事件不应在回放时重放 |
| REPLAY_STARTED | False | 回放开始事件不应在回放时重放 |
| REPLAY_FINISHED | False | 回放结束事件不应在回放时重放 |
| REPLAY_PROGRESS | False | 回放进度事件不应在回放时重放 |

### 5.2 默认规则

- 全局订阅：按 `event_type` 订阅
- 精细订阅：按 `event_type + instrument_id` 订阅
- 系统广播事件：如 TIMER、SYSTEM、CONFIG_CHANGED
- 回放事件：必须保留原始 `trace_id`
- 发往前端的事件必须经过桥接层过滤与格式标准化

### 5.3 禁止行为

- 禁止插件直接调用其他插件内部方法作为主协作通道
- 禁止 UI 组件直接订阅底层原始回调而绕过事件引擎
- 禁止将不可序列化对象塞入 `payload`
- 禁止前端自行拼装伪事件回写主总线

## 6. 幂等要求

任一事件处理函数必须满足：

1. 同一事件重复消费不应导致不可恢复副作用。
2. 对持久化写入必须支持去重键。
3. 对指标更新必须支持按 `event_id` 或时间主键判重。
4. 对前端订阅重连场景必须支持安全重放或状态重建。

## 7. 失败处理

- 单个 handler 抛错不得中断整个事件循环
- 事件处理异常必须产生日志
- 插件异常必须转化为 `PLUGIN_ERROR`
- 可恢复异常允许重试，不可恢复异常进入告警面板
- 发往前端的桥接异常必须独立记录

### 7.1 队列容量与背压策略

**队列容量约束：**

- 最大队列长度：10000 条事件
- 队列积压阈值：8000 条事件（触发背压）
- 队列告警阈值：9000 条事件（触发告警）

**背压触发条件：**

- 队列长度达到积压阈值（8000）
- 事件处理平均延迟超过 100ms
- 连续 10 次事件处理超时

**背压降级策略：**

当触发背压时，按以下优先级降级处理：

1. **低优先级事件降采样**：TIMER_* 事件按 10:1 比例降采样
2. **非关键事件丢弃**：WORKSPACE_CHANGED、PANEL_CHANGED、THEME_CHANGED 事件直接丢弃
3. **告警触发**：产生 EVENT_BACKPRESSURE 告警事件
4. **日志记录**：记录背压触发时间、队列长度、处理延迟

**禁止行为：**

- 禁止丢弃 TICK、BAR、ORDER、TRADE 等核心业务事件
- 禁止在背压时阻塞事件发布线程
- 禁止静默丢弃事件而不记录日志

## 8. Python 参考接口

```python
from dataclasses import dataclass
from datetime import datetime
from typing import Any

@dataclass(slots=True)
class EventEnvelope:
    event_id: str
    event_type: str
    source: str
    ts: datetime
    instrument_id: str | None
    session_id: str | None
    payload: Any
    trace_id: str
    replayable: bool = True
    version: str = "1.2"
```

```python
from abc import ABC, abstractmethod
from collections.abc import Callable

EventHandler = Callable[[EventEnvelope], None]

class EventBus(ABC):
    @abstractmethod
    def start(self) -> None: ...
    @abstractmethod
    def stop(self) -> None: ...
    @abstractmethod
    def put(self, event: EventEnvelope) -> None: ...
    @abstractmethod
    def subscribe(self, event_type: str, handler: EventHandler) -> None: ...
    @abstractmethod
    def subscribe_instrument(
        self, event_type: str, instrument_id: str, handler: EventHandler
    ) -> None: ...
```

## 9. 前端订阅边界

- 前端订阅只能通过 UI Bridge 进行。
- UI Bridge 可以基于事件类型、合约、工作区和回放上下文进行过滤。
- 前端不得依赖未声明字段。
- 前端断线重连后，应先拉取快照，再恢复事件订阅。
- 回放模式与实时模式必须使用同一种事件消费结构。

## 10. 最低测试要求

- 单事件发布 / 订阅测试
- 多 handler 异常隔离测试
- instrument 精细订阅测试
- trace_id 透传测试
- 回放日志重建一致性测试
- 前端订阅重连一致性测试