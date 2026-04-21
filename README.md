# Chronobar
> 面向中国期货市场的个人量化桌面平台

[![GitHub release](https://img.shields.io/github/v/release/GeoFound/Chronobar)](https://github.com/GeoFound/Chronobar/releases)
[![License](https://img.shields.io/badge/License-MIT-green)](LICENSE)
[![Platform](https://img.shields.io/badge/Platform-Tauri%20%2B%20React%20%2B%20Python-orange)](docs/system/architecture.md)

## 平台简介

Chronobar 是面向个人量化用户和个人交易用户的期货量化桌面平台，采用"开源核心 + 商业扩展"的双层模式。与 vnpy、WonderTrader 不同，Chronobar 专注于桌面端体验，使用 Tauri + React + Python sidecar 架构。

**目标用户：** 个人量化交易者、个人量化用户、技术型交易者

**核心特性：**
- 桌面优先设计 - 原生桌面体验，非脚本驱动，降低使用门槛
- 原生 AI 插件支持 - 受控智能体增强决策，非自主操盘，符合监管要求
- 高性能 Tick 数据存储 - DuckDB + Parquet 双层架构，支持大规模历史数据
- 实时/回测/仿真统一接口 - 一套代码三种模式，保证一致性
- 前后端分离 - React + Python sidecar，前端可独立升级

**与同类工具对比：**

| 维度 | Chronobar | vnpy | WonderTrader |
|------|-----------|------|--------------|
| 部署形态 | 桌面 (Tauri) | Python 脚本 | 服务端 |
| 目标用户 | 个人量化 | 开发者/机构 | 机构/量化团队 |
| 前端技术 | React | Qt/Web | C++ |
| AI 插件支持 | 原生受控 | 第三方扩展 | 无 |
| 数据存储 | DuckDB + Parquet | SQLite | 自研 |
| 商业模式 | 开源核心 + 商业扩展 | 完全开源 | 商业授权 |

## 快速开始

> **M2 阶段将提供完整安装指南**

本仓库当前处于 M1 协议定稿阶段，仅包含文档和配置文件。M2 阶段将提供：
- 完整的安装依赖说明
- 环境配置指南
- 第一个可运行的最小闭环示例
- 快速启动脚本

如需提前了解开发规划，请参阅 [`docs/CONTRIBUTING.md`](docs/CONTRIBUTING.md)。

## 当前状态

**M1 协议定稿阶段**

本仓库当前处于 M1 协议定稿阶段，仅包含文档（docs/）和配置文件，尚未创建代码目录（core/、gateways/、compute/ 等）。代码目录将在 M2 阶段按 [`docs/engineering/engineering_baseline.md`](docs/engineering/engineering_baseline.md) 规定的结构创建。

**路线图：**
- M1: 协议定稿（当前）
- M2: 核心框架搭建
- M3: 插件系统实现
- M4: 回测系统实现
- M5: 前端界面完善

---

## 文档地图

| 文档 | 核心职责 | 层级 |
|------|---------|------|
| [`docs/core/data_protocol.md`](docs/core/data_protocol.md) | 模块间数据交换（Tick、Bar、Instrument、AI 对象） | 第一层 |
| [`docs/core/event_protocol.md`](docs/core/event_protocol.md) | 模块间默认通信方式（EventEnvelope、订阅规则） | 第一层 |
| [`docs/core/gateway_protocol.md`](docs/core/gateway_protocol.md) | 网关接口标准化、连接状态管理、重连策略 | 第一层 |
| [`docs/core/plugin_protocol.md`](docs/core/plugin_protocol.md) | 扩展能力接入、权限控制、输出契约（5 层插件分类） | 第一层 |
| [`docs/core/ai_protocol.md`](docs/core/ai_protocol.md) | AI 插件协议、AI 数据对象、AI 风控检查 | 第一层 |
| [`docs/core/strategy_protocol.md`](docs/core/strategy_protocol.md) | 策略插件安全交易执行（Host API、权限模型） | 第一层 |
| [`docs/core/risk_protocol.md`](docs/core/risk_protocol.md) | 交易前风控检查（6 类风控检查、RiskChecker） | 第一层 |
| [`docs/core/backtest_protocol.md`](docs/core/backtest_protocol.md) | 回测/仿真/实盘统一接口（BacktestEngine、撮合模拟） | 第一层 |
| [`docs/system/architecture.md`](docs/system/architecture.md) | 系统分层、模块协作、依赖方向约束 | 第二层 |
| [`docs/system/config_protocol.md`](docs/system/config_protocol.md) | 系统配置组织、校验、迁移 | 第二层 |
| [`docs/system/ui_bridge_protocol.md`](docs/system/ui_bridge_protocol.md) | React 前端与 Python 核心协作（Query/Command/Subscription API） | 第二层 |
| [`docs/engineering/engineering_baseline.md`](docs/engineering/engineering_baseline.md) | 代码仓库组织、质量门槛、可交付标准 | 第三层 |
| [`docs/core/golden_examples.md`](docs/core/golden_examples.md) | 插件和策略正确实现（5 个黄金样例） | 第三层 |

**层级说明：**
- **第一层（核心协议层）**：定义系统最核心的交换边界
- **第二层（系统组织与接入层）**：定义模块如何组合、配置如何进入系统、前端如何访问核心
- **第三层（工程执行与落地层）**：把前两层文档变成真正可执行的工程规则

---

## 推荐阅读顺序

如果你是第一次接手这个项目，建议按下面顺序阅读：

1. [`docs/system/architecture.md`](docs/system/architecture.md) - 整体骨架、系统分层、主流程
2. [`docs/core/data_protocol.md`](docs/core/data_protocol.md) - 标准对象
3. [`docs/core/event_protocol.md`](docs/core/event_protocol.md) - 事件模型
4. [`docs/core/gateway_protocol.md`](docs/core/gateway_protocol.md) - 网关接口定义
5. [`docs/core/plugin_protocol.md`](docs/core/plugin_protocol.md) - 扩展能力接入
6. [`docs/core/ai_protocol.md`](docs/core/ai_protocol.md) - AI 插件协议
7. [`docs/core/strategy_protocol.md`](docs/core/strategy_protocol.md) - 策略交易
8. [`docs/core/risk_protocol.md`](docs/core/risk_protocol.md) - 风控检查
9. [`docs/core/backtest_protocol.md`](docs/core/backtest_protocol.md) - 回测/仿真/实盘
10. [`docs/system/config_protocol.md`](docs/system/config_protocol.md) - 配置管理
11. [`docs/system/ui_bridge_protocol.md`](docs/system/ui_bridge_protocol.md) - 前后端边界
12. [`docs/core/golden_examples.md`](docs/core/golden_examples.md) - 黄金样例
13. [`docs/engineering/engineering_baseline.md`](docs/engineering/engineering_baseline.md) - 工程约束

---

## 按角色/任务快速索引

| 角色/任务 | 必读文档 | 参考文档 |
|----------|---------|---------|
| 🔧 新增核心功能 | [`docs/system/architecture.md`](docs/system/architecture.md) · [`docs/core/data_protocol.md`](docs/core/data_protocol.md) · [`docs/core/event_protocol.md`](docs/core/event_protocol.md) | - |
| ⚙️ 新增配置项 | [`docs/system/config_protocol.md`](docs/system/config_protocol.md) | - |
| 🧩 新增插件 | [`docs/core/plugin_protocol.md`](docs/core/plugin_protocol.md) · [`docs/core/event_protocol.md`](docs/core/event_protocol.md) · [`docs/core/data_protocol.md`](docs/core/data_protocol.md) | [`docs/core/golden_examples.md`](docs/core/golden_examples.md) · [`docs/engineering/engineering_baseline.md`](docs/engineering/engineering_baseline.md) |
| 📊 新增策略 | [`docs/core/strategy_protocol.md`](docs/core/strategy_protocol.md) · [`docs/core/risk_protocol.md`](docs/core/risk_protocol.md) · [`docs/core/backtest_protocol.md`](docs/core/backtest_protocol.md) · [`docs/core/data_protocol.md`](docs/core/data_protocol.md) · [`docs/core/event_protocol.md`](docs/core/event_protocol.md) | [`docs/core/golden_examples.md`](docs/core/golden_examples.md) |
| 🛡️ 新增风控规则 | [`docs/core/risk_protocol.md`](docs/core/risk_protocol.md) | - |
| 📈 做回测 | [`docs/core/backtest_protocol.md`](docs/core/backtest_protocol.md) | - |
| 🎨 改前端体验 | [`docs/system/architecture.md`](docs/system/architecture.md) · [`docs/core/event_protocol.md`](docs/core/event_protocol.md) · [`docs/system/config_protocol.md`](docs/system/config_protocol.md) · [`docs/system/ui_bridge_protocol.md`](docs/system/ui_bridge_protocol.md) | - |
| ✅ 落代码和提测 | [`docs/engineering/engineering_baseline.md`](docs/engineering/engineering_baseline.md) | - |
| 👨‍💻 前端开发 | [`docs/system/architecture.md`](docs/system/architecture.md) · [`docs/core/event_protocol.md`](docs/core/event_protocol.md) · [`docs/system/config_protocol.md`](docs/system/config_protocol.md) · [`docs/system/ui_bridge_protocol.md`](docs/system/ui_bridge_protocol.md) | - |
| ⚡ 核心计算 | [`docs/system/architecture.md`](docs/system/architecture.md) · [`docs/core/data_protocol.md`](docs/core/data_protocol.md) · [`docs/core/event_protocol.md`](docs/core/event_protocol.md) · [`docs/engineering/engineering_baseline.md`](docs/engineering/engineering_baseline.md) | - |
| 🔌 插件体系 | [`docs/core/plugin_protocol.md`](docs/core/plugin_protocol.md) · [`docs/core/event_protocol.md`](docs/core/event_protocol.md) · [`docs/core/data_protocol.md`](docs/core/data_protocol.md) · [`docs/engineering/engineering_baseline.md`](docs/engineering/engineering_baseline.md) | [`docs/core/golden_examples.md`](docs/core/golden_examples.md) |
| 💰 策略交易 | [`docs/core/strategy_protocol.md`](docs/core/strategy_protocol.md) · [`docs/core/risk_protocol.md`](docs/core/risk_protocol.md) · [`docs/core/backtest_protocol.md`](docs/core/backtest_protocol.md) · [`docs/core/data_protocol.md`](docs/core/data_protocol.md) · [`docs/core/event_protocol.md`](docs/core/event_protocol.md) | [`docs/core/golden_examples.md`](docs/core/golden_examples.md) |
| 🚀 整体推进 | 全部 12 份文档 | 本 README 作为总索引 |

---

## 核心共识

- **平台优先依赖正式协议**，不依赖口头约定
- **默认协作通道是事件总线**，不是跨层直连
- **展示层只消费标准结果**，不直接依赖网关私有字段
- **插件是受控扩展单元**，不是任意脚本入口
- **AI 插件是受控智能体**，不是自主决策单元，必须通过 HostAPI 与核心交互，不能绕过风控直接操盘
- **配置必须可迁移**，回放必须可复验，日志必须可追踪
- **React 前端体验可以持续升级**，但不能反向污染核心边界

---

## 贡献指南

Chronobar 欢迎社区贡献。详见 [`docs/CONTRIBUTING.md`](docs/CONTRIBUTING.md) 了解开发流程、阶段规划和工程标准。

## 许可证

本项目采用 MIT 许可证。详见 [LICENSE](LICENSE) 文件。