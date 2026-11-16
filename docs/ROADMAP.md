# Hroshyky — AI-Driven Development Roadmap

## Principle

All code is written by AI agents. The human (Vadym) owns the specs, the decisions and acceptance.
Specs describe **what the result must be**. Architecture, data model, libraries and internal design are entirely the implementing model's call. Significant decisions are recorded as ADRs.

## Stage lifecycle

Every stage goes through the same loop:

1. **Spec**: `docs/stages/STAGE-N.md` covers scope, expected behaviour and acceptance criteria. The human approves it before work starts.
2. **Plan**: the agent reads the spec and `CLAUDE.md`, proposes an architecture and a plan with checkpoints in plan mode, and waits for approval.
3. **Implementation**: one branch and one PR per checkpoint, following the Git rules in `CLAUDE.md`.
4. **Independent review**: a different model reviews each PR in a fresh context, checking it against the spec and acceptance criteria. It does not see the author's conversation. Findings go back to the author.
5. **Human acceptance**: the human runs the acceptance criteria and uses the product for a week. Bugs become hotfixes or go into the next stage.
6. **Knowledge capture**: the agent updates `CLAUDE.md`, `docs/adr/` and `docs/architecture.md`, so the next stage starts with accurate context.

## Stages

| # | Stage | Model | Effort | Depends on |
|---|-------|-------|--------|------------|
| 1 | Backend, Telegram bot, receipts (eKasa QR + photo recognition), Excel import | **Fable 5.2** | ★★★★★ | — |
| 2 | Vue admin panel | Opus 5.5 / Sonnet 5.5 | ★★★ | 1 |
| 3 | Telegram Mini App | Sonnet 5.5 | ★★ | 1 |
| 4 | Banks: Monobank, CSV statements, matching bank transactions with receipts | Opus 5.5 | ★★★★ | 1 |
| 5 | Budgets, notifications, subscription detection, analytics | Sonnet 5.5 | ★★★ | 1, 4 |
| 6 | Production: deployment, monitoring, backups, LLM quality evals | Sonnet 5.5 | ★★ | all |

Stage 1 is reviewed by Opus 5.5. Every other stage is reviewed by a model different from its author.

### Stage 1: Core (Fable)
Everything the later stages build on. Details are in `docs/stages/STAGE-1.md`.
- Expenses can be added from Telegram by text or by a receipt photo
- Receipts with an eKasa QR code are pulled with full line items, and receipts without one are recognised from the photo
- Items are categorised automatically, and the system learns from corrections
- The full Excel history is imported and reconciled
- A documented, stable API is ready for the admin panel and the Mini App

### Stage 2: Admin panel (Vue)
Detailed work with data: a transaction table with filters and bulk editing, receipt details with items, management of categories, shops, accounts and categorisation rules, reports and charts, and Excel re-import from the UI.

### Stage 3: Telegram Mini App
Lightweight viewing inside Telegram: the current month, top categories, recent transactions and receipt details. It must open fast.

### Stage 4: Banks
Automatic import from Monobank and from Tatra banka and Revolut statements. A bank transaction and the receipt for the same purchase must never be counted twice.

### Stage 5: Money features
Per-category budgets with alerts in the bot, weekly and monthly digests, detection of recurring payments (YouTube, Apple, Lifecell…), and product price history.

### Stage 6: Production
Deployment to a VPS, backups, error monitoring, and an LLM eval suite running in CI.

## Before Stage 1 starts
- [ ] Telegram bot token (@BotFather) and own Telegram ID
- [ ] LLM provider API key: **optional**, development starts without one (see the LLM constraint in `docs/stages/STAGE-1.md`). It is needed later for photo recognition, the LLM categorisation fallback and the eval run
- [ ] 15–20 receipt photos: ~10 with an eKasa QR code, ~5 without a QR code or with an unreadable one, 2–3 foreign or unusual ones. They go into `data/private/receipts/` with an `expected.yaml` (format below), and this becomes the eval set

```yaml
# data/private/receipts/expected.yaml
- file: kaufland-2026-11-14.jpg
  merchant: Kaufland
  date: 2026-11-14
  total: 23.47
  currency: EUR
  has_qr: true
  items:            # optional, but makes item and category accuracy measurable
    - name: Молоко
      total: 0.79
      category: Продукти
```
- [ ] The Excel file, placed in `data/private/` (never committed)
- [ ] Answers to "Open decisions" in `docs/stages/STAGE-1.md` (defaults are provided)
