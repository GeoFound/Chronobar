# 中国期货专用平台风控协议 v1.2

## 1. 文档定位

本文档定义平台的风控检查接口、风控事件模型、风控规则配置和风控集成机制。
风控是交易执行前的必要安全屏障，所有订单必须通过风控检查才能提交到交易所。

## 2. 风控目标

1. 在订单提交前进行多层次风险检查，防止异常交易。
2. 支持可配置的风控规则，适应不同策略和用户需求。
3. 保证风控检查在实盘、仿真、回测模式下行为一致。
4. 提供清晰的风控拦截原因和可追溯的日志。
5. 支持策略级别的风控参数声明和系统级别的风控规则。

## 3. 风控检查类型

### 3.1 持仓限制检查 (position_limit)

检查当前持仓是否超过限制：
- 单合约最大持仓数
- 单方向最大持仓数
- 总持仓限制

### 3.2 订单限制检查 (order_limit)

检查订单频率和数量：
- 每日最大订单数
- 每分钟最大订单数
- 单笔订单最大数量

### 3.3 资金检查 (margin_check)

检查账户资金是否充足：
- 可用资金是否足够
- 保证金是否充足
- 预估冻结资金检查

### 3.4 价格检查 (price_band)

检查订单价格是否在合理区间：
- 涨跌停板检查
- 价格偏离度检查
- 最小价格单位检查

### 3.5 冻结检查 (frozen_check)

检查账户或合约状态：
- 账户是否被冻结
- 合约是否被冻结
- 交易是否被暂停

### 3.6 自定义风控检查 (custom)

支持用户自定义风控规则：
- 自定义条件检查
- 自定义阈值检查
- 自定义逻辑检查

### 3.7 AI 风控检查 (ai)

AI 风控检查器作为 custom 检查器的特殊实现，用于识别异常模式：

**异常下单行为检测：**
- 识别策略在高波动期的异常高频下单
- 自动触发 RISK_WARNING 事件
- 建议暂停策略信号或降低下单频率

**市场微结构异常检测：**
- 基于 Tick 数据识别闪崩/流动性枯竭等异常状态
- 自动暂停策略信号
- 发出 RISK_BLOCKED 事件

**重要约束：**
- AI 风控检查器只能发出 RISK_BLOCKED / RISK_WARNING 事件
- 不能直接操作仓位或修改订单
- 必须通过事件总线输出结果
- 需要大量历史数据训练，建议在 M3 阶段实施

## 4. 风控检查接口

### 4.1 RiskChecker 接口

```python
from abc import ABC, abstractmethod
from dataclasses import dataclass

@dataclass(slots=True)
class RiskCheckRequest:
    gateway_name: str
    account_id: str
    order_request: OrderRequest
    current_positions: list[Position]
    current_account: Account
    current_orders: list[Order]
    strategy_id: str | None = None
    context: dict | None = None

@dataclass(slots=True)
class RiskCheckResult:
    passed: bool
    check_type: RiskCheckType
    block_reason: str | None
    block_code: str | None
    check_time: datetime
    context: dict | None = None

class RiskChecker(ABC):
    @abstractmethod
    def check(self, request: RiskCheckRequest) -> RiskCheckResult:
        """执行风控检查"""
        ...

    @abstractmethod
    def get_check_type(self) -> str:
        """返回风控检查类型"""
        ...
```

### 4.2 RiskManager 接口

```python
class RiskManager(ABC):
    def register_checker(self, checker: RiskChecker) -> None:
        """注册风控检查器"""
        ...

    def unregister_checker(self, check_type: str) -> None:
        """注销风控检查器"""
        ...

    def check_order(self, request: RiskCheckRequest) -> RiskCheckResult:
        """执行订单风控检查"""
        ...

    def get_all_check_types(self) -> list[str]:
        """获取所有注册的风控检查类型"""
        ...
```

## 5. 风控检查流程

### 5.1 执行方式

风控检查采用**串行执行**方式，按优先级顺序依次执行：

