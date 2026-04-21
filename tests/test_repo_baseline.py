from __future__ import annotations

import json
from pathlib import Path

import yaml
from jsonschema import Draft202012Validator

REPO_ROOT = Path(__file__).resolve().parents[1]


def _load_yaml(relative_path: str) -> dict:
    return yaml.safe_load((REPO_ROOT / relative_path).read_text(encoding="utf-8"))


def _load_json(relative_path: str) -> dict:
    return json.loads((REPO_ROOT / relative_path).read_text(encoding="utf-8"))


def test_required_baseline_files_exist() -> None:
    required_paths = [
        "pyproject.toml",
        "uv.lock",
        "ai-instructions.md",
        "AGENTS.md",
        "justfile",
        ".envrc",
        ".pre-commit-config.yaml",
        ".github/workflows/ci.yml",
        "config/defaults/system.yaml",
        "config/defaults/market.yaml",
        "config/defaults/rules.yaml",
        "config/defaults/indicator.yaml",
        "config/defaults/workspace.yaml",
        "config/schemas/system.schema.json",
        "config/schemas/market.schema.json",
        "config/schemas/rules.schema.json",
        "config/schemas/indicator.schema.json",
        "config/schemas/workspace.schema.json",
        "tests/ui_contract/query_response.json",
        "tests/ui_contract/subscription_event.json",
        "tests/ui_contract/error_codes.json",
    ]

    missing = [path for path in required_paths if not (REPO_ROOT / path).exists()]
    assert not missing, f"Missing baseline files: {missing}"


def test_default_configs_validate_against_schemas() -> None:
    pairs = [
        ("config/defaults/system.yaml", "config/schemas/system.schema.json"),
        ("config/defaults/market.yaml", "config/schemas/market.schema.json"),
        ("config/defaults/rules.yaml", "config/schemas/rules.schema.json"),
        ("config/defaults/indicator.yaml", "config/schemas/indicator.schema.json"),
        ("config/defaults/workspace.yaml", "config/schemas/workspace.schema.json"),
    ]

    for config_path, schema_path in pairs:
        validator = Draft202012Validator(_load_json(schema_path))
        errors = sorted(validator.iter_errors(_load_yaml(config_path)), key=lambda item: item.path)
        assert not errors, (
            f"{config_path} failed schema validation: {[error.message for error in errors]}"
        )


def test_readme_mentions_m1_baseline_state() -> None:
    readme = (REPO_ROOT / "README.md").read_text(encoding="utf-8")

    assert "M1 基线收敛中" in readme
    assert "默认配置、Schema 与基础测试/CI 已入仓" in readme


def test_ui_contract_examples_match_protocol_baseline() -> None:
    query_response = _load_json("tests/ui_contract/query_response.json")
    subscription_event = _load_json("tests/ui_contract/subscription_event.json")
    error_codes = _load_json("tests/ui_contract/error_codes.json")

    assert query_response["ok"] is True
    assert "data" in query_response
    assert isinstance(query_response["trace_id"], str)

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
    assert required_event_fields.issubset(subscription_event.keys())

    assert "BRIDGE_VALIDATION_ERROR" in error_codes
    assert "WORKSPACE_NOT_FOUND" in error_codes
    assert "INVALID_INTERVAL" in error_codes
