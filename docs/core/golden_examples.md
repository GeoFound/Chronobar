# 中国期货专用平台黄金样例 v1.2

**基于协议版本：v1.2**

## 1. 文档定位

本文档提供 4 个黄金样例：MA 指标插件、双均线信号插件、仿真策略插件、回放测试用例。
这些样例作为 AI 生成代码的参考模板，确保代码风格和接口使用的一致性。

**重要：** 本文档基于协议版本 v1.2 编写。每次协议 major/minor 升级时，必须同步更新样例代码中的字段定义和接口使用方式。

## 2. 样例 1：MA 指标插件

### 2.1 目录结构

```text
ma_indicator/
  manifest.json
  plugin.py
  README.md
```

### 2.2 manifest.json

```json
{
  "name": "ma_indicator",
  "version": "1.0.0",
  "api_version": "1.2",
  "kind": "indicator",
  "entry": "plugin.py",
  "dependencies": [],
  "permissions": {
    "read_market_data": true,
    "emit_alert": false,
    "write_file": false,
    "read_workspace": false
  },
  "compatibility": {
    "min_core_version": "1.2",
    "max_core_version": "1.x"
  }
}
```

### 2.3 plugin.py

```python
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any
from collections import deque

from chronobar.core.data_protocol import Bar, Tick
from chronobar.core.plugin_protocol import BasePlugin, PluginContext

@dataclass(slots=True)
class MAIndicator(BasePlugin):
    """移动平均线指标插件"""
    
    period: int = 20
    prices: deque = field(default_factory=lambda: deque(maxlen=100))
    
    def manifest(self) -> dict:
        return {
            "name": "ma_indicator",
            "version": "1.0.0",
            "api_version": "1.2",
            "kind": "indicator"
        }
    
    def on_init(self, ctx: PluginContext) -> None:
        """初始化指标参数"""
        config = ctx.get_config("ma_indicator")
        if config:
            self.period = config.get("period", 20)
        ctx.subscribe("BAR", self._on_bar)
    
    def on_start(self, ctx: PluginContext) -> None:
        """启动指标"""
        ctx.log_info(f"MA指标启动，周期={self.period}")
    
    def on_stop(self, ctx: PluginContext) -> None:
        """停止指标"""
        ctx.log_info("MA指标停止")
    
    def _on_bar(self, ctx: PluginContext, event: Any) -> None:
        """处理 Bar 事件"""
        bar: Bar = event.payload
        if bar.instrument_id not in ctx.get_config("watchlist", []):
            return
        
        # 计算移动平均
        self.prices.append(bar.close)
        if len(self.prices) >= self.period:
            ma_value = sum(self.prices) / len(self.prices)
            
            # 输出到图表
            ctx.emit("INDICATOR_UPDATE", {
                "plugin": "ma_indicator",
                "instrument_id": bar.instrument_id,
                "datetime": bar.datetime,
                "value": ma_value,
                "type": "line",
                "color": "#FF6B6B"
            })
    
    def outputs(self) -> dict:
        return {
            "ma_line": {
                "type": "line",
                "description": f"MA{self.period} 移动平均线"
            }
        }
    
    def schema(self) -> dict:
        return {
            "parameters": {
                "period": {
                    "type": "int",
                    "min": 5,
                    "max": 200,
                    "default": 20,
                    "description": "移动平均周期"
                }
            }
        }
```

## 3. 样例 2：双均线信号插件

### 3.1 目录结构

```text
dual_ma_signal/
  manifest.json
  plugin.py
  README.md
```

### 3.2 manifest.json

```json
{
  "name": "dual_ma_signal",
  "version": "1.0.0",
  "api_version": "1.2",
  "kind": "signal",
  "entry": "plugin.py",
  "dependencies": [],
  "permissions": {
    "read_market_data": true,
    "emit_alert": true,
    "write_file": false,
    "read_workspace": false
  },
  "compatibility": {
    "min_core_version": "1.2",
    "max_core_version": "1.x"
  }
}
```

### 3.3 plugin.py

