# Chronobar Protocol Changelog

This document tracks version changes across all protocol documents, following [Keep a Changelog](https://keepachangelog.com/en/1.0.0/) format.

## [Unreleased]

### Added
- M1 baseline repository artifacts:
  - Added `pyproject.toml` with Python, pytest, ruff, and mypy baseline configuration
  - Added `.pre-commit-config.yaml` and `.github/workflows/ci.yml`
  - Added `config/defaults/*.yaml` example configuration files
  - Added `config/schemas/*.json` JSON Schema baseline files
  - Added `tests/test_repo_baseline.py` and `tests/ui_contract/*.json` contract samples
  - Added `.github/CODEOWNERS`, `docs/getting_started_for_contributors.md`, and `examples/README.md`
  - Added `ai-instructions.md`, `AGENTS.md`, `justfile`, and `.envrc` to satisfy workstation SOP governance requirements
  - Added `tests/test_docs_links.py` for repository-local markdown link validation
  - Added `uv.lock` as the repository lockfile for uv-based local and CI workflows
- Documentation architecture improvements:
  - Created `docs/decisions/` ADR directory with storage architecture decision record
  - Created `docs/glossary.md` with unified terminology
  - Created `docs/roadmap.md` with M1→M2→M3 deliverables
  - Created `docs/faq.md` with common questions
  - Created `docs/system/ai_assistant_architecture.md` and `docs/system/ai_assistant_product_contract.md` as AI Assistant supplemental design docs
  - Created `docs/engineering/delivery_master_plan.md`, `docs/engineering/implementation_task_packages.md`, and `.windsurf/workflows/execute-chronobar-delivery.md` for phased delivery execution
  - Created `docs/engineering/current_phase_and_truth_source.md` to define the official current phase, truth-source priority, and early runtime scope freeze
  - Created `docs/engineering/runtime_nonfunctional_baseline.md` to define performance targets, benchmark expectations, and minimum observability requirements
  - Created `docs/system/storage_lifecycle_and_recovery.md` to define data retention, backup/restore, corruption handling, and recovery paths
  - Renamed document layers from 第一层/第二层/第三层 to Contracts/Architecture/Engineering Standards
  - GitHub Issue templates for bug reports and feature requests

### Changed
- Merged strategic execution decisions directly into planning documents instead of creating a new long-lived decision layer:
  - `docs/roadmap.md` now prioritizes `SimGateway`, local Tick persistence, session/trading_date correctness, and sidecar lifecycle handling
  - `docs/engineering/delivery_master_plan.md` now treats data flywheel, replay consistency, and desktop recovery paths as first-class delivery constraints
  - `docs/engineering/implementation_task_packages.md` now turns those priorities into executable task packages for M2-M5
  - `.windsurf/workflows/execute-chronobar-delivery.md` continues to use delivery plan + task packages as the execution source of truth
  - Strengthened AI Assistant contracts and repository artifacts around user-owned usable outputs instead of one-off drafts:
    - `docs/system/ai_assistant_product_contract.md` now defines usable candidate artifacts, user-owned outputs, controlled real-world research access, and memory-use disclosure
    - `docs/system/ai_assistant_architecture.md` now includes candidate validation / change-set building, managed memory tiers, and controlled external-context access as first-class architecture elements
    - `docs/system/ui_bridge_protocol.md` now defines AI query/command/subscription categories and error codes for confirmation, artifact validation, external context, and memory management
  - `docs/system/config_protocol.md`, `config/defaults/system.yaml`, `config/schemas/system.schema.json`, and `docs/core/ai_protocol.md` now align on nested AI config for features, external_context, memory, and apply_policy
  - `docs/engineering/delivery_master_plan.md` and `docs/engineering/implementation_task_packages.md` now treat candidate artifact application, external context, and memory governance as formal P5 delivery work instead of implicit future ideas
  - Added `tests/ui_contract/ai_pending_change.json` and expanded `tests/test_repo_baseline.py` / `tests/ui_contract/error_codes.json` to anchor the AI confirmation/apply contract in repository samples and baseline checks
  - Added `tests/ui_contract/research_workspace.json` and `tests/ui_contract/research_publish_candidate.json` to anchor research workspace and publish-confirmation bridge samples in baseline checks
  - Added `tests/ui_contract/research_subscription_event.json` and expanded research contract assertions to cover query / publish / subscription flows against existing bridge error-code samples
    - Added `tests/test_ui_contract_research.py` and updated `just docs-check` so research workspace / publish / subscription samples are validated through dedicated protocol-field mapping assertions
    - Added `tests/ui_contract/research_workspace.schema.json`, `tests/ui_contract/research_publish_candidate.schema.json`, and `tests/ui_contract/research_subscription_event.schema.json` to provide JSON Schema-level contract validation for research UI contract samples, with baseline checks ensuring these schemas exist and samples validate against them
  - Clarified across `README.md`, `ai-instructions.md`, `docs/engineering/engineering_baseline.md`, `docs/system/ai_assistant_architecture.md`, and `docs/system/ai_assistant_product_contract.md` that repository AI and product AI are distinct layers, and anchored this boundary in `tests/test_repo_baseline.py`
  - Landed long-term platform foundations in repository governance and system architecture:
    - `docs/engineering/engineering_baseline.md` now lists the formal contract families that must be gradually formalized over time: Artifact Graph / User Asset Dependency Model, State Machine Contract, Evidence Bundle Contract, AI Change Set Contract, Capability Registry Contract, Policy Engine as Data Contract, Migration / Portability Contract, Storage Boundary Contract, AI Session Model 与 Memory Governance, and Regional Market / Compliance Abstraction Contract
    - `docs/system/architecture.md` now defines long-term platform foundation sections for object relationships / asset graphs (4.5), state machines / three-domain boundaries (4.6), evidence bundles / change sets / confirmation semantics (4.7), capability registry / policy data / internationalization abstractions (4.8), and migration / replay / storage boundaries (4.9)
    - `docs/roadmap.md` now includes these long-term platform foundations as M1 deliverables
    - `docs/engineering/delivery_master_plan.md` now includes repository AI / product AI boundary clarification and long-term platform foundation formalization as P0 goals
    - `tests/test_repo_baseline.py` now anchors these long-term platform foundations with explicit assertions across architecture, engineering baseline, roadmap, and delivery master plan
  - Formalized Chronobar as a user-owned futures skeleton platform across system and delivery docs:
    - `docs/system/architecture.md` now defines the platform as a stable skeleton, adds a user asset model, and separates build-state assembly from run-state execution
    - `docs/system/ai_assistant_product_contract.md` now positions AI as a user system-assembly copilot, adds gateway/strategy/workspace asset assistance, and reinforces build-state publication before run-state use
  - `docs/system/ai_assistant_architecture.md` now adds multi-factor research copilot, research-tool boundaries, and research-result repeatability metrics
  - `docs/system/config_protocol.md` now introduces research config as a first-class protocol layer for factor definitions, experiment configs, and publish records
  - `config/defaults/research.yaml`, `config/schemas/research.schema.json`, and `tests/test_repo_baseline.py` now anchor research config as a baseline repository artifact with schema validation aligned with config_protocol.md field commitments
  - `docs/system/ui_bridge_protocol.md` now defines research workspace, factor table, experiment comparison, and publish-confirmation bridge flows, with these commitments anchored in structured UI contract schema tests and sample validation
  - `docs/system/ai_assistant_product_contract.md` now adds multi-factor research assistance, research-state display, and publish confirmation expectations
  - `docs/core/gateway_protocol.md` now treats gateways as adapter specifications with explicit capability declaration and degradation rules instead of one-off broker integrations
  - `docs/engineering/delivery_master_plan.md` and `docs/engineering/implementation_task_packages.md` now carry gateway adapter capability, user asset compatibility, research skeleton, and AI-assisted research responsibilities into phased delivery work
- Unified M1 wording across `README.md`, `docs/CONTRIBUTING.md`, `docs/roadmap.md`, and `docs/engineering/m1_checklist.md` to mean docs + config/schema + baseline validation, not runtime completion
- Aligned `docs/system/config_protocol.md` bridge port examples with `docs/system/ui_bridge_protocol.md`
- Fixed roadmap version references for `config_protocol.md` and `ui_bridge_protocol.md`
- Fixed the LICENSE relative link in `docs/CONTRIBUTING.md`
  - Updated `docs/engineering/engineering_baseline.md` dependency baseline to include YAML and JSON Schema tooling
  - Unified current-phase wording across `README.md`, `ai-instructions.md`, `docs/roadmap.md`, `docs/CONTRIBUTING.md`, `docs/getting_started_for_contributors.md`, `examples/README.md`, and `tests/test_repo_baseline.py` to keep the repository in M1 baseline convergence until P1 / M2 gates are formally passed
  - Reframed `docs/engineering/p1_completion_summary.md` as a pre-P1 review record instead of an authoritative completion claim
  - Aligned `docs/engineering/engineering_baseline.md` Python version wording with `pyproject.toml` (`>=3.14`) and linked it to the new nonfunctional and storage recovery baselines
  - Upgraded the `pyarrow` dependency baseline from `>=14.0,<15` to `>=23.0,<24` to match the Python 3.14 workspace baseline and avoid failing local validation on unsupported wheels/builds
  - Expanded `docs/engineering/implementation_task_packages.md` into a full productization task system from P0 to P6, including D1-D10 cross-stage dimensions, phase closure packages, richer desktop / AI / release tasks, and a final product completion definition
  - Strengthened `docs/engineering/delivery_master_plan.md` to require stage proof artifacts, evidence gates, blocker gates, and explicit beta / GA release readiness conditions
  - Updated `.windsurf/workflows/execute-chronobar-delivery.md` so phased execution must track closure packages, blocker state, evidence outputs, and multi-dimension task coverage
  - Strengthened markdown lint coverage to validate heading slug uniqueness and fragment anchor resolution
  - README layer naming to use Contracts/Architecture/Engineering Standards instead of Chinese layer names
  - Comparison table data接入 entry to be more specific and honest (国内主流期货 API（计划）)
- Core principles table to fix duplicate text

## [1.2.0] - 2026-04-21

### Strategic Decisions
- **Target Users**: Personal quant users and personal trading users
- **Business Model**: Open core + commercial extensions
- **Deployment Form**: Desktop client (Tauri + React + Python sidecar)
- **Storage Architecture**: DuckDB + Parquet for Tick data, SQLite for metadata

### Architecture Layer (system/architecture.md)
- Added target user persona section
- Added business boundary section
- Added deployment form decision (Tauri + React + Python sidecar)
- Added storage layer decision (DuckDB + Parquet)
- Added minimum loop acceptance criteria with observable outputs

### Data Protocol (core/data_protocol.md)
- Added `cancellation_reason` and `cancel_reason_code` fields to Order object
- Added CancelReasonCode enum with 6 values (timeout, rejected_by_user, rejected_by_risk, rejected_by_exchange, connection_lost, other)
- Updated Python reference definitions to match text definitions for Position, Account, and Trade
- Added gateway_trade_id and commission fields to Trade

### Event Protocol (core/event_protocol.md)
- Added REPLAY_TICK and REPLAY_BAR event types
- Added replayable annotation table for all event types
- Added queue capacity and backpressure strategy (max 10000 events, threshold 8000)
- Added backpressure degradation strategy for low-priority events

### Plugin Protocol (core/plugin_protocol.md)
- Added `depends_on` and `load_after` fields to PluginManifest
- Added dependency loading strategy (hard dependency enforcement, circular dependency detection)
- Fixed section numbering error (duplicate ## 3)

### Risk Protocol (core/risk_protocol.md)
- Updated version from v1.0 to v1.2
- Changed RiskCheckResult.check_type from str to RiskCheckType enum
- Defined serial execution with priority ordering
- Added short-circuit logic on risk check failure

### Backtest Protocol (core/backtest_protocol.md)
- Changed mode field from str to BacktestMode enum
- Added HistoricalDataFormat enum (PARQUET, CSV, DATABASE)
- Set data_format default to PARQUET
- Added Parquet data loading strategy (sharding by trading day, concurrent reading, memory limits)

### Gateway Protocol (core/gateway_protocol.md) - NEW
- Created new gateway protocol document
- Defined BaseGateway interface (connect, disconnect, subscribe, submit_order, cancel_order, query_account, query_position, query_orders)
- Defined GatewayCallback interface (on_tick, on_trade, on_order, on_position, on_account, on_error, on_log)
- Defined GatewayStatus enum
- Defined ReconnectPolicy with exponential backoff
- Added callback mapping constraints and exception isolation

### UI Bridge Protocol (system/ui_bridge_protocol.md)
- Added Tauri IPC binding decision section
- Specified Query/Command API using tauri::invoke
- Specified Subscription API using WebSocket
- Defined port conventions (HTTP: 18080, WebSocket: 18081)

### Engineering Baseline (engineering/engineering_baseline.md)
- Added test coverage targets (core ≥80%, protocol ≥95%)
- Added AI collaboration constraints with pre-generation declaration template
- Added storage layer technical decision (DuckDB + Parquet)
- Added pyproject.toml baseline (Python 3.14+, dependency tiers)
- Added strict file-level ordering in development phase 2

### README.md
- Added strategic positioning section (target users, business boundary, deployment form, storage architecture)

### Golden Examples (core/golden_examples.md)
- Updated version from v1.0 to v1.2
- Added protocol version note and sync requirement

### M1 Checklist (engineering/m1_checklist.md)
- Aligned M1 acceptance criteria with engineering_baseline.md milestone definitions

## v1.0 (Initial Release)

### Architecture Layer
- Defined 7-layer architecture
- Defined main engine coordination model
- Defined real-time and replay main flows

### Data Protocol
- Defined core data objects (Tick, Bar, Instrument, SessionContext)
- Defined trading execution objects (Order, Trade, Position, Account, OrderRequest, CancelRequest)

### Event Protocol
- Defined event model and EventEnvelope
- Defined standard event types
- Defined routing rules and idempotency requirements

### Plugin Protocol
- Defined plugin classification (indicator, signal, strategy, ui-extension)
- Defined plugin manifest structure
- Defined lifecycle interfaces
- Defined Host API baseline
- Defined permission model

### Risk Protocol
- Defined risk check request/result objects
- Defined RiskChecker and RiskManager interfaces
- Defined risk check execution order

### Backtest Protocol
- Defined BacktestConfig and BacktestResult
- Defined BacktestEngine interface
- Defined OrderMatcher interface

### UI Bridge Protocol
- Defined Query, Command, Subscription APIs
- Defined standard response formats
- Defined workspace synchronization protocol

### Engineering Baseline
- Defined repository structure
- Defined code standards
- Defined test requirements
- Defined configuration governance
- Defined plugin governance
- Defined development order
- Defined delivery standards
- Defined AI collaboration constraints
- Defined milestone acceptance criteria

### Golden Examples
- Provided MA indicator plugin example
- Provided dual MA signal plugin example
- Provided simulation strategy plugin example
- Provided replay test case example
