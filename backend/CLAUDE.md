# Backend

Python 3.14 and FastAPI. Everything runs through uv. The root `CLAUDE.md` always applies.

## Commands (run from the repo root)
- `make install` — create the environment from `uv.lock`. `make hooks` — install the git hooks.
- `make check` — every quality gate. Single gates: `lint`, `complexity`, `types`, `test`, `coverage`, `contract`, `secrets`, `deps`.
- `make format` — auto-format and auto-fix. `make openapi` — regenerate `backend/openapi.json` after any API change and commit it.

## Layout
- `src/hroshyky/` — the application package. `scripts/` — gate helpers. `tests/` — pytest.

## Gotchas
- A suppression needs a rule code and a reason in a second comment: `# noqa: S105  # why this is safe`. The lint gate rejects anything else.
- Tests may connect only to localhost. Mock every external service.
- The test client needs `httpx2` (Starlette deprecated `httpx` for it).
- `create_app()` must not read settings: the OpenAPI export runs without an environment.
- `make coverage` needs coverage data from `make test`. The first run on a new base commit also runs that commit's tests.
- `make secrets` needs gitleaks on PATH. Without it, the pre-commit hook still scans staged changes.
