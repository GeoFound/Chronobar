"""Integration tests for EventBus with other P1 components.

These tests verify EventBus integration with:
- BarAggregator (event-driven bar aggregation)
- RuleEngine (event-driven session determination)
- UiBridge (event-driven query responses)
"""

from datetime import date, datetime

import pytest

from core.bar_aggregator import BarAggregator
from core.enums import Interval, SessionType
from core.event_engine import EventBus
from core.models import Tick
from core.rule_engine import RuleEngine


@pytest.fixture
def event_bus():
    """Initialize and start event bus."""
    bus = EventBus()
    bus.start()
    yield bus
    bus.stop()


def test_event_bus_with_bar_aggregator_integration(event_bus):
    """Test EventBus integration with BarAggregator for event-driven bar aggregation."""
    bar_aggregator = BarAggregator(Interval.M1)
    bars_produced = []

    def on_bar_event(event):
        bars_produced.append(event.payload)

    # Subscribe to bar events
    event_bus.subscribe("bar", on_bar_event)

    # Create and process ticks
    ticks = [
        Tick(
            gateway_name="gateway.ctp_main",
            exchange="SHFE",
            symbol="rb",
            instrument_id="rb2509",
            datetime=datetime(2025, 1, 15, 21, i, 0),
            trading_date=date(2025, 1, 16),
            calendar_date=date(2025, 1, 15),
            session_type=SessionType.NIGHT,
            last_price=3500.0 + i * 10,
            volume=100 + i * 10,
            turnover=(3500.0 + i * 10) * (100 + i * 10),
            open_interest=10000 + i * 10,
            bid_price_1=3499.0 + i * 10,
            ask_price_1=3501.0 + i * 10,
            bid_volume_1=50 + i * 5,
            ask_volume_1=50 + i * 5,
        )
        for i in range(5)
    ]

    # Aggregate bars and publish as events
    for tick in ticks:
        bar = bar_aggregator.on_tick(tick)
        if bar:
            from core.events import EventEnvelope

            bar_event = EventEnvelope(
                event_type="bar",
                event_id=f"bar_{bar.datetime}",
                source="bar_aggregator",
                ts=bar.datetime,
                instrument_id=bar.instrument_id,
                payload=bar,
            )
            event_bus.put(bar_event)

    # Allow event processing
    import time

    time.sleep(0.1)

    # Verify bars were received via EventBus
    assert len(bars_produced) == 4  # 5 ticks produce 4 bars (first tick starts new minute)
    assert bars_produced[0].instrument_id == "rb2509"


def test_event_bus_with_rule_engine_integration(event_bus):
    """Test EventBus integration with RuleEngine for event-driven session determination."""
    rule_engine = RuleEngine()
    session_events = []

    def on_session_event(event):
        session_events.append(event.payload)

    # Subscribe to session events
    event_bus.subscribe("session", on_session_event)

    # Load session template
    config = {
        "session_templates": {
            "rb_night_session": {
                "exchange": "SHFE",
                "trading_date_rule": "night_belongs_next_trading_date",
                "segments": [
                    {"type": "night", "start": "21:00", "end": "23:00"},
                    {"type": "night", "start": "00:00", "end": "02:30"},
                ],
            }
        }
    }
    rule_engine.load_session_template("rb_night_session", config)

    # Create tick and determine session
    tick = Tick(
        gateway_name="gateway.ctp_main",
        exchange="SHFE",
        symbol="rb",
        instrument_id="rb2509",
        datetime=datetime(2025, 1, 15, 21, 30, 0),
        trading_date=date(2025, 1, 16),
        calendar_date=date(2025, 1, 15),
        session_type=SessionType.NIGHT,
        last_price=3500.0,
        volume=100,
        turnover=350000.0,
        open_interest=10000,
        bid_price_1=3499.0,
        ask_price_1=3501.0,
        bid_volume_1=50,
        ask_volume_1=50,
    )

    session_type, segment_start, segment_end = rule_engine.determine_session(
        tick.datetime, "rb_night_session"
    )

    # Publish session event
    from core.events import EventEnvelope

    session_event = EventEnvelope(
        event_type="session",
        event_id=f"session_{tick.datetime}",
        source="rule_engine",
        ts=tick.datetime,
        instrument_id=tick.instrument_id,
        payload={
            "session_type": session_type,
            "segment_start": segment_start,
            "segment_end": segment_end,
        },
    )
    event_bus.put(session_event)

    # Allow event processing
    import time

    time.sleep(0.1)

    # Verify session event was received
    assert len(session_events) == 1
    assert session_events[0]["session_type"] == SessionType.NIGHT


def test_event_bus_multiple_subscribers_integration(event_bus):
    """Test EventBus with multiple subscribers for the same event type."""
    subscriber1_events = []
    subscriber2_events = []

    def subscriber1(event):
        subscriber1_events.append(event)

    def subscriber2(event):
        subscriber2_events.append(event)

    # Multiple subscribers to same event type
    event_bus.subscribe("tick", subscriber1)
    event_bus.subscribe("tick", subscriber2)

    # Publish tick events
    from core.events import EventEnvelope

    for i in range(3):
        tick_event = EventEnvelope(
            event_type="tick",
            event_id=f"tick_{i}",
            source="test",
            ts=datetime(2025, 1, 15, 21, i, 0),
            instrument_id="rb2509",
            payload={"price": 3500.0 + i * 10},
        )
        event_bus.put(tick_event)

    # Allow event processing
    import time

    time.sleep(0.1)

    # Verify both subscribers received all events
    assert len(subscriber1_events) == 3
    assert len(subscriber2_events) == 3
    assert subscriber1_events[0].event_id == "tick_0"
    assert subscriber2_events[0].event_id == "tick_0"


def test_event_bus_instrument_specific_subscription_integration(event_bus):
    """Test EventBus instrument-specific subscription in integration context."""
    rb_events = []
    cu_events = []

    def on_rb_tick(event):
        rb_events.append(event)

    def on_cu_tick(event):
        cu_events.append(event)

    # Subscribe to specific instruments
    event_bus.subscribe_instrument("tick", "rb2509", on_rb_tick)
    event_bus.subscribe_instrument("tick", "cu2509", on_cu_tick)

    # Publish events for different instruments
    from core.events import EventEnvelope

    rb_event = EventEnvelope(
        event_type="tick",
        event_id="rb_tick",
        source="test",
        ts=datetime(2025, 1, 15, 21, 0, 0),
        instrument_id="rb2509",
        payload={"price": 3500.0},
    )
    cu_event = EventEnvelope(
        event_type="tick",
        event_id="cu_tick",
        source="test",
        ts=datetime(2025, 1, 15, 21, 0, 0),
        instrument_id="cu2509",
        payload={"price": 50000.0},
    )

    event_bus.put(rb_event)
    event_bus.put(cu_event)

    # Allow event processing
    import time

    time.sleep(0.1)

    # Verify instrument-specific filtering
    assert len(rb_events) == 1
    assert len(cu_events) == 1
    assert rb_events[0].instrument_id == "rb2509"
    assert cu_events[0].instrument_id == "cu2509"
