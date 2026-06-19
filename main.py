# main.py — FastAPI entry point + pipeline orchestration
# Owner: Person 6 (feat/main-pipeline)
# Do not touch other modules — import and call only.

from fastapi import FastAPI
from dotenv import load_dotenv
import os

load_dotenv()

app = FastAPI(title="Kuzana AI Financial Controller")
USE_MOCK = os.getenv("ZOHO_MOCK", "true").lower() == "true"


@app.get("/")
def health():
    return {"status": "ok", "mock_mode": USE_MOCK}


@app.post("/run-analysis")
async def run_analysis():
    """
    Full pipeline:
    1. Fetch transactions (Zoho or mock)
    2. Analyze with Claude
    3. Write report to Google Sheets
    4. Send email notification
    5. Anchor report hash on Avalanche Fuji
    """
    # Step 1 — Transactions
    if USE_MOCK:
        from demo_data import DEMO_TRANSACTIONS, COMPANY_NAME, REPORT_MONTH
        transactions = DEMO_TRANSACTIONS
        company    = COMPANY_NAME
        month      = REPORT_MONTH
    else:
        from zoho_client import fetch_transactions
        transactions, company, month = await fetch_transactions()

    # Step 2 — AI Analysis
    from analyzer import analyze
    report = await analyze(transactions, company, month)

    # Step 3 — Google Sheets
    from report import write_report
    write_report(report)

    # Step 4 — Email
    from notifier import send_notification
    send_notification(report)

    # Step 5 — Avalanche
    from chain import anchor_report
    tx_hash = anchor_report(report)
    report["tx_hash"] = tx_hash

    return {
        "status": "complete",
        "company": company,
        "month": month,
        "flags_found": len(report.get("flags", [])),
        "tx_hash": tx_hash,
    }
