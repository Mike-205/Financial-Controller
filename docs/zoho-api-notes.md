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

## Gotchas
- [ ] Add your findings here as you build