```python
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any
from collections import deque

from chronobar.core.data_protocol import Bar
from chronobar.core.plugin_protocol import BasePlugin, PluginContext

@dataclass(slots=True)
class DualMASignal(BasePlugin):
    """双均线信号插件"""
    
    fast_period: int = 10
    slow_period: int = 30
    fast_prices: deque = field(default_factory=lambda: deque(maxlen=200))
    slow_prices: deque = field(default_factory=lambda: deque(maxlen=200))
    last_signal: str = None
    
    def manifest(self) -> dict:
        return {
            "name": "dual_ma_signal",
            "version": "1.0.0",
            "api_version": "1.2",
            "kind": "signal"
        }
    
    def on_init(self, ctx: PluginContext) -> None:
        """初始化信号参数"""
        config = ctx.get_config("dual_ma_signal")
        if config:
            self.fast_period = config.get("fast_period", 10)
            self.slow_period = config.get("slow_period", 30)
        ctx.subscribe("BAR", self._on_bar)
    
    def on_start(self, ctx: PluginContext) -> None:
        """启动信号"""
        ctx.log_info(f"双均线信号启动，快线={self.fast_period}，慢线={self.slow_period}")
    
    def on_stop(self, ctx: PluginContext) -> None:
        """停止信号"""
        ctx.log_info("双均线信号停止")
    
    def _on_bar(self, ctx: PluginContext, event: Any) -> None:
        """处理 Bar 事件"""
        bar: Bar = event.payload
        if bar.instrument_id not in ctx.get_config("watchlist", []):
            return
        
        # 计算双均线
        self.fast_prices.append(bar.close)
        self.slow_prices.append(bar.close)
        
        if len(self.fast_prices) >= self.fast_period and len(self.slow_prices) >= self.slow_period:
            fast_ma = sum(self.fast_prices) / self.fast_period
            slow_ma = sum(self.slow_prices) / self.slow_period
            
            # 判断信号
            signal = self._detect_signal(fast_ma, slow_ma)
            
            if signal and signal != self.last_signal:
                self.last_signal = signal
                
                # 输出信号
                ctx.emit("SIGNAL_GENERATED", {
                    "plugin": "dual_ma_signal",
                    "instrument_id": bar.instrument_id,
                    "datetime": bar.datetime,
                    "signal": signal,
                    "fast_ma": fast_ma,
                    "slow_ma": slow_ma,
                    "price": bar.close
                })
                
                # 发布告警
                ctx.publish_alert(
                    level="info",
                    title=f"双均线信号：{bar.instrument_id}",
                    content=f"{signal} @ {bar.close}，快线={fast_ma:.2f}，慢线={slow_ma:.2f}"
                )
    
    def _detect_signal(self, fast_ma: float, slow_ma: float) -> str:
        """检测信号"""
        if fast_ma > slow_ma:
            return "BUY"
        elif fast_ma < slow_ma:
            return "SELL"
        return None
    
    def outputs(self) -> dict:
        return {
            "signal": {
                "type": "signal",
                "description": "双均线交易信号"
            },
            "fast_ma": {
                "type": "line",
                "description": f"MA{self.fast_period} 快线"
            },
            "slow_ma": {
                "type": "line",
                "description": f"MA{self.slow_period} 慢线"
            }
        }
    
    def schema(self) -> dict:
        return {
            "parameters": {
                "fast_period": {
                    "type": "int",
                    "min": 5,
                    "max": 50,
                    "default": 10,
                    "description": "快线周期"
                },
                "slow_period": {
                    "type": "int",
                    "min": 20,
                    "max": 200,
                    "default": 30,
                    "description": "慢线周期"
                }
            }
        }
```

## 4. 样例 3：仿真策略插件

### 4.1 目录结构

```text
dual_ma_strategy/
  manifest.json
  strategy.py
  README.md
```

### 4.2 manifest.json

```json
{
  "name": "dual_ma_strategy",
  "version": "1.0.0",
  "api_version": "1.0",
  "kind": "strategy",
  "entry": "strategy.py",
  "dependencies": [],
  "permissions": {
    "read_market_data": true,
    "emit_alert": true,
    "write_file": false,
    "read_workspace": false,
    "submit_order": true,
    "cancel_order": true,
    "read_position": true,
    "read_account": true,
    "read_open_orders": true
  },
  "risk_profile": {
    "max_position_per_instrument": 10,
    "max_orders_per_day": 100,
    "max_loss_per_day": 10000
  },
  "compatibility": {
    "min_core_version": "1.2",
    "max_core_version": "1.x"
  }
}
```

### 4.3 strategy.py

