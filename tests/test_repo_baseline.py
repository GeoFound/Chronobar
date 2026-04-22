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
        "config/defaults/research.yaml",
        "config/defaults/workspace.yaml",
        "config/schemas/system.schema.json",
        "config/schemas/market.schema.json",
        "config/schemas/rules.schema.json",
        "config/schemas/indicator.schema.json",
        "config/schemas/research.schema.json",
        "config/schemas/workspace.schema.json",
        "docs/engineering/current_phase_and_truth_source.md",
        "docs/engineering/runtime_nonfunctional_baseline.md",
        "docs/system/storage_lifecycle_and_recovery.md",
        "tests/ui_contract/query_response.json",
        "tests/ui_contract/research_workspace.json",
        "tests/ui_contract/research_workspace.schema.json",
        "tests/ui_contract/research_subscription_event.json",
        "tests/ui_contract/research_subscription_event.schema.json",
        "tests/ui_contract/subscription_event.json",
        "tests/ui_contract/ai_pending_change.json",
        "tests/ui_contract/research_publish_candidate.json",
        "tests/ui_contract/research_publish_candidate.schema.json",
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
        ("config/defaults/research.yaml", "config/schemas/research.schema.json"),
        ("config/defaults/workspace.yaml", "config/schemas/workspace.schema.json"),
    ]

    for config_path, schema_path in pairs:
        validator = Draft202012Validator(_load_json(schema_path))
        errors = sorted(validator.iter_errors(_load_yaml(config_path)), key=lambda item: item.path)
        assert not errors, (
            f"{config_path} failed schema validation: {[error.message for error in errors]}"
        )


def test_readme_mentions_m1_baseline_status() -> None:
    readme = (REPO_ROOT / "README.md").read_text(encoding="utf-8")
    assert "当前状态：M1 基线收敛" in readme
    assert "current_phase_and_truth_source.md" in readme
    assert "P1 核心闭环完成" not in readme


def test_repository_ai_and_product_ai_boundaries_are_explicit() -> None:
    readme = (REPO_ROOT / "README.md").read_text(encoding="utf-8")
    ai_instructions = (REPO_ROOT / "ai-instructions.md").read_text(encoding="utf-8")
    eng_baseline_path = REPO_ROOT / "docs/engineering/engineering_baseline.md"
    engineering_baseline = eng_baseline_path.read_text(encoding="utf-8")
    prod_contract_path = REPO_ROOT / "docs/system/ai_assistant_product_contract.md"
    product_contract = prod_contract_path.read_text(encoding="utf-8")
    ai_arch_path = REPO_ROOT / "docs/system/ai_assistant_architecture.md"
    ai_architecture = ai_arch_path.read_text(encoding="utf-8")

    assert "产品 AI" in readme
    assert "仓库 AI" in readme
    assert "本文件约束的是**仓库 AI**" in ai_instructions
    assert "仓库 AI 长期协作原则" in ai_instructions
    assert "本节约束的是**仓库 AI**" in engineering_baseline
    assert "长期结构稳定性要求" in engineering_baseline
    assert "本文档约束的是 Chronobar 产品内部面向产品使用者的 **产品 AI**" in product_contract
    assert "仓库维护者与仓库 AI 的协作边界不由本契约定义" in product_contract
    assert "它约束的是 Chronobar 产品内部面向产品使用者的 **产品 AI**" in ai_architecture
    assert "与仓库 AI 治理文档的关系" in ai_architecture


def test_long_term_platform_foundations_are_explicit() -> None:
    architecture = (REPO_ROOT / "docs/system/architecture.md").read_text(encoding="utf-8")
    eng_baseline_path = REPO_ROOT / "docs/engineering/engineering_baseline.md"
    engineering_baseline = eng_baseline_path.read_text(encoding="utf-8")
    roadmap = (REPO_ROOT / "docs/roadmap.md").read_text(encoding="utf-8")
    delivery_plan_path = REPO_ROOT / "docs/engineering/delivery_master_plan.md"
    delivery_master_plan = delivery_plan_path.read_text(encoding="utf-8")

    # Architecture should have long-term foundation sections
    assert "4.5 对象关系与资产图谱" in architecture
    assert "4.6 状态机与三域边界" in architecture
    assert "4.7 证据包、变更集与确认语义" in architecture
    assert "4.8 能力注册表、策略数据化与国际化抽象" in architecture
    assert "4.9 迁移、重放与存储边界" in architecture
    assert "Artifact Graph / User Asset Dependency Model" in architecture
    assert "显式状态机" in architecture
    assert "Evidence Bundle" in architecture
    assert "AI Change Set" in architecture
    assert "Capability Registry" in architecture
    assert "Policy Engine as Data" in architecture
    assert "Migration / Portability Contract" in architecture
    assert "Storage Boundary Contract" in architecture

    # Engineering baseline should list contract families
    assert "长期看，仓库至少应把以下契约族逐步做成正式对象" in engineering_baseline
    assert "Artifact Graph / User Asset Dependency Model" in engineering_baseline
    assert "State Machine Contract" in engineering_baseline
    assert "Evidence Bundle Contract" in engineering_baseline
    assert "AI Change Set Contract" in engineering_baseline
    assert "Capability Registry Contract" in engineering_baseline
    assert "Policy Engine as Data Contract" in engineering_baseline
    assert "Migration / Portability Contract" in engineering_baseline
    assert "Storage Boundary Contract" in engineering_baseline
    assert "AI Session Model 与 Memory Governance" in engineering_baseline
    assert "Regional Market / Compliance Abstraction Contract" in engineering_baseline

    # Roadmap should mention these as M1 deliverables
    assert (
        "架构文档已明确 Artifact Graph、状态机、证据包、变更集、"
        "能力注册表、策略数据化、迁移/重放与存储边界等长期平台基础契约"
    ) in roadmap
    assert (
        "工程基线已明确仓库 AI 长期协作原则与结构稳定性要求，并列出必须逐步形成的正式契约族"
    ) in roadmap

    # Delivery master plan should include these as P0 goals
    assert (
        "明确仓库 AI 与产品 AI 的边界，并长期把对象模型、状态机、"
        "证据包、能力注册表、策略数据化、迁移契约与存储边界等"
        "基础能力写成正式契约"
    ) in delivery_master_plan


def test_ui_contract_examples_match_protocol_baseline() -> None:
    query_response = _load_json("tests/ui_contract/query_response.json")
    subscription_event = _load_json("tests/ui_contract/subscription_event.json")
    ai_pending_change = _load_json("tests/ui_contract/ai_pending_change.json")
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
    assert required_ai_change_fields.issubset(ai_pending_change.keys())
    assert ai_pending_change["status"] == "pending_confirmation"
    assert ai_pending_change["validation"]["ok"] is True

    assert "BRIDGE_VALIDATION_ERROR" in error_codes
    assert "WORKSPACE_NOT_FOUND" in error_codes
    assert "INVALID_INTERVAL" in error_codes
    assert "AI_CONFIRMATION_REQUIRED" in error_codes
    assert "AI_EXTERNAL_CONTEXT_DISABLED" in error_codes
    assert "AI_MEMORY_POLICY_DENIED" in error_codes
