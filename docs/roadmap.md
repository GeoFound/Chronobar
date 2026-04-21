# Chronobar 路线图

本文档定义 Chronobar 项目的开发路线图和各阶段的可交付物。

## 阶段概览

| 阶段 | 目标 | 状态 | 预计时间 |
|------|------|------|---------|
| M1 | 基线收敛 | 🚧 进行中 | 2026 Q1 |
| M2 | 核心框架搭建 | 🔄 未开始 | 2026 Q2 |
| M3 | 插件系统实现 | 🔄 未开始 | 2026 Q3 |
| M4 | 回测系统实现 | 🔄 未开始 | 2026 Q4 |
| M5 | 前端界面完善 | 🔄 未开始 | 2027 Q1 |

## M1: 基线收敛（当前阶段）

**目标：** 完成协议文档、默认配置、Schema 与基础校验入口的收敛，确保系统边界清晰、可执行，并为 M2 实现提供稳定基线。

### 可交付物

- ✅ [`docs/core/data_protocol.md`](core/data_protocol.md) - 数据协议 v1.2
- ✅ [`docs/core/event_protocol.md`](core/event_protocol.md) - 事件协议 v1.2
- ✅ [`docs/core/gateway_protocol.md`](core/gateway_protocol.md) - 网关协议 v1.0
- ✅ [`docs/core/plugin_protocol.md`](core/plugin_protocol.md) - 插件协议 v1.2
- ✅ [`docs/core/ai_protocol.md`](core/ai_protocol.md) - AI 协议 v1.2
- ✅ [`docs/core/strategy_protocol.md`](core/strategy_protocol.md) - 策略协议 v1.2
- ✅ [`docs/core/risk_protocol.md`](core/risk_protocol.md) - 风控协议 v1.2
- ✅ [`docs/core/backtest_protocol.md`](core/backtest_protocol.md) - 回测协议 v1.2
- ✅ [`docs/system/architecture.md`](system/architecture.md) - 架构文档 v1.2
- ✅ [`docs/system/config_protocol.md`](system/config_protocol.md) - 配置协议 v1.2
- ✅ [`docs/system/ui_bridge_protocol.md`](system/ui_bridge_protocol.md) - UI 桥接协议 v1.2
- ✅ [`docs/engineering/engineering_baseline.md`](engineering/engineering_baseline.md) - 工程基线 v1.2
- ✅ [`docs/core/golden_examples.md`](core/golden_examples.md) - 黄金样例 v1.2
- ✅ [`docs/CONTRIBUTING.md`](CONTRIBUTING.md) - 贡献指南
- ✅ [`docs/glossary.md`](glossary.md) - 术语表
- ✅ [`docs/decisions/`](decisions/) - 架构决策记录
- ✅ `config/defaults/*.yaml` - 默认配置样例
- ✅ `config/schemas/*.json` - JSON Schema 基线
- ✅ `pyproject.toml` / `.pre-commit-config.yaml` / `.github/workflows/ci.yml` - 基础工程门禁
- ✅ `tests/` 最小测试入口 - 仓库基线校验

### 验收标准

- 所有协议文档状态标记为 ✅ 已定稿
- 13 份正式基线文档相互引用无冲突
- 示例配置可以被加载并通过 schema 校验
- 基础校验入口和 CI 门禁已入仓
- 黄金样例可通过人工审查
- README 文档地图与正式基线文档数量一致（13 份）

## M2: 核心框架搭建

**目标：** 搭建可运行的最小闭环，实现核心模块的基础功能。

### M2 可交付物

- 🔄 Python 核心引擎框架（MainEngine、EventBus）
- 🔄 GatewayAdapter 抽象层（支持至少 1 个期货交易所）
- 🔄 TickCache + Parquet 落盘机制
- 🔄 DuckDB 查询引擎集成
- 🔄 基础配置管理（YAML + Schema + migration）
- 🔄 单元测试覆盖率 ≥ 80%
- 🔄 集成测试：Gateway → EventBus → TickCache → Parquet
- 🔄 最小可运行示例：订阅一个合约，接收 Tick，落盘为 Parquet

