# 中国期货专用平台策略协议 v1.2

## 1. 文档定位

本文档定义策略插件的接口契约、Host API、生命周期、权限模型和回测一致性要求。
策略插件是具备交易执行能力的受控扩展单元，必须通过显式权限授权才能参与下单链路。

## 2. 策略目标

1. 让用户可以编写自己的交易策略，接入实盘、仿真和回测。
2. 保证实盘、仿真、回测使用同一套策略接口和逻辑。
3. 让策略具备最小权限、可测试、可回放、可风控。
4. 让策略输出可以稳定进入图表层、面板层和日志层。

## 3. 插件分类体系

插件分类体系详见 [`plugin_protocol.md`](plugin_protocol.md) 第 3 节。本文档仅说明策略插件（strategy）特有的扩展接口、权限模型和风控约束。

## 4. 策略目录结构

```text
strategy_name/
  manifest.json
  strategy.py
  assets/
  tests/
  README.md
```

## 5. manifest 基线

```json
{
  "name": "dual_ma_strategy",
  "version": "1.0.0",
  "api_version": "1.2",
  "kind": "strategy",
  "entry": "strategy.py",
  "dependencies": [],
  "permissions": {
    "read_market_data": true,
    "emit_alert": true,
    "write_file": false,
    "read_workspace": false,
    "submit_order": true,
    "cancel_order": true,
    "read_position": true,
    "read_account": true,
    "read_open_orders": true
  },
  "risk_profile": {
    "max_position_per_instrument": 10,
    "max_orders_per_day": 100,
    "max_loss_per_day": 10000
  },
  "compatibility": {
    "min_core_version": "1.2",
    "max_core_version": "1.x"
  }
}
```

## 6. 策略生命周期接口

```python
def manifest() -> dict: ...
def on_init(ctx) -> None: ...
def on_start(ctx) -> None: ...
def on_stop(ctx) -> None: ...
def on_tick(ctx, tick) -> None: ...
def on_bar(ctx, bar) -> None: ...
def on_order(ctx, order) -> None: ...
def on_trade(ctx, trade) -> None: ...
def on_risk_event(ctx, event) -> None: ...
def outputs() -> dict: ...
def schema() -> dict: ...
```

**说明：**
- 策略插件不包含通用 `on_event` 回调（基础插件协议有），因为策略插件有专用的强类型回调（on_tick、on_bar、on_order、on_trade、on_risk_event），足以覆盖所有策略场景
- 如需处理自定义事件，可通过订阅特定事件类型在专用回调中处理

说明：
- `on_init`：资源初始化、订阅声明、参数读取
- `on_start`：正式启动
- `on_stop`：释放资源、平仓处理
- `on_order`：接收订单状态变化
- `on_trade`：接收成交回报
- `on_risk_event`：接收风控事件（被拦截、警告等）
- `outputs`：声明策略可向系统暴露的标准输出（信号、日志、告警）
- `schema`：声明参数面板、样式项、校验规则

## 7. Strategy Host API

### 7.1 订单操作

```python
class StrategyHostAPI(Protocol):
    def submit_order(self, request: OrderRequest) -> str:
        """提交订单，返回 order_id"""
        ...

    def cancel_order(self, order_id: str) -> bool:
        """撤单，返回是否成功"""
        ...

    def cancel_all_orders(self, instrument_id: str | None = None) -> int:
        """撤单，可指定合约，返回撤单数量"""
        ...
```

### 7.2 查询操作

```python
class StrategyHostAPI(Protocol):
    def get_positions(self, instrument_id: str | None = None) -> list[Position]:
        """查询持仓，可指定合约"""
        ...

    def get_account(self) -> Account:
        """查询账户信息"""
        ...

    def get_open_orders(self, instrument_id: str | None = None) -> list[Order]:
        """查询未成交委托，可指定合约"""
        ...

    def get_order(self, order_id: str) -> Order | None:
        """查询单个订单"""
        ...
```

### 7.3 行情与指标

```python
class StrategyHostAPI(Protocol):
    def subscribe_tick(self, instrument_id: str) -> None:
        """订阅 tick"""
        ...

    def subscribe_bar(self, instrument_id: str, interval: Interval) -> None:
        """订阅 bar"""
        ...

    def get_current_bar(self, instrument_id: str, interval: Interval) -> Bar | None:
        """获取当前 bar"""
        ...

    def get_history_bars(self, instrument_id: str, interval: Interval, count: int) -> list[Bar]:
        """获取历史 bar"""
        ...
```

### 7.4 告警与日志

```python
class StrategyHostAPI(Protocol):
    def publish_alert(self, level: str, title: str, content: str) -> None:
        """发布告警"""
        ...

    def log_info(self, message: str) -> None:
        """记录信息日志"""
        ...

    def log_warning(self, message: str) -> None:
        """记录警告日志"""
        ...

    def log_error(self, message: str) -> None:
        """记录错误日志"""
        ...
```

### 7.5 缓存与配置

