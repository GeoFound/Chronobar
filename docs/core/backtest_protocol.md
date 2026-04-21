# 中国期货专用平台回测协议 v1.0

## 1. 文档定位

本文档定义回测引擎的接口、数据回放、撮合模拟、性能评估和报告生成。
回测引擎保证策略在回测、仿真、实盘模式下使用同一套接口和逻辑。

## 2. 回测目标

1. 让策略在历史数据上验证逻辑，评估性能。
2. 保证回测、仿真、实盘使用同一套策略接口。
3. 提供准确的撮合模拟和滑点模型。
4. 生成详细的回测报告和性能指标。
5. 支持参数优化和多策略对比。

## 3. 回测模式分类

### 3.1 历史回放模式 (replay)

- **用途**：历史数据回放，验证策略逻辑
- **数据源**：历史 tick/bar 数据文件
- **撮合**：基于历史数据模拟撮合
- **时间**：按历史时间推进
- **输出**：回测报告、性能指标

### 3.2 仿真交易模式 (sim)

- **用途**：实时仿真交易，验证策略在实时环境下的表现
- **数据源**：实时行情数据
- **撮合**：模拟撮合引擎
- **时间**：实时时间
- **输出**：仿真报告、实时监控

### 3.3 实盘交易模式 (live)

- **用途**：真实交易
- **数据源**：实时行情数据
- **撮合**：真实交易所撮合
- **时间**：实时时间
- **输出**：实盘报告、实时监控

## 4. 回测引擎接口

### 4.1 BacktestEngine 接口

```python
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime, date
from enum import Enum

class BacktestMode(Enum):
    REPLAY = "replay"
    SIM = "sim"
    LIVE = "live"

class HistoricalDataFormat(Enum):
    PARQUET = "parquet"
    CSV = "csv"
    DATABASE = "database"

@dataclass(slots=True)
class BacktestConfig:
    start_date: date
    end_date: date
    initial_capital: float
    commission_rate: float
    slippage: float
    mode: BacktestMode  # BacktestMode.REPLAY, BacktestMode.SIM, BacktestMode.LIVE
    data_source: str
    data_format: HistoricalDataFormat = HistoricalDataFormat.PARQUET  # 默认使用 Parquet
    strategy_id: str
    parameters: dict

@dataclass(slots=True)
class BacktestResult:
    strategy_id: str
    start_date: date
    end_date: date
    total_trades: int
    winning_trades: int
    losing_trades: int
    win_rate: float
    total_pnl: float
    max_drawdown: float
    sharpe_ratio: float
    trade_details: list[dict]
    equity_curve: list[dict]
    metrics: dict

class BacktestEngine(ABC):
    @abstractmethod
    def load_data(self, config: BacktestConfig, progress_callback: Callable[[float], None] | None = None) -> None:
        """加载历史数据

        Parquet 数据加载策略：
        - 按交易日分片加载：instrument_id/trading_date.parquet
        - 支持懒加载：仅在需要时加载特定交易日数据
        - 并发读取：最多 4 个并发 Parquet 文件读取任务
        - 内存上限：单次加载不超过 1GB 内存
        - 进度回调：progress_callback(0.0-1.0) 报告加载进度
        """
        ...

    @abstractmethod
    def run(self, config: BacktestConfig) -> BacktestResult:
        """执行回测"""
        ...

    @abstractmethod
    def get_result(self) -> BacktestResult:
        """获取回测结果"""
        ...

    @abstractmethod
    def export_report(self, path: str) -> None:
        """导出回测报告"""
        ...
```

### 4.2 OrderMatcher 接口

```python
class OrderMatcher(ABC):
    @abstractmethod
    def match_order(self, order: Order, tick: Tick) -> list[Trade]:
        """撮合订单"""
        ...

    @abstractmethod
    def apply_slippage(self, price: float, order: Order) -> float:
        """应用滑点"""
        ...

    @abstractmethod
    def calculate_commission(self, trade: Trade) -> float:
        """计算手续费"""
        ...
```

## 5. 撮合模拟

### 5.1 限价单撮合

限价单撮合规则：
- 如果订单价格 <= 卖一价，立即成交
- 如果订单价格 >= 买一价，立即成交
- 否则挂单等待
- 成交价格取订单价格和对手价的较差价

### 5.2 市价单撮合

市价单撮合规则：
- 买入单以卖一价成交
- 卖出单以买一价成交
- 如果对手盘不足，部分成交
- 应用滑点模型

