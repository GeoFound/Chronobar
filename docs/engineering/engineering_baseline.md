# 中国期货专用平台工程基线 v1.2

## 1. 文档定位

本文档定义平台工程组织、代码质量要求、测试规范、版本策略、开发流程和交付门槛。
所有后续开发、重构、AI 生成代码和外部协作都必须遵守本基线。

## 2. 工程目标

1. 保证核心协议长期稳定。
2. 保证模块可测试、可替换、可迁移。
3. 保证 AI 生成代码能被统一吸纳，而不是污染核心结构。
4. 保证回放结果、配置迁移和插件行为可验证。
5. 保证 Python 核心与 React 前端可以分层协作，而不互相侵入。

## 3. 仓库结构

推荐目录如下：

```text
futures_platform/
  pyproject.toml
  README.md
  docs/
    core/
      data_protocol.md
      event_protocol.md
      plugin_protocol.md
    system/
      architecture.md
      config_protocol.md
      ui_bridge_protocol.md
    engineering/
      engineering_baseline.md
  app/
    main.py
  core/
    enums.py
    models.py
    events.py
    exceptions.py
    event_engine.py
    main_engine.py
    ui_bridge.py
  gateways/
    base.py
    openctp_gateway.py
    mappers/
  rules/
    trading_calendar.py
    session_engine.py
    templates/
  compute/
    bar_aggregator.py
    indicators/
    replay/
    signals/
  storage/
    sqlite_repo.py
    config_repo.py
    log_repo.py
  plugins/
    host_api.py
    loader.py
    sandbox.py
    builtins/
  strategy/
    host_api.py
    context.py
    base_strategy.py
  ui/
    desktop/
      app_shell/
      workspace/
      chart/
      panels/
      state/
      shared/
  config/
    defaults/
    schemas/
    migration.py
    loader.py
  tests/
    unit/
    integration/
    replay/
    migration/
    plugins/
    ui_contract/
```

说明：
- `core/ui_bridge.py` 为展示层桥接边界实现。
- `ui/desktop/` 为 React 桌面前端目录。
- `tests/ui_contract/` 用于验证前端与桥接层契约稳定性。

## 4. 代码规范

### 4.1 Python 版本

- Python 3.11+ 为最低支持版本。
- 新特性使用需以 3.11 为兼容下限。

### 4.2 Python 类型要求

- 核心模块必须全量类型标注。
- 公共函数禁止无返回类型。
- 公共接口禁止使用无约束 `dict` 作为长期数据边界。
- 协议对象优先使用 dataclass / Enum / Protocol / ABC。
- 动态数据的结构校验必须落在 schema 或 validator，而不是散落在 UI 中。

### 4.3 前端要求

- React 前端必须使用 TypeScript。
- 页面状态、工作区状态、订阅状态必须分层管理。
- 前端不得直接发明业务字段。
- 前端消费的所有业务数据必须来自受控桥接接口。
- UI 组件不得绕过桥接层访问核心进程内部模块。

### 4.4 命名规范

- Python 模块名：小写下划线
- 类名：大驼峰
- 常量：全大写下划线
- 事件类型：全大写
- 配置键：小写下划线
- 前端组件名：大驼峰
- 前端状态切片名：语义化小写命名

### 4.5 异常规范

- 不允许裸 `except`
- 业务异常、协议异常、插件异常、桥接异常分层定义
- 所有可恢复异常必须记录日志
- 所有不可恢复异常必须阻断当前任务并给出可追踪信息

## 5. 质量门槛

### 5.1 测试基线

测试框架建议：
- Python：pytest
- Frontend：Vitest / Playwright

测试覆盖率目标：
- 核心模块（event_engine、main_engine、storage、risk、backtest）：≥80%
- 协议层（data_protocol、event_protocol、plugin_protocol）：≥95%

关键路径必须覆盖：
- 订单生命周期
- 风控拦截
- 事件投递
- 历史 Tick 读取
- 回放模式切换

必须覆盖：
- 单元测试
- 协议测试
- 配置迁移测试
- 回放一致性测试
- 插件隔离测试
- 关键集成测试
- 前端桥接契约测试

