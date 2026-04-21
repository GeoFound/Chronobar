# AI 插件协议 v1.2

## 1. 文档定位

本文档定义 AI 智能体插件的接入规范、能力分类、权限约束、配置管理和安全要求。AI 插件是受控智能体，不是自主决策单元，必须通过 HostAPI 与核心交互，不能绕过风控直接操盘。

## 2. AI 插件目标

1. 让 AI 作为 Copilot 增强人类决策，而非替代人类
2. 让 AI 插件以标准协议接入，具备最小权限、可测试、可下线、可回放
3. 让 AI 输出通过类型检查门槛才能进入系统
4. 让 AI 风控检查器只能发出事件，不能直接操作仓位
5. 符合监管合规要求和风险控制原则

## 3. AI 插件分类

### 3.1 AI Copilot

- **能力**：自然语言生成策略代码骨架
- **权限**：读取工作区配置、写入文件（需用户授权）
- **限制**：不能直接下单，只能生成代码供用户审查
- **适用场景**：策略研究助手、代码生成助手

### 3.2 AI 信号插件

- **能力**：LLM Alpha 因子生成、情感分析、市场状态分类
- **权限**：读取市场数据、emit_alert、call_external_api
- **限制**：不能直接下单，只能输出信号供策略参考
- **适用场景**：智能信号生成、情感分析、市场状态识别

### 3.3 AI 回测分析师

- **能力**：智能回测报告生成
- **权限**：读取回测结果、读取市场数据、call_external_api
- **限制**：不能修改回测配置，只能生成分析报告
- **适用场景**：回测分析、性能归因、策略优化建议

### 3.4 AI 风控增强

- **能力**：异常行为检测、微结构异常识别
- **权限**：读取市场数据、读取订单流、emit_alert
- **限制**：只能发出 RISK_BLOCKED/RISK_WARNING 事件，不能直接操作仓位
- **适用场景**：风控增强、异常检测、微结构分析

### 3.5 AI 自动调参

- **能力**：超参数优化 Agent
- **权限**：读取回测结果、修改策略参数（需用户授权）
- **限制**：参数修改必须通过用户确认，不能自动上线
- **适用场景**：参数优化、超参数搜索

## 4. AI 插件 manifest

### 4.1 基本结构

```json
{
  "name": "llm_sentiment_signal",
  "version": "1.0.0",
  "api_version": "1.2",
  "kind": "ai-agent",
  "entry": "plugin.py",
  "ai_capabilities": ["sentiment", "regime"],
  "permissions": {
    "read_market_data": true,
    "emit_alert": true,
    "write_file": false,
    "read_workspace": false,
    "call_external_api": true
  },
  "ai_config": {
    "model_provider": "local",
    "max_tokens": 1024,
    "timeout": 10
  },
  "compatibility": {
    "min_core_version": "1.2",
    "max_core_version": "1.x"
  }
}
```

### 4.2 字段说明

- `ai_capabilities`：AI 插件具备的能力列表（sentiment、regime、factor、anomaly）
- `permissions.call_external_api`：AI 插件独有的网络外呼权限，用于调用 LLM API
- `ai_config`：AI 模型配置
  - `model_provider`：模型提供商（local、deepseek、openai、anthropic）
  - `max_tokens`：最大 token 消耗限制
  - `timeout`：超时限制（秒）

## 5. AI 数据对象

### 5.1 AISignal

AI 生成的交易信号对象。

```python
@dataclass(slots=True)
class AISignal:
    signal_id: str
    plugin_id: str
    timestamp: datetime
    instrument_id: str
    signal_type: str  # sentiment, regime, factor, anomaly
    confidence: float  # 0.0-1.0
    metadata: dict[str, Any]
    raw_llm_output: str | None = None
```

### 5.2 SentimentScore

市场情感评分对象。

```python
@dataclass(slots=True)
class SentimentScore:
    instrument_id: str
    timestamp: datetime
    sentiment: str  # positive, negative, neutral
    score: float  # -1.0 to 1.0
    confidence: float  # 0.0-1.0
    source: str  # plugin_id
```

### 5.3 RegimeLabel

市场状态标签对象。

```python
@dataclass(slots=True)
class RegimeLabel:
    instrument_id: str
    timestamp: datetime
    regime: str  # trending, ranging, volatile
    confidence: float  # 0.0-1.0
    source: str  # plugin_id
```

## 6. AI 风控检查

### 6.1 AI 风控检查器接口

AI 风控检查器只能发出事件，不能直接操作仓位。

