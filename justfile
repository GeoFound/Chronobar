set shell := ["bash", "-lc"]

default:
    just --list

install:
    uv sync --group dev

test:
    uv run pytest

docs-check:
    uv run pytest tests/test_docs_links.py tests/test_repo_baseline.py tests/test_ui_contract_research.py

lint:
    uv run pre-commit run --all-files

check:
    just docs-check
    just lint
    just test
