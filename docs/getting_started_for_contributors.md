# Chronobar 贡献者快速开始

本文档面向第一次参与 Chronobar 的贡献者，帮助你在 10 分钟内理解当前阶段、仓库结构和最适合介入的任务。

## 当前阶段

Chronobar 当前处于 **M1 基线收敛** 阶段。

这意味着：
- 协议文档已经基本定稿
- 默认配置与 JSON Schema 已入仓
- 基础测试入口和 CI 基线已入仓
- 核心运行时代码尚未开始，计划在 M2 推进

如果你想了解完整阶段说明，请优先阅读 [`docs/roadmap.md`](roadmap.md)。

## 第一次阅读建议

建议按下面顺序阅读：

1. [`README.md`](../README.md)
2. [`docs/roadmap.md`](roadmap.md)
3. [`docs/system/architecture.md`](system/architecture.md)
4. [`docs/core/data_protocol.md`](core/data_protocol.md)
5. [`docs/core/event_protocol.md`](core/event_protocol.md)
6. [`docs/system/config_protocol.md`](system/config_protocol.md)
7. [`docs/system/ui_bridge_protocol.md`](system/ui_bridge_protocol.md)
8. [`docs/engineering/engineering_baseline.md`](engineering/engineering_baseline.md)
9. [`docs/engineering/m1_checklist.md`](engineering/m1_checklist.md)

## 当前最适合贡献的任务

### 文档与一致性

- 修正文档中的术语、版本、链接不一致
- 为协议文档补充交叉引用
- 完善 FAQ、术语表和 ADR

### 配置与校验

- 扩展 `config/defaults/` 示例配置
- 扩展 `config/schemas/` 的结构约束
- 增加配置迁移样例与测试

### 测试与工程门禁

- 完善 `tests/test_repo_baseline.py`
- 增加链接检查、schema 检查和样例校验
- 强化 CI 的文档与配置一致性检查

## 当前不建议直接做的事情

在进入 M2 前，不建议直接开始：

- 编写完整交易引擎
- 先写前端界面再补内核
- 绕过协议文档自行发明字段或接口
- 在没有 schema / 样例 / 测试的情况下引入新配置结构

## 提交前自查

提交 Pull Request 前，请至少确认：

- 变更符合 [`docs/engineering/engineering_baseline.md`](engineering/engineering_baseline.md)
- 如修改协议，已同步更新相关文档与 `CHANGELOG.md`
- 如修改配置结构，已同步更新 schema 与样例
- 如新增桥接结构，已同步更新 `tests/ui_contract/` 样例

## 推荐的第一类 Issue

如果你是第一次贡献，优先选择：

- `documentation`
- `protocol-question`
- `good first issue`
- `design-decision`

## 进一步了解

- 贡献流程：[`docs/CONTRIBUTING.md`](CONTRIBUTING.md)
- 架构决策：[`docs/decisions/`](decisions/)
- 当前路线图：[`docs/roadmap.md`](roadmap.md)