### 5.2 类型检查

类型检查工具建议：
- Python：mypy
- Frontend：tsc

要求：
- `core / rules / compute / plugins.host_api` 必须通过类型检查
- 新增公共接口必须补类型声明
- 忽略规则必须最小化，禁止大面积跳过

### 5.3 日志要求

- 核心流程必须有结构化日志
- 关键事件必须记录 `trace_id`
- 插件异常必须生成独立日志事件
- 回放模式必须可导出事件日志
- 前端命令失败与订阅异常必须可追踪

## 6. 配置治理

### 6.1 配置来源优先级

1. 系统默认
2. 环境配置
3. 品种模板
4. 合约实例
5. 工作区局部覆盖

### 6.2 配置变更要求

- 修改 schema 必须同步更新示例文件
- 修改字段含义必须补 migration
- 删除字段必须保留兼容层
- 所有迁移必须附测试样例
- 桥接层配置变更必须同步更新契约说明

## 7. 插件治理

### 7.1 接入要求

- 必须提供 manifest
- 必须提供 schema
- 必须声明权限
- 必须具备最小测试样例

### 7.2 卸载要求

- 卸载插件不得破坏主程序启动
- 卸载后旧工作区应允许降级加载
- 缺失插件必须显示可恢复提示，而不是直接崩溃

### 7.3 安全要求

- 默认最小权限
- 文件写入、网络访问、告警发射都必须显式授权
- 插件不得直接访问数据库连接对象
- 插件不得直接持有前端组件实例或前端状态仓库

## 8. 开发顺序

### 第一阶段：协议定稿

- core/data_protocol.md
- core/event_protocol.md
- system/config_protocol.md
- core/plugin_protocol.md
- system/ui_bridge_protocol.md

### 第二阶段：核心闭环（严格依序生成）

1. core/enums.py
2. core/models.py（验证所有协议对象可序列化）
3. core/events.py
4. core/exceptions.py
5. core/event_engine.py
6. core/main_engine.py
7. rules/session_engine.py
8. compute/bar_aggregator.py
9. plugins/host_api.py
10. core/ui_bridge.py

**注意：** 必须严格按此顺序生成，防止 AI 在 event_engine.py 中重复定义 EventEnvelope 等已在 models.py 中定义的对象。

### 第三阶段：接入与展示

- openctp_gateway.py
- workspace 基础框架
- chart 基础视图
- 参数面板自动生成
- React 工作区壳层

### 第四阶段：验证体系

- replay engine
- migration test
- plugin sandbox test
- integration test
- ui contract test

## 9. 交付标准

一个功能只有满足以下条件才算完成：

1. 协议有定义
2. 配置有样例
3. 代码有实现
4. 测试可运行
5. 日志可追踪
6. 回放可复现
7. 文档已更新

## 10. AI 协作约束

### 10.1 生成前声明模板

AI 在生成代码前必须声明：

```
本次生成声明：
- 所属层：Infrastructure / Core / Gateway / UI Bridge / Plugin / Risk / Backtest
- 实现目标：实现哪个类/模块
- 对应协议：引用哪个 protocol 文档中的哪个接口/对象
- 依赖对象：依赖哪些已存在类、枚举、事件、模型
- 禁止事项：不得新增重复模型，不得跨层直接调用未授权对象
```

### 10.2 生成约束

- AI 生成代码不得绕过协议文档
- AI 生成新功能必须先声明所属层级
- AI 生成插件必须使用标准生命周期接口
- AI 修改配置结构必须同步生成 migration
- AI 生成桥接接口必须同步更新契约说明
- AI 生成代码在合并前必须通过测试与类型检查

## 11. 存储层技术决策

### 11.1 历史 Tick 存储

- **技术选型**：DuckDB + Parquet 双层架构
- **实时写入路径**：GatewayAdapter → TickCache (内存 deque) → 定时落盘 → Parquet 文件（按交易日分片）
- **查询/回测路径**：BacktestEngine → DuckDB (直接查询 Parquet) → Strategy
- **Parquet 文件**：按 instrument_id/trading_date.parquet 分片存储，支持时间分区裁剪
- **DuckDB**：作为查询引擎直接读取 Parquet，不额外存储数据，仅作为 SQL 计算层使用