```python
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any
from collections import deque

from chronobar.core.data_protocol import Bar, Order, Trade, Position, Account, OrderRequest
from chronobar.core.strategy_protocol import BaseStrategy, StrategyContext
from chronobar.core.data_protocol import OrderType, Direction, Offset

@dataclass(slots=True)
class DualMAStrategy(BaseStrategy):
    """双均线策略插件"""
    
    fast_period: int = 10
    slow_period: int = 30
    volume: int = 1
    fast_prices: deque = field(default_factory=lambda: deque(maxlen=200))
    slow_prices: deque = field(default_factory=lambda: deque(maxlen=200))
    last_signal: str = None
    current_position: int = 0
    
    def manifest(self) -> dict:
        return {
            "name": "dual_ma_strategy",
            "version": "1.0.0",
            "api_version": "1.0",
            "kind": "strategy"
        }
    
    def on_init(self, ctx: StrategyContext) -> None:
        """初始化策略参数"""
        config = ctx.get_config("dual_ma_strategy")
        if config:
            self.fast_period = config.get("fast_period", 10)
            self.slow_period = config.get("slow_period", 30)
            self.volume = config.get("volume", 1)
        
        # 订阅行情
        instrument_id = config.get("instrument_id")
        if instrument_id:
            ctx.subscribe_bar(instrument_id, "1m")
        
        ctx.log_info(f"双均线策略初始化，快线={self.fast_period}，慢线={self.slow_period}，手数={self.volume}")
    
    def on_start(self, ctx: StrategyContext) -> None:
        """启动策略"""
        ctx.log_info("双均线策略启动")
        
        # 查询当前持仓
        positions = ctx.get_positions()
        for pos in positions:
            if pos.direction == "long":
                self.current_position = pos.volume
            elif pos.direction == "short":
                self.current_position = -pos.volume
    
    def on_stop(self, ctx: StrategyContext) -> None:
        """停止策略"""
        ctx.log_info("双均线策略停止")
        
        # 平仓
        if self.current_position > 0:
            self._close_position(ctx, "short")
        elif self.current_position < 0:
            self._close_position(ctx, "long")
    
    def on_bar(self, ctx: StrategyContext, bar: Bar) -> None:
        """处理 Bar 事件"""
        # 计算双均线
        self.fast_prices.append(bar.close)
        self.slow_prices.append(bar.close)
        
        if len(self.fast_prices) >= self.fast_period and len(self.slow_prices) >= self.slow_period:
            fast_ma = sum(self.fast_prices) / self.fast_period
            slow_ma = sum(self.slow_prices) / self.slow_period
            
            # 判断信号
            signal = self._detect_signal(fast_ma, slow_ma)
            
            if signal and signal != self.last_signal:
                self.last_signal = signal
                self._execute_signal(ctx, signal, bar)
    
    def _detect_signal(self, fast_ma: float, slow_ma: float) -> str:
        """检测信号"""
        if fast_ma > slow_ma:
            return "BUY"
        elif fast_ma < slow_ma:
            return "SELL"
        return None
    
    def _execute_signal(self, ctx: StrategyContext, signal: str, bar: Bar) -> None:
        """执行信号"""
        if signal == "BUY":
            if self.current_position <= 0:
                # 先平空仓
                if self.current_position < 0:
                    self._close_position(ctx, "long")
                # 开多仓
                self._open_position(ctx, "long", bar)
        elif signal == "SELL":
            if self.current_position >= 0:
                # 先平多仓
                if self.current_position > 0:
                    self._close_position(ctx, "short")
                # 开空仓
                self._open_position(ctx, "short", bar)
    
    def _open_position(self, ctx: StrategyContext, direction: str, bar: Bar) -> None:
        """开仓"""
        request = OrderRequest(
            gateway_name="sim",
            exchange=bar.exchange,
            symbol=bar.symbol,
            instrument_id=bar.instrument_id,
            order_type=OrderType.MARKET,
            direction=Direction.LONG if direction == "long" else Direction.SHORT,
            offset=Offset.OPEN,
            price=bar.close,
            volume=self.volume
        )
        
        try:
            order_id = ctx.submit_order(request)
            ctx.log_info(f"开仓提交成功: {direction} {bar.instrument_id} {self.volume}手 @ {bar.close}")
            ctx.publish_alert(
                level="info",
                title=f"开仓: {bar.instrument_id}",
                content=f"{direction} {self.volume}手 @ {bar.close}"
            )
        except Exception as e:
            ctx.log_error(f"开仓失败: {e}")
    
    def _close_position(self, ctx: StrategyContext, direction: str) -> None:
        """平仓"""
        # 获取当前持仓
        positions = ctx.get_positions()
        for pos in positions:
            if pos.direction == direction and pos.volume > 0:
                request = OrderRequest(
                    gateway_name="sim",
                    exchange=pos.exchange,
                    symbol=pos.symbol,
                    instrument_id=pos.instrument_id,
                    order_type=OrderType.MARKET,
                    direction=Direction.SHORT if direction == "long" else Direction.LONG,
                    offset=Offset.CLOSE_TODAY,
                    price=pos.avg_price,
                    volume=pos.volume
                )
                
                try:
                    order_id = ctx.submit_order(request)
                    ctx.log_info(f"平仓提交成功: {direction} {pos.instrument_id} {pos.volume}手")
                    ctx.publish_alert(
                        level="info",
                        title=f"平仓: {pos.instrument_id}",
                        content=f"{direction} {pos.volume}手"
                    )
                except Exception as e:
                    ctx.log_error(f"平仓失败: {e}")
    
    def on_order(self, ctx: StrategyContext, order: Order) -> None:
        """处理订单事件"""
        ctx.log_info(f"订单状态更新: {order.order_id} {order.status}")
    
    def on_trade(self, ctx: StrategyContext, trade: Trade) -> None:
        """处理成交事件"""
        ctx.log_info(f"成交回报: {trade.trade_id} {trade.direction} {trade.volume}手 @ {trade.price}")
        
        # 更新持仓
        if trade.offset == "open":
            if trade.direction == "long":
                self.current_position += trade.volume
            else:
                self.current_position -= trade.volume
        else:
            if trade.direction == "long":
                self.current_position -= trade.volume
            else:
                self.current_position += trade.volume
    
    def on_risk_event(self, ctx: StrategyContext, event: Any) -> None:
        """处理风控事件"""
        ctx.log_warning(f"风控事件: {event.check_type} - {event.block_reason}")
        ctx.publish_alert(
            level="warning",
            title="风控拦截",
            content=f"{event.check_type}: {event.block_reason}"
        )
    
    def outputs(self) -> dict:
        return {
            "signal": {
                "type": "signal",
                "description": "双均线交易信号"
            },
            "position": {
                "type": "number",
                "description": "当前持仓"
            }
        }
    
    def schema(self) -> dict:
        return {
            "parameters": {
                "fast_period": {
                    "type": "int",
                    "min": 5,
                    "max": 50,
                    "default": 10,
                    "description": "快线周期"
                },
                "slow_period": {
                    "type": "int",
                    "min": 20,
                    "max": 200,
                    "default": 30,
                    "description": "慢线周期"
                },
                "volume": {
                    "type": "int",
                    "min": 1,
                    "max": 10,
                    "default": 1,
                    "description": "交易手数"
                },
                "instrument_id": {
                    "type": "string",
                    "description": "交易合约"
                }
            }
        }
```

