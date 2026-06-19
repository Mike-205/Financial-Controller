# notifier.py — Email notification via Resend
# Owner: Person 4 (feat/notifier)
#
# Responsibilities:
#   - Build a plain-text email body from the report dict
#   - Send to FOUNDER_EMAIL and ACCOUNTANT_EMAIL via Resend API
#   - Subject format: "⚠️ {n} financial flags found — {company} — {month}"
#
# Resend free tier: send from onboarding@resend.dev during testing.
# Upgrade to custom domain for production.
#
# Email body structure:
#   Greeting
#   → MIXED_FUNDS flags (if any)
#   → DUPLICATE flags (if any)
#   → ROUND_NUMBER flags (if any)
#   → Plain summary paragraph
#   → Link to Google Sheet

import os
import resend
from dotenv import load_dotenv

load_dotenv()

resend.api_key = os.getenv("RESEND_API_KEY")


def _build_email_body(report: dict) -> str:
    """Build plain-text email from report flags."""
    # TODO Person 4: implement
    # Group flags by type, format each group clearly
    # End with report["summary"] and a Google Sheets link
    raise NotImplementedError("Person 4: implement _build_email_body()")


def send_notification(report: dict):
    """Send flag report email to founder and accountant."""
    flags_count = len(report.get("flags", []))
    subject = f"⚠️ {flags_count} financial flags found — {report['company']} — {report['month']}"
    body    = _build_email_body(report)

    recipients = [
        os.getenv("FOUNDER_EMAIL"),
        os.getenv("ACCOUNTANT_EMAIL"),
    ]

    # TODO Person 4: call resend.Emails.send(...)
    raise NotImplementedError("Person 4: implement send_notification()")
