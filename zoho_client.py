# zoho_client.py — Zoho Books OAuth2 + data fetching
# Owner: Person 1 (feat/zoho)
#
# Responsibilities:
#   - OAuth2 authorization flow (redirect + callback)
#   - Token refresh (access token expires every 1 hour)
#   - Fetch last 30 days of transactions
#   - Return list matching DEMO_TRANSACTIONS shape in demo_data.py
#
# GOTCHA: Always refresh the access token before every API call.
#         Store refresh token in zoho_tokens.json (gitignored).

import os, json, httpx
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

TOKEN_FILE = "zoho_tokens.json"
BASE_URL   = "https://books.zoho.com/api/v3"
TOKEN_URL  = "https://accounts.zoho.com/oauth/v2/token"


def _mock_enabled() -> bool:
    """ZOHO_MOCK=true → use demo_data.py, never touch the network.
    Defaults to True (mock-on) so we never accidentally hit live Zoho."""
    return os.getenv("ZOHO_MOCK", "true").strip().lower() in ("1", "true", "yes")


def _load_tokens() -> dict:
    if os.path.exists(TOKEN_FILE):
        with open(TOKEN_FILE) as f:
            return json.load(f)
    return {}


def _save_tokens(tokens: dict):
    with open(TOKEN_FILE, "w") as f:
        json.dump(tokens, f)


async def refresh_access_token() -> str:
    """Exchange the stored refresh token for a new access token.

    Zoho access tokens expire every 1 hour, so we refresh before each fetch.
    The refresh token itself is long-lived and stays in zoho_tokens.json.
    """
    tokens = _load_tokens()
    refresh_token = tokens.get("refresh_token")
    if not refresh_token:
        raise RuntimeError(
            "No refresh_token in zoho_tokens.json — run the OAuth flow first "
            "(or keep ZOHO_MOCK=true during development)."
        )

    params = {
        "grant_type":    "refresh_token",
        "refresh_token": refresh_token,
        "client_id":     os.getenv("ZOHO_CLIENT_ID"),
        "client_secret": os.getenv("ZOHO_CLIENT_SECRET"),
    }

    async with httpx.AsyncClient() as client:
        resp = await client.post(TOKEN_URL, params=params)
        resp.raise_for_status()
        data = resp.json()

    # Zoho returns an error payload with HTTP 200, so check the body too.
    if "access_token" not in data:
        raise RuntimeError(f"Zoho token refresh failed: {data}")

    access_token = data["access_token"]
    expires_in   = data.get("expires_in", 3600)  # seconds; default 1 hour
    tokens["access_token"] = access_token
    tokens["expires_at"]   = (datetime.now() + timedelta(seconds=expires_in)).isoformat()
    _save_tokens(tokens)
    return access_token


def _map_expense(raw: dict) -> dict:
    """Map a Zoho expense object into the pipeline transaction shape.

    Contract (see CLAUDE.md): keys are date, amount, description, vendor,
    reference — reference is "" when absent, never None.
    """
    return {
        "date":        raw.get("date", ""),
        "amount":      float(raw.get("total", raw.get("amount", 0)) or 0),
        "description": raw.get("description") or raw.get("account_name", ""),
        "vendor":      raw.get("vendor_name") or raw.get("paid_through_account_name", ""),
        "reference":   raw.get("reference_number") or "",
    }


async def fetch_transactions() -> tuple[list, str, str]:
    """
    Pull last 30 days of expenses from Zoho Books.
    Returns: (transactions, company_name, month_label)
    Each transaction must match this shape:
    {
        "date": "YYYY-MM-DD",
        "amount": float,
        "description": str,
        "vendor": str,
        "reference": str   # empty string if none
    }
    """
    # ── Development / test path: never touches the network ──────────
    if _mock_enabled():
        from demo_data import DEMO_TRANSACTIONS, COMPANY_NAME, REPORT_MONTH
        return DEMO_TRANSACTIONS, COMPANY_NAME, REPORT_MONTH

    # ── Live path (only when ZOHO_MOCK=false) ───────────────────────
    access_token = await refresh_access_token()
    org_id       = os.getenv("ZOHO_ORGANIZATION_ID")
    if not org_id:
        raise RuntimeError("ZOHO_ORGANIZATION_ID is not set")

    today       = datetime.now()
    date_after  = (today - timedelta(days=30)).strftime("%Y-%m-%d")
    date_before = today.strftime("%Y-%m-%d")

    headers = {"Authorization": f"Zoho-oauthtoken {access_token}"}
    params  = {
        "organization_id": org_id,
        "date_after":      date_after,
        "date_before":     date_before,
        "per_page":        200,  # max page size; pagination is an August concern
    }

    async with httpx.AsyncClient() as client:
        resp = await client.get(f"{BASE_URL}/{org_id}/expenses", headers=headers, params=params)
        resp.raise_for_status()
        data = resp.json()

    expenses     = data.get("expenses", [])
    transactions = [_map_expense(e) for e in expenses]
    company_name = (data.get("organization", {}) or {}).get("name", "")
    month_label  = today.strftime("%B %Y")
    return transactions, company_name, month_label
