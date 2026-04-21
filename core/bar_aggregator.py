"""Bar aggregator implementation for Chronobar platform."""

import logging
from collections import deque
from datetime import datetime, time, timedelta
from typing import Any

from core.enums import Interval, SessionType
from core.exceptions import ChronobarError
from core.models import Bar, Tick


logger = logging.getLogger(__name__)


class BarAggregatorError(ChronobarError):
    """Exception raised for bar aggregator errors."""
    pass


class BarAggregator:
    """Aggregates ticks into bars."""

    def __init__(self, interval: Interval):
        """Initialize bar aggregator.

        Args:
            interval: Bar interval (e.g., Interval.M1 for 1-minute bars)
        """
        self._interval = interval
        self._bars: dict[str, deque[Bar]] = {}
        self._pending_ticks: dict[str, deque[Tick]] = {}

    def on_tick(self, tick: Tick) -> Bar | None:
        """Process a tick and potentially produce a new bar.

        Args:
            tick: Tick to process

        Returns:
            New bar if the interval is complete, None otherwise
        """
        key = tick.instrument_id

        # Initialize pending ticks for this instrument if needed
        if key not in self._pending_ticks:
            self._pending_ticks[key] = deque()

        # Add tick to pending
        self._pending_ticks[key].append(tick)

        # Calculate the bar datetime based on interval
        bar_datetime = self._calculate_bar_datetime(tick.datetime, self._interval)

        # Check if we have a current bar for this instrument
        if key not in self._bars or not self._bars[key]:
            # Create new bar
            bar = self._create_bar_from_ticks(tick, bar_datetime)
            self._bars[key] = deque([bar])
            return None

        # Check if the tick belongs to the same bar
        current_bar = self._bars[key][-1]
        if current_bar.datetime == bar_datetime:
            # Update existing bar
            self._update_bar(current_bar, tick)
            return None

        # Tick belongs to new bar, finalize current bar
        completed_bar = self._finalize_bar(current_bar, self._pending_ticks[key])

        # Create new bar
        new_bar = self._create_bar_from_ticks(tick, bar_datetime)
        self._bars[key].append(new_bar)

        # Keep only the last bar
        if len(self._bars[key]) > 1:
            self._bars[key].popleft()

        # Clear pending ticks for the completed bar
        self._pending_ticks[key] = deque([tick])

        return completed_bar

    def _calculate_bar_datetime(self, tick_dt: datetime, interval: Interval) -> datetime:
        """Calculate bar datetime from tick datetime.

        Args:
            tick_dt: Tick datetime
            interval: Bar interval

        Returns:
            Bar datetime (truncated to interval boundary)
        """
        if interval == Interval.M1:
            return tick_dt.replace(second=0, microsecond=0)
        elif interval == Interval.M5:
            minute = (tick_dt.minute // 5) * 5
            return tick_dt.replace(minute=minute, second=0, microsecond=0)
        elif interval == Interval.M15:
            minute = (tick_dt.minute // 15) * 15
            return tick_dt.replace(minute=minute, second=0, microsecond=0)
        elif interval == Interval.M30:
            minute = (tick_dt.minute // 30) * 30
            return tick_dt.replace(minute=minute, second=0, microsecond=0)
        elif interval == Interval.H1:
            return tick_dt.replace(minute=0, second=0, microsecond=0)
        elif interval == Interval.D1:
            return tick_dt.replace(hour=0, minute=0, second=0, microsecond=0)
        else:
            raise BarAggregatorError(f"Unsupported interval: {interval}")

    def _create_bar_from_ticks(self, tick: Tick, bar_datetime: datetime) -> Bar:
        """Create a new bar from a tick.

        Args:
            tick: Tick to create bar from
            bar_datetime: Bar datetime

        Returns:
            New bar
        """
        return Bar(
            gateway_name=tick.gateway_name,
            exchange=tick.exchange,
            symbol=tick.symbol,
            instrument_id=tick.instrument_id,
            interval=self._interval,
            datetime=bar_datetime,
            calendar_date=tick.calendar_date,
            trading_date=tick.trading_date,
            session_type=tick.session_type,
            session_id="",  # Will be filled by session context
            segment_seq=0,  # Will be filled by session context
            open=tick.last_price,
            high=tick.last_price,
            low=tick.last_price,
            close=tick.last_price,
            volume=tick.volume,
            turnover=tick.turnover,
            open_interest=tick.open_interest,
        )

    def _update_bar(self, bar: Bar, tick: Tick) -> None:
        """Update bar with tick data.

        Args:
            bar: Bar to update
            tick: Tick to update with
        """
        bar.high = max(bar.high, tick.last_price)
        bar.low = min(bar.low, tick.last_price)
        bar.close = tick.last_price
        bar.volume += tick.volume
        bar.turnover += tick.turnover
        bar.open_interest = tick.open_interest

    def _finalize_bar(self, bar: Bar, ticks: deque[Tick]) -> Bar:
        """Finalize a bar.

        Args:
            bar: Bar to finalize
            ticks: Pending ticks for this bar

        Returns:
            Finalized bar
        """
        # Calculate average open_interest from ticks
        if ticks:
            total_oi = sum(t.open_interest for t in ticks)
            bar.open_interest = total_oi / len(ticks)

        return bar

    def get_current_bar(self, instrument_id: str) -> Bar | None:
        """Get current (in-progress) bar for an instrument.

        Args:
            instrument_id: Instrument ID

        Returns:
            Current bar or None if no bars exist
        """
        if instrument_id not in self._bars or not self._bars[instrument_id]:
            return None
        return self._bars[instrument_id][-1]

    def reset(self, instrument_id: str | None = None) -> None:
        """Reset aggregator state.

        Args:
            instrument_id: Instrument ID to reset, or None to reset all
        """
        if instrument_id is None:
            self._bars.clear()
            self._pending_ticks.clear()
        else:
            self._bars.pop(instrument_id, None)
            self._pending_ticks.pop(instrument_id, None)
