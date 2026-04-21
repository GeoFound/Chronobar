# Chronobar 交付总计划 v1.0

## 1. 文档定位

本文档定义 Chronobar 从 M1 基线收敛到产品可落地的总交付计划，覆盖阶段目标、进入条件、退出条件、回滚条件、关键风险和实施顺序。

它是 [`engineering_baseline.md`](engineering_baseline.md)、[`m1_checklist.md`](m1_checklist.md)、[`../roadmap.md`](../roadmap.md) 的执行层补充文档，目的是把“路线图”变成“可操作的阶段推进机制”。

## 2. 当前审查结论

截至当前仓库状态，Chronobar 的主要缺口不再是协议文档，而是交付执行层：

- 已有协议、架构、AI Assistant 蓝图与工程门禁
- 已有默认配置、Schema、基础测试和 CI
- 已有分支保护与 PR 流程

仍缺：

- 跨阶段统一执行主计划
- 进入下一阶段的明确 gate
- 阶段失败时的回滚条件
- 面向任务 AI 的实施任务包
- 从“最小闭环”到“产品发布”的统一推进顺序

## 3. 总体原则

- **协议先行**：所有实现必须以正式协议为边界，不反向发明字段。
- **竖切优先**：优先做可验证的最小闭环，而不是横向铺满模块空壳。
- **可回滚**：每阶段都必须有明确回退目标和冻结点。
- **先内核后体验**：先完成核心运行链路，再叠加 UI 复杂体验。
- **AI 受控接入**：AI Assistant 在产品中按受控、证据优先、可拒答原则逐步落地。
- **阶段冻结**：每阶段退出前必须先完成验证、文档和回滚预案，不得带着高风险歧义进入下一阶段。

## 4. 阶段总览

| 阶段 | 对应路线图 | 核心目标 | 是否允许进入下一阶段 |
|------|-----------|---------|--------------------|
| P0 | M1 | 冻结协议、配置、测试与工程基线 | 仅当 M1 gate 全部满足 |
| P1 | M2 | 跑通核心最小闭环（Tick -> Event -> Bar -> Indicator -> Chart Snapshot） | 仅当核心链路可运行 |
| P2 | M3 | 建立可加载、可隔离、可验证的插件系统 | 仅当插件治理与隔离达标 |
| P3 | M4 | 跑通回测系统并验证与实时链路一致 | 仅当回测结果可复验 |
| P4 | M5 | 做成可演示、可安装、可操作的桌面产品骨架 | 仅当桌面体验稳定 |
| P5 | M6+ | 受控引入 AI Assistant 产品能力 | 仅当治理与评测基础达标 |
| P6 | Release | 形成 beta / GA 发布与运维闭环 | 仅当发布门禁通过 |

## 5. P0：M1 基线冻结

### 5.1 目标

- 冻结协议、系统架构、AI Assistant 补充设计
- 冻结配置样例与 Schema
- 冻结最小工程门禁和基础测试入口
- 形成可直接进入实现的稳定地基

### 5.2 进入条件

- 仓库处于 docs-first 阶段
- 核心协议已达成一致
- 团队确认桌面优先、Tauri + React + Python sidecar 路线不再反复变更

### 5.3 退出条件

- [`m1_checklist.md`](m1_checklist.md) 中所有必选项完成
- `just docs-check` 与 `just check` 通过
- README / roadmap / CONTRIBUTING / baseline 口径一致
- 分支保护、CI、PR 流程可阻断不合规合并

### 5.4 回滚条件

出现以下任一情况，必须回到 P0：

- 实现阶段发现核心协议存在结构性冲突
- UI Bridge 无法承载最小闭环所需查询/订阅结构
- Schema 与默认配置严重偏离，无法维持兼容
- 团队对主架构路线再次出现分歧

### 5.5 回滚动作

- 停止新增运行时代码合并
- 回到协议 / 架构 / 配置文档修订
- 更新 CHANGELOG 和相关契约样例
- 重新执行 M1 gate 验证

