---
description: Chronobar phased delivery execution workflow
---
# Chronobar 分阶段交付执行工作流

本工作流用于指导任务 AI 或协作者按 Chronobar 的正式规划，从 M1 冻结一路推进到产品落地。

## 1. 启动前检查

在开始任何阶段前，先阅读：

1. `ai-instructions.md`
2. `AGENTS.md`
3. `README.md`
4. `docs/roadmap.md`
5. `docs/engineering/engineering_baseline.md`
6. `docs/engineering/delivery_master_plan.md`
7. `docs/engineering/implementation_task_packages.md`

## 2. 阶段推进规则

- 一次只推进一个阶段
- 一个阶段内一次只推进一个任务包到 in progress
- 只有当前阶段 gate 全部满足，才允许进入下一阶段
- 任一回滚条件触发，立即停止推进，回到上一个稳定阶段

## 3. 当前阶段识别

执行前先判断当前处于哪个阶段：

- M1 / P0：基线冻结
- M2 / P1：核心最小闭环
- M3 / P2：插件系统
- M4 / P3：回测系统
- M5 / P4：桌面产品骨架
- M6+ / P5：AI Assistant 受控落地
- Release / P6：beta / GA

## 4. 执行步骤

### Step A：确认进入条件

逐项检查当前阶段的进入条件。
若存在未满足项：
- 不开始写代码
- 先补齐进入条件

### Step B：选择单个任务包

从 `docs/engineering/implementation_task_packages.md` 中选择当前阶段的下一个任务包。
记录：
- 任务包 ID
- 目标
- 依赖
- 预期产出
- 验证方法

### Step C：实施最小变更

- 只做当前任务包所需最小改动
- 不顺手扩展下一阶段目标
- 同步补测试和必要文档

### Step D：执行验证

优先使用仓库入口：

```bash
just docs-check
just test
just check
```

如任务包引入新的子系统测试，应补充对应命令。

### Step E：阶段 gate 检查

在任务包完成后，检查：
- 范围 gate
- 实现 gate
- 测试 gate
- 文档 gate
- 治理 gate
- 回滚 gate

只有全部满足，才能标记任务包完成。

## 5. 回滚规则

出现以下情况之一，立即回滚：

- 核心协议被隐式改坏
- UI Bridge 与前端契约不一致
- 回测与实时链路出现不可解释偏差
- 插件可越权访问核心状态
- AI Assistant 出现越权、无审计或无证据强答
- 无法给出可重复验证路径

回滚动作：

1. 停止当前阶段新增开发
2. 回到最近稳定提交或稳定目标范围
3. 只修复阻塞问题，不扩写新能力
4. 更新文档中的限制与风险记录

## 6. 下一阶段放行条件

只有在以下条件全部满足时，才允许开始下一阶段：

- 当前阶段退出条件全部满足
- 当前阶段回滚方案可执行
- 当前阶段关键测试稳定通过
- 当前阶段文档与样例已同步
- 当前阶段没有未关闭 blocker

## 7. 输出要求

每次完成一个任务包后，必须输出：

- 已完成项
- 未完成项
- 风险项
- 是否允许进入下一个任务包
- 若不允许，阻塞点是什么
