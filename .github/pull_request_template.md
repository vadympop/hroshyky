<!--
Keep every section. Write "n/a" if a section does not apply.
Be short: bullets over prose. Write for a reader who has 2 minutes.
-->

## Summary
<!-- 1–3 sentences: what this PR does and why. -->

**Stage / checkpoint:** <!-- e.g. Stage 1 · Checkpoint 2 — Excel import -->
**Spec:** <!-- link to the spec section(s), e.g. docs/stages/STAGE-1.md#5-excel-import -->

## What changed
<!-- Bullets, grouped by area. Behaviour first, internals second. -->
-

## How to verify
<!-- Exact commands and what the human should see. Copy-pasteable. -->
```bash

```
**Expected:**
-

## Acceptance criteria
<!-- From the stage spec. Mark only what is actually verified. -->
| # | Criterion | Status | Evidence |
|---|-----------|--------|----------|
|   |           | ✅ done / 🟡 partial / ⏭️ later checkpoint | <!-- test name, command output, screenshot --> |

## ⚠️ Needs your attention
<!-- Read this first if you read nothing else. -->
- **Deviations from spec:** <!-- what differs and why, or "none" -->
- **Decisions for you:** <!-- questions only the human can answer, or "none" -->
- **Not done / deferred:** <!-- anything partial, untested or postponed, with the backlog entry -->

## Decisions & dependencies
- **ADRs:** <!-- links to new or updated docs/adr/*, or "none" -->
- **New dependencies:** <!-- name, why it is needed, why existing ones are not enough, or "none" -->
- **Config / env changes:** <!-- new variables (already in .env.example), migrations, or "none" -->

## Risk
<!-- What could break, and how it is contained (tests, flags, rollback). One or two lines. -->

## Checklist
- [ ] All quality gates green in CI (no new suppressions without an inline reason)
- [ ] No tests deleted, skipped or weakened. If any test was changed, the reason is stated above
- [ ] New and changed behaviour covered by tests. Diff coverage ≥ 85%
- [ ] PR within the size limit (~600 changed lines, excluding lock files, generated code and fixtures)
- [ ] Docs updated: `CLAUDE.md`, `docs/architecture.md`, ADRs, README (as applicable)
- [ ] `.env.example` and OpenAPI schema up to date
- [ ] No secrets, no `data/private/` content, no commented-out code, no stray `TODO`s
- [ ] Commits follow Conventional Commits and carry the `Agent:` trailer

---
<!-- Filled in by the reviewer model -->
**Reviewer:** <!-- model name --> · **Verdict:** <!-- approve / changes requested -->
