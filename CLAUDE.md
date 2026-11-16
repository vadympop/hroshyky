# Hroshyky — expense tracker

A personal expense tracker (multi-user later): a Telegram bot for input, a Vue admin panel, a Telegram Mini App, one backend.
Roadmap and process: `docs/ROADMAP.md`. Current stage spec: `docs/stages/STAGE-N.md`. Architecture: `docs/architecture.md`. Decisions: `docs/adr/`.

## Repository layout
- **One repository (monorepo)** for everything. Each application lives in its own top-level directory: `backend/` (stage 1), `admin/` (stage 2), `miniapp/` (stage 3). Where shared frontend code lives is decided in stage 2.
- `docs/` holds the roadmap, stage specs, architecture, ADRs and the backlog. Repo-wide config (`docker-compose.yml`, `.github/`, this file) lives at the root.
- CI runs only the checks relevant to the paths a PR touches, plus repo-wide checks (secrets, contract).
- An application directory may have its own `CLAUDE.md` for app-specific commands and gotchas. This root file always applies.

## How to work
- Plan first (plan mode), wait for the human's approval, then write code.
- Specs define the expected result. Architecture and technical choices are yours: record significant ones as ADRs (`docs/adr/NNNN-title.md`: context, decision, alternatives, consequences).
- Stay within the current stage's scope. Ideas for later go to `docs/backlog.md`.
- If the spec contradicts reality, write an ADR and flag it to the human. Never work around it silently.
- At the end of each checkpoint: all quality gates green, docs updated, and a PR opened with the template's checklist completed (see below).
- Keep this file up to date: commands, conventions and gotchas that the next agent needs to know.

## Git rules

### Branches
- `main` is always green and deployable. **Never commit or push to `main` directly.**
- One branch per checkpoint: `stage-<N>/<checkpoint-number>-<short-topic>`, e.g. `stage-1/2-excel-import`.
- Hotfixes: `fix/<short-topic>`, branched from `main`.
- Rebase on the latest `main` before opening a PR. Do not merge `main` into feature branches.

### Commits
- [Conventional Commits](https://www.conventionalcommits.org/): `type(scope): summary`. Types: `feat`, `fix`, `refactor`, `test`, `docs`, `chore`, `ci`, `perf`. Scope = area (`bot`, `api`, `importer`, `ekasa`, `llm`, …).
- Summary in English, imperative mood, ≤ 72 characters. Add a body when the *why* is not obvious.
- One logical change per commit. Every commit builds, and tests pass at every commit where practical.
- Every commit made by an agent ends with a trailer naming the model: `Agent: <model-name>`.
- Never commit secrets, `.env`, or anything from `data/private/`. Before each commit, check `git status` for unexpected files.

### Pull requests
- One PR per checkpoint. Title in Conventional Commit style.
- Fill in `.github/pull_request_template.md` completely. Write "n/a" where a section does not apply, never delete sections.
- Size limit: ~600 changed lines, excluding lock files, generated code (e.g. the OpenAPI schema) and test fixtures. If a checkpoint is bigger, split it into several PRs before review. The reviewer returns oversized PRs.
- CI must be green before review.
- The PR is reviewed by a different model than its author, in a fresh context. The author addresses every finding with a fix or a written reply.
- **Only the human merges.** An agent never merges its own PR. Merge method: squash merge. The squash message follows Conventional Commits.

### History and releases
- Never rewrite published history: no force-pushes to `main`, and no force-pushes to a branch once its PR is under review (`--force-with-lease` on your own unreviewed branch is fine).
- Never delete branches or tags you did not create.
- When a stage is accepted, the human tags `main` as `v0.<N>.0` and the agent adds a stage entry to `CHANGELOG.md`.

## Quality gates (enforced by CI)

These rules are not advice: each one must be implemented as a CI check that fails the build, and the same checks run as pre-commit hooks. **Checkpoint 1 of stage 1 is not accepted until every gate below is in place and demonstrably fails on a violation.**

| Gate | Rule |
|---|---|
| Format & lint | Zero warnings. Every suppression (`noqa`, `type: ignore`, etc.) has an inline comment explaining why. |
| Types | Strict type checking on the whole codebase, tests included. |
| Complexity | Cyclomatic complexity ≤ 10 per function, file length ≤ 400 lines (generated code excluded). |
| Tests | All tests pass. No network or real LLM calls. |
| Coverage | Diff coverage of changed lines ≥ 85%. Overall coverage must not decrease. |
| Migrations | Every migration applies and rolls back cleanly on a fresh database. |
| API contract | The committed OpenAPI schema matches the code. |
| Secrets | Secret scanning on every commit (e.g. gitleaks). |
| Dependencies | Lock file committed and in sync. Vulnerability audit passes. |

The tools are your choice. Thresholds change only by an explicit human decision recorded in an ADR.

## Agent conduct

- **Never weaken a check to get green.** Do not delete, skip, `xfail` or loosen a test or assertion, lower a threshold, or add a suppression just to pass CI. If a test is wrong, fix it in a separate commit whose message explains why it was wrong.
- **Never game evals.** No hardcoded expected values, no special cases for eval-set inputs, no reading `expected.yaml` from code under test.
- **Stay on task.** Do not touch files unrelated to the current task. Opportunistic refactors go to `docs/backlog.md`.
- **No leftovers.** No commented-out code, no debug prints, and no `TODO` without a matching entry in `docs/backlog.md`.
- **New dependencies are justified** in the PR description: why it is needed and why the standard library or an existing dependency is not enough.
- **Stop when stuck.** If the same problem survives 3 honest attempts, stop and write up what you tried, what failed and your hypotheses, instead of working around it.
- **Report honestly.** PR descriptions and checkpoint summaries state what is actually done and verified. Anything partial, untested or deferred is listed explicitly.

## Data and secrets
- `data/private/` (the Excel file, receipt photos, the eval set) is git-ignored. Never commit it, never quote it in logs, and never use it in fixtures without anonymising it.
- Secrets live only in `.env`. When you add a variable, update `.env.example` with a description.
- Logs must never contain tokens or API keys.

## Domain notes
- Base currency is **EUR**. Amounts in other currencies keep their original value and currency and are converted at the historical rate of their date. Amounts are exact to the cent.
- A purchase (one receipt) has line items. Income is tracked too.
- Some Excel-era expenses are known only to the month, not the day.
- Corrections from the user must teach the categorisation, so the same item is not re-asked or re-sent to an LLM.
- Shop aliases used in the Excel history: Кауф = Kaufland, Лідл = Lidl, Біла = Billa, Теско = Tesco, Дм = dm drogerie.
- Bot texts are in Ukrainian. Code, docs and commits are in English.
- Time zone: Europe/Bratislava.
