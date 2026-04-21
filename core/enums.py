"""Core enumerations for Chronobar platform."""

from enum import Enum


class SessionType(str, Enum):
    """Trading session types."""
    MORNING = "morning"
    AFTERNOON = "afternoon"
    NIGHT = "night"


class Interval(str, Enum):
    """Bar interval types."""
    TICK = "tick"
    S1 = "1s"
    M1 = "1m"
    M3 = "3m"
    M5 = "5m"
    M15 = "15m"
    M30 = "30m"
    H1 = "60m"
    D1 = "1d"


class OrderType(str, Enum):
    """Order types."""
    LIMIT = "limit"
    MARKET = "market"
    STOP = "stop"
    STOP_LIMIT = "stop_limit"
    ICEBERG = "iceberg"
    CONDITIONAL = "conditional"


class Direction(str, Enum):
    """Order direction."""
    LONG = "long"
    SHORT = "short"


class Offset(str, Enum):
    """Order offset."""
    OPEN = "open"
    CLOSE = "close"
    CLOSE_TODAY = "close_today"
    CLOSE_YESTERDAY = "close_yesterday"


class OrderStatus(str, Enum):
    """Order status."""
    SUBMITTING = "submitting"
    SUBMITTED = "submitted"
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    PARTIAL_FILLED = "partial_filled"
    FILLED = "filled"
    CANCELLED = "cancelled"
    CANCELLING = "cancelling"


class CancelReasonCode(str, Enum):
    """Order cancellation reason codes."""
    TIMEOUT = "timeout"
    REJECTED_BY_USER = "rejected_by_user"
    REJECTED_BY_RISK = "rejected_by_risk"
    REJECTED_BY_EXCHANGE = "rejected_by_exchange"
    CONNECTION_LOST = "connection_lost"
    OTHER = "other"


class TimeInForce(str, Enum):
    """Order time in force."""
    GTC = "GTC"
    IOC = "IOC"
    FOK = "FOK"
    GTD = "GTD"


class RiskCheckType(str, Enum):
    """Risk check types."""
    POSITION_LIMIT = "position_limit"
    ORDER_LIMIT = "order_limit"
    MARGIN_CHECK = "margin_check"
    PRICE_BAND = "price_band"
    FROZEN_CHECK = "frozen_check"
    CUSTOM = "custom"


class SignalType(str, Enum):
    """AI signal types."""
    SENTIMENT = "sentiment"
    REGIME = "regime"
    FACTOR = "factor"
    ANOMALY = "anomaly"


class Sentiment(str, Enum):
    """Sentiment classification."""
    POSITIVE = "positive"
    NEGATIVE = "negative"
    NEUTRAL = "neutral"


class Regime(str, Enum):
    """Market regime classification."""
    TREND = "trend"
    RANGE = "range"
    HIGH_VOLATILITY = "high_volatility"
    LOW_VOLATILITY = "low_volatility"
    TRANSITION = "transition"