1. **冻结检查** (frozen_check)：检查账户和合约状态
2. **价格检查** (price_band)：检查订单价格合法性
3. **资金检查** (margin_check)：检查资金充足性
4. **持仓限制检查** (position_limit)：检查持仓是否超限
5. **订单限制检查** (order_limit)：检查订单频率和数量
6. **自定义风控检查** (custom)：执行自定义规则

### 5.2 短路逻辑

一旦某个风控检查失败（`passed=False`），立即返回失败结果，**跳过后续所有检查**。

短路逻辑的好处：
- **性能优化**：避免不必要的计算
- **可解释性**：订单被拦截的原因清晰明确
- **审计友好**：日志中只记录实际执行的检查

### 5.3 检查结果

- **全部通过**：返回 `passed=True`，订单可以提交
- **任一失败**：返回 `passed=False`，订单被拦截，返回失败原因（包含 checker_name、reason_code、reason_text）

### 5.4 检查日志

所有风控检查结果必须记录日志，包括：
- 检查时间
- 检查类型
- 检查结果
- 拦截原因（如果失败）
- 相关订单信息
- 相关账户和持仓信息

## 6. 风控事件

### 6.1 RISK_BLOCKED 事件

当风控检查失败时触发：

```python
event = EventEnvelope(
    event_type="RISK_BLOCKED",
    source="risk.position_limit",
    ts=datetime.now(),
    instrument_id=order_request.instrument_id,
    payload=RiskCheckResult(
        passed=False,
        check_type="position_limit",
        block_reason="持仓超过限制: 当前15手, 最大10手",
        block_code="POSITION_LIMIT_EXCEEDED",
        check_time=datetime.now(),
        context={"current_position": 15, "limit": 10}
    )
)
```

### 6.2 RISK_WARNING 事件

当风控检查通过但接近阈值时触发：

```python
event = EventEnvelope(
    event_type="RISK_WARNING",
    source="risk.margin_check",
    ts=datetime.now(),
    instrument_id=order_request.instrument_id,
    payload={
        "check_type": "margin_check",
        "warning_reason": "可用资金不足20%",
        "current_available": 10000,
        "required_margin": 8500,
        "usage_ratio": 0.85
    }
)
```

## 7. 风控配置

### 7.1 系统级风控配置

```json
{
  "risk_settings": {
    "position_limits": {
      "max_position_per_instrument": 50,
      "max_position_per_direction": 100,
      "max_total_position": 500
    },
    "order_limits": {
      "max_orders_per_day": 1000,
      "max_orders_per_minute": 50,
      "max_volume_per_order": 100
    },
    "margin_settings": {
      "min_available_ratio": 0.2,
      "warn_available_ratio": 0.3
    },
    "price_band_settings": {
      "enable_limit_check": true,
      "max_deviation_ratio": 0.1
    }
  }
}
```

### 7.2 策略级风控配置

在策略 manifest 中声明：

```json
{
  "risk_profile": {
    "max_position_per_instrument": 10,
    "max_orders_per_day": 100,
    "max_loss_per_day": 10000
  }
}
```

策略级配置优先于系统级配置。

## 8. 风控集成

### 8.1 与策略插件集成

策略插件通过 `on_risk_event` 回调接收风控事件：

```python
def on_risk_event(ctx, event) -> None:
    if event.check_type == "position_limit":
        ctx.log_warning(f"持仓限制被触发: {event.block_reason}")
        # 可以选择暂停策略或调整参数
    elif event.check_type == "margin_check":
        ctx.log_error(f"资金不足: {event.block_reason}")
        # 可以选择平仓或停止策略
```

### 8.2 与 Gateway 集成

在订单提交前执行风控检查：

```python
def submit_order(self, request: OrderRequest) -> str:
    # 构建风控检查请求
    risk_request = RiskCheckRequest(
        gateway_name=request.gateway_name,
        account_id=self.account_id,
        order_request=request,
        current_positions=self.get_positions(),
        current_account=self.get_account(),
        current_orders=self.get_open_orders()
    )

    # 执行风控检查
    result = self.risk_manager.check_order(risk_request)

    # 检查结果
    if not result.passed:
        # 触发 RISK_BLOCKED 事件
        self.event_bus.put(EventEnvelope(
            event_type="RISK_BLOCKED",
            source="risk_manager",
            ts=datetime.now(),
            payload=result
        ))
        raise RiskCheckError(result.block_reason)

    # 通过风控检查，提交订单
    return self.gateway.submit_order(request)
```

