# Chronobar AI Instructions

## 项目定位

Chronobar 是一个面向中国个人量化交易者的桌面优先交易平台，当前仓库处于 **M1 基线收敛** 阶段。
正式阶段口径以 [`docs/engineering/current_phase_and_truth_source.md`](docs/engineering/current_phase_and_truth_source.md) 与 [`docs/roadmap.md`](docs/roadmap.md) 为准。

本文件约束的是**仓库 AI**：也就是参与仓库文档、协议、代码、测试、维护、迁移与重构的 AI 协作行为。
本文件**不**定义 Chronobar 产品内部提供给产品使用者的 **产品 AI**；产品 AI 的边界与能力应以 `docs/system/ai_assistant_architecture.md` 与 `docs/system/ai_assistant_product_contract.md` 为准。

当前阶段重点是：
- 协议文档稳定
- 默认配置与 JSON Schema 对齐
- 基础测试与 CI 门禁可执行
- 为 M2 的核心闭环实现提供稳定基线

当前阶段不应假装已具备：
- 核心运行时引擎
- 可运行的交易网关
- 前端桌面应用
- 回测与实盘完整能力

## 技术栈

- Python: 3.14+
- 配置格式: YAML
- 配置校验: JSON Schema
- 文档: Markdown
- 目标架构: Tauri + React + Python sidecar
- 存储方向: DuckDB + Parquet（Tick）+ SQLite（元数据）

## 架构风格

- 仓库形态：文档优先、协议驱动、单仓库
- 当前阶段：M1 基线收敛，允许存在实验性运行时代码，但不以此宣称 P1 已放行
- 后续阶段：Python 核心 + React 前端 + UI Bridge 分层协作

## 端口约定

Chronobar 当前协议基线使用：

- Python sidecar HTTP / Query / Command: `18080`
- Python sidecar WebSocket / Subscription: `18081`

注意：当前仓库尚未提供运行时实现，这些端口属于协议保留值，不代表本仓库当前已有服务在监听。

## 当前阶段的工作原则

- 优先修文档、配置、Schema、测试、CI 的一致性
- 修改协议相关内容时，必须同步更新文档与 `CHANGELOG.md`
- 不要在 M1 阶段偷偷引入大量运行时代码
- 不要发明未在协议中声明的新业务字段
- 不要让 README 承担协议级字段定义

## 仓库 AI 长期协作原则

- **AI 不是仓库里的聊天挂件，而是受控协作者**：可参与研究、配置、代码、验证、运维文档、迁移与重构，但永远不是最终决策者。
- **对象优先于页面与流程**：优先冻结协议对象、状态、依赖关系与构建态/运行态边界，而不是先围绕页面交互扩展语义。
- **政策与能力优先数据化**：市场差异、合规差异、网关差异、AI 权限与确认要求应优先写入协议、Schema、样例和策略数据，而不是硬编码在分支逻辑里。
- **高价值变更必须可重放、可追责、可迁移**：仓库 AI 生成的候选对象、证据、确认点、迁移规则与验证结果应保留语义，便于后续维护、重写和跨国家平台迁移。

## 测试与检查命令

优先通过 `just` 统一执行：

```bash
just install
just test
just check
just docs-check
```

在未使用 `just` 时，可直接执行：

```bash
uv sync --group dev
uv run pytest
uv run pre-commit run --all-files
```

## 代码风格与质量要求

- Python 类型与工程要求以 `docs/engineering/engineering_baseline.md` 为准
- 格式与静态检查通过 `ruff`、`mypy`、`pytest` 收口
- 文档变更必须尽量精准，不做无关重写
- 新增文件应服务于当前里程碑，不预埋大段投机性实现

## 文档优先阅读顺序

1. `README.md`
2. `docs/roadmap.md`
3. `docs/engineering/current_phase_and_truth_source.md`
4. `docs/system/architecture.md`
5. `docs/core/data_protocol.md`
6. `docs/core/event_protocol.md`
7. `docs/system/config_protocol.md`
8. `docs/system/ui_bridge_protocol.md`
9. `docs/system/storage_lifecycle_and_recovery.md`
10. `docs/engineering/runtime_nonfunctional_baseline.md`
11. `docs/engineering/engineering_baseline.md`
12. `docs/engineering/m1_checklist.md`

## AI 协作注意事项

- 任何 AI 助手在动手前先读本文件
- 若修改协议边界、配置结构或桥接结构，必须同步补测试或契约样例
- 若本地环境缺少关键工具或依赖，必须明确指出，不要假装已验证成功
- 若任务跨越 M1 与 M2 边界，应先向用户确认是否允许进入实现阶段
