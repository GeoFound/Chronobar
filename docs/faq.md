# Chronobar 常见问题 (FAQ)

本文档回答 Chronobar 项目相关的常见问题。

## 项目定位

### Q: Chronobar 与 vnpy、WonderTrader 有什么区别？

**A:** Chronobar 专注于**桌面端体验**，面向个人量化用户，而 vnpy 和 WonderTrader 更适合开发者/机构用户。

| 维度 | Chronobar | vnpy | WonderTrader |
|------|-----------|------|--------------|
| 部署形态 | 桌面应用 (Tauri) | Python 脚本 | 服务端 |
| 目标用户 | 个人量化交易者 | 开发者/机构 | 机构/量化团队 |
| 学习曲线 | 低（桌面优先） | 中（需 Python） | 高（需 C++） |
| AI 插件 | 原生受控 | 第三方扩展 | 无 |

### Q: 为什么不直接基于 vnpy 扩展？

**A:** vnpy 的架构是 Python 脚本驱动，更适合有编程能力的开发者。Chronobar 的目标是让量化交易变成"打开即用"的桌面应用，降低使用门槛。

### Q: Chronobar 是免费的吗？

**A:** Chronobar 采用"开源核心 + 商业扩展"的双层模式。核心协议和基础功能开源（MIT 许可证），高级功能（如 AI 智能体、高级回测）可能采用商业授权。

## 技术架构

### Q: 为什么选择 DuckDB + Parquet 而不是 TimescaleDB？

**A:** Chronobar 是桌面应用，需要单进程部署。DuckDB + Parquet 不需要独立的数据库服务，部署更简单，同时 Parquet 的列式存储压缩率高，适合大规模 Tick 数据存储。

详细决策记录：[`docs/decisions/001-storage-architecture.md`](decisions/001-storage-architecture.md)

### Q: 为什么使用 Tauri 而不是 Electron？

**A:** Tauri 使用 Rust 后端，内存占用和安装包体积都比 Electron 小得多，更适合桌面应用场景。

### Q: 为什么选择 React 作为前端框架？

**A:** React 生态成熟，组件库丰富（如 Ant Design、ECharts），开发效率高。同时 React 社区活跃，人才储备充足。

## AI 插件

### Q: "AI 受控"是什么意思？

**A:** Chronobar 的 AI 插件是"受控智能体"，不是"自主决策单元"。

- ✅ **可以：** 通过 HostAPI 读取市场数据、生成交易信号
- ❌ **不能：** 绕过风控直接提交订单、修改系统配置、访问敏感数据

所有 AI 插件的交易行为必须经过风控检查，符合监管要求。

### Q: AI 插件会自动操盘吗？

**A:** 不会。AI 插件只能生成交易信号，最终下单决策由用户或策略插件控制。

### Q: AI 插件使用什么模型？

**A:** Chronobar 不限制 AI 模型类型，支持 LLM、强化学习、传统机器学习等。插件开发者可以自由选择模型。

## 协议与开发

### Q: 什么是"协议驱动"开发？

**A:** Chronobar 的开发分为三层：
- **协议契约层（Contracts）**：定义数据对象、事件模型、插件接口等不可随意更改的边界
- **系统架构层（Architecture）**：定义模块如何组合、配置如何进入系统
- **工程规范层（Engineering Standards）**：定义代码质量、测试要求、交付标准

协议驱动的好处是确保模块间协作的一致性和可预测性。

### Q: 如何修改协议？

**A:** 协议变更需要经过 RFC（Request for Comments）流程，确保变更的合理性和向后兼容性。详细流程请参阅 [`docs/CONTRIBUTING.md`](CONTRIBUTING.md)。

### Q: 如何贡献代码？

**A:** 欢迎社区贡献！请参阅 [`docs/CONTRIBUTING.md`](CONTRIBUTING.md) 了解贡献流程、工程标准和 PR 评审要求。

## 使用场景

### Q: Chronobar 支持哪些交易所？

**A:** Chronobar 计划支持国内主流期货交易所（如上期所、大商所、郑商所、中金所）。M2 阶段将首先支持 1-2 个交易所，后续逐步扩展。

### Q: Chronobar 支持实盘交易吗？

**A:** M1-M4 阶段专注于协议定稿、核心框架、插件系统和回测系统。实盘交易支持计划在 M8 阶段实现。

### Q: Chronobar 支持哪些策略语言？

**A:** Chronobar 的策略插件使用 Python 编写。未来可能支持其他语言（如 Rust、C++），但 Python 仍然是主要策略语言。

## 数据与回测

### Q: Chronobar 支持哪些数据源？

**A:** Chronobar 计划支持期货交易所 API 直接获取数据，同时支持第三方数据源（如 Tushare、AkShare）。

### Q: 回测数据从哪里来？

**A:** 用户可以通过网关订阅实时数据并落盘为 Parquet 文件，也可以导入第三方历史数据。回测引擎直接读取 Parquet 文件。

### Q: 回测性能如何？

**A:** 目标是 1 年历史数据回测时间 < 5 分钟（单线程）。回测引擎使用 DuckDB 向量化查询，性能优秀。

## 其他

### Q: Chronobar 适合初学者吗？

**A:** Chronobar 的桌面优先设计降低了使用门槛，但量化交易本身需要一定的金融知识和编程基础。如果你是编程初学者，建议先学习 Python 基础。

### Q: Chronobar 有培训课程吗？

**A:** 目前没有官方培训课程。我们计划在未来提供教程和文档，帮助新用户快速上手。

### Q: 如何联系 Chronobar 团队？

**A:** 你可以通过以下方式联系我们：
- 提交 [GitHub Issue](https://github.com/GeoFound/Chronobar/issues)
- 参与 [GitHub Discussions](https://github.com/GeoFound/Chronobar/discussions)
- 发送邮件至 [待补充]

### Q: Chronobar 什么时候发布 M2 版本？

**A:** M2 版本预计在 2026 Q2 发布。具体时间取决于 M1 协议定稿的进度。你可以点击 GitHub 页面右上角「Watch」按钮关注进展。
