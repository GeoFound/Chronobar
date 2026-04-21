# 中国期货专用平台配置协议 v1.2

## 1. 文档定位

本文档定义平台配置分层、覆盖规则、版本治理、迁移要求与校验方式。
平台所有配置默认采用 YAML 编写，采用 JSON Schema 进行结构校验，并可结合 Pydantic 或自定义 validator 进行业务校验。

本文档的目标是让系统配置、市场配置、规则配置、指标配置和工作区配置具备长期演进能力。
所有配置必须可导入、可导出、可迁移、可校验、可回放。

## 2. 配置分层

平台配置分为五类：

1. 系统配置
2. 市场配置
3. 规则配置
4. 指标配置
5. 工作区配置

## 3. 配置总原则

- 所有配置必须包含 `version`。
- 所有配置必须可以导入、导出、迁移。
- 支持多级覆盖：系统默认 < 环境配置 < 品种模板 < 合约实例 < 工作区局部覆盖。
- 删除字段必须经过兼容期。
- 同名配置项以后加载者覆盖先加载者。
- UI 不得写入未经 schema 声明的隐式字段。
- 前端布局配置与业务配置必须分开治理。
- 工作区配置可以变化较快，但必须保持结构稳定和迁移能力。

## 4. 配置结构

### 4.1 系统配置

```yaml
system:
  version: "1.2"
  app_name: "futures_platform"
  timezone: "Asia/Shanghai"
  log_level: "INFO"
  cache_dir: "./data/cache"
  db_url: "sqlite:///./data/app.db"
  ui_backend: "react-desktop"
  replay_dir: "./data/replay"
  bridge:
    host: "127.0.0.1"
    port: 18777
    query_protocol: "http"
    command_protocol: "http"
    subscription_protocol: "ws"
```

说明：
- `ui_backend` 用于标识当前展示层实现。
- `bridge` 定义前端与核心进程的桥接方式。
- `bridge` 的实现方式可替换，但语义边界应保持稳定。

### 4.2 市场配置

```yaml
market:
  gateways:
    ctp_main:
      type: "ctp"
      md_front: "tcp://..."
      td_front: "tcp://..."
      broker_id: "9999"
      auth_code: ""
      app_id: ""
  exchanges:
    SHFE: {}
    DCE: {}
    CZCE: {}
    INE: {}
    CFFEX: {}
```

### 4.3 规则配置

```yaml
rules:
  calendars:
    cn_futures:
      timezone: "Asia/Shanghai"
      holiday_source: "local"
  session_templates:
    SHFE_A_NIGHT_2300:
      exchange: "SHFE"
      trading_date_rule: "night_belongs_next_trading_date"
      segments:
        - {type: "morning", start: "09:00", end: "10:15"}
        - {type: "morning", start: "10:30", end: "11:30"}
        - {type: "afternoon", start: "13:30", end: "15:00"}
        - {type: "night", start: "21:00", end: "23:00"}
```

### 4.4 指标配置

```yaml
indicator:
  ma_01:
    type: "moving_average"
    enabled: true
    input: "close"
    window: 20
    continuity: "segmented"
    session_scope: "current_session"
    style:
      color: "#ffcc00"
      width: 2
```

### 4.5 工作区配置

```yaml
workspace:
  default:
    watchlist: ["rb2509", "i2509", "ag2506"]
    chart_template: "futures_intraday_v1"
    panels: ["price", "volume", "indicator", "log", "alert"]
    layout:
      type: "grid"
      preset: "trader-3pane"
    theme: "dark"
    interactions:
      crosshair_sync: true
      symbol_link_group: "A"
      interval_link_group: "A"
```

说明：
- `workspace` 用于描述前端展示层的可恢复状态。
- `layout` 只描述布局结果，不描述具体组件内部实现。
- `interactions` 用于声明跨图表联动策略。
- 工作区配置不得反向承担规则判定或指标语义。

## 5. 覆盖规则

### 5.1 配置优先级

优先级从低到高如下：

1. 系统默认
2. 环境配置
3. 品种模板
4. 合约实例
5. 工作区局部覆盖

### 5.2 覆盖原则

- 后加载配置覆盖先加载配置。
- 未声明字段不得隐式注入。
- 工作区局部覆盖只影响展示行为，不得覆盖底层交易语义。
- 合约实例覆盖不得破坏通用 schema 结构。

## 6. 迁移规则

### 6.1 升级规则

- 新增字段：允许，但必须补默认值。
- 重命名字段：必须提供 migration。
- 删除字段：必须经历至少一个兼容版本。
- 字段含义变化：必须提升 major 版本。

### 6.2 迁移函数接口

```python
def migrate_config(data: dict, from_version: str, to_version: str) -> dict: ...
```

### 6.3 迁移顺序

迁移顺序必须为：

旧版本配置 -> migration -> schema validate -> business validate

## 7. Schema 基线

### 7.1 根要求

- 根对象必须显式声明模块命名空间。
- `system`、`market`、`rules`、`indicator`、`workspace` 应具备独立 schema。
- 各配置段必须禁止未声明字段。
- schema 只负责结构正确性，业务语义由业务校验补充。

### 7.2 示例根结构

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "https://example.local/schemas/system.schema.json",
  "title": "SystemConfig",
  "type": "object",
  "required": ["system"],
  "properties": {
    "system": {
      "type": "object",
      "required": ["version", "timezone", "db_url", "ui_backend"],
      "properties": {
        "version": {"type": "string"},
        "timezone": {"type": "string"},
        "log_level": {"type": "string"},
        "cache_dir": {"type": "string"},
        "db_url": {"type": "string"},
        "ui_backend": {"type": "string"}
      },
      "additionalProperties": false
    }
  },
  "additionalProperties": false
}
```

## 8. 校验建议

- 配置载入：YAML -> dict
- 结构校验：JSON Schema
- 业务校验：Pydantic / 自定义 validator
- UI 工作区合法性校验：布局合法、联动组合法、面板类型合法
- 最终装载：通过 MainEngine 统一装配

## 9. 展示层配置约束

- 前端不得把组件运行时临时字段写回正式配置。
- 临时 UI 状态应与可持久化工作区配置区分。
- 允许持久化的展示配置应限于布局、主题、面板开关、联动组、图表模板和默认周期等稳定字段。
- 不允许把瞬时 hover、局部缓存或未确认拖拽状态写入配置。

## 10. 最低测试要求

- 配置文件 schema 校验测试
- 旧版本迁移测试
- 非法字段拦截测试
- 指标参数边界测试
- session 模板合法性测试
- 工作区布局配置兼容性测试
- `ui_backend` 与 `bridge` 配置装载测试