```python
class AIRiskChecker:
    def check(self, context: dict) -> RiskCheckResult:
        """
        执行 AI 风控检查

        返回：
        - RiskCheckResult(check_type="ai", passed=True/False, message="...")
        """
        pass
```

### 6.2 AI 风控事件

AI 风控检查器只能发出以下事件：
- `EVENT_RISK_BLOCKED`：风控拦截
- `EVENT_RISK_WARNING`：风控警告

禁止行为：
- 不能直接修改 Position
- 不能直接调用 submit_order/cancel_order
- 不能绕过标准 RiskChecker

## 7. AI 配置管理

### 7.1 系统配置

在 `docs/system/config_protocol.md` 中定义的 `ai_config` 节点：

```json
{
  "ai": {
    "enabled": true,
    "model_provider": "local",
    "api_endpoint": null,
    "api_key": null,
    "max_tokens": 4096,
    "timeout": 30,
    "features": {
      "copilot": true,
      "signal": true,
      "backtest_analyst": true,
      "risk_enhancement": true,
      "auto_tuning": false
    }
  }
}
```

### 7.2 模型提供商约束

`model_provider` 字段必须为以下枚举值之一：
- `local`：本地模型
- `deepseek`：DeepSeek API
- `openai`：OpenAI API
- `anthropic`：Anthropic API

### 7.3 LLMProvider 接口协议

AI 插件不得直接调用 HTTP 接口访问 LLM API，必须通过 HostAPI 获取 LLMProvider 实例。这确保了统一的 token 消耗控制、超时管理和可测试性。

```python
from typing import Protocol, runtime_checkable

@dataclass(slots=True)
class LLMResponse:
    """LLM 响应对象"""
    content: str
    tokens_used: int
    model: str
    provider: str

@runtime_checkable
class LLMProvider(Protocol):
    """LLM 提供商接口协议"""

    async def complete(
        self,
        prompt: str,
        max_tokens: int,
        timeout: float,
        temperature: float = 0.7
    ) -> LLMResponse:
        """
        异步调用 LLM 完成任务

        参数：
            prompt: 提示词
            max_tokens: 最大 token 数
            timeout: 超时时间（秒）
            temperature: 温度参数（0.0-1.0）

        返回：
            LLMResponse 对象

        异常：
            TimeoutError: 调用超时
            RuntimeError: API 错误
        """
        ...

    def get_provider_name(self) -> str:
        """返回提供商名称"""
        ...

    def is_available(self) -> bool:
        """检查提供商是否可用"""
        ...

    def estimate_tokens(self, text: str) -> int:
        """估算文本的 token 数量"""
        ...
```

**约束：**
- AI 插件必须通过 `PluginContext.get_llm_provider(provider_name)` 获取 LLMProvider 实例
- 禁止 AI 插件直接 import httpx、aiohttp 等 HTTP 库
- LLMProvider 实现由核心提供，支持 MockLLMProvider 用于测试
- 调用此方法需要 `call_external_api: true` 权限

## 8. 安全约束

### 8.1 权限约束

- AI 插件必须通过 HostAPI 与核心交互
- AI 插件必须受同等权限模型约束
- `call_external_api` 权限仅授予 ai-agent 插件
- LLM API Key 权限受限，不能暴露给其他插件

### 8.2 资源约束

- 最大 token 消耗限制
- 超时限制
- 并发请求限制
- 失败重试限制

### 8.3 输出约束

- AI 输出必须通过类型检查门槛
- AI 输出必须可序列化
- AI 输出必须带来源插件标识
- AI 输出必须在回放模式下可重现

## 9. 最低测试要求

- AISignal 序列化/反序列化测试
- SentimentScore 边界值测试（score 范围 -1.0 到 1.0）
- RegimeLabel 枚举值测试
- AI manifest 解析测试
- AI 风控检查器事件发射测试
- call_external_api 权限拦截测试
- AI 输出类型检查测试
- AI 配置迁移测试

## 10. 相关文档

- [`docs/core/plugin_protocol.md`](plugin_protocol.md)：通用插件协议（AI 插件继承其生命周期和 Host API）
- [`docs/core/data_protocol.md`](data_protocol.md)：AI 数据对象定义
- [`docs/core/event_protocol.md`](event_protocol.md)：AI 事件类型（EVENT_AI_SIGNAL、EVENT_REGIME_CHANGE）
- [`docs/core/risk_protocol.md`](risk_protocol.md)：AI 风控检查器接口
- [`docs/core/backtest_protocol.md`](backtest_protocol.md)：AI 回测分析师集成
- [`../system/config_protocol.md`](../system/config_protocol.md)：AI 系统配置
