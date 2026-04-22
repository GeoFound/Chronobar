# Chronobar 贡献指南

本文档面向项目贡献者和协作者，说明开发流程、阶段规划和维护原则。

## 阶段规划

### M1 阶段：基线收敛（当前）

本仓库当前处于 M1 基线收敛阶段：核心协议文档已定稿，默认配置、Schema、基础测试入口和 CI 基线已入仓；仓库中允许存在实验性运行时代码与演示脚本，但它们不构成 P1 / M2 已正式放行。

### 第一阶段最小落地建议

M1 阶段（基线收敛）的具体实施顺序如下：

1. 先定稿核心协议：[`docs/core/data_protocol.md`](core/data_protocol.md)、[`docs/core/event_protocol.md`](core/event_protocol.md)、[`docs/core/plugin_protocol.md`](core/plugin_protocol.md)
2. 再定稿系统组织：[`docs/system/architecture.md`](system/architecture.md)、[`docs/system/config_protocol.md`](system/config_protocol.md)、[`docs/system/ui_bridge_protocol.md`](system/ui_bridge_protocol.md)
3. 补充定稿交易协议：[`docs/core/strategy_protocol.md`](core/strategy_protocol.md)、[`docs/core/risk_protocol.md`](core/risk_protocol.md)、[`docs/core/backtest_protocol.md`](core/backtest_protocol.md)
4. 按 [`docs/engineering/m1_checklist.md`](engineering/m1_checklist.md) 补齐默认配置、Schema、最小测试入口和仓库骨架
5. 完成文档—配置—测试一致性检查，冻结 M1，进入 M2

M1 的目标不是把所有界面都做漂亮，而是先把协议边界、配置边界和工程边界固定住，为 M2 的最小闭环实现扫清歧义。

当前阶段的里程碑目标、状态和后续可交付物，请以 [`docs/roadmap.md`](roadmap.md) 与 [`docs/engineering/current_phase_and_truth_source.md`](engineering/current_phase_and_truth_source.md) 作为正式阶段说明来源。

### 后续阶段

- M2: 核心框架搭建
- M3: 插件系统实现
- M4: 回测系统实现
- M5: 前端界面完善

如需把仓库从当前 M1 基线持续推进到产品落地，请额外参考：

- [`docs/engineering/delivery_master_plan.md`](engineering/delivery_master_plan.md)
- [`docs/engineering/implementation_task_packages.md`](engineering/implementation_task_packages.md)
- [`docs/engineering/runtime_nonfunctional_baseline.md`](engineering/runtime_nonfunctional_baseline.md)
- [`docs/system/storage_lifecycle_and_recovery.md`](system/storage_lifecycle_and_recovery.md)
- [`.windsurf/workflows/execute-chronobar-delivery.md`](../.windsurf/workflows/execute-chronobar-delivery.md)

## 开发流程

### PR 流程规范

详见 [`docs/engineering/engineering_baseline.md`](engineering/engineering_baseline.md) §9（PR 流程规范）。

**核心要求：**
- 禁止直接 push 到 main 分支
- 所有代码变更必须通过 Pull Request 流程
- 遵循 Conventional Commits 格式
- 至少一名 Reviewer 批准方可合并

### 工程标准

详见 [`docs/engineering/engineering_baseline.md`](engineering/engineering_baseline.md)。

**核心要求：**
- 核心模块必须全量类型标注
- 测试覆盖率：核心模块 ≥80%，协议层 ≥95%
- 禁止无约束 `dict` 作为长期数据边界
- AI 生成代码必须通过声明模板验证

## 协议变更流程

### 协议契约层（Contracts）变更

协议契约层（包括 `docs/core/` 下的所有协议文档）是系统的核心边界，变更需要严格流程：

1. **提案阶段**：提交 GitHub Issue，标签使用 `protocol-change`，描述变更原因和影响范围
2. **RFC 流程**：对于重大变更（如新增协议、修改核心数据结构），需要提交 RFC（Request for Comments）文档
3. **社区讨论**：RFC 需要至少 7 天社区讨论期，收集反馈
4. **审批决策**：由项目维护者审批，审批通过后方可实施
5. **实施变更**：通过 Pull Request 提交变更，关联 Issue 和 RFC
6. **版本更新**：更新协议文档版本号，同步更新 CHANGELOG.md

### 系统架构层（Architecture）和工程规范层（Engineering Standards）变更

这两层变更相对宽松，但仍需：

1. 提交 GitHub Issue 描述变更
2. 通过 Pull Request 提交变更
3. 至少一名 Reviewer 批准
4. 更新相关文档和 CHANGELOG.md

### 文档模板

所有协议文档应遵循以下头部格式：

```markdown
# [文档标题]

**状态：** ✅ 已定稿 / 🔄 草稿 / ⚠️ 待审核
**版本：** v1.0
**最后更新：** 2026-04-21
**负责人：** @username

## 概述

[文档简要说明]

## 内容

[文档正文]
```

### Issue 标签体系

使用以下标签帮助快速分类贡献：

- `protocol-question` - 协议理解问题
- `protocol-change` - 协议变更提案
- `m2-blocker` - M2 阶段阻塞问题
- `design-decision` - 架构设计决策
- `bug` - Bug 报告
- `enhancement` - 功能增强
- `documentation` - 文档改进
- `good first issue` - 适合新贡献者的任务

## 维护原则

### README 维护

README 不是详细协议文档，不承载字段级定义，也不替代正式协议。
它只负责回答一个问题：**当你面对整套架构文档时，应该先看什么、每份文档负责什么、它们之间怎么协作。**

当任何正式协议发生结构变化时，README 也必须同步更新。

### 协议文档维护

- 协议文档变更必须同步更新相关文档
- 修改 schema 必须同步更新示例文件
- 修改字段含义必须补 migration
- 所有迁移必须附测试样例

## 贡献清单

在提交 Pull Request 前，请确保：

1. 代码符合 [`docs/engineering/engineering_baseline.md`](engineering/engineering_baseline.md) 规定的工程标准
2. 通过所有测试用例
3. 更新相关文档（如有必要）
4. 提交信息清晰描述变更内容
5. 使用 PR 模板填写变更描述

## 许可证

本项目采用 MIT 许可证。详见 [LICENSE](../LICENSE) 文件。
