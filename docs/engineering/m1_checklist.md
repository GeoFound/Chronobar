# Milestone M1 Checklist

## 1. 目标定义

M1 的目标不是完成整个平台，而是完成"第一阶段可开发基线"。
达到 M1 后，团队应具备以下能力：

- 核心协议定稿
- 文档体系可导航
- 配置 schema 可校验
- 示例配置可加载
- 基础工程门禁可执行
- 最小测试入口可运行
- 后续 M2 能在此基础上直接进入实现

M1 不要求：
- 完整交易功能
- 完整图表体验
- 完整前端界面
- 全量插件生态
- 核心运行时代码完成

M1 关注的是：**协议和工程边界已经稳定，后续开发不会反复推翻地基。**

---

## 2. M1 验收口径

**本文件是 `engineering/engineering_baseline.md` §14 的可操作展开版本。两者以本文件为执行准则，以 baseline 为概念锚点。**

M1 验收标准参考 `engineering/engineering_baseline.md` 第14节定义：

- 四类协议定稿
- UI Bridge 协议定稿
- schema 可校验
- 示例配置可加载
- 基础校验入口和 CI 门禁可运行

本检查清单作为 M1 的执行检查表，详细拆解上述验收标准的各项任务。

---

## 3. 文档清单

以下文档必须存在，并完成初版定稿：

- [ ] `docs/system/architecture.md`
- [ ] `docs/core/data_protocol.md`
- [ ] `docs/core/event_protocol.md`
- [ ] `docs/system/config_protocol.md`
- [ ] `docs/core/plugin_protocol.md`
- [ ] `docs/engineering/engineering_baseline.md`
- [ ] `docs/system/ui_bridge_protocol.md`
- [ ] `README.md`

检查项：
- [ ] 文档版本号统一
- [ ] 文档中的术语一致，例如 `Tick`、`Bar`、`EventEnvelope`、`UiBridge`
- [ ] 文档之间无明显冲突
- [ ] React 展示层路线与 Python 核心路线描述一致
- [ ] M1、M2、M3 里程碑定义一致

---

## 4. 仓库结构

以下目录应完成初始化：

- [ ] `config/defaults/`
- [ ] `config/schemas/`
- [ ] `tests/`
- [ ] `tests/ui_contract/`
- [ ] `.github/workflows/`
- [ ] `docs/`

建议最小基线文件：
- [ ] `pyproject.toml`
- [ ] `.pre-commit-config.yaml`
- [ ] `.github/workflows/ci.yml`
- [ ] `tests/test_repo_baseline.py`

---

## 5. 配置与 Schema

### 5.1 示例配置文件

以下示例文件必须存在：

- [ ] `config/defaults/system.yaml`
- [ ] `config/defaults/market.yaml`
- [ ] `config/defaults/rules.yaml`
- [ ] `config/defaults/indicator.yaml`
- [ ] `config/defaults/workspace.yaml`

### 5.2 Schema 文件

以下 schema 文件必须建立：

- [ ] `config/schemas/system.schema.json`
- [ ] `config/schemas/market.schema.json`
- [ ] `config/schemas/rules.schema.json`
- [ ] `config/schemas/indicator.schema.json`
- [ ] `config/schemas/workspace.schema.json`

### 5.3 配置检查项

- [ ] `system.version` 已定义
- [ ] `system.ui_backend` 已改为 `react-desktop`
- [ ] `system.bridge` 段已存在
- [ ] `workspace.layout` 结构已定义
- [ ] `workspace.interactions` 结构已定义
- [ ] 所有 schema 设置 `additionalProperties: false`
- [ ] 示例配置可以被加载为 dict
- [ ] 示例配置可以通过 schema validate

---

## 6. 工程门禁基线

### 6.1 Python 工程入口

- [ ] `pyproject.toml` 已声明 Python 版本范围
- [ ] Runtime 依赖与 Dev 依赖分组存在
- [ ] `pytest`、`ruff`、`mypy` 有最小配置

### 6.2 CI / Hook 基线

- [ ] CI 可执行文档与测试校验
- [ ] pre-commit 可执行基础格式检查
- [ ] 失败时能阻断不合规提交或合并

### 6.3 契约样例准备

- [ ] Query 响应结构样例已入仓
- [ ] Subscription 推送结构样例已入仓
- [ ] 前端错误码样例列表已入仓

---

## 7. 测试基线

### 7.1 Python 测试框架

- [ ] `pytest` 已接入
- [ ] `tests/` 目录可被发现
- [ ] 至少有 1 个测试能成功运行

### 7.2 M1 必须具备的测试

- [ ] 配置 schema 校验测试
- [ ] 示例配置加载测试
- [ ] 文档地图存在性测试
- [ ] 桥接响应样例结构测试

### 7.3 前端相关测试准备

M1 不要求完整前端测试，但至少应准备：

- [ ] `tests/ui_contract/` 目录
- [ ] Query 响应结构快照或契约样例
- [ ] Subscription 推送结构样例
- [ ] 前端错误码样例列表

---

## 8. 文档与配置一致性检查

以下项目必须逐项确认：

- [ ] `docs/system/config_protocol.md` 中的示例字段可被 schema 接受
- [ ] `docs/system/ui_bridge_protocol.md` 中的响应结构在样例中可找到
- [ ] `README.md` 的阶段说明与 `docs/roadmap.md` 一致
- [ ] `docs/CONTRIBUTING.md` 的阶段说明与 `docs/roadmap.md` 一致
- [ ] `docs/engineering/engineering_baseline.md` 中的 pyproject 基线已落到仓库文件

---

## 9. M2 前的准备结论

只有以下条件全部满足，才允许进入 M2：

- [ ] 协议文档已冻结到当前版本
- [ ] 示例配置文件可加载
- [ ] schema 可校验
- [ ] 基础测试已跑通
- [ ] 文档与配置结构一致
- [ ] 团队对"Python 核心 + React 前端 + UiBridge"路线无歧义

---

## 10. 建议执行顺序

建议按下面顺序推进 M1：

1. 完成核心文档与 README 总览
2. 写默认配置与 schema
3. 接入 pyproject、pre-commit 和 CI
4. 接入 pytest 与最小测试
5. 准备桥接契约样例
6. 做一次文档—配置—测试一致性检查
7. 冻结 M1，进入 M2

---

## 11. M1 完成后的产出物

M1 结束时，仓库应至少具备：

- 一套正式协议文档
- 一套 README 导航文档
- 一套可校验的默认配置
- 一套基础工程门禁
- 一组最小测试
- 一个清晰、稳定、可继续开发的骨架

M1 的成功标准不是"功能很多"，而是"地基稳定"。
