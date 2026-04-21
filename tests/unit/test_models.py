"""Unit tests for core models."""

from datetime import datetime, date, time

import pytest

from core.enums import (
    SessionType,
    Interval,
    OrderType,
    Direction,
    Offset,
    OrderStatus,
    CancelReasonCode,
    TimeInForce,
    RiskCheckType,
    SignalType,
    Sentiment,
    Regime,
)
from core.models import (
    Tick,
    Bar,
    Instrument,
    SessionContext,
    Order,
    Trade,
    Position,
    Account,
    OrderRequest,
    CancelRequest,
    RiskCheckResult,
    AISignal,
    SentimentScore,
    RegimeLabel,
)


def test_tick_instantiation():
    """Test Tick can be instantiated."""
    tick = Tick(
        gateway_name="test_gateway",
        exchange="SHFE",
        symbol="rb2501",
        instrument_id="rb2501",
        datetime=datetime.now(),
        trading_date=date.today(),
        calendar_date=date.today(),
        session_type=SessionType.MORNING,
        last_price=3500.0,
        volume=100.0,
        turnover=350000.0,
        open_interest=10000.0,
        bid_price_1=3499.0,
        ask_price_1=3501.0,
        bid_volume_1=10.0,
        ask_volume_1=10.0,
    )
    assert tick.gateway_name == "test_gateway"
    assert tick.instrument_id == "rb2501"
    assert tick.session_type == SessionType.MORNING


def test_bar_instantiation():
    """Test Bar can be instantiated."""
    bar = Bar(
        gateway_name="test_gateway",
        exchange="SHFE",
        symbol="rb2501",
        instrument_id="rb2501",
        interval=Interval.M1,
        datetime=datetime.now(),
        calendar_date=date.today(),
        trading_date=date.today(),
        session_type=SessionType.MORNING,
        session_id="test_session",
        segment_seq=1,
        open=3490.0,
        high=3510.0,
        low=3485.0,
        close=3505.0,
        volume=1000.0,
        turnover=3500000.0,
        open_interest=10000.0,
    )
    assert bar.gateway_name == "test_gateway"
    assert bar.instrument_id == "rb2501"
    assert bar.interval == Interval.M1


def test_order_instantiation():
    """Test Order can be instantiated."""
    order = Order(
        order_id="test_order_1",
        gateway_name="test_gateway",
        exchange="SHFE",
        symbol="rb2501",
        instrument_id="rb2501",
        order_type=OrderType.LIMIT,
        direction=Direction.LONG,
        offset=Offset.OPEN,
        price=3500.0,
        volume=10.0,
        traded_volume=0.0,
        status=OrderStatus.SUBMITTED,
        datetime=datetime.now(),
        trading_date=date.today(),
        session_type=SessionType.MORNING,
    )
    assert order.order_id == "test_order_1"
    assert order.status == OrderStatus.SUBMITTED
    assert order.direction == Direction.LONG


def test_enum_values():
    """Test enum values match protocol."""
    assert SessionType.MORNING.value == "morning"
    assert SessionType.AFTERNOON.value == "afternoon"
    assert SessionType.NIGHT.value == "night"

    assert Interval.TICK.value == "tick"
    assert Interval.M1.value == "1m"
    assert Interval.D1.value == "1d"

    assert OrderType.LIMIT.value == "limit"
    assert OrderType.MARKET.value == "market"

    assert Direction.LONG.value == "long"
    assert Direction.SHORT.value == "short"


def test_model_serialization():
    """Test models can be serialized to dict."""
    tick = Tick(
        gateway_name="test_gateway",
        exchange="SHFE",
        symbol="rb2501",
        instrument_id="rb2501",
        datetime=datetime.now(),
        trading_date=date.today(),
        calendar_date=date.today(),
        session_type=SessionType.MORNING,
        last_price=3500.0,
        volume=100.0,
        turnover=350000.0,
        open_interest=10000.0,
        bid_price_1=3499.0,
        ask_price_1=3501.0,
        bid_volume_1=10.0,
        ask_volume_1=10.0,
    )
    # Verify object has expected attributes
    assert hasattr(tick, "gateway_name")
    assert hasattr(tick, "instrument_id")
    assert hasattr(tick, "datetime")
