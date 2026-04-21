"""UI Bridge implementation for Chronobar platform."""

import logging
from datetime import datetime
from enum import Enum
from typing import Any

from core.exceptions import ChronobarError

logger = logging.getLogger(__name__)


class BridgeError(ChronobarError):
    """Exception raised for bridge errors."""

    pass


class BridgeErrorCode(Enum):
    """Standard error codes for UI Bridge."""

    # General errors
    BRIDGE_VALIDATION_ERROR = "BRIDGE_VALIDATION_ERROR"
    BRIDGE_TIMEOUT = "BRIDGE_TIMEOUT"
    BRIDGE_PERMISSION_DENIED = "BRIDGE_PERMISSION_DENIED"
    BRIDGE_NOT_IMPLEMENTED = "BRIDGE_NOT_IMPLEMENTED"
    BRIDGE_INTERNAL_ERROR = "BRIDGE_INTERNAL_ERROR"

    # Query errors
    WORKSPACE_NOT_FOUND = "WORKSPACE_NOT_FOUND"
    INSTRUMENT_NOT_FOUND = "INSTRUMENT_NOT_FOUND"
    CHART_SNAPSHOT_NOT_FOUND = "CHART_SNAPSHOT_NOT_FOUND"
    PLUGIN_NOT_FOUND = "PLUGIN_NOT_FOUND"
    QUERY_INVALID_PARAMS = "QUERY_INVALID_PARAMS"

    # Command errors
    COMMAND_INVALID_PARAMS = "COMMAND_INVALID_PARAMS"
    COMMAND_EXECUTION_FAILED = "COMMAND_EXECUTION_FAILED"
    COMMAND_NOT_ALLOWED = "COMMAND_NOT_ALLOWED"
    WORKSPACE_SAVE_FAILED = "WORKSPACE_SAVE_FAILED"
    PLUGIN_LOAD_FAILED = "PLUGIN_LOAD_FAILED"
    PLUGIN_UNLOAD_FAILED = "PLUGIN_UNLOAD_FAILED"
    INVALID_COMMAND = "INVALID_COMMAND"
    INVALID_INTERVAL = "INVALID_INTERVAL"
    REPLAY_NOT_READY = "REPLAY_NOT_READY"

    # Subscription errors
    SUBSCRIPTION_INVALID_PARAMS = "SUBSCRIPTION_INVALID_PARAMS"
    SUBSCRIPTION_LIMIT_EXCEEDED = "SUBSCRIPTION_LIMIT_EXCEEDED"
    SUBSCRIPTION_FAILED = "SUBSCRIPTION_FAILED"


class BridgeResponse:
    """Standard bridge response format."""

    def __init__(
        self,
        ok: bool,
        data: Any | None = None,
        error: dict[str, str] | None = None,
        trace_id: str | None = None,
    ):
        """Initialize bridge response.

        Args:
            ok: Whether the operation succeeded
            data: Response data (if successful)
            error: Error information (if failed)
            trace_id: Trace ID for request tracking
        """
        self.ok = ok
        self.data = data
        self.error = error
        self.trace_id = trace_id

    def to_dict(self) -> dict[str, Any]:
        """Convert response to dictionary.

        Returns:
            Dictionary representation of response
        """
        result: dict[str, Any] = {
            "ok": self.ok,
            "trace_id": self.trace_id or "",
        }

        if self.ok:
            result["data"] = self.data
        else:
            result["error"] = self.error or {}

        return result

    @classmethod
    def success(cls, data: Any, trace_id: str | None = None) -> "BridgeResponse":
        """Create a successful response.

        Args:
            data: Response data
            trace_id: Trace ID for request tracking

        Returns:
            Successful response
        """
        return cls(ok=True, data=data, trace_id=trace_id)

    @classmethod
    def failure(cls, code: str, message: str, trace_id: str | None = None) -> "BridgeResponse":
        """Create an error response.

        Args:
            code: Error code
            message: Error message
            trace_id: Trace ID for request tracking

        Returns:
            Error response
        """
        return cls(
            ok=False,
            error={"code": code, "message": message},
            trace_id=trace_id,
        )


class UiBridge:
    """UI Bridge for frontend-backend communication."""

    def __init__(self):
        """Initialize UI Bridge."""
        self._started = False

    def start(self) -> None:
        """Start UI Bridge."""
        if self._started:
            return

        self._started = True
        logger.info("UI Bridge started")

    def stop(self) -> None:
        """Stop UI Bridge."""
        if not self._started:
            return

        self._started = False
        logger.info("UI Bridge stopped")

    def query(self, method: str, params: dict[str, Any] | None = None) -> BridgeResponse:
        """Execute a query.

        Args:
            method: Query method name (e.g., "system.get_status")
            params: Query parameters

        Returns:
            Bridge response

        Raises:
            BridgeError: If bridge is not started
        """
        if not self._started:
            raise BridgeError("UI Bridge is not started")

        if method == "system.get_status":
            return self._handle_system_get_status(params)
        else:
            return BridgeResponse.failure(
                code=BridgeErrorCode.BRIDGE_NOT_IMPLEMENTED.value,
                message=f"Query method '{method}' not implemented",
            )

    def _handle_system_get_status(self, params: dict[str, Any] | None) -> BridgeResponse:
        """Handle system.get_status query.

        Args:
            params: Query parameters (unused)

        Returns:
            Bridge response with system status
        """
        status_data = {
            "status": "running",
            "version": "0.1.0",
            "started_at": datetime.now().isoformat(),
        }
        return BridgeResponse.success(data=status_data)
