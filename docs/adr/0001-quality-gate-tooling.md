# ADR 0001: Quality gate tooling

**Status:** accepted · **Date:** 2026-11-16 · **Stage:** 1, checkpoint 1

## Context

`CLAUDE.md` lists nine quality gates that must fail the build in CI and run as git hooks. The tools are the implementer's choice. Python tooling must go through uv.

## Decision

Each gate is one `make` target. CI jobs and git hooks call the same targets, so there is one definition of every check.

| Gate | Target | Tool |
|---|---|---|
| Format & lint | `lint` | `ruff format --check`, `ruff check`, and `scripts/check_source.py suppressions`, which rejects any suppression comment without a rule code and a written reason |
| Types | `types` | `mypy --strict` over `src`, `tests`, `scripts` (and `migrations` once they exist) |
| Complexity | `complexity` | ruff `C901` (max 10) and `scripts/check_source.py length` (max 400 lines per Python file) |
| Tests | `test` | pytest, warnings as errors, strict xfail. `pytest-socket --allow-hosts` permits only local connections |
| Coverage | `coverage` | `diff-cover --fail-under=85` against the PR base, and `scripts/coverage_ratchet.sh`, which runs the base commit's tests in a git worktree and fails if the total went down |
| Migrations | `migrate-check` | Alembic upgrade → downgrade to base → upgrade on an empty PostgreSQL, then `alembic check`. **Added in the next checkpoint 1 PR, together with the database** |
| API contract | `contract` | regenerate `backend/openapi.json`, fail on `git diff` |
| Secrets | `secrets` | gitleaks: whole history in CI, staged changes in the pre-commit hook |
| Dependencies | `deps` | `uv lock --check` and `uv audit` |

CI is one workflow. Backend gates run only when backend paths change. Secrets and contract always run. The `ci-ok` job fails unless every other job passed or was skipped by the path filter, so it is the single check to mark as required.

Hooks use the pre-commit framework. Format/lint, complexity, contract and secrets run on commit. Types, tests with coverage, migrations and dependencies run on push, because they are slow or need the database.

## Alternatives

- **pyright or ty instead of mypy:** mypy has the pydantic plugin and mature SQLAlchemy support.
- **`--disable-socket` in pytest-socket:** it breaks asyncio on Windows, where the event loop needs a local socket pair. `--allow-hosts` still blocks every non-local connection.
- **A committed coverage baseline file:** every PR would edit it and conflict. Measuring the base commit needs no stored state.
- **gitleaks-action:** running the pinned binary keeps CI and the local `make secrets` identical.
- **Path-filtered workflows (`on.paths`):** a skipped workflow never reports, which blocks a required check. One workflow with an aggregator avoids that.

## Consequences

- The coverage ratchet runs the base commit's tests once per base commit (cached), which lengthens the first run on a new base.
- `uv audit` is still experimental in uv 0.12. If its interface changes, only the `deps` target changes.
- Once the migrations gate exists, the pre-push hooks need the local database.
- Thresholds live in `backend/pyproject.toml`, `backend/scripts/check_source.py` and the `Makefile`. Changing one needs a new ADR.
