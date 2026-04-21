# Core Protocol Documents

本目录包含核心协议文档，定义系统最基础的交换边界和协作契约。

## 文档列表

- **data_protocol.md** - 数据对象定义（Tick、Bar、Instrument、Order、Trade、Position、Account、AI 对象等）
- **event_protocol.md** - 事件模型和协作总线（EventEnvelope、标准事件类型、订阅规则、回放一致性）
- **gateway_protocol.md** - 网关接口标准化（BaseGateway、GatewayCallback、GatewayStatus、重连策略）
- **plugin_protocol.md** - 插件接入和权限模型（5 层插件分类、manifest、Host API、权限分级）
- **strategy_protocol.md** - 策略交易执行边界（策略 Host API、交易权限、回测一致性）
- **risk_protocol.md** - 风控检查机制（6 类风控检查、RiskChecker、风控事件模型）
- **backtest_protocol.md** - 回测/仿真/实盘统一接口（BacktestEngine、撮合模拟、性能指标）
- **golden_examples.md** - 黄金样例（MA 指标、双均线信号、策略、AI 情感信号、回放测试）

## 层级归属

这些文档属于第一层：最稳定的核心协议层。如果这一层不稳定，计算链路、回放链路、插件链路、策略链路和风控链路都会反复返工。
