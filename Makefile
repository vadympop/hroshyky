# Every quality gate from CLAUDE.md is a target here (the migrations gate arrives with the database). CI and the git hooks call these same targets.
BASE_REF ?= origin/main
PATHS := src tests scripts
B := cd backend &&

.PHONY: install hooks format lint complexity types test coverage openapi contract secrets deps check

install: ## install the locked environment
	$(B) uv sync --locked

hooks: ## install the pre-commit and pre-push hooks
	$(B) uv run pre-commit install

format: ## rewrite files in place
	$(B) uv run ruff format . && uv run ruff check --fix .

lint: ## gate: format, lint, explained suppressions
	$(B) uv run ruff format --check . && uv run ruff check . && uv run python scripts/check_source.py suppressions $(PATHS)

complexity: ## gate: cyclomatic complexity and file length
	$(B) uv run ruff check --select C901 . && uv run python scripts/check_source.py length $(PATHS)

types: ## gate: strict typing
	$(B) uv run mypy

test: ## gate: tests (writes coverage data)
	$(B) uv run pytest

coverage: ## gate: diff coverage and total coverage, after `make test`
	$(B) uv run diff-cover coverage.xml --compare-branch=$(BASE_REF) --fail-under=85 && bash scripts/coverage_ratchet.sh $(BASE_REF)

openapi: ## regenerate the committed OpenAPI schema
	$(B) uv run python -m hroshyky.tools.export_openapi openapi.json

contract: openapi ## gate: the committed schema matches the code
	git diff --exit-code -- backend/openapi.json

secrets: ## gate: scan the whole history (needs gitleaks on PATH; the hook scans staged changes)
	gitleaks git --redact --verbose .

deps: ## gate: lock file in sync, no known vulnerabilities
	$(B) uv lock --check && uv audit --preview-features audit-command

check: lint complexity types test coverage contract secrets deps ## all gates
