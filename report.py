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
import gspread
from google.oauth2.service_account import Credentials
from dotenv import load_dotenv

load_dotenv()

SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]


def _get_sheet():
    creds_path = os.getenv("GOOGLE_SHEETS_CREDENTIALS_JSON")
    sheet_id   = os.getenv("GOOGLE_SHEET_ID")
    creds = Credentials.from_service_account_file(creds_path, scopes=SCOPES)
    client = gspread.authorize(creds)
    return client.open_by_key(sheet_id)


def write_report(report: dict):
    """
    Write all flags + summary row to Google Sheets.
    report shape matches analyzer.py output.
    """
    # TODO Person 3: implement
    # 1. Open sheet with _get_sheet()
    # 2. Build rows from report["flags"]
    # 3. batch_update to "Flags" tab
    # 4. Append summary row to "Summary" tab
    raise NotImplementedError("Person 3: implement write_report()")
