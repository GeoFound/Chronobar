from __future__ import annotations

import json
from pathlib import Path

from jsonschema import Draft202012Validator

REPO_ROOT = Path(__file__).resolve().parents[1]
UI_BRIDGE_PROTOCOL_PATH = REPO_ROOT / "docs/system/ui_bridge_protocol.md"


def _load_json(relative_path: str) -> dict | list:
    return json.loads((REPO_ROOT / relative_path).read_text(encoding="utf-8"))


def test_research_workspace_sample_maps_to_ui_bridge_protocol() -> None:
    protocol_text = UI_BRIDGE_PROTOCOL_PATH.read_text(encoding="utf-8")
    research_workspace = _load_json("tests/ui_contract/research_workspace.json")

    assert "research.get_workspace" in protocol_text
    assert "research.compare_experiments" in protocol_text
    assert "research.get_publish_records" in protocol_text
    assert "当前研究工作区" in protocol_text
    assert "当前因子表筛选条件" in protocol_text
    assert "当前实验对比集合" in protocol_text
    assert "当前待发布研究候选对象" in protocol_text

    assert research_workspace["ok"] is True
    assert research_workspace["data"]["workspace_id"] == "research.default"
    assert research_workspace["data"]["factor_set_id"] == "intraday_alpha_v1"
    assert research_workspace["data"]["factor_filters"]["status"] == "candidate"
    assert research_workspace["data"]["comparison_set"] == ["exp_001", "exp_002"]
    assert research_workspace["data"]["publish_queue"][0]["status"] == "pending_confirmation"


def test_research_publish_candidate_maps_to_ui_bridge_protocol_and_error_codes() -> None:
    protocol_text = UI_BRIDGE_PROTOCOL_PATH.read_text(encoding="utf-8")
    research_publish_candidate = _load_json("tests/ui_contract/research_publish_candidate.json")
    error_codes = _load_json("tests/ui_contract/error_codes.json")

    assert "research.publish_candidate" in protocol_text
    assert "research.reject_publish_candidate" in protocol_text
    assert "研究候选对象的发布命令必须复用标准确认链路" in protocol_text

    required_ai_change_fields = {
        "candidate_id",
        "kind",
        "status",
        "target",
        "validation",
        "sources",
        "diff_summary",
        "reversible",
        "trace_id",
    }
    assert required_ai_change_fields.issubset(research_publish_candidate.keys())
    assert research_publish_candidate["kind"] == "research_publish"
    assert research_publish_candidate["status"] == "pending_confirmation"
    assert research_publish_candidate["validation"]["ok"] is True
    assert "confirmation_required" in research_publish_candidate["validation"]["checks"]
    assert research_publish_candidate["target"]["publish_target"] == "workspace.default.factor_board"

    assert "QUERY_INVALID_PARAMS" in error_codes
    assert "COMMAND_INVALID_PARAMS" in error_codes
    assert "AI_CONFIRMATION_REQUIRED" in error_codes


def test_research_subscription_sample_maps_to_ui_bridge_protocol_and_error_codes() -> None:
    protocol_text = UI_BRIDGE_PROTOCOL_PATH.read_text(encoding="utf-8")
    research_subscription_event = _load_json("tests/ui_contract/research_subscription_event.json")
    error_codes = _load_json("tests/ui_contract/error_codes.json")

    assert "research 发布状态订阅" in protocol_text
    assert "RESEARCH_PUBLISH_STATE_CHANGED" in protocol_text

    required_event_fields = {
        "event_id",
        "event_type",
        "source",
        "ts",
        "instrument_id",
        "session_id",
        "payload",
        "trace_id",
        "replayable",
        "version",
    }
    assert required_event_fields.issubset(research_subscription_event.keys())
    assert research_subscription_event["event_type"] == "RESEARCH_PUBLISH_STATE_CHANGED"
    assert research_subscription_event["payload"]["current_status"] == "pending_confirmation"
    assert research_subscription_event["payload"]["publish_target"] == "workspace.default.factor_board"

    assert "SUBSCRIPTION_INVALID_PARAMS" in error_codes
    assert "SUBSCRIPTION_FAILED" in error_codes


def test_research_ui_contract_samples_validate_against_schemas() -> None:
    schema_pairs = [
        ("tests/ui_contract/research_workspace.json", "tests/ui_contract/research_workspace.schema.json"),
        ("tests/ui_contract/research_publish_candidate.json", "tests/ui_contract/research_publish_candidate.schema.json"),
        ("tests/ui_contract/research_subscription_event.json", "tests/ui_contract/research_subscription_event.schema.json"),
    ]

    for sample_path, schema_path in schema_pairs:
        validator = Draft202012Validator(_load_json(schema_path))
        errors = sorted(validator.iter_errors(_load_json(sample_path)), key=lambda item: item.path)
        assert not errors, f"{sample_path} failed schema validation: {[error.message for error in errors]}"
