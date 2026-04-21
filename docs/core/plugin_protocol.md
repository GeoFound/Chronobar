# 中国期货专用平台插件协议 v1.2

## 1. 文档定位

本文档定义平台插件的目录结构、生命周期、权限模型、Host API、输出契约和异常隔离机制。
插件是受控扩展单元，不是任意脚本执行器。

## 2. 插件目标

1. 让新增指标、提醒、导出器、图层和规则扩展尽量不改核心程序。
2. 让插件以标准协议接入，而不是以项目私有写法接入。
3. 让插件具备最小权限、可测试、可下线、可回放。
4. 让插件输出可以稳定进入图表层、面板层和回放体系。

## 3. 插件分类

### 3.1 指标插件 (indicator)

- **权限**：只读市场数据，输出线、柱、标记、告警
- **能力**：计算指标、输出图表数据、触发告警
- **限制**：不能下单、不能读取账户、不能读取持仓
- **适用场景**：技术指标计算、自定义分析、可视化扩展

### 3.2 信号插件 (signal)

- **权限**：可读取指标和事件，输出开平仓建议
- **能力**：生成交易信号、输出建议、触发告警
- **限制**：不能直接下单，只能输出信号供策略参考
- **适用场景**：信号生成器、策略信号模块、交易建议系统

### 3.3 策略插件 (strategy)

- **权限**：可下单、撤单、读持仓、读账户，但必须单独授权
- **能力**：submit_order、cancel_order、get_positions、get_account、get_open_orders
- **限制**：必须通过风控检查，必须单独沙箱隔离，必须显式用户授权
- **适用场景**：自动交易策略、量化策略、算法交易

### 3.4 UI 扩展插件 (ui-extension)

- **权限**：扩展前端面板、自定义组件
- **能力**：添加自定义面板、自定义图表组件、自定义交互
- **限制**：不能直接访问核心交易逻辑，只能通过 UI Bridge
- **适用场景**：自定义面板、第三方工具集成、特殊可视化需求

**注：** AI 智能体插件（ai-agent）的详细协议定义请参考 [`docs/core/ai_protocol.md`](ai_protocol.md)

## 4. 插件目录结构

```text
plugin_name/
  manifest.json
  plugin.py
  assets/
  tests/
  README.md
```

## 5. manifest 基线

### 5.1 指标插件 manifest

```json
{
  "name": "ma_segmented",
  "version": "1.0.0",
  "api_version": "1.2",
  "kind": "indicator",
  "entry": "plugin.py",
  "dependencies": [],
  "depends_on": [],
  "load_after": [],
  "permissions": {
    "read_market_data": true,
    "emit_alert": false,
    "write_file": false,
    "read_workspace": false
  },
  "compatibility": {
    "min_core_version": "1.2",
    "max_core_version": "1.x"
  }
}
```

### 5.2 信号插件 manifest

```json
{
  "name": "dual_ma_signal",
  "version": "1.0.0",
  "api_version": "1.2",
  "kind": "signal",
  "entry": "plugin.py",
  "dependencies": [],
  "depends_on": ["ma_segmented"],
  "load_after": [],
  "permissions": {
    "read_market_data": true,
    "emit_alert": true,
    "write_file": false,
    "read_workspace": false
  },
  "compatibility": {
    "min_core_version": "1.2",
    "max_core_version": "1.x"
  }
}
```

### 5.3 策略插件 manifest

