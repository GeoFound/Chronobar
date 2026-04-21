# 中国期货专用平台工程基线 v1.2

## 1. 文档定位

本文档定义平台工程组织、代码质量要求、测试规范、版本策略、开发流程和交付门槛。
所有后续开发、重构、AI 生成代码和外部协作都必须遵守本基线。

## 2. 工程目标

1. 保证核心协议长期稳定。
2. 保证模块可测试、可替换、可迁移。
3. 保证 AI 生成代码能被统一吸纳，而不是污染核心结构。
4. 保证回放结果、配置迁移和插件行为可验证。
5. 保证 Python 核心与 React 前端可以分层协作，而不互相侵入。

## 3. 仓库结构

推荐目录如下：

```text
futures_platform/
  pyproject.toml
  README.md
  docs/
    core/
      data_protocol.md
      event_protocol.md
      plugin_protocol.md
    system/
      architecture.md
      config_protocol.md
      ui_bridge_protocol.md
    engineering/
      engineering_baseline.md
  app/
    main.py
  core/
    enums.py
    models.py
    events.py
    exceptions.py
    event_engine.py
    main_engine.py
    ui_bridge.py
  gateways/
    base.py
    openctp_gateway.py
    mappers/
  rules/
    trading_calendar.py
    session_engine.py
    templates/
  compute/
    bar_aggregator.py
    indicators/
    replay/
    signals/
  storage/
    sqlite_repo.py
    config_repo.py
    log_repo.py
  plugins/
    host_api.py
    loader.py
    sandbox.py
    builtins/
  ui/
    desktop/
      app_shell/
      workspace/
      chart/
      panels/
      state/
      shared/
  config/
    defaults/
    schemas/
    migration.py
    loader.py
  tests/
    unit/
    integration/
    replay/
    migration/
    plugins/
    ui_contract/
```

说明：
- `core/ui_bridge.py` 为展示层桥接边界实现。
- `ui/desktop/` 为 React 桌面前端目录。
- `tests/ui_contract/` 用于验证前端与桥接层契约稳定性。

## 4. 代码规范

### 4.1 Python 版本

- Python 3.11+ 为最低支持版本。
- 新特性使用需以 3.11 为兼容下限。

### 4.2 Python 类型要求

- 核心模块必须全量类型标注。
- 公共函数禁止无返回类型。
- 公共接口禁止使用无约束 `dict` 作为长期数据边界。
- 协议对象优先使用 dataclass / Enum / Protocol / ABC。
- 动态数据的结构校验必须落在 schema 或 validator，而不是散落在 UI 中。

### 4.3 前端要求

- React 前端必须使用 TypeScript。
- 页面状态、工作区状态、订阅状态必须分层管理。
- 前端不得直接发明业务字段。
- 前端消费的所有业务数据必须来自受控桥接接口。
- UI 组件不得绕过桥接层访问核心进程内部模块。

### 4.4 命名规范

- Python 模块名：小写下划线
- 类名：大驼峰
- 常量：全大写下划线
- 事件类型：全大写
- 配置键：小写下划线
- 前端组件名：大驼峰
- 前端状态切片名：语义化小写命名

### 4.5 异常规范

- 不允许裸 `except`
- 业务异常、协议异常、插件异常、桥接异常分层定义
- 所有可恢复异常必须记录日志
- 所有不可恢复异常必须阻断当前任务并给出可追踪信息

## 5. 质量门槛

### 5.1 测试基线

测试框架建议：
- Python：pytest
- Frontend：Vitest / Playwright

必须覆盖：
- 单元测试
- 协议测试
- 配置迁移测试
- 回放一致性测试
- 插件隔离测试
- 关键集成测试
- 前端桥接契约测试

### 5.2 类型检查

类型检查工具建议：
- Python：mypy
- Frontend：tsc

要求：
- `core / rules / compute / plugins.host_api` 必须通过类型检查
- 新增公共接口必须补类型声明
- 忽略规则必须最小化，禁止大面积跳过

### 5.3 日志要求

- 核心流程必须有结构化日志
- 关键事件必须记录 `trace_id`
- 插件异常必须生成独立日志事件
- 回放模式必须可导出事件日志
- 前端命令失败与订阅异常必须可追踪

## 6. 配置治理

### 6.1 配置来源优先级

1. 系统默认
2. 环境配置
3. 品种模板
4. 合约实例
5. 工作区局部覆盖

### 6.2 配置变更要求

- 修改 schema 必须同步更新示例文件
- 修改字段含义必须补 migration
- 删除字段必须保留兼容层
- 所有迁移必须附测试样例
- 桥接层配置变更必须同步更新契约说明

## 7. 插件治理

### 7.1 接入要求

- 必须提供 manifest
- 必须提供 schema
- 必须声明权限
- 必须具备最小测试样例

### 7.2 卸载要求

- 卸载插件不得破坏主程序启动
- 卸载后旧工作区应允许降级加载
- 缺失插件必须显示可恢复提示，而不是直接崩溃

### 7.3 安全要求

- 默认最小权限
- 文件写入、网络访问、告警发射都必须显式授权
- 插件不得直接访问数据库连接对象
- 插件不得直接持有前端组件实例或前端状态仓库

## 8. 开发顺序

### 第一阶段：协议定稿

- core/data_protocol.md
- core/event_protocol.md
- system/config_protocol.md
- core/plugin_protocol.md
- system/ui_bridge_protocol.md

### 第二阶段：核心闭环

- models.py
- event_engine.py
- main_engine.py
- session_engine.py
- bar_aggregator.py
- plugin_host.py
- ui_bridge.py

### 第三阶段：接入与展示

- openctp_gateway.py
- workspace 基础框架
- chart 基础视图
- 参数面板自动生成
- React 工作区壳层

### 第四阶段：验证体系

- replay engine
- migration test
- plugin sandbox test
- integration test
- ui contract test

## 9. 交付标准

一个功能只有满足以下条件才算完成：

1. 协议有定义
2. 配置有样例
3. 代码有实现
4. 测试可运行
5. 日志可追踪
6. 回放可复现
7. 文档已更新

## 10. AI 协作约束

- AI 生成代码不得绕过协议文档
- AI 生成新功能必须先声明所属层级
- AI 生成插件必须使用标准生命周期接口
- AI 修改配置结构必须同步生成 migration
- AI 生成桥接接口必须同步更新契约说明
- AI 生成代码在合并前必须通过测试与类型检查

## 11. 禁止事项

- 禁止先堆 UI 再补内核
- 禁止核心对象长期使用松散 dict 传递
- 禁止跨层直接调用成为默认协作路径
- 禁止插件直接改核心状态
- 禁止没有测试就合并核心模块
- 禁止为了临时需求破坏协议兼容性
- 禁止前端组件依赖未声明桥接字段

## 12. 里程碑验收

### M1：协议完成
- 四类协议定稿
- UI Bridge 协议定稿
- schema 可校验
- 示例配置可加载

### M2：核心闭环完成
- Tick -> Event -> Bar -> Indicator -> Chart 跑通
- 夜盘 session 正确切分
- 插件可加载、可隔离、可卸载
- React 前端可消费标准查询结果与标准事件

### M3：验证体系完成
- 回放结果与实时结果一致
- 配置迁移可自动完成
- 关键模块通过 pytest、mypy、tsc 和契约测试检查