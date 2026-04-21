# Chronobar Protocol Changelog

This document tracks version changes across all protocol documents.

## v1.2 (2024-04-21)

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
