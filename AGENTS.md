# Chronobar Agent Rules

## Start Here

Before making changes in this repository, read:

1. `ai-instructions.md`
2. `README.md`
3. `docs/roadmap.md`
4. `docs/engineering/engineering_baseline.md`

## Repository Status

This repository is currently in **M1 baseline convergence**.

That means agents should primarily work on:
- documentation consistency
- config examples and JSON Schema
- contract samples
- tests and CI baseline
- contribution workflow and governance files

Agents should not assume that runtime modules already exist.

## Change Rules

- Keep edits tightly scoped to the user request
- If a protocol changes, update related docs and `CHANGELOG.md`
- Do not invent new business fields outside the documented protocols
- Do not add large runtime implementations unless the user explicitly asks to move into M2 work
- Prefer repository-local tooling and reproducible commands

## Validation Rules

Use the project entrypoints when available:

- `just install`
- `just test`
- `just docs-check`
- `just check`

If the local environment is missing required tools, report the gap clearly.