## 5. 样例 4：回放测试用例

### 5.1 测试文件结构

```text
tests/
  test_replay_dual_ma.py
  test_data/
    rb2501_1m_20240101.parquet
```

### 5.2 test_replay_dual_ma.py

```python
import pytest
from datetime import date, datetime
from pathlib import Path

from chronobar.core.backtest_protocol import BacktestEngine, BacktestConfig, BacktestMode
from chronobar.core.data_protocol import Bar
from chronobar.core.strategy_protocol import DualMAStrategy
from chronobar.core.event_protocol import EventEngine

class TestReplayDualMA:
    """双均线策略回放测试"""
    
    @pytest.fixture
    def backtest_config(self):
        """回测配置"""
        return BacktestConfig(
            start_date=date(2024, 1, 1),
            end_date=date(2024, 1, 31),
            initial_capital=100000.0,
            commission_rate=0.0001,
            slippage=0.0002,
            mode=BacktestMode.REPLAY,
            data_source="test_data/rb2501_1m_20240101.parquet",
            strategy_id="dual_ma_strategy",
            parameters={
                "fast_period": 10,
                "slow_period": 30,
                "volume": 1,
                "instrument_id": "rb2501"
            }
        )
    
    @pytest.fixture
    def backtest_engine(self):
        """回测引擎"""
        event_engine = EventEngine()
        engine = BacktestEngine(event_engine)
        return engine
    
    def test_replay_basic(self, backtest_engine, backtest_config):
        """基础回放测试"""
        # 加载策略
        strategy = DualMAStrategy()
        backtest_engine.load_strategy(strategy)
        
        # 执行回测
        result = backtest_engine.run(backtest_config)
        
        # 验证结果
        assert result is not None
        assert result.total_trades >= 0
        assert result.start_date == backtest_config.start_date
        assert result.end_date == backtest_config.end_date
        assert len(result.equity_curve) > 0
    
    def test_replay_with_signal(self, backtest_engine, backtest_config):
        """带信号的回放测试"""
        # 修改参数以产生更多信号
        backtest_config.parameters["fast_period"] = 5
        backtest_config.parameters["slow_period"] = 20
        
        strategy = DualMAStrategy()
        backtest_engine.load_strategy(strategy)
        
        result = backtest_engine.run(backtest_config)
        
        # 验证产生交易
        assert result.total_trades > 0
        assert len(result.trade_details) > 0
    
    def test_replay_risk_check(self, backtest_engine, backtest_config):
        """风控检查测试"""
        # 设置极端参数触发风控
        backtest_config.parameters["volume"] = 1000  # 超大手数
        
        strategy = DualMAStrategy()
        backtest_engine.load_strategy(strategy)
        
        result = backtest_engine.run(backtest_config)
        
        # 验证风控拦截
        # 预期订单会被风控拦截，交易次数为0
        assert result.total_trades == 0
    
    def test_replay_consistency(self, backtest_engine, backtest_config):
        """回放一致性测试"""
        # 执行两次回放
        strategy1 = DualMAStrategy()
        backtest_engine.load_strategy(strategy1)
        result1 = backtest_engine.run(backtest_config)
        
        strategy2 = DualMAStrategy()
        backtest_engine.load_strategy(strategy2)
        result2 = backtest_engine.run(backtest_config)
        
        # 验证结果一致
        assert result1.total_trades == result2.total_trades
        assert result1.total_pnl == pytest.approx(result2.total_pnl)
        assert result1.max_drawdown == pytest.approx(result2.max_drawdown)
    
    def test_replay_export_report(self, backtest_engine, backtest_config, tmp_path):
        """报告导出测试"""
        strategy = DualMAStrategy()
        backtest_engine.load_strategy(strategy)
        
        result = backtest_engine.run(backtest_config)
        
        # 导出报告
        report_path = tmp_path / "backtest_report.html"
        backtest_engine.export_report(str(report_path))
        
        # 验证文件存在
        assert report_path.exists()
        assert report_path.stat().st_size > 0
    
    def test_replay_metrics_calculation(self, backtest_engine, backtest_config):
        """性能指标计算测试"""
        strategy = DualMAStrategy()
        backtest_engine.load_strategy(strategy)
        
        result = backtest_engine.run(backtest_config)
        
        # 验证指标计算
        if result.total_trades > 0:
            assert 0 <= result.win_rate <= 1
            assert result.sharpe_ratio is not None
            assert result.max_drawdown >= 0
            assert result.winning_trades + result.losing_trades == result.total_trades

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
```

