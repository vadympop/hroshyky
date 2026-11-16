# Stage 1 — Core: backend, Telegram bot, receipts, Excel import

**Implementer:** Claude Fable 5.2 · **Reviewer:** Opus 5.5 · **Approver:** Vadym

Read this document and `CLAUDE.md` in full. Then, in plan mode, propose the architecture, the data model and a plan split into checkpoints, and wait for approval. **This spec defines only the expected result. Every architectural and technical decision is yours**, and the key ones go into `docs/adr/`. If reality contradicts the spec (for example, the eKasa service behaves differently), do not work around it silently: write it up and flag it.

---

## 1. Goal

A personal expense tracker that fully replaces the Excel spreadsheet. The main flow: come back from a shop, send a photo of the receipt to Telegram, and a few seconds later every line item is saved with a category. The secondary flow: type something like `coffee 3.5` and it is saved. The whole Excel history is imported and reconciled to the cent.

Stage 1 is the foundation for the Vue admin panel (stage 2), the Telegram Mini App (stage 3), bank imports (stage 4) and budgets (stage 5). The result must not block those stages, but only the stage 1 scope is implemented.

## 2. Scope

**In scope:** backend with an API, Telegram bot, receipt processing (eKasa QR and photo recognition), automatic categorisation with learning, Excel import with reconciliation, currencies, authentication for the future web clients, local run via Docker Compose, CI, tests.

**Out of scope:** any web UI, bank integrations, budgets and alerts, shared/multi-user features in the UI, production deployment.

## 3. Fixed constraints

These are the only technical constraints. Everything else is up to you.
- Backend in Python with FastAPI, PostgreSQL as the main database, everything runs with `docker compose up`.
- Python tooling goes through **uv**: project and dependency management (`pyproject.toml` + committed `uv.lock`), virtual environments, Python version pinning, and running every command (`uv run …`). Docker images are also built with uv from the lock file. No pip, Poetry or requirements files.
- **Base currency is EUR.** All totals and reports are in EUR. Amounts in other currencies (mostly UAH) keep their original amount and currency and are converted to EUR at the historical rate of their date.
- Amounts are exact to the cent: no rounding drift anywhere, totals always add up.
- Single user now, but data is owned per user, so multi-user later does not require a migration of meaning.
- Bot interface language: Ukrainian. Code, docs, commits: English.
- Times are shown in the Europe/Bratislava time zone.
- Configuration comes from a git-ignored `.env` at the repo root. `.env.example` already defines `TELEGRAM_BOT_TOKEN`, `TELEGRAM_ALLOWED_USER_IDS` and `LLM_API_KEY`: keep these names, add new variables with descriptions. You cannot read `.env` itself: rely on `.env.example`, and fail fast with a clear error when a required variable is missing.
- **The system must be fully usable without an LLM API key.** No key is available at the start of development. Everything that does not strictly need an LLM must work without one. LLM features turn on once a key is configured. Switching the LLM provider (hosted API or a local model) is a configuration change, not a code change.

## 4. Expected behaviour

### 4.1 Telegram bot
- Only allowlisted Telegram users can use it.
- **Quick add by text.** All of these must work without an LLM:
  - `кава 3.5` · `лідл 23.40` · `молоко 2x0.79` · `яблука 1.2кг 0.99`
  - a multi-line message where the first line may name a shop and/or a date (`кауф вчора`) and each next line is an item
  - `+270 налік` → income
  - `500 грн епл` → an expense in UAH, converted to EUR

  Free-form text that the rules do not cover (`вчора в кауфі на 23.40 продукти`) may be understood with an LLM.
- **Receipt photo or file (image or PDF).** The user immediately sees that processing has started. Then a confirmation card appears with the shop, date, account, items with categories, total and any warnings. From the card the user can save, change an item's category, the shop, the date or the account, or cancel. Changing a category is a pick from a list, not typing.
- The same receipt sent twice → "already added", pointing to the existing transaction.
- **Commands:** today / week / month summary (total, top categories, comparison with the previous period), last transactions, undo, choose default account, get a login link for the admin panel, help.
- The user never sees a stack trace. If any processing step fails, the user still gets an editable draft.

### 4.2 Receipts
- **eKasa QR codes (Slovak receipts).** Domain facts:
  - A QR code holds either a receipt ID (`O-` + 32 hex characters, online receipts) or, for offline receipts, a string `OKP:cash_register_code:yyMMddHHmmss:receipt_number:total`.
  - The Slovak Financial Administration exposes receipt data publicly (opd.financnasprava.sk; third-party apps call `POST https://ekasa.financnasprava.sk/mdu/api/v1/opd/receipt/find` with `{"receiptId": …}`). **The first task of this area is to verify the current endpoint, the request formats for both QR types and the response structure.** Document the findings in `docs/integrations/ekasa.md` and save 3–5 real responses (anonymised if needed) as test fixtures.
  - Offline receipts may not exist in the system yet when they are scanned.
