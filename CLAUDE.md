# Kuzana AI Financial Controller — CLAUDE.md

> Read this entire file before writing any code. This is the source of truth.

## What this project is

AI Financial Controller for Kenyan SMEs.
Pipeline: Zoho Books → Claude Analysis → Google Sheets → Email → Avalanche audit trail.
Submission for Kuzana x MiniHack Bounty 1. Stage 1 deadline: June 27, 2026.

## Team — who owns what

| File           | Branch             | Owner    | Responsibility                          |
| -------------- | ------------------ | -------- | --------------------------------------- |
| zoho_client.py | feat/zoho          | Person 1 | OAuth2 + fetch transactions             |
| analyzer.py    | feat/analyzer      | Person 2 | Claude prompt + JSON parsing            |
| report.py      | feat/report        | Person 3 | Write flags to Google Sheets            |
| notifier.py    | feat/notifier      | Person 4 | Send email via Resend                   |
| chain.py       | feat/chain         | Person 5 | SHA-256 hash + Avalanche Fuji tx        |
| main.py        | feat/main-pipeline | Person 6 | FastAPI routes + pipeline orchestration |

Touch only your file and your test. Person 6 integrates last.

## MVP scope — DO NOT expand before Stage 1

Only 3 flag types:

1. MIXED_FUNDS — personal transactions in business account
2. DUPLICATE — same vendor, same amount, within 7 days
3. ROUND_NUMBER — exact round amounts to individuals, no invoice reference

August scope (ignore for now): cash flow scoring, dashboard UI, multi-company, real-time monitoring.

## Always use mock data during development

ZOHO_MOCK=true in .env → imports from demo_data.py.
Never call live Zoho API during development or testing.

## Transaction shape (this is the contract between all modules)

```python
{
    "date": "YYYY-MM-DD",   # string
    "amount": float,         # in Kenyan Shillings
    "description": str,
    "vendor": str,
    "reference": str         # empty string if none — never None
}
```

## Kenyan context for the AI prompt

- Amounts are in Kenyan Shillings (Ksh)
- Personal merchants: Naivas, Carrefour, Quickmart, personal KPLC prepaid, M-Pesa send money
- Round number threshold: amounts divisible by 5000 paid to individuals with no reference

## Known gotchas — read before touching these files

- analyzer.py: Claude sometimes wraps JSON in backticks. Strip with regex before json.loads()
- zoho_client.py: access token expires every 1 hour. Always refresh before API call
- chain.py: gas = (21000 + len(data_bytes) _ 68) _ 1.2 — the 20% buffer is not optional
- report.py: use batch_update not append_row in a loop — smoother on the demo recording

## Never do this

- Never commit .env, credentials.json, or zoho_tokens.json (all gitignored)
- Never log or print API keys
- Never call live Claude or Zoho APIs in unit tests — use tests/fixtures/
- Never write to the production Google Sheet during dev (SHEET_ENV must be dev)
