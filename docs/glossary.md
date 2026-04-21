# Chronobar 术语表

本文档定义 Chronobar 项目中的关键术语，确保跨文档的一致理解。

## 数据对象

### Tick

**定义：** 单个价格变动数据点，包含时间戳、最新价、买一价、卖一价、成交量等信息。

**用途：** 高频交易的基础数据单位，用于实时行情展示和高频策略计算。

**相关文档：** [`docs/core/data_protocol.md`](core/data_protocol.md)

### Bar

**定义：** 聚合后的 K 线数据，包含开盘价、最高价、最低价、收盘价、成交量，按时间窗口聚合（如 1 分钟、5 分钟）。

**用途：** 中低频策略计算、技术指标计算、图表展示。

**相关文档：** [`docs/core/data_protocol.md`](core/data_protocol.md)

### Instrument

**定义：** 交易标的（合约）的基础信息，包括合约代码、交易所、最小变动价位、交易时段等。

**用途：** 标识可交易的合约，提供合约元数据。

**相关文档：** [`docs/core/data_protocol.md`](core/data_protocol.md)

### EventEnvelope

**定义：** 事件封装对象，包含事件类型、事件数据、时间戳、事件 ID 等元数据。

**用途：** 模块间默认通信方式，通过事件总线传递。

**相关文档：** [`docs/core/event_protocol.md`](core/event_protocol.md)

### Order

**定义：** 订单对象，包含订单 ID、合约代码、方向（买/卖）、数量、价格、状态等信息。

**用途：** 策略向网关提交的交易指令。

**相关文档：** [`docs/core/data_protocol.md`](core/data_protocol.md)

### Trade

**定义：** 成交对象，包含成交 ID、订单 ID、合约代码、成交价格、成交数量等信息。

**用途：** 订单成交后的回执，用于更新持仓和账户。

**相关文档：** [`docs/core/data_protocol.md`](core/data_protocol.md)

### Position

**定义：** 持仓对象，包含合约代码、方向（多头/空头）、数量、可用数量、浮动盈亏等信息。

**用途：** 记录当前持仓状态。

**相关文档：** [`docs/core/data_protocol.md`](core/data_protocol.md)

### Account

**定义：** 账户对象，包含账户 ID、总资金、可用资金、保证金、冻结资金等信息。

**用途：** 记录账户资金状态。

**相关文档：** [`docs/core/data_protocol.md`](core/data_protocol.md)

## 系统概念

### 插件 (Plugin)

**定义：** 可扩展的功能模块，通过标准协议接入系统，分为 5 层：指标插件、信号插件、策略插件、UI 扩展插件、AI 智能体插件。

**用途：** 扩展系统能力，避免核心代码膨胀。

**相关文档：** [`docs/core/plugin_protocol.md`](core/plugin_protocol.md)

### Host API

**定义：** 插件可调用的核心接口集合，提供受限能力（如读取市场数据、提交订单），受权限模型约束。

**用途：** 插件与核心交互的安全边界。

**相关文档：** [`docs/core/plugin_protocol.md`](core/plugin_protocol.md)

### 事件总线 (Event Bus)

**定义：** 模块间默认协作通道，基于发布-订阅模式的事件传递机制。

**用途：** 解耦模块间依赖，支持异步通信。

**相关文档：** [`docs/core/event_protocol.md`](core/event_protocol.md)

### 风控检查器 (Risk Checker)

**定义：** 交易前风控检查接口，按优先级串行执行，任何检查失败则拒绝订单。

**用途：** 交易前风险控制，防止违规交易。

**相关文档：** [`docs/core/risk_protocol.md`](core/risk_protocol.md)

### 回测引擎 (Backtest Engine)

**定义：** 基于历史数据的仿真执行引擎，支持实时/回测/仿真三种模式统一接口。

**用途：** 策略回测、参数优化、仿真测试。

**相关文档：** [`docs/core/backtest_protocol.md`](core/backtest_protocol.md)

### AI 智能体 (AI Agent)

**定义：** 受控的 AI 插件，通过 HostAPI 与核心交互，不能绕过风控直接操盘。

**用途：** AI Copilot、AI 信号生成、AI 回测分析。

**相关文档：** [`docs/core/ai_protocol.md`](core/ai_protocol.md)

## 技术术语

### DuckDB

**定义：** 列式存储数据库，支持向量化查询，可直接读取 Parquet 文件。

**用途：** Chronobar 的查询引擎，用于回测和历史数据查询。

**相关文档：** [`docs/decisions/001-storage-architecture.md`](decisions/001-storage-architecture.md)

### Parquet

**定义：** 列式存储文件格式，支持压缩和时间分区裁剪。

**用途：** Chronobar 的 Tick 历史数据存储格式，按交易日分片。

**相关文档：** [`docs/decisions/001-storage-architecture.md`](decisions/001-storage-architecture.md)

### Tauri

**定义：** 跨平台桌面应用框架，使用 Rust 后端 + Web 前端。

**用途：** Chronobar 的桌面应用框架，提供原生桌面体验。

**相关文档：** [`docs/system/architecture.md`](system/architecture.md)

### UI Bridge

**定义：** React 前端与 Python 核心之间的通信桥接，提供 Query/Command/Subscription API。

**用途：** 前后端分离架构下的交互边界。

**相关文档：** [`docs/system/ui_bridge_protocol.md`](system/ui_bridge_protocol.md)

## 协议术语

### 协议 (Protocol)

**定义：** 定义系统边界的正式文档，包括数据对象、事件模型、插件接口、风控规则等。

**用途：** 确保模块间协作的一致性和可预测性。

**相关文档：** [`README.md`](../README.md) 文档地图

### ADR (Architecture Decision Record)

**定义：** 架构决策记录，记录关键技术决策及其背景、替代方案、后果。

**用途：** 记录技术决策历史，帮助新贡献者理解设计选择。

**相关文档：** [`docs/decisions/`](decisions/)
