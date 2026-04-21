"""Core exceptions for Chronobar platform."""


class ChronobarError(Exception):
    """Base exception for Chronobar platform."""

    pass


class ProtocolError(ChronobarError):
    """Exception raised for protocol violations."""

    pass


class ValidationError(ChronobarError):
    """Exception raised for data validation failures."""

    pass


class GatewayError(ChronobarError):
    """Exception raised for gateway-related errors."""

    pass


class RiskError(ChronobarError):
    """Exception raised for risk control violations."""

    pass


class PluginError(ChronobarError):
    """Exception raised for plugin-related errors."""

    pass


class UIBridgeError(ChronobarError):
    """Exception raised for UI bridge errors."""

    pass
