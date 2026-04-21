"""Technical indicators implementation for Chronobar platform."""

import logging
from collections import deque
from typing import Any

from core.exceptions import ChronobarError
from core.models import Bar

logger = logging.getLogger(__name__)


class IndicatorError(ChronobarError):
    """Exception raised for indicator errors."""

    pass


class MovingAverage:
    """Simple moving average indicator."""

    def __init__(self, period: int):
        """Initialize moving average.

        Args:
            period: Period for moving average
        """
        if period <= 0:
            raise IndicatorError(f"Period must be positive, got {period}")

        self._period = period
        self._values: deque[float] = deque(maxlen=period)
        self._current_value: float | None = None

    def on_bar(self, bar: Bar) -> float | None:
        """Update indicator with new bar.

        Args:
            bar: Bar to update with

        Returns:
            Current MA value if enough data, None otherwise
        """
        self._values.append(bar.close)

        if len(self._values) < self._period:
            return None

        self._current_value = sum(self._values) / len(self._values)
        return self._current_value

    def value(self) -> float | None:
        """Get current indicator value.

        Returns:
            Current MA value or None if not enough data
        """
        return self._current_value

    def reset(self) -> None:
        """Reset indicator state."""
        self._values.clear()
        self._current_value = None


class IndicatorManager:
    """Manages multiple indicators."""

    def __init__(self) -> None:
        """Initialize indicator manager."""
        self._indicators: dict[str, Any] = {}

    def add_indicator(self, name: str, indicator: Any) -> None:
        """Add an indicator.

        Args:
            name: Indicator name
            indicator: Indicator instance
        """
        self._indicators[name] = indicator

    def on_bar(self, bar: Bar) -> dict[str, float | None]:
        """Update all indicators with new bar.

        Args:
            bar: Bar to update with

        Returns:
            Dictionary of indicator values
        """
        results = {}
        for name, indicator in self._indicators.items():
            if hasattr(indicator, "on_bar"):
                results[name] = indicator.on_bar(bar)
        return results

    def get_values(self) -> dict[str, float | None]:
        """Get current indicator values.

        Returns:
            Dictionary of current indicator values
        """
        results = {}
        for name, indicator in self._indicators.items():
            if hasattr(indicator, "value"):
                results[name] = indicator.value()
        return results

    def reset(self) -> None:
        """Reset all indicators."""
        for indicator in self._indicators.values():
            if hasattr(indicator, "reset"):
                indicator.reset()
