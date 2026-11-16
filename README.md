# Hroshyky

A personal expense tracker: a Telegram bot for input, a web admin panel and a Telegram Mini App, on one backend. Roadmap: [docs/ROADMAP.md](docs/ROADMAP.md). Current stage: [docs/stages/STAGE-1.md](docs/stages/STAGE-1.md).

Stage 1 is in progress. So far the repository contains the backend skeleton and the quality gates.

## Development setup

Requirements: [uv](https://docs.astral.sh/uv/), GNU Make, Git.

```bash
make install   # Python environment from the lock file
make hooks     # git hooks: the same gates as CI
make check     # every quality gate (the secrets gate needs gitleaks on PATH)
```

The gates and their tools are described in [docs/adr/0001-quality-gate-tooling.md](docs/adr/0001-quality-gate-tooling.md). Backend commands and conventions: [backend/CLAUDE.md](backend/CLAUDE.md).