## 9. 风控规则扩展

### 9.1 自定义风控检查器

用户可以实现自定义风控检查器：

```python
class CustomRiskChecker(RiskChecker):
    def get_check_type(self) -> str:
        return "custom"

    def check(self, request: RiskCheckRequest) -> RiskCheckResult:
        # 自定义风控逻辑
        if some_condition:
            return RiskCheckResult(
                passed=False,
                check_type="custom",
                block_reason="自定义风控规则触发",
                block_code="CUSTOM_RULE_TRIGGERED",
                check_time=datetime.now()
            )
        return RiskCheckResult(
            passed=True,
            check_type="custom",
            block_reason=None,
            block_code=None,
            check_time=datetime.now()
        )
```

### 9.2 注册自定义检查器

```python
custom_checker = CustomRiskChecker()
risk_manager.register_checker(custom_checker)
```

## 10. 回测模式下的风控

回测模式下，风控检查必须与实盘模式保持一致：

- 使用相同的风控检查接口
- 使用相同的风控规则配置
- 使用相同的风控检查流程
- 记录相同的风控检查日志

回测模式下，风控检查失败时：
- 订单不会成交
- 记录风控拦截事件
- 策略可以继续运行或停止

## 11. Python 参考实现

```python
from dataclasses import dataclass
from datetime import datetime
from typing import Any
from abc import ABC, abstractmethod
from enum import Enum

class RiskCheckType(str, Enum):
    POSITION_LIMIT = "position_limit"
    ORDER_LIMIT = "order_limit"
    MARGIN_CHECK = "margin_check"
    PRICE_BAND = "price_band"
    FROZEN_CHECK = "frozen_check"
    CUSTOM = "custom"

@dataclass(slots=True)
class RiskCheckRequest:
    gateway_name: str
    account_id: str
    order_request: OrderRequest
    current_positions: list[Position]
    current_account: Account
    current_orders: list[Order]
    strategy_id: str | None = None
    context: dict[str, Any] | None = None

@dataclass(slots=True)
class RiskCheckResult:
    passed: bool
    check_type: str
    block_reason: str | None
    block_code: str | None
    check_time: datetime
    context: dict[str, Any] | None = None

class RiskChecker(ABC):
    @abstractmethod
    def check(self, request: RiskCheckRequest) -> RiskCheckResult:
        ...

    @abstractmethod
    def get_check_type(self) -> str:
        ...

class RiskManager:
    def __init__(self):
        self._checkers: dict[str, RiskChecker] = {}

    def register_checker(self, checker: RiskChecker) -> None:
        self._checkers[checker.get_check_type()] = checker

    def unregister_checker(self, check_type: str) -> None:
        self._checkers.pop(check_type, None)

    def check_order(self, request: RiskCheckRequest) -> RiskCheckResult:
        # 按顺序执行所有检查
        check_order = [
            RiskCheckType.FROZEN_CHECK,
            RiskCheckType.PRICE_BAND,
            RiskCheckType.MARGIN_CHECK,
            RiskCheckType.POSITION_LIMIT,
            RiskCheckType.ORDER_LIMIT,
            RiskCheckType.CUSTOM
        ]

        for check_type in check_order:
            checker = self._checkers.get(check_type)
            if checker:
                result = checker.check(request)
                if not result.passed:
                    return result

        return RiskCheckResult(
            passed=True,
            check_type="all",
            block_reason=None,
            block_code=None,
            check_time=datetime.now()
        )
```

## 12. 最低测试要求

- 单个风控检查器测试
- 风控检查顺序测试
- 风控拦截事件触发测试
- 风控警告事件触发测试
- 策略级风控配置优先级测试
- 自定义风控检查器测试
- 回测模式风控一致性测试
- 风控日志记录测试
- 风控检查性能测试
