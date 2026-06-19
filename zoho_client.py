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


def _load_tokens() -> dict:
    if os.path.exists(TOKEN_FILE):
        with open(TOKEN_FILE) as f:
            return json.load(f)
    return {}


def _save_tokens(tokens: dict):
    with open(TOKEN_FILE, "w") as f:
        json.dump(tokens, f)


async def refresh_access_token() -> str:
    """Exchange refresh token for a new access token."""
    tokens = _load_tokens()
    # TODO: POST to https://accounts.zoho.com/oauth/v2/token
    #       params: grant_type=refresh_token, refresh_token, client_id, client_secret
    #       Save new access_token back to TOKEN_FILE
    raise NotImplementedError("Person 1: implement token refresh")


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
    access_token = await refresh_access_token()
    org_id       = os.getenv("ZOHO_ORGANIZATION_ID")
    # TODO: GET {BASE_URL}/{org_id}/expenses?date_after=...
    raise NotImplementedError("Person 1: implement fetch_transactions")
