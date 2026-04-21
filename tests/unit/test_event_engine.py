"""Unit tests for event engine."""

import time
from datetime import datetime

import pytest

from core.event_engine import EventBus, EventBusError
from core.events import EventEnvelope


def test_event_envelope_creation():
    """Test EventEnvelope can be created."""
    event = EventEnvelope(
        event_id="test_event_1",
        event_type="TICK",
        source="gateway.ctp_main",
        ts=datetime.now(),
        instrument_id="rb2501",
        trace_id="trace_123",
    )
    assert event.event_id == "test_event_1"
    assert event.event_type == "TICK"
    assert event.source == "gateway.ctp_main"
    assert event.instrument_id == "rb2501"
    assert event.trace_id == "trace_123"
    assert event.replayable is True
    assert event.version == "1.2"


def test_event_bus_start_stop():
    """Test EventBus can be started and stopped."""
    bus = EventBus()
    assert not bus._running

    bus.start()
    assert bus._running
    assert bus._thread is not None

    bus.stop()
    assert not bus._running


def test_event_bus_subscribe_and_publish():
    """Test event subscription and publishing."""
    bus = EventBus()
    bus.start()

    received_events: list[EventEnvelope] = []

    def handler(event: EventEnvelope) -> None:
        received_events.append(event)

    bus.subscribe("TICK", handler)

    event = EventEnvelope(
        event_id="test_event_1",
        event_type="TICK",
        source="gateway.ctp_main",
        ts=datetime.now(),
    )
    bus.put(event)

    # Wait for event to be processed
    time.sleep(0.1)

    assert len(received_events) == 1
    assert received_events[0].event_id == "test_event_1"

    bus.stop()


def test_event_bus_instrument_subscription():
    """Test instrument-specific subscription."""
    bus = EventBus()
    bus.start()

    received_events: list[EventEnvelope] = []

    def handler(event: EventEnvelope) -> None:
        received_events.append(event)

    bus.subscribe_instrument("TICK", "rb2501", handler)

    # Event for rb2501 should be received
    event1 = EventEnvelope(
        event_id="test_event_1",
        event_type="TICK",
        source="gateway.ctp_main",
        ts=datetime.now(),
        instrument_id="rb2501",
    )
    bus.put(event1)

    # Event for rb2505 should not be received
    event2 = EventEnvelope(
        event_id="test_event_2",
        event_type="TICK",
        source="gateway.ctp_main",
        ts=datetime.now(),
        instrument_id="rb2505",
    )
    bus.put(event2)

    time.sleep(0.1)

    assert len(received_events) == 1
    assert received_events[0].instrument_id == "rb2501"

    bus.stop()


def test_event_bus_handler_exception_isolation():
    """Test that handler exceptions don't interrupt event processing."""
    bus = EventBus()
    bus.start()

    received_events: list[EventEnvelope] = []

    def failing_handler(event: EventEnvelope) -> None:
        raise RuntimeError("Handler failed")

    def working_handler(event: EventEnvelope) -> None:
        received_events.append(event)

    bus.subscribe("TICK", failing_handler)
    bus.subscribe("TICK", working_handler)

    event = EventEnvelope(
        event_id="test_event_1",
        event_type="TICK",
        source="gateway.ctp_main",
        ts=datetime.now(),
    )
    bus.put(event)

    time.sleep(0.1)

    # Working handler should still receive event despite failing handler
    assert len(received_events) == 1

    bus.stop()


def test_event_bus_queue_full_error():
    """Test that queue full raises EventBusError."""
    bus = EventBus(max_queue_size=2)
    bus.start()

    # Fill queue
    for i in range(2):
        event = EventEnvelope(
            event_id=f"test_event_{i}",
            event_type="TICK",
            source="gateway.ctp_main",
            ts=datetime.now(),
        )
        bus.put(event)

    # Third event should raise error
    event = EventEnvelope(
        event_id="test_event_3",
        event_type="TICK",
        source="gateway.ctp_main",
        ts=datetime.now(),
    )

    with pytest.raises(EventBusError):
        bus.put(event)

    bus.stop()


def test_trace_id_preservation():
    """Test that trace_id is preserved through event processing."""
    bus = EventBus()
    bus.start()

    received_trace_ids: list[str] = []

    def handler(event: EventEnvelope) -> None:
        received_trace_ids.append(event.trace_id)

    bus.subscribe("TICK", handler)

    event = EventEnvelope(
        event_id="test_event_1",
        event_type="TICK",
        source="gateway.ctp_main",
        ts=datetime.now(),
        trace_id="trace_12345",
    )
    bus.put(event)

    time.sleep(0.1)

    assert len(received_trace_ids) == 1
    assert received_trace_ids[0] == "trace_12345"

    bus.stop()