### 11.2 元数据存储

- 合约基础信息、交易日历、策略参数等小表继续使用 SQLite
- DuckDB + Parquet 专门处理 Tick 时序数据

### 11.3 禁止事项

- 禁止使用 TimescaleDB（需服务进程，违反单进程原则）
- 禁止使用 InfluxDB（需服务进程，版权复杂）
- 禁止将 SQLite 用于 Tick 历史数据存储（量级天花板低）

## 12. pyproject.toml 基线

### 12.1 Python 版本

```
requires-python = ">=3.11,<3.13"
```

### 12.2 Runtime 必选依赖

```
pydantic>=2.5,<3
fastapi>=0.110,<1
uvicorn>=0.27,<1
duckdb>=0.10,<2
pyarrow>=14.0,<15
orjson>=3.9,<4
typing-extensions>=4.9,<5
tenacity>=8.2,<9
```

### 12.3 Dev 必选依赖

```
pytest
pytest-asyncio
pytest-cov
ruff
mypy
pre-commit
```

### 12.4 可选扩展

按阶段启用：

```
pandas
polars
msgspec
openctp-ctp
apscheduler
```

### 12.5 依赖管理原则

- Runtime 依赖必须显式列出
- Dev 依赖单独分组
- 所有关键库必须锁定大版本
- FastAPI、Pydantic、DuckDB 必须确认可用版本范围

## 13. 禁止事项

- 禁止先堆 UI 再补内核
- 禁止核心对象长期使用松散 dict 传递
- 禁止跨层直接调用成为默认协作路径
- 禁止插件直接改核心状态
- 禁止没有测试就合并核心模块
- 禁止为了临时需求破坏协议兼容性
- 禁止前端组件依赖未声明桥接字段

## 14. 里程碑验收

### M1：协议完成
- 四类协议定稿
- UI Bridge 协议定稿
- schema 可校验
- 示例配置可加载

### M2：核心闭环完成
- Tick -> Event -> Bar -> Indicator -> Chart 跑通
- 夜盘 session 正确切分
- 插件可加载、可隔离、可卸载
- React 前端可消费标准查询结果与标准事件

### M3：验证体系完成
- 回放结果与实时结果一致
- 配置迁移可自动完成
- 关键模块通过 pytest、mypy、tsc 和契约测试检查

## 15. 成熟项目参考

根据 Chronobar 的技术栈和定位，以下成熟项目有明确借鉴价值：

### 核心架构参考

| 项目 | 借鉴点 |
|------|--------|
| **vn.py** | 中国期货事件驱动架构的事实标准；BaseGateway 接口设计、MainEngine 协调模式、CTP 回调映射均是 Chronobar 同类问题的成熟解 |
| **backtrader** | 回测引擎的 Broker 抽象、数据 Feed 接口、策略生命周期设计，与 backtest_protocol.md 高度重叠 |
| **nautilus_trader** | Rust/Python 混合架构、强类型 Protocol 定义、回放一致性设计，与 Chronobar 技术方向最接近 |

### UI/前端参考

| 项目 | 借鉴点 |
|------|--------|
| **TradingView Lightweight Charts** | K 线图表组件的标准实现，React 集成方案成熟 |
| **OpenBB Terminal** | 桌面金融终端的工作区布局、面板管理、插件体系 |

### 工程规范参考

| 项目 | 借鉴点 |
|------|--------|
| **Pydantic** | 与 data_protocol.md 中的强类型对象定义直接对应；迁移验证（model_validator）可用于 config migration |
| **FastAPI** | UiBridge 的 HTTP + WebSocket 边界实现的最佳实践 |

**注意：** 以上项目作为参考，不意味着直接复制代码或架构。Chronobar 的设计决策应基于自身需求（桌面客户端、Tauri + React + Python sidecar、DuckDB + Parquet 存储）独立评估后确定。