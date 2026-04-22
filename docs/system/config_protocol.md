# 中国期货专用平台配置协议 v1.2

## 1. 文档定位

本文档定义平台配置分层、覆盖规则、版本治理、迁移要求与校验方式。
平台所有配置默认采用 YAML 编写，采用 JSON Schema 进行结构校验，并可结合 Pydantic 或自定义 validator 进行业务校验。

本文档的目标是让系统配置、市场配置、规则配置、指标配置、研究配置和工作区配置具备长期演进能力。
所有配置必须可导入、可导出、可迁移、可校验、可回放。

## 2. 配置分层

平台配置分为六类：

1. 系统配置
2. 市场配置
3. 规则配置
4. 指标配置
5. 研究配置
6. 工作区配置

## 3. 配置总原则

- 所有配置必须包含 `version`。
- 所有配置必须可以导入、导出、迁移。
- 支持多级覆盖：系统默认 < 环境配置 < 品种模板 < 合约实例 < 工作区局部覆盖。
- 删除字段必须经过兼容期。
- 同名配置项以后加载者覆盖先加载者。
- UI 不得写入未经 schema 声明的隐式字段。
- 前端布局配置与业务配置必须分开治理。
- 工作区配置可以变化较快，但必须保持结构稳定和迁移能力。
- AI 生成的候选产物与正式配置必须区分治理。
- AI 对正式对象的写入或应用必须受确认策略约束。

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
    port: 18080
    query_protocol: "http"
    command_protocol: "http"
    subscription_protocol: "websocket"
    subscription_port: 18081
  ai:
    enabled: false
    model_provider: "local"  // enum[local, deepseek, openai, anthropic]
    local_model_path: "./models/qwen2.5-coder"
    api_endpoint: ""  // API endpoint for cloud providers
    api_key: ""  // API key for cloud providers
    max_tokens: 4096
    timeout: 30
    temperature: 0.7
    features:
      copilot: true
      signal_generation: false
      risk_check: false
      backtest_analysis: false
      auto_tuning: false
      artifact_builder: true
      external_context: true
      memory: true
    external_context:
      enabled: false
      whitelist_mode: "strict"
      allowed_sources: ["shfe", "dce", "czce", "cffex", "ine"]
      require_confirmation: true
    memory:
      mode: "session_only"  // enum[disabled, session_only, user_scoped]
      retention_days: 30
      allow_user_delete: true
      capture_user_preferences: true
    apply_policy:
      require_confirmation: true
      allow_workspace_write: true
      allow_strategy_write: true
      allow_high_risk_actions: false
```

说明：
- `ui_backend` 用于标识当前展示层实现。
- `bridge` 定义前端与核心进程的桥接方式。
- `bridge` 的实现方式可替换，但语义边界应保持稳定。
- `ai.features` 用于声明当前允许暴露给产品层的 AI 能力面。
- `ai.external_context` 用于约束真实世界访问能力，必须受白名单和确认策略控制。
- `ai.memory` 用于声明默认记忆模式和用户管理边界。
- `ai.apply_policy` 用于约束 AI 生成候选产物后是否允许进入正式对象写入路径。

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

### 4.5 研究配置

```yaml
research:
  factor_sets:
    intraday_alpha_v1:
      factors:
        - id: "rv_01"
          type: "realized_volatility"
          input: "close"
          window: 30
        - id: "mom_01"
          type: "return_momentum"
          input: "close"
          window: 20
      labels:
        next_bar_ret:
          type: "forward_return"
          horizon: "5m"
      experiments:
        exp_001:
          universe: ["rb", "i", "ag"]
          split: "walk_forward"
          cost_model: "default_cn_futures"
          publish_target: "factor_candidate"
      publish_records:
        - experiment_id: "exp_001"
          status: "candidate"
          target: "workspace.default.factor_board"
          confirmed: false
```

说明：
- `research` 用于描述因子定义、标签定义、实验配置和研究发布记录。
- 研究配置属于构建态资产，不得直接等同于运行态正式对象。
- `publish_records` 用于记录研究候选对象的发布状态、目标范围和确认结果。
- 研究配置必须支持复跑、导出、迁移和审计。

### 4.6 工作区配置

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
- `system`、`market`、`rules`、`indicator`、`research`、`workspace` 应具备独立 schema。
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
        "ui_backend": {"type": "string"},
        "ai": {
          "type": "object",
          "properties": {
            "enabled": {"type": "boolean"},
            "model_provider": {"type": "string", "enum": ["local", "deepseek", "openai", "anthropic"]},
            "local_model_path": {"type": "string"},
            "api_endpoint": {"type": "string"},
            "api_key": {"type": "string"},
            "max_tokens": {"type": "integer"},
            "timeout": {"type": "integer"},
            "temperature": {"type": "number"},
            "features": {"type": "object"},
            "external_context": {"type": "object"},
            "memory": {"type": "object"},
            "apply_policy": {"type": "object"}
          },
          "additionalProperties": false
        }
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
- AI 候选产物校验：schema / 类型检查 / 最小运行检查 / 来源保留检查
- 研究配置校验：因子定义合法、实验配置可复跑、发布记录与确认状态一致
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
- 研究配置迁移与发布记录一致性测试
- `ui_backend` 与 `bridge` 配置装载测试
- AI 外部上下文策略与记忆策略配置装载测试
- AI 候选产物确认策略配置装载测试
