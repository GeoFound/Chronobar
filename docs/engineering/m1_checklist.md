# Milestone M1 Checklist

## 1. 目标定义

M1 的目标不是完成整个平台，而是完成"第一阶段可开发基线"。
达到 M1 后，团队应具备以下能力：

- 核心协议定稿
- 文档体系可导航
- 配置 schema 可校验
- 示例配置可加载
- 仓库结构可初始化
- 最小核心对象与接口骨架可落代码
- 后续 M2 能在此基础上直接进入实现

M1 不要求：
- 完整交易功能
- 完整图表体验
- 完整前端界面
- 全量插件生态

M1 关注的是：**协议和工程边界已经稳定，后续开发不会反复推翻地基。**

---

## 2. M1 验收口径

**本文件是 `engineering/engineering_baseline.md` §14 的可操作展开版本。两者以本文件为执行准则，以 baseline 为概念锚点。**

M1 验收标准参考 `engineering/engineering_baseline.md` 第14节定义：

- 四类协议定稿
- UI Bridge 协议定稿
- schema 可校验
- 示例配置可加载

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

以下目录必须完成初始化：

- [ ] `app/`
- [ ] `core/`
- [ ] `gateways/`
- [ ] `rules/`
- [ ] `compute/`
- [ ] `storage/`
- [ ] `plugins/`
- [ ] `ui/desktop/`
- [ ] `config/defaults/`
- [ ] `config/schemas/`
- [ ] `tests/unit/`
- [ ] `tests/integration/`
- [ ] `tests/replay/`
- [ ] `tests/migration/`
- [ ] `tests/plugins/`
- [ ] `tests/ui_contract/`
- [ ] `docs/`

建议最小文件骨架：
- [ ] `app/main.py`
- [ ] `core/models.py`
- [ ] `core/events.py`
- [ ] `core/event_engine.py`
- [ ] `core/main_engine.py`
- [ ] `core/ui_bridge.py`
- [ ] `rules/session_engine.py`
- [ ] `compute/bar_aggregator.py`
- [ ] `plugins/host_api.py`
- [ ] `config/loader.py`
- [ ] `config/migration.py`

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

以下 schema 文件建议建立：

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

## 6. 核心协议代码骨架

### 6.1 数据协议骨架

以下对象至少建立代码壳：

- [ ] `SessionType`
- [ ] `Interval`
- [ ] `Tick`
- [ ] `Bar`
- [ ] `Instrument`
- [ ] `SessionContext`

检查项：
- [ ] 使用 dataclass / Enum
- [ ] 字段名与协议文档一致
- [ ] 支持最小序列化转换
- [ ] 保留 `extra` 扩展区

### 6.2 事件协议骨架

以下对象和接口至少建立代码壳：

- [ ] `EventEnvelope`
- [ ] `EventBus` 抽象接口
- [ ] `EventEngine` 最小实现
- [ ] `subscribe(event_type, handler)`
- [ ] `subscribe_instrument(event_type, instrument_id, handler)`

检查项：
- [ ] `trace_id` 字段存在
- [ ] `replayable` 字段存在
- [ ] 支持最小发布 / 订阅流程
- [ ] handler 异常隔离逻辑有占位

### 6.3 插件协议骨架

以下接口至少建立：

- [ ] `BasePlugin`
- [ ] `PluginContext`
- [ ] `plugins/host_api.py`
- [ ] `plugins/loader.py` 最小壳

检查项：
- [ ] 生命周期接口完整
- [ ] Host API 方法名与协议一致
- [ ] 插件输出约束有占位
- [ ] 权限模型有基础结构

### 6.4 策略协议骨架

以下接口至少建立：

- [ ] `BaseStrategy` 抽象基类
- [ ] `StrategyContext` 接口
- [ ] `StrategyHostAPI` 接口（submit_order、cancel_order、get_positions、get_account）
- [ ] `strategy/host_api.py` 最小壳

检查项：
- [ ] BaseStrategy 生命周期接口完整（on_init、on_start、on_stop、on_tick、on_bar、on_event）
- [ ] StrategyHostAPI 方法名与协议一致
- [ ] 交易权限模型有基础结构
- [ ] 回测一致性保证有占位

### 6.5 风控协议骨架

以下接口至少建立：

- [ ] `RiskChecker` 抽象接口
- [ ] `RiskManager` 接口
- [ ] `RiskCheckRequest` 数据类
- [ ] `RiskCheckResult` 数据类
- [ ] `rules/session_engine.py` 最小壳

