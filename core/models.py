"""Core data models for Chronobar platform."""

from dataclasses import dataclass, field
from datetime import date, datetime, time
from typing import Any

from core.enums import (
    CancelReasonCode,
    Direction,
    Interval,
    Offset,
    OrderStatus,
    OrderType,
    Regime,
    RiskCheckType,
    Sentiment,
    SessionType,
    SignalType,
    TimeInForce,
)


@dataclass(slots=True)
class Tick:
    """Tick data from market gateway."""

    gateway_name: str
    exchange: str
    symbol: str
    instrument_id: str
    datetime: datetime
    trading_date: date
    calendar_date: date
    session_type: SessionType
    last_price: float
    volume: float
    turnover: float
    open_interest: float
    bid_price_1: float
    ask_price_1: float
    bid_volume_1: float
    ask_volume_1: float
    extra: dict[str, Any] | None = field(default=None)


@dataclass(slots=True)
class Bar:
    """Bar data aggregated from ticks."""

    gateway_name: str
    exchange: str
    symbol: str
    instrument_id: str
    interval: Interval
    datetime: datetime
    calendar_date: date
    trading_date: date
    session_type: SessionType
    session_id: str
    segment_seq: int
    open: float
    high: float
    low: float
    close: float
    volume: float
    turnover: float
    open_interest: float
    extra: dict[str, Any] | None = field(default=None)


@dataclass(slots=True)
class Instrument:
    """Instrument information."""

    exchange: str
    product_id: str
    instrument_id: str
    name: str
    price_tick: float
    contract_multiplier: float
    volume_multiple: float
    session_template_id: str
    timezone: str
    is_active: bool
    listed_date: date | None = None
    expire_date: date | None = None
    extra: dict[str, Any] | None = field(default=None)


@dataclass(slots=True)
class SessionContext:
    """Trading session context."""

    session_id: str
    exchange: str
    product_id: str
    session_type: SessionType
    calendar_date: date
    trading_date: date
    start_time: time
    end_time: time
    is_cross_day: bool
    template_id: str


@dataclass(slots=True)
class Order:
    """Order information."""

    order_id: str
    gateway_name: str
    exchange: str
    symbol: str
    instrument_id: str
    order_type: OrderType
    direction: Direction
    offset: Offset
    price: float
    volume: float
    traded_volume: float
    status: OrderStatus
    datetime: datetime
    trading_date: date
    session_type: SessionType
    gateway_order_id: str | None = None
    error_message: str | None = None
    cancellation_reason: str | None = None
    cancel_reason_code: CancelReasonCode | None = None
    extra: dict[str, Any] | None = None


@dataclass(slots=True)
class Trade:
    """Trade information."""

    trade_id: str
    order_id: str
    gateway_name: str
    exchange: str
    symbol: str
    instrument_id: str
    direction: Direction
    offset: Offset
    price: float
    volume: float
    datetime: datetime
    trading_date: date
    session_type: SessionType
    gateway_trade_id: str | None = None
    commission: float | None = None
    extra: dict[str, Any] | None = None


@dataclass(slots=True)
class Position:
    """Position information."""

    gateway_name: str
    exchange: str
    symbol: str
    instrument_id: str
    direction: Direction
    volume: float
    available_volume: float
    avg_price: float
    open_price: float
    unrealized_pnl: float
    realized_pnl: float
    margin: float
    datetime: datetime
    trading_date: date
    extra: dict[str, Any] | None = None


@dataclass(slots=True)
class Account:
    """Account information."""

    gateway_name: str
    account_id: str
    balance: float
    available: float
    margin: float
    frozen_margin: float
    commission: float
    position_profit: float
    close_profit: float
    datetime: datetime
    trading_date: date
    extra: dict[str, Any] | None = None


@dataclass(slots=True)
class OrderRequest:
    """Order request."""

    gateway_name: str
    exchange: str
    symbol: str
    instrument_id: str
    order_type: OrderType
    direction: Direction
    offset: Offset
    price: float
    volume: float
    time_in_force: TimeInForce | None = None
    stop_price: float | None = None
    reference: str | None = None
    extra: dict[str, Any] | None = None


@dataclass(slots=True)
class CancelRequest:
    """Cancel order request."""

    gateway_name: str
    order_id: str
    gateway_order_id: str | None = None
    reference: str | None = None
    extra: dict[str, Any] | None = None


@dataclass(slots=True)
class RiskCheckResult:
    """Risk check result."""

    passed: bool
    check_type: RiskCheckType
    block_reason: str | None = None
    block_code: str | None = None
    check_time: datetime = field(default_factory=datetime.now)
    context: dict[str, Any] | None = None


@dataclass(slots=True)
class AISignal:
    """AI-generated signal."""

    signal_id: str
    signal_type: SignalType
    source: str
    confidence: float
    timestamp: datetime
    instrument_id: str | None = None
    value: float | None = None
    label: str | None = None
    metadata: dict[str, Any] | None = None


@dataclass(slots=True)
class SentimentScore:
    """Sentiment analysis score."""

    instrument_id: str
    source: str
    sentiment: Sentiment
    score: float
    confidence: float
    timestamp: datetime
    keywords: list[str] | None = None


@dataclass(slots=True)
class RegimeLabel:
    """Market regime label."""

    instrument_id: str | None
    regime: Regime
    confidence: float
    duration: int
    timestamp: datetime
    metadata: dict[str, Any] | None = None
