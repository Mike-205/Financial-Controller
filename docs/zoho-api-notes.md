# Zoho Books API Notes
> Person 1: fill this in as you discover things.

## Auth endpoints
- Authorization: `https://accounts.zoho.com/oauth/v2/auth`
- Token exchange: `https://accounts.zoho.com/oauth/v2/token`
- Scopes needed: `ZohoBooks.fullaccess.all`

## Data endpoints
- Expenses: `GET https://books.zoho.com/api/v3/{org_id}/expenses`
  - Params: `date_after`, `date_before`, `per_page` (max 200)
- Trial balance: `GET https://books.zoho.com/api/v3/{org_id}/reports/trialbalance`

## Token file shape (zoho_tokens.json — gitignored)
```json
{
  "access_token": "...",
  "refresh_token": "...",
  "expires_at": "2026-05-03T14:00:00"
}
```

## Token refresh (implemented)
- POST to `https://accounts.zoho.com/oauth/v2/token` with query params:
  `grant_type=refresh_token`, `refresh_token`, `client_id`, `client_secret`.
- Response includes `access_token` and `expires_in` (seconds, ~3600 = 1 hour).
  We compute and store `expires_at` from `expires_in`.
- The refresh token is long-lived; only the access token rotates.

## Expense → transaction field mapping (`_map_expense`)
| Pipeline key  | Zoho expense field                                |
| ------------- | ------------------------------------------------- |
| `date`        | `date`                                            |
| `amount`      | `total` (fallback `amount`) → cast to `float`     |
| `description` | `description` (fallback `account_name`)           |
| `vendor`      | `vendor_name` (fallback `paid_through_account_name`) |
| `reference`   | `reference_number` → `""` when absent (never None) |

## Gotchas
- [x] Auth requests use header `Authorization: Zoho-oauthtoken <token>` (NOT `Bearer`).
- [x] Zoho can return an error body with HTTP 200 — check for `access_token` in the
      JSON, don't rely on status code alone.
- [x] `ZOHO_MOCK` defaults to **true** (mock-on) if unset, so dev never hits live Zoho.
- [ ] Pagination: `per_page` max is 200. Multi-page fetch deferred to August scope.
- [ ] Live field names above are best-effort from docs — verify against a real
      expenses payload when OAuth is wired up, then tighten `_map_expense`.
