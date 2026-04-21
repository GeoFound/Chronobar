"""Unit tests for UI Bridge."""

import pytest

from core.ui_bridge import BridgeError, BridgeErrorCode, BridgeResponse, UiBridge


def test_bridge_response_success():
    """Test bridge response success format."""
    response = BridgeResponse.success(data={"key": "value"}, trace_id="test-trace")

    assert response.ok is True
    assert response.data == {"key": "value"}
    assert response.error is None
    assert response.trace_id == "test-trace"

    result = response.to_dict()
    assert result["ok"] is True
    assert result["data"] == {"key": "value"}
    assert "error" not in result
    assert result["trace_id"] == "test-trace"


def test_bridge_response_error():
    """Test bridge response error format."""
    response = BridgeResponse.failure(
        code="TEST_ERROR",
        message="Test error message",
        trace_id="test-trace",
    )

    assert response.ok is False
    assert response.data is None
    assert response.error == {"code": "TEST_ERROR", "message": "Test error message"}
    assert response.trace_id == "test-trace"

    result = response.to_dict()
    assert result["ok"] is False
    assert result["error"] == {"code": "TEST_ERROR", "message": "Test error message"}
    assert "data" not in result
    assert result["trace_id"] == "test-trace"


def test_bridge_response_empty_trace_id():
    """Test bridge response with empty trace ID."""
    response = BridgeResponse.success(data={"key": "value"})

    assert response.trace_id is None

    result = response.to_dict()
    assert result["trace_id"] == ""


def test_ui_bridge_creation():
    """Test UI Bridge can be created."""
    bridge = UiBridge()
    assert bridge is not None
    assert bridge._started is False


def test_ui_bridge_start():
    """Test UI Bridge start."""
    bridge = UiBridge()
    bridge.start()

    assert bridge._started is True

    # Starting again should be idempotent
    bridge.start()
    assert bridge._started is True


def test_ui_bridge_stop():
    """Test UI Bridge stop."""
    bridge = UiBridge()
    bridge.start()
    bridge.stop()

    assert bridge._started is False

    # Stopping again should be idempotent
    bridge.stop()
    assert bridge._started is False


def test_ui_bridge_query_not_started():
    """Test UI Bridge query when not started."""
    bridge = UiBridge()

    with pytest.raises(BridgeError, match="UI Bridge is not started"):
        bridge.query("system.get_status")


def test_ui_bridge_query_system_get_status():
    """Test UI Bridge system.get_status query."""
    bridge = UiBridge()
    bridge.start()

    response = bridge.query("system.get_status")

    assert response.ok is True
    assert response.data is not None
    assert "status" in response.data
    assert response.data["status"] == "running"
    assert "version" in response.data
    assert "started_at" in response.data


def test_ui_bridge_query_not_implemented():
    """Test UI Bridge query for unimplemented method."""
    bridge = UiBridge()
    bridge.start()

    response = bridge.query("unknown.method")

    assert response.ok is False
    assert response.error is not None
    assert response.error["code"] == BridgeErrorCode.BRIDGE_NOT_IMPLEMENTED.value
    assert "not implemented" in response.error["message"]


def test_bridge_error_code_enum():
    """Test bridge error code enum values."""
    # General errors
    assert BridgeErrorCode.BRIDGE_VALIDATION_ERROR.value == "BRIDGE_VALIDATION_ERROR"
    assert BridgeErrorCode.BRIDGE_TIMEOUT.value == "BRIDGE_TIMEOUT"
    assert BridgeErrorCode.BRIDGE_PERMISSION_DENIED.value == "BRIDGE_PERMISSION_DENIED"
    assert BridgeErrorCode.BRIDGE_NOT_IMPLEMENTED.value == "BRIDGE_NOT_IMPLEMENTED"
    assert BridgeErrorCode.BRIDGE_INTERNAL_ERROR.value == "BRIDGE_INTERNAL_ERROR"

    # Query errors
    assert BridgeErrorCode.WORKSPACE_NOT_FOUND.value == "WORKSPACE_NOT_FOUND"
    assert BridgeErrorCode.INSTRUMENT_NOT_FOUND.value == "INSTRUMENT_NOT_FOUND"
    assert BridgeErrorCode.CHART_SNAPSHOT_NOT_FOUND.value == "CHART_SNAPSHOT_NOT_FOUND"
    assert BridgeErrorCode.PLUGIN_NOT_FOUND.value == "PLUGIN_NOT_FOUND"
    assert BridgeErrorCode.QUERY_INVALID_PARAMS.value == "QUERY_INVALID_PARAMS"

    # Command errors
    assert BridgeErrorCode.COMMAND_INVALID_PARAMS.value == "COMMAND_INVALID_PARAMS"
    assert BridgeErrorCode.COMMAND_EXECUTION_FAILED.value == "COMMAND_EXECUTION_FAILED"
    assert BridgeErrorCode.COMMAND_NOT_ALLOWED.value == "COMMAND_NOT_ALLOWED"
    assert BridgeErrorCode.WORKSPACE_SAVE_FAILED.value == "WORKSPACE_SAVE_FAILED"
    assert BridgeErrorCode.PLUGIN_LOAD_FAILED.value == "PLUGIN_LOAD_FAILED"
    assert BridgeErrorCode.PLUGIN_UNLOAD_FAILED.value == "PLUGIN_UNLOAD_FAILED"
    assert BridgeErrorCode.INVALID_COMMAND.value == "INVALID_COMMAND"
    assert BridgeErrorCode.INVALID_INTERVAL.value == "INVALID_INTERVAL"
    assert BridgeErrorCode.REPLAY_NOT_READY.value == "REPLAY_NOT_READY"

    # Subscription errors
    assert BridgeErrorCode.SUBSCRIPTION_INVALID_PARAMS.value == "SUBSCRIPTION_INVALID_PARAMS"
    assert BridgeErrorCode.SUBSCRIPTION_LIMIT_EXCEEDED.value == "SUBSCRIPTION_LIMIT_EXCEEDED"
    assert BridgeErrorCode.SUBSCRIPTION_FAILED.value == "SUBSCRIPTION_FAILED"


def test_bridge_response_serialization():
    """Test bridge response can be serialized to JSON."""
    response = BridgeResponse.success(data={"key": "value"}, trace_id="test-trace")
    result = response.to_dict()

    # Verify all values are JSON-serializable
    import json

    json_str = json.dumps(result)
    assert json_str is not None

    # Verify it can be deserialized
    deserialized = json.loads(json_str)
    assert deserialized["ok"] is True
    assert deserialized["data"] == {"key": "value"}
