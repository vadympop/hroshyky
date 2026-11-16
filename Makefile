# Every quality gate from CLAUDE.md is a target here (the migrations gate arrives with the database). CI and the git hooks call these same targets.
# Report every failing check in one run, not only the first one.
MAKEFLAGS += --keep-going
BASE_REF ?= origin/main
PATHS := src tests scripts
B := cd backend &&

.PHONY: install hooks format lint lint-format lint-rules lint-suppressions complexity complexity-functions complexity-files \n	types test coverage coverage-diff coverage-total openapi contract secrets deps deps-lock deps-audit check

install: ## install the locked environment
	$(B) uv sync --locked

hooks: ## install the pre-commit and pre-push hooks
	$(B) uv run pre-commit install

format: ## rewrite files in place
	$(B) uv run ruff format . && uv run ruff check --fix .

lint: lint-format lint-rules lint-suppressions ## gate: format, lint, explained suppressions
lint-format: ; $(B) uv run ruff format --check .
lint-rules: ; $(B) uv run ruff check .
lint-suppressions: ; $(B) uv run python scripts/check_source.py suppressions $(PATHS)

complexity: complexity-functions complexity-files ## gate: cyclomatic complexity and file length
complexity-functions: ; $(B) uv run ruff check --select C901 .
complexity-files: ; $(B) uv run python scripts/check_source.py length $(PATHS)

types: ## gate: strict typing
	$(B) uv run mypy

test: ## gate: tests (writes coverage data)
	$(B) uv run pytest

coverage: coverage-diff coverage-total ## gate: diff coverage and total coverage, after `make test`
coverage-diff: ; $(B) uv run diff-cover coverage.xml --compare-branch=$(BASE_REF) --fail-under=85
coverage-total: ; $(B) bash scripts/coverage_ratchet.sh $(BASE_REF)

openapi: ## regenerate the committed OpenAPI schema
	$(B) uv run python -m hroshyky.tools.export_openapi openapi.json

contract: openapi ## gate: the committed schema matches the code
	git diff --exit-code -- backend/openapi.json

secrets: ## gate: scan the history of the current commit (needs gitleaks on PATH; the hook scans staged changes)
	gitleaks git --redact --verbose --log-opts=HEAD .

deps: deps-lock deps-audit ## gate: lock file in sync, no known vulnerabilities
deps-lock: ; $(B) uv lock --check
deps-audit: ; $(B) uv audit --preview-features audit-command

check: lint complexity types test coverage contract secrets deps ## all gates