```python
class StrategyHostAPI(Protocol):
    def write_cache(self, key: str, value: object) -> None:
        """写入缓存"""
        ...

    def read_cache(self, key: str) -> object | None:
        """读取缓存"""
        ...

    def get_config(self, path: str) -> object:
        """读取配置"""
        ...

    def get_instrument(self, instrument_id: str) -> Instrument:
        """获取合约信息"""
        ...
```

## 8. 权限模型

### 8.1 权限分级

- **read_market_data**：读取市场数据（tick、bar、instrument）
- **emit_alert**：发布告警
- **write_file**：写入文件（需用户授权）
- **read_workspace**：读取工作区配置
- **submit_order**：提交订单（策略专用，需用户授权）
- **cancel_order**：撤销订单（策略专用，需用户授权）
- **read_position**：读取持仓（策略专用，需用户授权）
- **read_account**：读取账户（策略专用，需用户授权）
- **read_open_orders**：读取未成交委托（策略专用，需用户授权）

### 8.2 授权流程

1. 插件在 manifest 中声明所需权限
2. 用户在插件安装时审查权限
3. 用户显式授权后才能加载策略插件
4. 运行时权限检查，未授权调用直接拒绝并记录日志
5. 风控参数在 manifest 中声明（max_position_per_instrument、max_orders_per_day、max_loss_per_day）

### 8.3 禁止行为

- 禁止策略插件绕过 Host API 直接调用 Gateway
- 禁止策略插件直接持有数据库连接
- 禁止策略插件直接修改核心对象私有状态
- 禁止策略插件绕过风控检查下单
- 禁止策略插件在未授权情况下执行交易操作

## 9. 风控集成

### 9.1 预交易风控

策略调用 `submit_order` 时，系统自动执行以下风控检查：

1. **持仓限制**：检查当前持仓是否超过 manifest 中声明的 max_position_per_instrument
2. **订单限制**：检查当日订单数量是否超过 max_orders_per_day
3. **资金检查**：检查账户可用资金是否足够
4. **价格检查**：检查订单价格是否在合理价格区间
5. **冻结检查**：检查账户或合约是否被冻结

风控检查失败时：
- 返回 RiskCheckResult
- 触发 RISK_BLOCKED 事件
- 策略的 on_risk_event 回调被调用
- 订单不会提交到交易所

### 9.2 风控事件

策略通过 `on_risk_event(ctx, event)` 接收风控事件：

```python
def on_risk_event(ctx, event) -> None:
    if event.check_type == "position_limit":
        ctx.log_warning(f"持仓限制被触发: {event.block_reason}")
    elif event.check_type == "margin_check":
        ctx.log_error(f"资金不足: {event.block_reason}")
```

## 10. 回测一致性

### 10.1 统一接口

策略接口在实盘、仿真、回测模式下完全一致：

- 同样的生命周期接口
- 同样的 Host API
- 同样的事件回调
- 同样的权限模型

### 10.2 模式差异

系统通过运行模式自动适配底层实现：

- **实盘模式**：Host API 调用真实 Gateway，真实下单
- **仿真模式**：Host API 调用仿真 Gateway，模拟撮合
- **回测模式**：Host API 调用回测引擎，历史数据回放

策略代码无需关心运行模式，只需实现业务逻辑。

### 10.3 回测特殊要求

- 回测模式下，时间按历史数据推进
- 回测模式下，订单成交由回测引擎模拟
- 回测模式下，持仓和账户由回测引擎维护
- 回测模式下，策略输出可导出为报告

## 11. Python 参考抽象

```python
from dataclasses import dataclass
from datetime import datetime
from typing import Any
from abc import ABC, abstractmethod

class BaseStrategy(ABC):
    @abstractmethod
    def manifest(self) -> dict: ...

    def on_init(self, ctx: StrategyContext) -> None:
        pass

    def on_start(self, ctx: StrategyContext) -> None:
        pass

    def on_stop(self, ctx: StrategyContext) -> None:
        pass

    def on_tick(self, ctx: StrategyContext, tick: Tick) -> None:
        pass

    def on_bar(self, ctx: StrategyContext, bar: Bar) -> None:
        pass

    def on_order(self, ctx: StrategyContext, order: Order) -> None:
        pass

    def on_trade(self, ctx: StrategyContext, trade: Trade) -> None:
        pass

    def on_risk_event(self, ctx: StrategyContext, event: RiskCheckResult) -> None:
        pass

    def outputs(self) -> dict:
        return {}

    def schema(self) -> dict:
        return {}
```

## 12. 最低测试要求

- manifest 解析与权限校验测试
- submit_order 风控拦截测试
- cancel_order 成功与失败测试
- get_positions 返回正确持仓测试
- get_account 返回正确账户测试
- on_order 回调触发测试
- on_trade 回调触发测试
- on_risk_event 回调触发测试
- 回测模式与实盘模式接口一致性测试
- 策略异常隔离测试
- 策略输出重放一致性测试
