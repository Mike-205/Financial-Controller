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

# Resend testing default — swap for a verified domain sender in production.
FROM_ADDRESS = os.getenv("RESEND_FROM", "onboarding@resend.dev")

# Only the 3 MVP flag types, in display order. Label shown in the email.
FLAG_TYPES = [
    ("MIXED_FUNDS", "MIXED FUNDS"),
    ("DUPLICATE", "DUPLICATE"),
    ("ROUND_NUMBER", "ROUND NUMBER"),
]


def _format_flag(flag: dict) -> str:
    """One plain-text block for a single flag."""
    amount = flag.get("amount", "")
    try:
        amount_str = f"Ksh {float(amount):,.0f}"
    except (TypeError, ValueError):
        amount_str = f"Ksh {amount}"
    return (
        f"- {flag.get('date', '')} · {amount_str} · {flag.get('description', '')}\n"
        f"  Why: {flag.get('explanation', '')}\n"
        f"  Action: {flag.get('action_required', '')}"
    )


def _build_email_body(report: dict) -> str:
    """Build plain-text email from report flags. No HTML."""
    company = report.get("company", "your business")
    month   = report.get("month", "")
    total   = report.get("total_transactions_reviewed", "")
    flags   = report.get("flags", [])

    lines = [
        "Hello,",
        "",
        f"We reviewed {total} transactions for {company} ({month}) "
        f"and found {len(flags)} issue(s) that need your attention.",
    ]

    for type_key, label in FLAG_TYPES:
        group = [f for f in flags if f.get("type") == type_key]
        if not group:
            continue
        lines.append("")
        lines.append(f"{label} ({len(group)})")
        for flag in group:
            lines.append(_format_flag(flag))

    summary = report.get("summary")
    if summary:
        lines += ["", "Summary:", summary]

    sheet_url = os.getenv("GOOGLE_SHEET_ID")
    if sheet_url:
        lines += ["", "Full details in the Google Sheet:", sheet_url]

    lines += ["", "— Kuzana AI Financial Controller"]
    return "\n".join(lines)


def send_notification(report: dict):
    """Send flag report email to founder and accountant."""
    flags_count = len(report.get("flags", []))
    subject = f"⚠️ {flags_count} financial flags found — {report['company']} — {report['month']}"
    body    = _build_email_body(report)

    recipients = [r for r in (
        os.getenv("FOUNDER_EMAIL"),
        os.getenv("ACCOUNTANT_EMAIL"),
    ) if r]

    if not recipients:
        raise RuntimeError("No recipients set — check FOUNDER_EMAIL / ACCOUNTANT_EMAIL.")

    # Plain-text only: pass "text", never "html".
    response = resend.Emails.send({
        "from": FROM_ADDRESS,
        "to": recipients,
        "subject": subject,
        "text": body,
    })
    return response