- Expected result for a receipt with a QR code: shop (with its company ID and address), date and time, every line item (name, quantity, price, VAT rate), discounts and deposit returns handled correctly, and a total that matches the receipt.
- If the QR code is missing or unreadable, or the eKasa lookup fails, the receipt is recognised from the photo with a vision-capable LLM. Items, discounts and total must be consistent. If they are not, the draft is marked for review and the card shows a warning.
- Receipts in other languages and currencies (Czech, Hungarian, Ukrainian…) also work.
- With no LLM configured, a receipt without a usable QR code becomes a draft with the photo attached, which the user fills in manually.
- An offline receipt that is not found yet produces a draft from the photo. Its eKasa data is fetched automatically later, and any differences are shown to the user.
- The original receipt image is stored and linked to the transaction.

### 4.3 Categorisation
- Every item gets a category automatically. Item names from receipts (often abbreviated Slovak, e.g. `MLIEKO POL. 1,5% 1L`) also get a human-readable Ukrainian name that reuses the user's own vocabulary ("Молоко", "Кайзерки") instead of inventing new names.
- The system learns from the user: after a correction, the same or a similar item is categorised correctly next time **without an LLM call**.
- The Excel history (≈960 items with Ukrainian names and categories) is used as the starting knowledge.
- For every item it is visible how its category was decided (learned, rule, similar item, LLM, user, Excel), so accuracy can be measured later.
- LLM usage is cost-conscious: no LLM call when the answer is already known.
- With no LLM configured, items the system does not recognise are marked as uncategorised in the confirmation card, and the user picks the category (which teaches the system as usual).

### 4.4 Currencies
- EUR is the base currency (see 3).
- Historical EUR rates are available for any date (ECB data or equivalent). Monthly average UAH rates from the Excel file are imported and used for the Excel history.

### 4.5 API and authentication
- The API covers everything the admin panel and the Mini App will need to read and edit: transactions with items, categories, shops (with aliases and merging), accounts, the learned product dictionary, categorisation rules, receipts with images, imports (upload, dry run, apply, report), reports (by month, category, shop, account, product price over time) and exchange rates. Lists can be filtered, sorted and paginated.
- The API is fully documented by its OpenAPI schema. The schema is committed, and CI fails if it is out of date, so the frontends of stages 2–3 can be built without touching the backend.
- Admin panel login works through a one-time link sent by the bot (no passwords). The link is short-lived and single-use. Stage 3 will add Telegram Mini App authentication, and the design must allow it.

### 4.6 LLM observability
For every LLM call it is possible to see the prompt, the response, latency and cost. Prompts are versioned in the repository.

## 5. Excel import

Available as a CLI command (with `--dry-run` and a report file) and through the API. Running it again on the same file creates no duplicates. Running it on an updated file updates the changed rows.

### 5.1 File format (analysed)
- One sheet per month: `Січень` … `Грудень` 2025 (there is **no** `Липень` sheet) plus `Січень 26`. The year and month come from cell A1 (`Витрати 2025 Січень`), not from the sheet name.
- **Main table**, from row 3: A date · B item name · C category · D quantity (fractions mean weight in kg, e.g. 0.562) · E unit price in € · F formula `=D*E` · G price in ₴ (always empty) · H shop alias.
  - Adjacent rows with the same date, shop and payment section form one purchase.
  - E sometimes holds a formula (`=1.28-0.38` is a discount, `=1.39/0.6` is a price per kg, `=4.59/30`). Use the calculated value. F is unreliable (it can be `.`), so the item total is D × E.
  - A section header in column A (`Оплачено через пумб:`, `Оплачено через єврову:`) sets the payment account for the rows that follow until the block ends.
  - 2 rows have no category → "Без категорії", flagged for review.
  - Shop aliases: Кауф = Kaufland, Лідл = Lidl, Біла = Billa, Теско = Tesco, Дм = dm drogerie, Пепко = Pepco, Ікеа = IKEA, Терно = Terno, Автомат = vending machine. Unknown aliases (`Шефт`) become shops with that name.
- **Side block, columns J:N.** This is a free layout, not a table, and is recognised by the labels in column J:
  - `Стірки`: K count × L price → one monthly expense, category "Прання", date known only to the month.
  - `Інші витрати` → a sub-table `Дата | Назва | Сума` (J/K/L). The date is often empty, which means the date is known only to the month. Columns M/N hold three kinds of notes: an account (`моно`, `татра`, `Пумб`, `еврова`), an original UAH amount (`250грн`), or free text (`з грошей на дн`), which becomes a note.
  - `З іншої карти` (label in column K, March–June) → a second sub-table of the same shape. The account comes from M/N or is "Інша карта".
  - `З евро карти:` (August): `147евро | младость` → expenses from the "Єврова карта" account.
  - `Надходження:` (from August) → income. `11000грн` with the formula `=11000/48.7` means income of 11000 UAH at a rate of 48.7. Numbers in K have their description in L.
  - `Середній курс €` (M5/N5) → monthly average UAH/EUR rate. `-` means none.
  - Free-text lines such as `-35евро (за закуп який оплатив іншими картками)` are not imported. They are listed in the report as unrecognised.