### M2 验收标准

- 可启动 MainEngine，连接至少 1 个期货交易所
- 可接收 Tick 并落盘为 Parquet 文件
- 可通过 DuckDB 查询 Parquet 文件中的 Tick 数据
- 单元测试覆盖率 ≥ 80%
- 代码符合 [`docs/engineering/engineering_baseline.md`](engineering/engineering_baseline.md) 规范

## M3: 插件系统实现

**目标：** 实现插件加载机制和 Host API，支持指标插件和信号插件。

### M3 可交付物

- 🔄 PluginManager（插件加载、依赖解析、生命周期管理）
- 🔄 Host API 基础实现（读取市场数据、提交订单）
- 🔄 权限模型 enforcement
- 🔄 指标插件示例（MA 指标）
- 🔄 信号插件示例（双均线信号）
- 🔄 插件 manifest 校验
- 🔄 插件隔离机制（进程级或沙箱）
- 🔄 **MockLLMProvider 实现**（验证 AI 协议 HostAPI 依赖路径，使 llm_sentiment_signal 样例可在本地无网络环境下运行通过测试）

### M3 验收标准

- 可加载至少 2 个指标插件
- 可加载至少 1 个信号插件
- 插件可调用 Host API 读取市场数据
- 插件权限模型生效（未授权操作被拒绝）
- 插件异常不影响核心引擎稳定性

## M4: 回测系统实现

**目标：** 实现回测引擎和撮合引擎，支持策略回测。

### M4 可交付物

- 🔄 BacktestEngine（历史数据回放、策略执行）
- 🔄 OrderMatcher（撮合引擎，支持限价单）
- 🔄 回测结果统计（收益率、最大回撤、夏普比率）
- 🔄 回测报告生成（HTML/PDF）
- 🔄 策略插件示例（双均线策略）
- 🔄 回测数据集（至少 1 个合约的 1 年历史数据）

### M4 验收标准

- 可运行双均线策略回测
- 回测结果与手工计算一致
- 回测报告包含关键指标
- 回测性能：1 年数据回测时间 < 5 分钟

## M5: 前端界面完善

**目标：** 实现 React 前端，提供桌面应用体验。

### M5 可交付物

- 🔄 Tauri 应用框架（Rust 后端 + React 前端）
- 🔄 UI Bridge 实现（Query/Command/Subscription API）
- 🔄 实时行情展示（Tick 图表）
- 🔄 K 线图表（使用 ECharts 或类似库）
- 🔄 订单管理界面（下单、撤单、查询）
- 🔄 持仓查询界面
- 🔄 回测界面（策略选择、参数配置、结果展示）
- 🔄 桌面应用打包（Windows/Mac/Linux）

### M5 验收标准

- 可打包为桌面应用（.exe/.dmg/.AppImage）
- 可实时展示 Tick 和 K 线图表
- 可通过界面下单、撤单
- 可通过界面运行回测并查看结果
- 前后端通信延迟 < 100ms

## 长期规划（M6+）

- M6: AI 智能体插件实现
- M7: 多网关支持（支持 3+ 期货交易所）
- M8: 实盘交易支持（连接实盘账户）
- M9: 策略市场（插件分发平台）
- M10: 云端回测服务（支持大规模并行回测）

## 参与贡献

如果你想参与某个阶段的开发，请参阅 [`docs/CONTRIBUTING.md`](CONTRIBUTING.md) 了解贡献流程。

如果你对路线图有建议或疑问，请：
- 提交 [GitHub Issue](https://github.com/GeoFound/Chronobar/issues)
- 参与 [GitHub Discussions](https://github.com/GeoFound/Chronobar/discussions)
