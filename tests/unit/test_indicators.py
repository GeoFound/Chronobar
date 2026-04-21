"""Unit tests for technical indicators."""

from datetime import date, datetime

import pytest

from core.enums import Interval, SessionType
from core.indicators import IndicatorError, IndicatorManager, MovingAverage
from core.models import Bar


def test_moving_average_creation():
    """Test moving average can be created."""
    ma = MovingAverage(10)
    assert ma._period == 10


def test_moving_average_invalid_period():
    """Test moving average with invalid period."""
    with pytest.raises(IndicatorError):
        MovingAverage(0)
    with pytest.raises(IndicatorError):
        MovingAverage(-5)


def test_moving_average_insufficient_data():
    """Test moving average with insufficient data."""
    ma = MovingAverage(10)

    bar = Bar(
        gateway_name="gateway.ctp_main",
        exchange="SHFE",
        symbol="rb",
        instrument_id="rb2509",
        interval=Interval.M1,
        datetime=datetime(2025, 1, 15, 9, 30, 0),
        calendar_date=date(2025, 1, 15),
        trading_date=date(2025, 1, 15),
        session_type=SessionType.MORNING,
        session_id="",
        segment_seq=0,
        open=3500.0,
        high=3505.0,
        low=3495.0,
        close=3502.0,
        volume=100,
        turnover=350200.0,
        open_interest=10000,
    )

    for _ in range(5):
        result = ma.on_bar(bar)
        assert result is None

    assert ma.value() is None


def test_moving_average_sufficient_data():
    """Test moving average with sufficient data."""
    ma = MovingAverage(3)

    bars = [
        Bar(
            gateway_name="gateway.ctp_main",
            exchange="SHFE",
            symbol="rb",
            instrument_id="rb2509",
            interval=Interval.M1,
            datetime=datetime(2025, 1, 15, 9, 30, i),
            calendar_date=date(2025, 1, 15),
            trading_date=date(2025, 1, 15),
            session_type=SessionType.MORNING,
            session_id="",
            segment_seq=0,
            open=3500.0 + i,
            high=3500.0 + i,
            low=3500.0 + i,
            close=3500.0 + i,
            volume=100,
            turnover=350000.0,
            open_interest=10000,
        )
        for i in range(5)
    ]

    for i, bar in enumerate(bars):
        result = ma.on_bar(bar)
        if i < 2:
            assert result is None
        else:
            assert result is not None

    # After 5 bars with values 3500, 3501, 3502, 3503, 3504
    # MA(3) of last 3: (3502 + 3503 + 3504) / 3 = 3503.0
    assert ma.value() == pytest.approx(3503.0)


def test_moving_average_reset():
    """Test moving average reset."""
    ma = MovingAverage(3)

    bar = Bar(
        gateway_name="gateway.ctp_main",
        exchange="SHFE",
        symbol="rb",
        instrument_id="rb2509",
        interval=Interval.M1,
        datetime=datetime(2025, 1, 15, 9, 30, 0),
        calendar_date=date(2025, 1, 15),
        trading_date=date(2025, 1, 15),
        session_type=SessionType.MORNING,
        session_id="",
        segment_seq=0,
        open=3500.0,
        high=3505.0,
        low=3495.0,
        close=3502.0,
        volume=100,
        turnover=350200.0,
        open_interest=10000,
    )

    for _ in range(5):
        ma.on_bar(bar)

    assert ma.value() is not None

    ma.reset()
    assert ma.value() is None


def test_indicator_manager():
    """Test indicator manager."""
    manager = IndicatorManager()
    ma1 = MovingAverage(5)
    ma2 = MovingAverage(10)

    manager.add_indicator("ma5", ma1)
    manager.add_indicator("ma10", ma2)

    bar = Bar(
        gateway_name="gateway.ctp_main",
        exchange="SHFE",
        symbol="rb",
        instrument_id="rb2509",
        interval=Interval.M1,
        datetime=datetime(2025, 1, 15, 9, 30, 0),
        calendar_date=date(2025, 1, 15),
        trading_date=date(2025, 1, 15),
        session_type=SessionType.MORNING,
        session_id="",
        segment_seq=0,
        open=3500.0,
        high=3505.0,
        low=3495.0,
        close=3502.0,
        volume=100,
        turnover=350200.0,
        open_interest=10000,
    )

    for _ in range(12):
        manager.on_bar(bar)

    values = manager.get_values()
    assert "ma5" in values
    assert "ma10" in values
    assert values["ma5"] is not None
    assert values["ma10"] is not None


def test_indicator_manager_reset():
    """Test indicator manager reset."""
    manager = IndicatorManager()
    ma = MovingAverage(5)

    manager.add_indicator("ma5", ma)

    bar = Bar(
        gateway_name="gateway.ctp_main",
        exchange="SHFE",
        symbol="rb",
        instrument_id="rb2509",
        interval=Interval.M1,
        datetime=datetime(2025, 1, 15, 9, 30, 0),
        calendar_date=date(2025, 1, 15),
        trading_date=date(2025, 1, 15),
        session_type=SessionType.MORNING,
        session_id="",
        segment_seq=0,
        open=3500.0,
        high=3505.0,
        low=3495.0,
        close=3502.0,
        volume=100,
        turnover=350200.0,
        open_interest=10000,
    )

    for _ in range(10):
        manager.on_bar(bar)

    assert manager.get_values()["ma5"] is not None

    manager.reset()
    assert manager.get_values()["ma5"] is None