- **Anomalies to handle and report:**
  - `Серпень` has the date `2025-05-08` in "Інші витрати", outside the sheet's month → keep the day, use the sheet's month, flag for review.
  - `Січень 26` has an empty main table, and its side block is a copy of December (J2 = `Грудень`). When the month label in J2 does not match A1, skip the side block with a warning (a flag overrides this).
  - Spelling variants (`Шампіньйони`/`Шампіньони`, `Кайзерка`/`Кайзерки`, `Лайфсел`/`Лайфселл`/`Lifecell`) are treated as one product. Every merge is listed in the report.

### 5.2 Reconciliation (main correctness check)
Each sheet has a cached `Сума` value in K5. Its formula is `SUMIFS` over the main table within the date range written in the formula, plus `M3` (laundry), plus `K4` (the sum of the "Інші витрати" range written in its own formula).
- The import parses that sheet's K5 and K4 formulas, recomputes the total from the imported data by the same rules, and it must **match the cached value to €0.01 on every sheet**.
- The report also shows the full monthly total of everything imported, including blocks the formula ignores, and explains the difference.

### 5.3 Report
Per month: purchases, items, income entries, totals in EUR. Plus merged names, unrecognised rows, anomalies, the reconciliation table, and the rows flagged for review.

## 6. Quality
- Automated tests cover: QR parsing (both formats and garbage input), every quick-add form from 4.1, the Excel import (a synthetic test workbook generated in tests reproduces every quirk from 5.1, and a test against the real file runs only when the file is present), the eKasa integration on recorded fixtures, and the main API flows.
- No real network or LLM calls in regular tests or CI.
- A separate, manually triggered eval run uses real LLM calls on `data/private/receipts/` with expected values and reports total accuracy, item accuracy and category accuracy.
- Lint, type checks and tests run in CI and must be green.

## 7. Acceptance criteria
1. From a clean clone + `.env`, `docker compose up` starts the whole system. All quality gates from `CLAUDE.md` are enforced in CI and green.
2. The Excel dry run produces the report from 5.3, and reconciliation (5.2) matches on every sheet.
3. Applying the import twice in a row creates 0 new records on the second run.
4. A receipt photo with an eKasa QR code → a correct confirmation card (items, shop, total) in under 10 s (median). Sending it again → "already added".
5. *(With an LLM key.)* A receipt photo without a QR code → a recognised draft. On the eval set the total is correct on ≥ 90% of receipts.
6. *(With an LLM key.)* After the Excel import, ≥ 80% of eKasa receipt items on the eval set get the correct category with no correction. After a correction, a similar receipt does not trigger an LLM call for the corrected items (visible in LLM traces).
6a. *(Without an LLM key.)* Criteria 1–4 and 7–10 pass. Receipts without a QR code produce a manual draft with the photo. Items already learned from Excel or from corrections are still categorised automatically.
7. Every quick-add form from 4.1 is parsed without an LLM.
8. The bot's month summary equals the API month report for the same period.
9. The bot login link → an authenticated session that can call protected API endpoints.
10. The committed OpenAPI schema is up to date. `docs/` contains an architecture overview, `integrations/ekasa.md`, ADRs for key decisions and a README with setup and usage.

## 8. Checkpoints (required order of delivery)
Each checkpoint is a PR (see Git rules in `CLAUDE.md`) with a summary: what was done, deviations from the spec, decisions the human needs to make.
1. Foundation: repository, local run, CI with **every quality gate from `CLAUDE.md`** (each shown to fail on a deliberate violation in the PR description), pre-commit hooks, data model, authentication.
2. Excel import + reconciliation (gives real data and the starting dictionary for everything after).
3. Bot: quick add, summaries, editing.
4. eKasa: investigation → integration → QR receipts.
5. Photo recognition + categorisation with learning + LLM observability.
6. Complete API, OpenAPI schema, documentation, full acceptance run.

## 9. Open decisions (defaults apply if not answered)
| Question | Default |
|---|---|
| Categories: keep the 16 from Excel, or merge some (Кайзерки + Булочки + Випічка, Йогурти → Молочне)? | Import as is, merge later in the admin panel |
| Which bank is "Єврова карта"? | A separate account named "Єврова карта" |
| Default account for new expenses | Tatra |
| `Січень 26` side block | Skip with a warning |
