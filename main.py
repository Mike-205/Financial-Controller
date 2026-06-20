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


async def _get_transactions():
    """Step 1 — transactions from mock (demo_data) or live Zoho."""
    if USE_MOCK:
        from demo_data import DEMO_TRANSACTIONS, COMPANY_NAME, REPORT_MONTH
        return DEMO_TRANSACTIONS, COMPANY_NAME, REPORT_MONTH
    from zoho_client import fetch_transactions
    return await fetch_transactions()


@app.post("/run-analysis")
async def run_analysis():
    """
    Full pipeline (built up incrementally this session):
    1. Fetch transactions (Zoho or mock)
    2. Analyze with Claude
    3. Write report to Google Sheets
    4. Send email notification
    5. Anchor report hash on Avalanche Fuji
    """
    warnings = []
    step = "transactions"
    try:
        # Step 1 — Transactions (fatal: live Zoho needs OAuth tokens in mock=false)
        transactions, company, month = await _get_transactions()

        # Step 2 — AI Analysis (fatal: produces the flags)
        step = "analyze"
        from analyzer import analyze
        report = await analyze(transactions, company, month)

        # Step 3 — Google Sheets (side effect; non-fatal)
        step = "report"
        try:
            from report import write_report
            write_report(report)
        except Exception as e:
            warnings.append(f"report: {type(e).__name__}: {e}")

        # Step 4 — Email (side effect; non-fatal).
        # NOTE: Resend test mode only delivers to the account owner's own address,
        # so a multi-recipient send raises here. We log it and keep the pipeline alive.
        step = "notify"
        try:
            from notifier import send_notification
            send_notification(report)
        except Exception as e:
            warnings.append(f"notifier: {type(e).__name__}: {e}")

        # Step 5 — Avalanche Fuji anchor (fatal: produces the tx_hash we return)
        step = "anchor"
        from chain import anchor_report
        tx_hash = anchor_report(report)
        report["tx_hash"] = tx_hash

        return {
            "status": "complete",
            "company": company,
            "month": month,
            "flags_found": len(report.get("flags", [])),
            "tx_hash": tx_hash,
            "warnings": warnings,
        }
    except Exception as e:
        # A fatal step failed — return a clean error instead of a raw 500.
        return {
            "status": "error",
            "failed_step": step,
            "detail": f"{type(e).__name__}: {e}",
            "warnings": warnings,
        }
