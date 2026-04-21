# ADR-001: Tick 存储架构选择

## 状态

已接受

## 上下文

Chronobar 需要存储高频 Tick 数据（每秒可能数百条），同时支持：
- 实时写入低延迟
- 大规模历史数据查询（用于回测）
- 单进程部署（桌面应用）
- 无需维护独立数据库服务

## 决策

采用 **DuckDB + Parquet 双层架构**：

- **实时写入路径**：GatewayAdapter → TickCache (内存 deque) → 定时落盘 → Parquet 文件（按交易日分片）
- **查询/回测路径**：BacktestEngine → DuckDB (直接查询 Parquet) → Strategy
- **Parquet 文件**：按 `instrument_id/trading_date.parquet` 分片存储，支持时间分区裁剪
- **DuckDB**：作为查询引擎直接读取 Parquet，不额外存储数据，仅作为 SQL 计算层使用

## 替代方案

### TimescaleDB（PostgreSQL 扩展）

**优点：**
- 成熟的时序数据库
- SQL 支持
- 支持实时写入和查询

**缺点：**
- 需要独立数据库服务进程，违反单进程原则
- 部署复杂（需要 Docker 或本地安装）
- 授权复杂（TimescaleDB 有商业许可限制）
- 对桌面应用场景过于重量级

### SQLite

**优点：**
- 无需独立服务
- Python 原生支持

**缺点：**
- Tick 数据量级天花板低（单文件 2TB 限制，实际性能瓶颈更低）
- 并发写入性能不足
- 不适合高频 Tick 场景

### 自研存储引擎

**优点：**
- 完全定制

**缺点：**
- 开发成本高
- 需要实现索引、压缩、查询优化等复杂功能
- 维护成本高

## 后果

### 正面影响

- 单进程部署，无数据库服务依赖
- Parquet 列式存储，压缩率高，节省磁盘空间
- DuckDB 向量化查询性能优秀
- 按交易日分片，天然支持时间分区裁剪
- 回测引擎可直接查询历史数据，无需额外转换

### 负面影响

- 需要实现 TickCache 内存缓冲和定时落盘逻辑
- 实时查询需要合并内存缓存 + Parquet 历史数据
- Parquet 文件不支持随机写入，只能追加

### 缓解措施

- 实现内存缓存与 Parquet 的透明合并查询接口
- 使用内存 deque 作为 TickCache，确保写入低延迟
- 定时落盘间隔可配置（默认 5 秒）

## 参考资料

- [`docs/core/data_protocol.md`](../core/data_protocol.md) - Tick 数据对象定义
- [`docs/engineering/engineering_baseline.md`](../engineering/engineering_baseline.md) - 存储层技术决策
