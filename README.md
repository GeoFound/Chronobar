# README Architecture Overview

## 1. 文档目的

本文件用于快速说明中国期货专用平台的架构文档体系，帮助开发者、协作者和 AI 辅助工具在进入编码前，先理解系统边界、模块职责、协议关系和开发顺序。

如果把整个平台看成一个长期演进的产品，那么这 11 份文档并不是彼此独立的说明书，而是一套相互咬合的正式基线：

---

## 1.5 战略定位

### 目标用户

本平台面向两类核心用户：

1. **个人量化用户**：需要本地化、低延迟、可回测、可扩展的交易终端，支持自定义策略和指标。
2. **个人交易用户**：需要稳定易用的桌面终端，支持实时行情、技术分析和辅助决策。

### 商业边界

本平台采用"开源核心 + 商业扩展"的双层模式：

- **开源核心**：协议层、架构层、基础引擎、插件框架、UI 桥接协议完全开源。
- **商业扩展**：高级策略库、专业数据服务、企业级风控、多账户管理等作为商业产品提供。

### 部署形态

**最终部署形式：桌面客户端**

- **桌面容器**：Tauri
- **前端**：React
- **核心引擎**：Python sidecar 进程
- **通信方式**：本地 HTTP + WebSocket（UiBridge 唯一边界）
- **禁止**：React 直接调用 Gateway / Strategy / Repository
- **禁止**：将核心交易逻辑写入 Tauri Rust 层

### 存储架构

**历史 Tick 存储：DuckDB + Parquet 双层架构**

- **实时写入路径**：GatewayAdapter → TickCache (内存 deque) → 定时落盘 → Parquet 文件（按交易日分片）
- **查询/回测路径**：BacktestEngine → DuckDB (直接查询 Parquet) → Strategy
- **元数据存储**：SQLite（合约基础信息、交易日历、策略参数等小表）

---

如果把整个平台看成一个长期演进的产品，那么这 11 份文档并不是彼此独立的说明书，而是一套相互咬合的正式基线：
- `system/architecture.md`
- `core/data_protocol.md`
- `core/event_protocol.md`
- `system/config_protocol.md`
- `core/plugin_protocol.md`
- `core/strategy_protocol.md`
- `core/risk_protocol.md`
- `core/backtest_protocol.md`
- `core/golden_examples.md`
- `engineering/engineering_baseline.md`
- `system/ui_bridge_protocol.md`

建议任何人在开始修改代码、补功能、重构模块或生成新文件之前，先通读本 README，再按推荐顺序阅读对应文档。

---

## 2. 11 份文档分别解决什么问题

### `system/architecture.md`
回答“系统怎么分层、模块怎么协作、依赖方向怎么约束”的问题。  
它定义七层架构、主引擎协调模式、实时 / 回放主流程，以及哪些跨层依赖是允许的、哪些是禁止的。

### `core/data_protocol.md`
回答“系统内部到底交换什么对象”的问题。  
它定义 Tick、Bar、Instrument、SessionContext 等标准对象，是接口层、规则层、计算层、展示层、插件层之间的共同语言。

### `core/event_protocol.md`
回答“模块之间默认怎么通信”的问题。  
它定义 EventEnvelope、标准事件类型、订阅规则、失败处理和回放一致性要求，是系统默认协作总线的正式约束。

### `system/config_protocol.md`
回答“系统配置怎么组织、怎么校验、怎么迁移”的问题。  
它定义系统配置、市场配置、规则配置、指标配置、工作区配置，以及 schema 校验和 migration 规则。

### `core/plugin_protocol.md`
回答“扩展能力怎么接入、权限怎么控制、输出怎么进入系统”的问题。  
它定义插件目录结构、生命周期、manifest、Host API、权限模型和输出契约。

### `core/strategy_protocol.md`
回答"策略插件如何安全参与交易执行"的问题。  
它定义策略 Host API（submit_order、cancel_order、get_positions、get_account）、4 层插件分类（indicator、signal、strategy、ui-extension）、交易权限模型和回测一致性保证。

### `core/risk_protocol.md`
回答"交易前如何进行风控检查"的问题。  
它定义 6 类风控检查（position_limit、order_limit、margin_check、price_band、frozen_check、custom）、RiskChecker 接口、风控事件模型（RISK_BLOCKED、RISK_WARNING）和系统级/策略级风控配置。

### `core/backtest_protocol.md`
回答"回测、仿真、实盘如何使用统一接口"的问题。  
它定义 BacktestEngine 接口、撮合模拟、滑点模型、性能指标体系、参数优化和多策略对比，保证 replay/sim/live 使用同一套策略接口。

