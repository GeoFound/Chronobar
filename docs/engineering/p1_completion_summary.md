# P1 核心闭环预演审查记录

## 概述

P1 (M2 核心闭环任务包) 的相关运行时代码和演示脚本曾做过一次预演性实现与审查。

本文件仅用于保留当时的实现观察与风险记录，不构成正式 gate 放行结论。
当前正式阶段口径仍以 [`current_phase_and_truth_source.md`](current_phase_and_truth_source.md) 与 [`../roadmap.md`](../roadmap.md) 为准。

## 预演覆盖范围

### P1-T1: 仓库运行时代码初始化
- 创建 Python runtime 目录骨架
- 目录结构与 `engineering_baseline.md` 一致
- pytest 可发现新增测试目录

### P1-T2: 标准对象与异常层
- 核心模型定义（Tick, Bar, Instrument, Order, etc.）
- 枚举定义（Interval, SessionType, OrderType, etc.）
- 异常层次结构
- 对象可实例化
- 协议测试通过
- mypy 不报公共接口错误

### P1-T3: EventEngine
- 统一事件总线实现
- 事件注册、订阅、分发
- trace_id 保留
- 异常隔离
- 事件投递单测与集成测试通过

### P1-T4: RuleEngine 最小 session 判定
- 交易时段模板加载
- session 判定
- 夜盘样例测试通过
- 支持 night_belongs_next_trading_date 规则
- 支持跨日时段检测

### P1-T5: BarAggregator + 1 个指标
- Tick -> Bar 聚合器实现
- 支持多种时间间隔（M1, M5, M15, M30, H1, D1）
- MovingAverage 指标实现
- IndicatorManager 实现
- 1 分钟 Bar 聚合测试通过

### P1-T6: UiBridge 最小投影
- Query API 最小实现
- 标准响应格式（ok/data/error/trace_id）
- 标准错误码枚举
- system.get_status 查询实现
- 契约测试与样例结构一致

### P1-T7: 核心闭环演示
- 演示脚本 `examples/core_loop_demo.py`
- 集成测试验证全链路
- Tick -> Event -> Bar -> Indicator -> Snapshot 全链路可复现

## 预演中已观察到的数据流

预演代码中已观察到以下链路片段：

1. **Tick 接收**：演示脚本创建 synthetic Tick 对象（P1 不要求真实 Gateway）
2. **Event 分发**：EventBus 事件发布、订阅、分发机制已验证（10 个事件成功接收）
3. **Session 判定**：RuleEngine 判定交易时段
4. **Bar 聚合**：BarAggregator 聚合 Tick 到 Bar
5. **指标计算**：IndicatorManager 计算 MA5 等指标
6. **查询响应**：UiBridge 提供前端查询接口

## 技术栈

- Python 3.14+
- pytest (单元测试)
- mypy (类型检查)
- ruff (代码检查和格式化)
- pre-commit (Git hooks)
- uv (依赖管理)

## 配置改进

- pre-commit 配置优化（增量 mypy 检查）
- 添加安全 hooks（detect-private-key, check-merge-conflict）
- 添加 check-toml hook
- CI 配置优化（Python 3.14 矩阵测试、缓存）

## 文档

- 协议文档完整（data_protocol.md, event_protocol.md, config_protocol.md, ui_bridge_protocol.md）
- 工程基线文档（engineering_baseline.md）
- 实施任务包文档（implementation_task_packages.md）
- README.md
- CHANGELOG.md

## 风险与限制

### 已知限制
- Gateway 未实现：P1 阶段使用 synthetic Tick 对象，未连接真实 CTP Gateway
- EventBus 异步处理：演示脚本需添加 sleep 等待事件队列处理，生产环境需更完善的同步机制
- 回放不可复现：P1 未实现回放机制（P3 回测阶段要求）
- 无真实数据持久化：Bar 数据未持久化存储（P3 回测阶段要求）

### 技术风险
- EventBus 线程安全：当前实现使用 RLock，高并发场景需进一步验证
- BarAggregator 内存占用：长时间运行可能积累大量 Bar 数据，需定期清理
- IndicatorManager 指标扩展：当前仅实现 MA5，更多指标需验证计算正确性

### 工程风险
- 直接推送到 main：EventBus 验证修改直接推送到 main，违反 PR 流程（engineering_baseline.md §9.1）
- 集成测试为空：tests/integration/ 目录为空，依赖演示脚本作为集成验证

## 审查结论

本次预演**不能作为 P1 已完成的依据**，原因包括但不限于：

- 正式阶段口径与仓库导航文档曾出现冲突
- Tick 持久化、回放一致性、恢复路径与 benchmark 尚未形成正式 gate 证据
- 实验性代码、演示脚本与正式验收结果没有被明确隔离

因此，后续动作应是继续完成 M1 / P0 收口，而不是据此直接宣称进入 P2 或 P3。

## 预演核对项

- [x] 存在预演性质的运行时代码与样例
- [x] 已识别这些产物与正式 gate 之间的差距
- [ ] P1 正式 gate 通过
- [ ] 可作为当前阶段正式状态说明