```json
{
  "name": "dual_ma_strategy",
  "version": "1.0.0",
  "api_version": "1.0",
  "kind": "strategy",
  "entry": "strategy.py",
  "dependencies": [],
  "depends_on": ["dual_ma_signal"],
  "load_after": [],
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

### 5.4 UI 扩展插件 manifest

```json
{
  "name": "custom_panel",
  "version": "1.0.0",
  "api_version": "1.2",
  "kind": "ui-extension",
  "entry": "plugin.py",
  "dependencies": [],
  "permissions": {
    "read_market_data": true,
    "emit_alert": false,
    "write_file": false,
    "read_workspace": true
  },
  "compatibility": {
    "min_core_version": "1.2",
    "max_core_version": "1.x"
  }
}
```

**注：** AI 智能体插件（ai-agent）的 manifest 示例请参考 [`docs/core/ai_protocol.md`](ai_protocol.md) 第 4 节。

### 5.5 依赖加载策略

**depends_on 字段处理：**

- **硬依赖缺失**：如果 depends_on 中声明的插件未加载或加载失败，加载器必须拦截当前插件的加载并报错，禁止降级加载。
- **版本不兼容**：如果 depends_on 中声明的插件版本不满足 compatibility 约束，加载器必须拦截当前插件的加载并报错。
- **循环依赖检测**：加载器必须检测循环依赖（A depends_on B，B depends_on A），发现循环依赖时必须拒绝加载所有涉及插件。

**load_after 字段处理：**

- load_after 仅用于提示加载顺序，不是硬依赖。
- 如果 load_after 中声明的插件未加载，加载器应发出警告但仍继续加载当前插件。
- load_after 不影响依赖关系的正确性，仅影响初始化顺序。

## 6. 生命周期接口

```python
def manifest() -> dict: ...
def on_init(ctx) -> None: ...
def on_start(ctx) -> None: ...
def on_stop(ctx) -> None: ...
def on_tick(ctx, tick) -> None: ...
def on_bar(ctx, bar) -> None: ...
def on_event(ctx, event) -> None: ...
def outputs() -> dict: ...
def schema() -> dict: ...
```

说明：
- `on_init`：资源初始化、订阅声明、参数读取
- `on_start`：正式启动
- `on_stop`：释放资源
- `outputs`：声明插件可向系统暴露的标准输出
- `schema`：声明参数面板、样式项、校验规则

## 7. Host API 基线

```python
class PluginContext(Protocol):
    def emit(self, event_type: str, payload: object) -> None: ...
    def subscribe(self, event_type: str, handler) -> None: ...
    def get_config(self, path: str) -> object: ...
    def get_instrument(self, instrument_id: str) -> object: ...
    def get_session_context(self, instrument_id: str, dt) -> object: ...
    def publish_alert(self, level: str, title: str, content: str) -> None: ...
    def write_cache(self, key: str, value: object) -> None: ...
    def read_cache(self, key: str) -> object | None: ...
    def get_llm_provider(self, provider_name: str) -> object | None: ...
```

**get_llm_provider() 说明：**
- 获取 LLM 提供商实例（仅 ai-agent 类型插件可用）
- 调用此方法需要 `call_external_api: true` 权限，否则返回 None 并记录拒绝日志
- 返回的 LLMProvider 实例遵循 [`ai_protocol.md`](ai_protocol.md) 第 7.3 节定义的接口协议
- 支持的 provider_name: local, deepseek, openai, anthropic

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
- **call_external_api**：调用外部 API（ai-agent 专用，需用户授权，详见 [`docs/core/ai_protocol.md`](ai_protocol.md)）

### 8.2 默认权限原则

- 默认无权限
- 按 manifest 显式声明
- 核心按权限表授予 Host API 能力
- 未授权调用直接拒绝并记录日志
- 策略插件需要用户显式授权才能加载

### 8.3 禁止行为

- 禁止插件直接持有数据库连接
- 禁止插件直接持有主窗口内部对象
- 禁止插件直接持有前端组件实例或前端状态仓库
- 禁止插件绕过事件总线推送业务消息
- 禁止插件修改核心对象私有状态
- 禁止插件在未授权情况下写文件或发网络请求

## 9. 输出契约

插件输出必须满足以下条件：

1. 输出对象必须可序列化。
2. 输出必须带来源插件标识。
3. 输出必须声明数据域，例如 `line` / `histogram` / `signal` / `alert`。
4. 输出必须允许图层显示 / 隐藏。
5. 输出必须可在回放模式下重现。
6. 输出进入展示层前必须经过标准映射。

## 10. 展示层映射约束

- 插件不得直接操作前端组件。
- 插件不得直接调用图表实例方法。
- 插件输出只能通过 Host API、事件总线和标准输出契约进入展示层。
- 展示层只消费声明过的数据域和标准输出结构。
- 插件输出在实时与回放模式下必须保持同构。

## 11. 异常隔离

- 插件异常不得拖垮主进程
- 单插件失败不影响其他插件
- 异常必须转化为 `PLUGIN_ERROR`
- 连续异常达到阈值可自动停用插件
- 停用行为必须可记录、可恢复、可告警

## 12. Python 参考抽象

```python
from abc import ABC, abstractmethod

class BasePlugin(ABC):
    @abstractmethod
    def manifest(self) -> dict: ...

    def on_init(self, ctx) -> None:
        pass

    def on_start(self, ctx) -> None:
        pass

    def on_stop(self, ctx) -> None:
        pass

    def on_tick(self, ctx, tick) -> None:
        pass

    def on_bar(self, ctx, bar) -> None:
        pass

    def on_event(self, ctx, event) -> None:
        pass

    def outputs(self) -> dict:
        return {}

    def schema(self) -> dict:
        return {}
```

## 13. 最低测试要求

- manifest 解析测试
- schema 参数校验测试
- 权限拦截测试
- 插件异常隔离测试
- 输出重放一致性测试
- 输出到展示层映射契约测试