## 6. P1：M2 核心最小闭环

### 6.1 目标

完成第一个可运行的竖切闭环：

```text
GatewayAdapter(Mock or Sim) -> EventEngine -> RuleEngine -> BarAggregator -> Indicator -> UiBridge Snapshot/Event
```

### 6.2 必做工作包

- 建立 Python 运行时代码目录结构
- 实现标准对象和基础异常层
- 实现 EventEngine
- 实现 RuleEngine 最小夜盘/交易日判定
- 实现 BarAggregator
- 实现至少 1 个 Indicator
- 实现 UiBridge 的最小 Query / Subscription 投影
- 建立最小 React / Tauri 前端壳或可替代前端契约消费者

### 6.3 退出条件

- 输入一条标准 Tick，可稳定得到：
  - Event 发布
  - session / trading_date 判定
  - 1 分钟 Bar 聚合结果
  - Indicator 输出
  - UiBridge 可消费的 snapshot / event
- 关键单元测试和最小集成测试通过
- 运行链路可由开发者在本地复现

### 6.4 禁止事项

- 不允许先做复杂 UI 再补核心链路
- 不允许把前端临时字段写入核心协议
- 不允许用大面积 mock 掩盖事件链路未打通

### 6.5 回滚条件

- 主链路无法稳定复现
- 事件模型与协议不一致
- 夜盘 session 判定错误无法解释
- UiBridge 输出与协议样例持续偏离

### 6.6 回滚动作

- 冻结新增特性
- 回退到最近可运行闭环 tag / 分支
- 只修复核心链路，不扩展 UI 范围

## 7. P2：M3 插件系统实现

### 7.1 目标

让指标插件和信号插件以受控方式接入系统，满足加载、隔离、卸载和权限治理要求。

### 7.2 必做工作包

- PluginManager
- Manifest 校验器
- Host API 最小实现
- 插件权限校验
- 插件加载顺序与依赖解析
- 插件异常隔离
- 至少 2 个 builtin 样例插件

### 7.3 退出条件

- 插件可发现、可加载、可禁用、可卸载
- 插件异常不影响主引擎稳定
- 未授权调用被拒绝
- 缺失插件时工作区可降级恢复

### 7.4 回滚条件

- 插件可直接破坏主引擎状态
- 卸载导致工作区不可恢复
- Host API 与 plugin_protocol 严重偏离

### 7.5 回滚动作

- 回退到仅保留 builtin 插件模式
- 暂停第三方插件开放
- 优先修复 manifest / Host API / 隔离边界

## 8. P3：M4 回测系统实现

### 8.1 目标

实现历史数据驱动的回测闭环，并保证与实时链路共享协议和关键行为。

### 8.2 必做工作包

- HistoricalDataLoader
- Replay Engine
- BacktestEngine
- OrderMatcher
- 回测统计模块
- 回测结果导出
- 回放一致性测试

### 8.3 退出条件

- 可运行一个最小策略回测
- 回测结果可复验
- 与实时模式共享协议对象和关键计算逻辑
- 回测报告至少包含收益、回撤、胜率、交易明细

### 8.4 回滚条件

- 回测链路大量复制实时逻辑而非复用
- 回测结果不可复验
- 数据读取性能或正确性无法满足最小可用要求

### 8.5 回滚动作

- 回退到“只保留 replay / event consistency”的较小目标
- 暂不承诺完整报告系统
- 先修一致性，再补性能和统计项

## 9. P4：M5 桌面产品骨架

### 9.1 目标

把核心能力包装成可安装、可演示、可操作的桌面产品骨架。

### 9.2 必做工作包

- Tauri 应用壳
- React + TypeScript 前端目录初始化
- 工作区布局
- 图表与面板骨架
- UiBridge Query / Command / Subscription 接入
- 基础错误提示与日志查看入口
- 打包与安装说明

### 9.3 退出条件