### `core/golden_examples.md`
回答"如何正确实现插件和策略"的问题。  
它提供 4 个黄金样例：MA 指标插件、双均线信号插件、双均线仿真策略插件、回放测试用例，作为 AI 生成代码的参考模板。

### `engineering/engineering_baseline.md`
回答“代码仓库怎么组织、质量门槛是什么、什么才算可交付”的问题。  
它定义目录结构、测试要求、类型检查、日志要求、开发顺序、里程碑和 AI 协作约束。

### `system/ui_bridge_protocol.md`
回答"React 前端如何和 Python 核心协作"的问题。  
它定义 Query API、Command API、Subscription API，以及前端状态同步、错误模型和订阅恢复策略。

---

## 3. 这些文档之间是什么关系

可以把这 11 份文档理解成 3 层：

### 第一层：最稳定的核心协议层
- `core/data_protocol.md`
- `core/event_protocol.md`
- `core/plugin_protocol.md`
- `core/strategy_protocol.md`
- `core/risk_protocol.md`
- `core/backtest_protocol.md`

这一层定义系统最核心的交换边界。  
如果这层不稳定，计算链路、回放链路、插件链路、策略链路和风控链路都会反复返工。

### 第二层：系统组织与接入层
- `system/architecture.md`
- `system/config_protocol.md`
- `system/ui_bridge_protocol.md`

这一层定义模块如何组合、配置如何进入系统、前端如何访问核心。  
它们建立的是“系统运行方式”，而不是某个具体功能的实现细节。

### 第三层：工程执行与落地层
- `engineering/engineering_baseline.md`
- `core/golden_examples.md`

这一层把前两层文档变成真正可执行的工程规则。  
它决定仓库怎么搭、测试怎么补、类型怎么检查、交付怎么验收，并提供参考实现。

---

## 4. 推荐阅读顺序

如果你是第一次接手这个项目，建议按下面顺序阅读：

1. `system/architecture.md`  
先看整体骨架，知道系统分几层、主流程怎么走、哪些依赖不能碰。

2. `core/data_protocol.md`  
再看标准对象，因为后面所有模块几乎都要依赖这些对象。

3. `core/event_protocol.md`  
接着看事件模型，理解系统默认协作方式。

4. `system/config_protocol.md`  
然后看配置如何进入系统，哪些字段可变、哪些字段要迁移。

5. `core/plugin_protocol.md`  
再看扩展能力如何接入，避免把插件写成绕过核心的“外挂脚本”。

6. `core/strategy_protocol.md`  
如果要做策略交易，必须读这份，理解策略 Host API、权限模型和回测一致性。

7. `core/risk_protocol.md`  
理解风控检查机制，这是交易执行前的必要安全屏障。

8. `core/backtest_protocol.md`  
理解回测、仿真、实盘的统一接口，保证策略可复验。

9. `system/ui_bridge_protocol.md`  
如果要做前端、工作区、图表或交互，就必须读这份，明确前后端边界。

10. `core/golden_examples.md`  
参考黄金样例，理解如何正确实现插件和策略。

11. `engineering/engineering_baseline.md`  
最后看工程约束，确认目录结构、测试门槛、交付标准和 AI 协作要求。

---

## 5. 一张图理解文档协作关系

```text
system/architecture.md
 ├── 规定系统分层、依赖方向、主流程
 ├── 依赖 core/data_protocol.md 提供标准对象
 ├── 依赖 core/event_protocol.md 提供事件协作模型
 ├── 依赖 system/config_protocol.md 提供配置装载边界
 ├── 依赖 core/plugin_protocol.md 提供插件接入边界
 ├── 依赖 core/strategy_protocol.md 提供策略执行边界
 ├── 依赖 core/risk_protocol.md 提供风控检查边界
 ├── 依赖 core/backtest_protocol.md 提供回测一致性边界
 └── 依赖 system/ui_bridge_protocol.md 提供前后端桥接边界

core/data_protocol.md
 ├── 定义系统通用标准对象（Tick、Bar、Instrument、SessionContext）
 └── 定义交易执行数据对象（Order、Trade、Position、Account）

core/event_protocol.md
 └── 定义系统默认协作总线（包含交易执行事件）

core/plugin_protocol.md
 └── 定义扩展能力接入方式（4 层插件分类）

core/strategy_protocol.md
 └── 定义策略插件接口和 Host API

core/risk_protocol.md
 └── 定义风控检查接口和事件模型

core/backtest_protocol.md
 └── 定义回测、仿真、实盘统一接口

core/golden_examples.md
 └── 提供参考实现样例（MA 指标、双均线信号、策略、测试）

system/config_protocol.md
 └── 定义系统配置输入、校验与迁移规则

system/ui_bridge_protocol.md
 └── 定义 React 展示层与 Python 核心的交互边界

engineering/engineering_baseline.md
 └── 把以上所有文档转化为仓库结构、测试门槛与交付标准
```