检查项：
- [ ] RiskChecker 接口方法完整（check、get_check_type）
- [ ] RiskManager 支持多检查器注册
- [ ] RiskCheckResult 字段与协议一致（passed、check_type、block_reason、block_code、check_time、context）
- [ ] 风控事件模型有占位（RISK_BLOCKED、RISK_WARNING）

### 6.6 UI Bridge 骨架

以下接口至少建立：

- [ ] `core/ui_bridge.py`
- [ ] Query API 最小壳
- [ ] Command API 最小壳
- [ ] Subscription API 最小壳

检查项：
- [ ] 能返回统一 `ok/data/trace_id` 结构
- [ ] 错误结构统一
- [ ] 事件推送结构与 `EventEnvelope` 对齐
- [ ] 不直接暴露核心内部对象

---

## 7. 测试基线

### 7.1 Python 测试框架

- [ ] `pytest` 已接入
- [ ] `tests/` 目录可被发现
- [ ] 至少有 1 个测试能成功运行

### 7.2 M1 必须具备的测试

- [ ] Tick 序列化 / 反序列化测试
- [ ] Bar 唯一键测试
- [ ] EventEnvelope 字段完整性测试
- [ ] 单事件发布 / 订阅测试
- [ ] 配置 schema 校验测试
- [ ] 旧版本配置迁移占位测试
- [ ] 插件 manifest 解析测试
- [ ] UiBridge Query 响应结构测试

### 7.3 前端相关测试准备

M1 不要求完整前端测试，但至少应准备：

- [ ] `tests/ui_contract/` 目录
- [ ] Query 响应结构快照或契约样例
- [ ] Subscription 推送结构样例
- [ ] 前端错误码样例列表

---

## 8. 前端最小准备

虽然 M1 不要求完成 React 前端，但以下最小准备建议完成：

- [ ] `ui/desktop/` 目录初始化
- [ ] `app_shell/` 子目录建立
- [ ] `workspace/` 子目录建立
- [ ] `chart/` 子目录建立
- [ ] `panels/` 子目录建立
- [ ] `state/` 子目录建立

建议至少补一个说明文件：
- [ ] `ui/desktop/README.md`

内容建议包括：
- 前端技术栈
- 目录职责
- 状态管理边界
- 仅通过 UiBridge 访问核心

---

## 9. 文档与代码一致性检查

以下项目必须逐项确认：

- [ ] `docs/system/architecture.md` 中的核心模块在代码目录中有对应落点
- [ ] `docs/core/data_protocol.md` 中的对象在代码里有同名或同义实现
- [ ] `docs/core/event_protocol.md` 中的字段与事件类型在代码中可找到
- [ ] `docs/system/config_protocol.md` 中的示例字段可被 schema 接受
- [ ] `docs/core/plugin_protocol.md` 中的 Host API 在代码中有接口壳
- [ ] `docs/system/ui_bridge_protocol.md` 中的 Query / Command / Subscription 在代码中有接口壳
- [ ] `docs/engineering/engineering_baseline.md` 中的仓库结构和测试目录已建立

---

## 10. M2 前的准备结论

只有以下条件全部满足，才允许进入 M2：

- [ ] 协议文档已冻结到当前版本
- [ ] 示例配置文件可加载
- [ ] schema 可校验
- [ ] 最小代码壳已建立
- [ ] 最小测试已跑通
- [ ] 文档与目录结构一致
- [ ] 团队对"Python 核心 + React 前端 + UiBridge"路线无歧义

---

## 11. 建议执行顺序

建议按下面顺序推进 M1：

1. 完成 7 份核心文档与 README 总览
2. 初始化仓库结构
3. 写默认配置与 schema
4. 写数据协议与事件协议代码壳
5. 写插件 Host API 和 UiBridge 代码壳
6. 接入 pytest 与最小测试
7. 做一次文档—代码—配置一致性检查
8. 冻结 M1，进入 M2

---

## 12. M1 完成后的产出物

M1 结束时，仓库应至少具备：

- 一套正式协议文档
- 一套 README 导航文档
- 一套可校验的默认配置
- 一组最小核心对象和接口壳
- 一组最小测试
- 一个清晰、稳定、可继续开发的骨架

M1 的成功标准不是"功能很多"，而是"地基稳定"。
