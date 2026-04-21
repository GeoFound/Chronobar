"""Unit tests for bar aggregator."""

from datetime import date, datetime

import pytest

from core.bar_aggregator import BarAggregator, BarAggregatorError
from core.enums import Interval, SessionType
from core.models import Tick


def test_bar_aggregator_creation():
    """Test bar aggregator can be created."""
    aggregator = BarAggregator(Interval.M1)
    assert aggregator._interval == Interval.M1


def test_bar_aggregator_on_tick_first_tick():
    """Test bar aggregator with first tick."""
    aggregator = BarAggregator(Interval.M1)

    tick = Tick(
        gateway_name="gateway.ctp_main",
        exchange="SHFE",
        symbol="rb",
        instrument_id="rb2509",
        datetime=datetime(2025, 1, 15, 9, 30, 1),
        trading_date=date(2025, 1, 15),
        calendar_date=date(2025, 1, 15),
        session_type=SessionType.MORNING,
        last_price=3500.0,
        volume=100,
        turnover=350000.0,
        open_interest=10000,
        bid_price_1=3499.0,
        ask_price_1=3501.0,
        bid_volume_1=50,
        ask_volume_1=50,
    )

    bar = aggregator.on_tick(tick)
    assert bar is None  # First tick doesn't produce a bar

    current_bar = aggregator.get_current_bar("rb2509")
    assert current_bar is not None
    assert current_bar.open == 3500.0
    assert current_bar.high == 3500.0
    assert current_bar.low == 3500.0
    assert current_bar.close == 3500.0
    assert current_bar.volume == 100


def test_bar_aggregator_same_minute():
    """Test bar aggregator with ticks in same minute."""
    aggregator = BarAggregator(Interval.M1)

    tick1 = Tick(
        gateway_name="gateway.ctp_main",
        exchange="SHFE",
        symbol="rb",
        instrument_id="rb2509",
        datetime=datetime(2025, 1, 15, 9, 30, 1),
        trading_date=date(2025, 1, 15),
        calendar_date=date(2025, 1, 15),
        session_type=SessionType.MORNING,
        last_price=3500.0,
        volume=100,
        turnover=350000.0,
        open_interest=10000,
        bid_price_1=3499.0,
        ask_price_1=3501.0,
        bid_volume_1=50,
        ask_volume_1=50,
    )

    tick2 = Tick(
        gateway_name="gateway.ctp_main",
        exchange="SHFE",
        symbol="rb",
        instrument_id="rb2509",
        datetime=datetime(2025, 1, 15, 9, 30, 30),
        trading_date=date(2025, 1, 15),
        calendar_date=date(2025, 1, 15),
        session_type=SessionType.MORNING,
        last_price=3505.0,
        volume=50,
        turnover=175250.0,
        open_interest=10050,
        bid_price_1=3504.0,
        ask_price_1=3506.0,
        bid_volume_1=30,
        ask_volume_1=30,
    )

    aggregator.on_tick(tick1)
    bar = aggregator.on_tick(tick2)

    assert bar is None  # Still same minute, no bar produced

    current_bar = aggregator.get_current_bar("rb2509")
    assert current_bar is not None
    assert current_bar.open == 3500.0
    assert current_bar.high == 3505.0
    assert current_bar.low == 3500.0
    assert current_bar.close == 3505.0
    assert current_bar.volume == 150


def test_bar_aggregator_new_minute():
    """Test bar aggregator with ticks in different minutes."""
    aggregator = BarAggregator(Interval.M1)

    tick1 = Tick(
        gateway_name="gateway.ctp_main",
        exchange="SHFE",
        symbol="rb",
        instrument_id="rb2509",
        datetime=datetime(2025, 1, 15, 9, 30, 1),
        trading_date=date(2025, 1, 15),
        calendar_date=date(2025, 1, 15),
        session_type=SessionType.MORNING,
        last_price=3500.0,
        volume=100,
        turnover=350000.0,
        open_interest=10000,
        bid_price_1=3499.0,
        ask_price_1=3501.0,
        bid_volume_1=50,
        ask_volume_1=50,
    )

    tick2 = Tick(
        gateway_name="gateway.ctp_main",
        exchange="SHFE",
        symbol="rb",
        instrument_id="rb2509",
        datetime=datetime(2025, 1, 15, 9, 31, 1),
        trading_date=date(2025, 1, 15),
        calendar_date=date(2025, 1, 15),
        session_type=SessionType.MORNING,
        last_price=3505.0,
        volume=50,
        turnover=175250.0,
        open_interest=10050,
        bid_price_1=3504.0,
        ask_price_1=3506.0,
        bid_volume_1=30,
        ask_volume_1=30,
    )

    aggregator.on_tick(tick1)
    bar = aggregator.on_tick(tick2)

    assert bar is not None  # New minute, bar produced
    assert bar.open == 3500.0
    assert bar.high == 3500.0
    assert bar.low == 3500.0
    assert bar.close == 3500.0
    assert bar.volume == 100

    current_bar = aggregator.get_current_bar("rb2509")
    assert current_bar is not None
    assert current_bar.open == 3505.0


