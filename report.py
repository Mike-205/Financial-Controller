# report.py — Google Sheets report builder
# Owner: Person 3 (feat/report)
#
# Responsibilities:
#   - Authenticate with Google Sheets via service account JSON
#   - Write one row per flag to the "Flags" tab
#   - Write one summary row to the "Summary" tab
#   - Use batch_update (NOT append_row in a loop) — faster and smoother for demo recording
#
# GOTCHA: Share your Google Sheet with the service account email address
#         (found in the credentials JSON as "client_email") or writes will fail silently.
#
# Sheet tabs expected:
#   "Flags"   — Date | Amount (Ksh) | Vendor | Flag Type | Explanation | Action Required | Tx Hash
#   "Summary" — Company | Month | Total Transactions | Flags Found | Run Timestamp | Tx Hash

import os, json
from datetime import datetime

import gspread
from gspread.exceptions import WorksheetNotFound
from google.oauth2.service_account import Credentials
from dotenv import load_dotenv

load_dotenv()

SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]

FLAGS_TAB   = "Flags"
SUMMARY_TAB = "Summary"

FLAGS_HEADER = [
    "Date", "Amount (Ksh)", "Vendor", "Flag Type",
    "Explanation", "Action Required", "Tx Hash",
]
SUMMARY_HEADER = [
    "Company", "Month", "Total Transactions",
    "Flags Found", "Run Timestamp", "Tx Hash",
]


def _require_dev_env():
    """Safety guard: only ever write to the dev sheet during development.
    SHEET_ENV must be explicitly set to 'dev' (see CLAUDE.md). Writing to
    production is intentionally blocked here — relax this for the final demo."""
    env = os.getenv("SHEET_ENV")
    if env is None:
        raise RuntimeError("SHEET_ENV is not set — expected 'dev' before writing.")
    if env != "dev":
        raise RuntimeError(
            f"Refusing to write: SHEET_ENV={env!r}, expected 'dev'. "
            "Never write to the production sheet during development."
        )


def _get_sheet():
    creds_path = os.getenv("GOOGLE_SHEETS_CREDENTIALS_JSON")
    sheet_id   = os.getenv("GOOGLE_SHEET_ID")
    creds = Credentials.from_service_account_file(creds_path, scopes=SCOPES)
    client = gspread.authorize(creds)
    # GOOGLE_SHEET_ID may be a full edit URL or a bare key — handle both.
    if sheet_id and sheet_id.startswith("http"):
        return client.open_by_url(sheet_id)
    return client.open_by_key(sheet_id)


def _get_or_create_ws(spreadsheet, title: str, header: list):
    """Return the worksheet, creating it (with a header row) if it's missing."""
    try:
        ws = spreadsheet.worksheet(title)
    except WorksheetNotFound:
        ws = spreadsheet.add_worksheet(title=title, rows=200, cols=len(header))
    if not ws.get_all_values():
        ws.batch_update([{"range": "A1", "values": [header]}])
    return ws


def _append_rows(ws, rows: list) -> int:
    """Append rows below existing content in ONE batch_update call.
    Returns the 1-based row index where writing started. (No append_row loop.)"""
    if not rows:
        return 0
    start = len(ws.get_all_values()) + 1
    ws.batch_update([{"range": f"A{start}", "values": rows}])
    return start


def _flag_to_row(flag: dict) -> list:
    # The analyzer flag schema has no "vendor" — fall back to "description".
    # "tx_hash" is filled in later by chain.py, so default to "".
    return [
        flag.get("date", ""),
        flag.get("amount", ""),
        flag.get("vendor") or flag.get("description", ""),
        flag.get("type", ""),
        flag.get("explanation", ""),
        flag.get("action_required", ""),
        flag.get("tx_hash", ""),
    ]


def write_report(report: dict) -> dict:
    """
    Write all flags + summary row to Google Sheets.
    report shape matches analyzer.py output.
    Returns a small summary of what was written (handy for the pipeline/tests).
    """
    _require_dev_env()

    spreadsheet = _get_sheet()
    flags = report.get("flags", [])

    # 1. Flags tab — all rows in a single batch_update.
    flags_ws = _get_or_create_ws(spreadsheet, FLAGS_TAB, FLAGS_HEADER)
    flag_rows = [_flag_to_row(f) for f in flags]
    _append_rows(flags_ws, flag_rows)

    # 2. Summary tab — one row, also via batch_update (no append_row).
    summary_ws = _get_or_create_ws(spreadsheet, SUMMARY_TAB, SUMMARY_HEADER)
    summary_row = [
        report.get("company", ""),
        report.get("month", ""),
        report.get("total_transactions_reviewed", ""),
        len(flags),
        datetime.now().isoformat(timespec="seconds"),
        report.get("tx_hash", ""),
    ]
    _append_rows(summary_ws, [summary_row])

    return {"flags_written": len(flag_rows), "summary_row": summary_row}