- 可启动桌面应用
- 可查看行情 / 图表基础结果
- 可进行回放操作
- 可消费标准命令与标准事件
- 打包产物可在至少一个目标平台运行

### 9.4 回滚条件

- UI 依赖未声明桥接字段
- 前端状态与核心状态严重耦合
- 桌面壳无法稳定拉起核心进程

### 9.5 回滚动作

- 回退到“Web/前端壳 + mock bridge consumer”阶段
- 暂停复杂交互与高级图表，保留最小展示闭环

## 10. P5：AI Assistant 受控落地

### 10.1 目标

按 [`../system/ai_assistant_architecture.md`](../system/ai_assistant_architecture.md) 与 [`../system/ai_assistant_product_contract.md`](../system/ai_assistant_product_contract.md) 将 AI Assistant 作为受控产品能力接入。

### 10.2 必做工作包

- Intent Router
- Policy Engine
- Knowledge Retriever
- Tool Executor
- Evidence Binder
- Answer Composer
- Audit Logger
- 至少 3 个能力面：产品问答 / 回测解读 / 风控解释

### 10.3 退出条件

- 回答可显示来源与不确定性
- 高风险请求可拒答
- 修改类动作要求确认
- 任务级评测可执行

### 10.4 回滚条件

- AI 助手越权调用
- 无证据强答频发
- 产品层无法稳定表达来源 / 不确定性 / 确认点

### 10.5 回滚动作

- 回退到仅文档问答模式
- 暂停外部搜索与高风险工具调用
- 优先修复策略引擎与审计链路

## 11. P6：发布准备与产品落地

### 11.1 目标

形成 beta / GA 发布闭环，而不是只停留在可运行 demo。

### 11.2 必做工作包

- 安装与升级路径
- 错误收集与崩溃恢复策略
- 配置迁移与兼容策略
- 发布说明模板
- Beta 验收清单
- 关键回滚预案

### 11.3 Beta 进入条件

- P1-P5 核心退出条件全部满足
- 至少一轮端到端演示通过
- 关键问题分级和 blocker 机制明确
- 文档、测试、打包和已知限制清单齐备

### 11.4 GA 进入条件

- Beta 反馈中的 blocker 全部关闭
- 安装、升级、回放、基础 AI 助手路径稳定
- 关键指标达到内部可接受阈值

### 11.5 回滚条件

- Beta 阶段出现数据一致性、风险边界或崩溃级问题
- 升级后配置损坏或回放结果不一致

### 11.6 回滚动作

- 停止推广当前版本
- 回退到最近稳定标签
- 锁定问题范围并只放行修复性改动

## 12. 每阶段统一 gate 模板

每个阶段在进入下一阶段前，必须统一检查：

- **范围 gate**：本阶段目标是否真的完成，是否偷偷扩大范围
- **实现 gate**：关键链路是否已可运行
- **测试 gate**：本阶段新增测试是否覆盖关键路径
- **文档 gate**：README / roadmap / 契约 / 示例是否同步
- **治理 gate**：是否引入越权、无审计、无确认点风险
- **回滚 gate**：是否存在可用回退点与降级方案

任一 gate 不满足，禁止进入下一阶段。

## 13. 实施顺序建议

推荐的实际推进顺序如下：

1. P0 冻结 M1
2. P1 跑通核心闭环
3. P2 建插件系统
4. P3 建回测闭环
5. P4 做桌面产品壳
6. P5 接 AI Assistant
7. P6 做 beta / GA

AI Assistant 不应早于核心闭环和回测闭环成为主轴开发项。

## 14. 相关文档

- [`engineering_baseline.md`](engineering_baseline.md)
- [`m1_checklist.md`](m1_checklist.md)
- [`../roadmap.md`](../roadmap.md)
- [`../system/ai_assistant_architecture.md`](../system/ai_assistant_architecture.md)
- [`../system/ai_assistant_product_contract.md`](../system/ai_assistant_product_contract.md)
