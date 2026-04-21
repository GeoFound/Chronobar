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
- Renamed document layers from 第一层/第二层/第三层 to Contracts/Architecture/Engineering Standards
- GitHub Issue templates for bug reports and feature requests

### Changed
- Unified M1 wording across `README.md`, `docs/CONTRIBUTING.md`, `docs/roadmap.md`, and `docs/engineering/m1_checklist.md` to mean docs + config/schema + baseline validation, not runtime completion
- Aligned `docs/system/config_protocol.md` bridge port examples with `docs/system/ui_bridge_protocol.md`
- Fixed roadmap version references for `config_protocol.md` and `ui_bridge_protocol.md`
- Fixed the LICENSE relative link in `docs/CONTRIBUTING.md`
- Updated `docs/engineering/engineering_baseline.md` dependency baseline to include YAML and JSON Schema tooling
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
- Added pyproject.toml baseline (Python 3.11+, dependency tiers)
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
