# 中国期货专用平台 UI Bridge 协议 v1.2

## 1. 文档定位

本文档定义 React 展示层与 Python 核心之间的桥接协议。
桥接协议负责约束前端如何查询状态、执行命令、订阅事件以及同步工作区。

UI Bridge 是展示层访问核心能力的唯一正式边界。
前端不得绕过 UI Bridge 直接访问 MainEngine、EventEngine、Gateway、Storage 或插件内部对象。

## 2. 设计目标

1. 为 React 前端提供统一、稳定、可测试的查询与订阅边界。
2. 保证实时模式与回放模式使用一致的展示接口。
3. 保证前端体验可以持续演进，而不反向污染核心协议。
4. 保证命令执行、状态查询和事件订阅彼此解耦。
5. 保证前端断线重连后可以恢复状态。

## 3. 协议模型

UI Bridge 包含三类接口：

1. Query API
2. Command API
3. Subscription API

推荐实现方式：
- Query API：本地 HTTP / IPC 请求响应
- Command API：本地 HTTP / IPC 请求响应
- Subscription API：WebSocket / IPC 流式推送

具体传输实现可以替换，但语义边界不得改变。

## 4. 通用约束

- 前端只消费标准对象或标准投影对象。
- Bridge 不得泄漏网关私有字段、数据库模型和核心内部引用。
- 所有返回结构必须可序列化。
- 所有错误返回必须具备机器可读错误码。
- 所有订阅事件必须带 trace_id、source 和 ts。
- 回放模式与实时模式应复用同一套前端消费结构。

## 5. Query API

### 5.1 用途

用于前端拉取当前状态快照。
典型场景包括：
- 启动时获取系统信息
- 获取工作区定义
- 获取当前图表数据
- 获取指标列表与插件输出
- 获取日志、告警和回放状态

### 5.2 查询类别

- system.get_status
- workspace.get_current
- workspace.get_layout
- market.get_watchlist
- chart.get_snapshot
- chart.get_indicators
- replay.get_status
- alert.get_recent
- log.get_recent
- plugin.get_enabled

### 5.3 查询结果约束

- 必须返回稳定对象结构。
- 必须支持前端冷启动。
- 必须允许前端根据快照重建 UI。
- 不得把“需要前端自行推理”的半成品状态返回给前端。

### 5.4 查询响应格式

```json
{
  "ok": true,
  "data": {},
  "trace_id": "..."
}
```

失败格式：

```json
{
  "ok": false,
  "error": {
    "code": "WORKSPACE_NOT_FOUND",
    "message": "workspace not found"
  },
  "trace_id": "..."
}
```

## 6. Command API

### 6.1 用途

用于前端发起明确动作。
Command 是意图表达，不是状态读取。

典型场景包括：
- 切换工作区
- 打开合约
- 修改图表周期
- 开始回放 / 停止回放
- 保存布局
- 启用 / 停用插件
- 确认告警
- 导出回放结果

### 6.2 命令类别

- workspace.switch
- workspace.save_layout
- workspace.reset_layout
- chart.open_instrument
- chart.change_interval
- chart.toggle_panel
- chart.apply_template
- replay.start
- replay.stop
- replay.seek
- plugin.enable
- plugin.disable
- alert.ack

### 6.3 命令约束

- 命令必须幂等或具备幂等保护策略。
- 命令成功后，应由事件流通知前端状态变化，而不是要求前端假定成功。
- 命令处理失败必须返回错误码和 trace_id。
- 命令不得直接暴露底层模块实例。

### 6.4 命令响应格式

```json
{
  "ok": true,
  "accepted": true,
  "trace_id": "..."
}
```

失败格式：

```json
{
  "ok": false,
  "error": {
    "code": "INVALID_INTERVAL",
    "message": "interval not supported"
  },
  "trace_id": "..."
}
```

## 7. Subscription API

### 7.1 用途

用于前端接收实时状态变化。
订阅层是前端实时体验的基础，不允许前端直接订阅底层原始回调。

### 7.2 订阅类型

- event_type 订阅
- event_type + instrument_id 精细订阅
- workspace 范围订阅
- replay 进度订阅
- alert / log 订阅

### 7.3 推送事件来源

推送事件必须来源于：
- EventEngine 标准事件
- WorkspaceManager 变更事件
- PluginHost 输出事件
- UiBridge 自身桥接状态事件

### 7.4 推送事件格式

```json
{
  "event_id": "...",
  "event_type": "BAR",
  "source": "compute.bar_1m",
  "ts": "2026-04-20T10:00:00+08:00",
  "instrument_id": "rb2509",
  "session_id": "SHFE.rb2509.20260420.night",
  "payload": {},
  "trace_id": "...",
  "replayable": true,
  "version": "1.0"
}
```

### 7.5 前端消费约束

- 前端必须按 event_type 明确消费事件。
- 前端不得依赖未声明字段。
- 前端必须允许事件乱序保护或以快照纠正。
- 前端重连后必须支持重新拉取快照再继续订阅。

## 8. 工作区同步

### 8.1 工作区状态范围

工作区同步包括：
- 当前选中合约
- 当前周期
- 图表模板
- 打开中的面板
- 布局定义
- 联动组
- 当前主题
- 回放上下文

### 8.2 同步原则

- 工作区保存由 Command API 发起。
- 工作区变化通过 Subscription API 广播。
- 工作区初始恢复通过 Query API 拉取。
- 工作区状态与业务计算状态分离管理。

### 8.3 推荐事件

- WORKSPACE_CHANGED
- PANEL_CHANGED
- SUBSCRIPTION_CHANGED
- THEME_CHANGED
- ACTIVE_INSTRUMENT_CHANGED

## 9. 图表数据边界

### 9.1 图表层可消费数据

图表层允许消费：
- Tick 投影
- Bar 投影
- 指标线输出
- 直方图输出
- 信号点输出
- session 边界信息
- 回放游标与进度信息

### 9.2 图表层禁止行为

- 禁止直接消费网关私有原始回调。
- 禁止前端自行推导 trading_date 与 session 规则。
- 禁止前端把交互临时状态回写为计算输入。
- 禁止图表组件直接调用插件内部方法。

## 10. 错误模型

### 10.1 错误分类

- BRIDGE_VALIDATION_ERROR
- BRIDGE_TIMEOUT
- WORKSPACE_NOT_FOUND
- INVALID_COMMAND
- INVALID_INTERVAL
- REPLAY_NOT_READY
- PLUGIN_NOT_FOUND
- PERMISSION_DENIED
- INTERNAL_ERROR

### 10.2 错误要求

- 错误必须返回稳定错误码。
- 错误必须包含 trace_id。
- 可恢复错误由前端提示并允许重试。
- 不可恢复错误必须进入日志与告警系统。

## 11. 可靠性要求

- 前端断线重连后必须支持状态恢复。
- 桥接层必须支持订阅取消。
- 桥接层必须支持基础节流与批量推送。
- 高流量场景下允许对 Tick 级展示做受控降采样，但不得影响核心计算链路。
- 回放模式必须保证事件顺序对展示层可解释。

## 12. 安全与权限

- 前端只获得展示所需最小数据。
- 未授权插件输出不得直接暴露到展示层。
- Bridge 不得暴露数据库连接、文件句柄和核心对象引用。
- 高风险命令必须具备额外校验或确认机制。

## 13. 测试要求

至少覆盖以下测试：

- Query API 结构契约测试
- Command API 成功 / 失败测试
- Subscription 重连恢复测试
- 工作区保存与恢复测试
- 回放模式前端订阅一致性测试
- 错误码稳定性测试