### 5.3 滑点模型

滑点计算方式：
- 固定滑点：订单价格 ± 固定值
- 百分比滑点：订单价格 × (1 ± 百分比)
- 波动率滑点：基于市场波动率动态调整

```python
def apply_slippage(self, price: float, order: Order) -> float:
    if order.direction == "long":
        return price * (1 + self.slippage)
    else:
        return price * (1 - self.slippage)
```

### 5.4 手续费计算

手续费计算方式：
- 按成交金额比例：成交金额 × 手续费率
- 按手数固定：成交手数 × 每手手续费
- 按成交额阶梯：分段累进计算

```python
def calculate_commission(self, trade: Trade) -> float:
    return trade.price * trade.volume * self.commission_rate
```

## 6. 回测流程

### 6.1 初始化阶段

1. 加载历史数据（tick/bar）
2. 初始化账户资金
3. 初始化持仓
4. 初始化策略实例
5. 订阅所需数据

### 6.2 回测执行阶段

1. 按时间顺序读取历史数据
2. 推进时间到下一个数据点
3. 触发策略回调（on_tick/on_bar）
4. 策略调用 submit_order 提交订单
5. 执行风控检查
6. 执行撮合模拟
7. 更新持仓和账户
8. 记录交易和资金曲线
9. 重复直到数据结束

### 6.3 结算阶段

1. 平仓所有持仓（按最后价格）
2. 计算最终盈亏
3. 计算性能指标
4. 生成回测报告
5. 导出结果

## 7. 性能指标

### 7.1 基础指标

- **总交易次数** (total_trades)：总成交笔数
- **盈利次数** (winning_trades)：盈利交易笔数
- **亏损次数** (losing_trades)：亏损交易笔数
- **胜率** (win_rate)：盈利次数 / 总交易次数
- **总盈亏** (total_pnl)：累计盈亏
- **平均盈亏** (avg_pnl)：总盈亏 / 总交易次数
- **最大盈利** (max_profit)：单笔最大盈利
- **最大亏损** (max_loss)：单笔最大亏损

### 7.2 风险指标

- **最大回撤** (max_drawdown)：资金曲线最大回撤幅度
- **回撤持续期** (drawdown_duration)：最大回撤持续天数
- **夏普比率** (sharpe_ratio)：(年化收益 - 无风险利率) / 年化波动率
- **收益波动率** (volatility)：收益标准差
- **卡尔玛比率** (calmar_ratio)：年化收益 / 最大回撤

### 7.3 效率指标

- **盈亏比** (profit_loss_ratio)：平均盈利 / 平均亏损
- **日均交易次数** (avg_trades_per_day)：总交易次数 / 交易日数
- **资金利用率** (capital_usage)：平均占用资金 / 初始资金
- **交易频率** (trade_frequency)：单位时间交易次数

## 8. 回测报告

### 8.1 报告内容

回测报告包含以下内容：

1. **概要信息**
   - 策略名称
   - 回测时间范围
   - 初始资金
   - 最终资金
   - 总收益率

2. **性能指标**
   - 所有基础指标
   - 所有风险指标
   - 所有效率指标

3. **交易明细**
   - 每笔交易的详细信息
   - 开仓时间、平仓时间
   - 开仓价格、平仓价格
   - 手续费、滑点、盈亏

4. **资金曲线**
   - 按时间序列的资金变化
   - 按时间序列的持仓变化
   - 按时间序列的回撤变化

5. **图表**
   - 资金曲线图
   - 回撤曲线图
   - 持仓分布图
   - 盈亏分布图

### 8.2 报告格式

支持多种报告格式：
- HTML 报告（可交互）
- JSON 报告（程序化处理）
- CSV 报告（Excel 分析）
- PDF 报告（打印归档）

## 9. 参数优化

### 9.1 参数空间定义

在策略 schema 中定义参数空间：

```python
def schema(self) -> dict:
    return {
        "parameters": {
            "fast_period": {
                "type": "int",
                "min": 5,
                "max": 20,
                "default": 10
            },
            "slow_period": {
                "type": "int",
                "min": 20,
                "max": 60,
                "default": 30
            },
            "volume": {
                "type": "int",
                "min": 1,
                "max": 10,
                "default": 3
            }
        }
    }
```

### 9.2 优化方法

支持多种优化方法：
- **网格搜索** (grid_search)：遍历所有参数组合
- **随机搜索** (random_search)：随机采样参数组合
- **贝叶斯优化** (bayesian_optimization)：基于概率模型优化
- **遗传算法** (genetic_algorithm)：进化算法优化