def test_bar_aggregator_5_minute_interval():
    """Test bar aggregator with 5-minute interval."""
    aggregator = BarAggregator(Interval.M5)

    tick1 = Tick(
        gateway_name="gateway.ctp_main",
        exchange="SHFE",
        symbol="rb",
        instrument_id="rb2509",
        datetime=datetime(2025, 1, 15, 9, 30, 1),
        trading_date=date(2025, 1, 15),
        calendar_date=date(2025, 1, 15),
        session_type=SessionType.MORNING,
        last_price=3500.0,
        volume=100,
        turnover=350000.0,
        open_interest=10000,
        bid_price_1=3499.0,
        ask_price_1=3501.0,
        bid_volume_1=50,
        ask_volume_1=50,
    )

    tick2 = Tick(
        gateway_name="gateway.ctp_main",
        exchange="SHFE",
        symbol="rb",
        instrument_id="rb2509",
        datetime=datetime(2025, 1, 15, 9, 34, 1),
        trading_date=date(2025, 1, 15),
        calendar_date=date(2025, 1, 15),
        session_type=SessionType.MORNING,
        last_price=3505.0,
        volume=50,
        turnover=175250.0,
        open_interest=10050,
        bid_price_1=3504.0,
        ask_price_1=3506.0,
        bid_volume_1=30,
        ask_volume_1=30,
    )

    aggregator.on_tick(tick1)
    bar = aggregator.on_tick(tick2)

    assert bar is None  # Still same 5-minute period

    tick3 = Tick(
        gateway_name="gateway.ctp_main",
        exchange="SHFE",
        symbol="rb",
        instrument_id="rb2509",
        datetime=datetime(2025, 1, 15, 9, 35, 1),
        trading_date=date(2025, 1, 15),
        calendar_date=date(2025, 1, 15),
        session_type=SessionType.MORNING,
        last_price=3510.0,
        volume=50,
        turnover=175500.0,
        open_interest=10100,
        bid_price_1=3509.0,
        ask_price_1=3511.0,
        bid_volume_1=30,
        ask_volume_1=30,
    )

    bar = aggregator.on_tick(tick3)
    assert bar is not None  # New 5-minute period


def test_bar_aggregator_reset():
    """Test bar aggregator reset."""
    aggregator = BarAggregator(Interval.M1)

    tick = Tick(
        gateway_name="gateway.ctp_main",
        exchange="SHFE",
        symbol="rb",
        instrument_id="rb2509",
        datetime=datetime(2025, 1, 15, 9, 30, 1),
        trading_date=date(2025, 1, 15),
        calendar_date=date(2025, 1, 15),
        session_type=SessionType.MORNING,
        last_price=3500.0,
        volume=100,
        turnover=350000.0,
        open_interest=10000,
        bid_price_1=3499.0,
        ask_price_1=3501.0,
        bid_volume_1=50,
        ask_volume_1=50,
    )

    aggregator.on_tick(tick)
    assert aggregator.get_current_bar("rb2509") is not None

    aggregator.reset("rb2509")
    assert aggregator.get_current_bar("rb2509") is None


def test_bar_aggregator_unsupported_interval():
    """Test bar aggregator with unsupported interval."""
    aggregator = BarAggregator(Interval.TICK)

    tick = Tick(
        gateway_name="gateway.ctp_main",
        exchange="SHFE",
        symbol="rb",
        instrument_id="rb2509",
        datetime=datetime(2025, 1, 15, 9, 30, 1),
        trading_date=date(2025, 1, 15),
        calendar_date=date(2025, 1, 15),
        session_type=SessionType.MORNING,
        last_price=3500.0,
        volume=100,
        turnover=350000.0,
        open_interest=10000,
        bid_price_1=3499.0,
        ask_price_1=3501.0,
        bid_volume_1=50,
        ask_volume_1=50,
    )

    with pytest.raises(BarAggregatorError):
        aggregator.on_tick(tick)