---

## 6. 开发时应该怎么使用这套文档

### 新增核心功能
先看 `system/architecture.md` 判断功能属于哪一层，再看 `core/data_protocol.md` 和 `core/event_protocol.md` 判断是否需要新增标准对象或事件类型。

### 新增配置项
先改 `system/config_protocol.md`，明确字段位置、默认值、覆盖关系和迁移要求，然后再写 loader、schema 和测试。

### 新增插件
先按 `core/plugin_protocol.md` 设计 manifest、schema、权限和 outputs，参考 `core/golden_examples.md` 中的样例，禁止直接把插件写成随意调用核心对象的脚本。

### 新增策略
先按 `core/strategy_protocol.md` 设计策略接口、权限模型和风控参数，参考 `core/golden_examples.md` 中的策略样例，确保回测一致性。

### 新增风控规则
先按 `core/risk_protocol.md` 设计风控检查器，定义检查类型、拦截逻辑和事件模型，确保风控在实盘、仿真、回测模式下行为一致。

### 做回测
先按 `core/backtest_protocol.md` 理解回测引擎接口、撮合模拟和性能指标，确保策略使用统一接口。

### 改前端体验
先看 `system/ui_bridge_protocol.md`，确认查询、命令、订阅边界，再决定 React 页面状态、工作区布局和图表联动的实现方式。

### 落代码和提测
最后回到 `engineering/engineering_baseline.md`，确认目录放置、测试补齐、类型检查和交付门槛都满足要求。

---

## 7. 最重要的几条共识

- 平台优先依赖正式协议，不依赖口头约定。
- 默认协作通道是事件总线，不是跨层直连。
- 展示层只消费标准结果，不直接依赖网关私有字段。
- 插件是受控扩展单元，不是任意脚本入口。
- 配置必须可迁移，回放必须可复验，日志必须可追踪。
- React 前端体验可以持续升级，但不能反向污染核心边界。

---

## 8. 第一阶段最小落地建议

如果要从零开始推进第一阶段，建议最小落地顺序为：

1. 先定稿 `core/data_protocol.md`、`core/event_protocol.md`、`core/plugin_protocol.md`
2. 再定稿 `system/architecture.md`、`system/config_protocol.md`、`system/ui_bridge_protocol.md`
3. 补充定稿 `core/strategy_protocol.md`、`core/risk_protocol.md`、`core/backtest_protocol.md`
4. 最后按 `engineering/engineering_baseline.md` 搭仓库、补 schema、补测试、建最小闭环
5. 参考 `core/golden_examples.md` 实现第一版插件和策略

第一阶段的目标不是把所有界面都做漂亮，而是先跑通这条主链路：

`Tick -> Event -> Rule -> Bar -> Indicator Plugin -> UiBridge -> React Chart -> Replay`

以及这条交易链路：

`Strategy -> Risk Check -> Order -> Trade -> Position -> Account`

只要这两条链路跑通，并且回放与实时结果一致，这个平台就具备第一版架构骨架。

---

## 9. 给新加入同学的建议

如果你只负责前端，请至少阅读：
- `system/architecture.md`
- `core/event_protocol.md`
- `system/config_protocol.md`
- `system/ui_bridge_protocol.md`

如果你只负责核心计算，请至少阅读：
- `system/architecture.md`
- `core/data_protocol.md`
- `core/event_protocol.md`
- `engineering/engineering_baseline.md`

如果你负责插件体系，请至少阅读：
- `core/plugin_protocol.md`
- `core/event_protocol.md`
- `core/data_protocol.md`
- `engineering/engineering_baseline.md`
- `core/golden_examples.md`

如果你负责策略交易，请至少阅读：
- `core/strategy_protocol.md`
- `core/risk_protocol.md`
- `core/backtest_protocol.md`
- `core/data_protocol.md`
- `core/event_protocol.md`
- `core/golden_examples.md`

如果你负责整体推进，请 11 份全部阅读，并以本 README 作为总索引。

---

## 10. 维护原则

本 README 不是详细协议文档，不承载字段级定义，也不替代正式协议。  
它只负责回答一个问题：**当你面对整套架构文档时，应该先看什么、每份文档负责什么、它们之间怎么协作。**

当任何正式协议发生结构变化时，本 README 也必须同步更新。