### 9.3 优化指标

可优化的指标：
- 总收益率
- 夏普比率
- 卡尔玛比率
- 最大回撤（最小化）
- 胜率
- 自定义指标

## 10. 多策略对比

### 10.1 对比维度

支持多策略对比：
- 不同参数组合的同一策略
- 不同策略的同一参数
- 不同时间段的同一策略

### 10.2 对比报告

对比报告包含：
- 各策略的性能指标对比
- 各策略的资金曲线对比
- 各策略的回撤对比
- 各策略的交易频率对比
- 综合评分和排名

## 11. 回测一致性保证

### 11.1 接口一致性

回测、仿真、实盘使用相同的策略接口：
- 相同的生命周期方法
- 相同的 Host API
- 相同的事件回调
- 相同的权限模型

### 11.2 数据一致性

回测使用标准数据协议：
- 使用相同的 Tick、Bar 对象
- 使用相同的 Order、Trade、Position、Account 对象
- 使用相同的事件协议

### 11.3 风控一致性

回测执行相同的风控检查：
- 使用相同的风控检查接口
- 使用相同的风控规则配置
- 记录相同的风控事件

### 11.4 时间一致性

回测按历史时间推进：
- 时间戳使用历史时间
- 交易时段使用历史时段
- 节假日使用历史节假日

## 12. Python 参考实现

```python
from dataclasses import dataclass
from datetime import datetime, date
from typing import Any
from abc import ABC, abstractmethod
from enum import Enum

class BacktestMode(str, Enum):
    REPLAY = "replay"
    SIM = "sim"
    LIVE = "live"

class HistoricalDataFormat(str, Enum):
    PARQUET = "parquet"
    CSV = "csv"
    DATABASE = "database"

@dataclass(slots=True)
class BacktestConfig:
    start_date: date
    end_date: date
    initial_capital: float
    commission_rate: float
    slippage: float
    mode: BacktestMode
    data_source: str
    data_format: HistoricalDataFormat = HistoricalDataFormat.PARQUET
    strategy_id: str
    parameters: dict[str, Any]

@dataclass(slots=True)
class BacktestResult:
    strategy_id: str
    start_date: date
    end_date: date
    total_trades: int
    winning_trades: int
    losing_trades: int
    win_rate: float
    total_pnl: float
    max_drawdown: float
    sharpe_ratio: float
    trade_details: list[dict[str, Any]]
    equity_curve: list[dict[str, Any]]
    metrics: dict[str, Any]

class BacktestEngine:
    def __init__(self):
        self.config: BacktestConfig | None = None
        self.data: list[Tick | Bar] = []
        self.strategy: BaseStrategy | None = None
        self.account: Account | None = None
        self.positions: dict[str, Position] = {}
        self.orders: dict[str, Order] = {}
        self.trades: list[Trade] = []
        self.equity_curve: list[dict[str, Any]] = []
    
    def load_data(self, config: BacktestConfig) -> None:
        # 从数据源加载历史数据
        pass
    
    def run(self, config: BacktestConfig) -> BacktestResult:
        self.config = config
        self.load_data(config)
        
        # 初始化账户
        self.account = Account(
            gateway_name="backtest",
            account_id="backtest_account",
            balance=config.initial_capital,
            available=config.initial_capital,
            margin=0,
            frozen_margin=0,
            commission=0,
            position_profit=0,
            close_profit=0,
            datetime=datetime.now(),
            trading_date=config.start_date
        )
        
        # 初始化策略
        self.strategy = load_strategy(config.strategy_id)
        self.strategy.on_init(StrategyContext(...))
        
        # 执行回测
        for data_point in self.data:
            self._process_data_point(data_point)
        
        # 计算结果
        return self._calculate_result()
    
    def _process_data_point(self, data_point: Tick | Bar) -> None:
        # 推进时间
        # 触发策略回调
        # 撮合订单
        # 更新持仓和账户
        # 记录资金曲线
        pass
    
    def _calculate_result(self) -> BacktestResult:
        # 计算性能指标
        pass
```

## 13. 最低测试要求

- 回测引擎基础功能测试
- 撮合模拟准确性测试
- 滑点模型测试
- 手续费计算测试
- 性能指标计算测试
- 回测报告生成测试
- 参数优化功能测试
- 多策略对比测试
- 回测与实盘接口一致性测试
- 回测结果可重复性测试