## 6. 样例使用说明

### 6.1 安装插件

```bash
# 复制插件目录到 plugins 目录
cp -r ma_indicator/ plugins/
cp -r dual_ma_signal/ plugins/
cp -r dual_ma_strategy/ plugins/
```

### 6.2 配置插件

在系统配置文件中添加插件配置：

```json
{
  "plugins": {
    "ma_indicator": {
      "enabled": true,
      "period": 20
    },
    "dual_ma_signal": {
      "enabled": true,
      "fast_period": 10,
      "slow_period": 30
    },
    "dual_ma_strategy": {
      "enabled": true,
      "fast_period": 10,
      "slow_period": 30,
      "volume": 1,
      "instrument_id": "rb2501"
    }
  }
}
```

### 6.3 运行回测

```bash
# 运行回放测试
python tests/test_replay_dual_ma.py

# 或使用命令行工具
chronobar backtest --strategy dual_ma_strategy --start 2024-01-01 --end 2024-01-31
```

### 6.4 查看回测报告

回测完成后，查看生成的 HTML 报告：

```bash
# 报告位于 output/backtest_reports/
open output/backtest_reports/dual_ma_strategy_20240101_20240131.html
```

## 7. 扩展建议

### 7.1 添加更多指标

参考 MA 指标插件，可以添加：
- MACD 指标
- RSI 指标
- 布林带指标
- KDJ 指标

### 7.2 添加更多信号

参考双均线信号插件，可以添加：
- 突破信号
- 均值回归信号
- 动量信号
- 波动率信号

### 7.3 添加更多策略

参考双均线策略插件，可以添加：
- 网格策略
- 趋势跟踪策略
- 套利策略
- 做市策略

### 7.4 添加更多测试

参考回放测试用例，可以添加：
- 参数优化测试
- 多策略对比测试
- 风控压力测试
- 性能压力测试
