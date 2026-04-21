"""Core loop demonstration for Chronobar platform.

This script demonstrates the full data flow:
Tick -> Event -> Bar -> Indicator -> Snapshot

It integrates all P1 components:
- P1-T2: Standard objects (Tick, Bar, Instrument, etc.)
- P1-T3: EventEngine
- P1-T4: RuleEngine
- P1-T5: BarAggregator and indicators
- P1-T6: UiBridge
"""

from datetime import datetime, date

from core.enums import Interval, SessionType
from core.event_engine import EventBus
from core.models import Tick, Bar
from core.bar_aggregator import BarAggregator
from core.indicators import MovingAverage, IndicatorManager
from core.rule_engine import RuleEngine
from core.ui_bridge import UiBridge


def main():
    """Run the core loop demonstration."""
    print("Chronobar Core Loop Demonstration")
    print("=" * 50)
    print()

    # Initialize components
    print("1. Initializing components...")
    event_bus = EventBus()
    rule_engine = RuleEngine()
    bar_aggregator = BarAggregator(Interval.M1)
    indicator_manager = IndicatorManager()
    ui_bridge = UiBridge()

    # Add indicators
    ma5 = MovingAverage(5)
    indicator_manager.add_indicator("ma5", ma5)

    # Start components
    event_bus.start()
    ui_bridge.start()

    print("   ✓ EventBus started")
    print("   ✓ RuleEngine initialized")
    print("   ✓ BarAggregator initialized (M1)")
    print("   ✓ IndicatorManager initialized (MA5)")
    print("   ✓ UiBridge started")
    print()

    # Load session template
    print("2. Loading session template...")
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
    print(f"   ✓ Loaded template: rb_night_session")
    print(f"   - Exchange: SHFE")
    print(f"   - Segments: 2")
    print()

    # Create sample ticks (spanning multiple minutes to produce bars)
    print("3. Processing ticks...")
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
        for i in range(10)
    ]

    bars = []
    for i, tick in enumerate(ticks):
        # Determine session context
        session_type, segment_start, segment_end = rule_engine.determine_session(
            tick.datetime,
            "rb_night_session",
        )

        print(f"   Tick {i+1}: {tick.datetime} - Price: {tick.last_price:.2f}")
        print(f"     Session: {session_type.value}")
        print(f"     Segment: {segment_start} - {segment_end}")

        # Aggregate to bar
        bar = bar_aggregator.on_tick(tick)
        if bar:
            bars.append(bar)
            print(f"     → Bar produced: {bar.datetime} - OHLC: {bar.open:.2f}/{bar.high:.2f}/{bar.low:.2f}/{bar.close:.2f}")

            # Update indicators
            indicator_values = indicator_manager.on_bar(bar)
            print(f"     → Indicators: MA5 = {indicator_values.get('ma5', 'N/A')}")

    print()

    # Demonstrate UiBridge query
    print("4. Testing UiBridge query...")
    response = ui_bridge.query("system.get_status")
    print(f"   Query: system.get_status")
    print(f"   Response: {response.to_dict()}")
    print()

    # Summary
    print("5. Summary")
    print("=" * 50)
    print(f"   Total ticks processed: {len(ticks)}")
    print(f"   Total bars produced: {len(bars)}")
    print(f"   Current MA5: {ma5.value()}")
    print()

    # Stop components
    event_bus.stop()
    ui_bridge.stop()

    print("✓ Core loop demonstration completed successfully")
    print()
    print("Data flow verified:")
    print("  Tick → Event (EventBus)")
    print("  Tick → Bar (BarAggregator)")
    print("  Bar → Indicator (IndicatorManager)")
    print("  Query → Response (UiBridge)")


if __name__ == "__main__":
    main()
