# Chronobar AI Instructions

## 项目定位

Chronobar 是一个面向中国个人量化交易者的桌面优先交易平台，当前仓库处于 **M1 基线收敛** 阶段。

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

- Python: 3.11+（当前基线兼容到 `<3.13`）
- 配置格式: YAML
- 配置校验: JSON Schema
- 文档: Markdown
- 目标架构: Tauri + React + Python sidecar
- 存储方向: DuckDB + Parquet（Tick）+ SQLite（元数据）

## 架构风格

- 仓库形态：文档优先、协议驱动、单仓库
- 当前阶段：docs-first baseline repo
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
3. `docs/system/architecture.md`
4. `docs/core/data_protocol.md`
5. `docs/core/event_protocol.md`
6. `docs/system/config_protocol.md`
7. `docs/system/ui_bridge_protocol.md`
8. `docs/engineering/engineering_baseline.md`
9. `docs/engineering/m1_checklist.md`

## AI 协作注意事项

- 任何 AI 助手在动手前先读本文件
- 若修改协议边界、配置结构或桥接结构，必须同步补测试或契约样例
- 若本地环境缺少关键工具或依赖，必须明确指出，不要假装已验证成功
- 若任务跨越 M1 与 M2 边界，应先向用户确认是否允许进入实现阶段
