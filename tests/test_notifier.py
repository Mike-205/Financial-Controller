# test_notifier.py — Owner: Person 4
# Tests for notifier.py. No live email sends — resend.Emails.send is mocked.

import json
import pytest

import notifier

FIXTURE = "tests/fixtures/sample_claude_response.json"


def load_fixture():
    with open(FIXTURE) as f:
        return json.load(f)


# ── _build_email_body ───────────────────────────────────────────────────
def test_body_is_plain_text_no_html():
    body = notifier._build_email_body(load_fixture())
    for token in ("<html", "<body", "<div", "<p>", "<br", "</"):
        assert token not in body.lower(), f"HTML token {token!r} found in body"


def test_body_includes_all_present_flag_types():
    body = notifier._build_email_body(load_fixture())
    # Fixture has all three MVP types.
    assert "MIXED FUNDS" in body
    assert "DUPLICATE" in body
    assert "ROUND NUMBER" in body


def test_body_includes_flag_details():
    body = notifier._build_email_body(load_fixture())
    assert "Naivas" in body            # description from first flag
    assert "Ksh 3,500" in body         # formatted amount
    assert "Why:" in body
    assert "Action:" in body


def test_body_includes_summary_and_sheet_link(monkeypatch):
    monkeypatch.setenv("GOOGLE_SHEET_ID", "https://docs.google.com/spreadsheets/d/ABC/edit")
    report = load_fixture()
    body = notifier._build_email_body(report)
    assert report["summary"] in body
    assert "https://docs.google.com/spreadsheets/d/ABC/edit" in body


def test_body_skips_empty_flag_groups():
    report = load_fixture()
    # Keep only the DUPLICATE flag.
    report["flags"] = [f for f in report["flags"] if f["type"] == "DUPLICATE"]
    body = notifier._build_email_body(report)
    assert "DUPLICATE" in body
    assert "MIXED FUNDS" not in body
    assert "ROUND NUMBER" not in body


# ── send_notification ────────────────────────────────────────────────────
@pytest.fixture
def captured(monkeypatch):
    calls = []
    monkeypatch.setattr(notifier.resend.Emails, "send",
                        lambda params: calls.append(params) or {"id": "fake-id"})
    monkeypatch.setenv("FOUNDER_EMAIL", "founder@example.com")
    monkeypatch.setenv("ACCOUNTANT_EMAIL", "accountant@example.com")
    return calls


def test_send_uses_text_not_html(captured):
    notifier.send_notification(load_fixture())
    params = captured[0]
    assert "text" in params
    assert "html" not in params


def test_send_to_both_recipients(captured):
    notifier.send_notification(load_fixture())
    assert captured[0]["to"] == ["founder@example.com", "accountant@example.com"]


def test_send_subject_format(captured):
    notifier.send_notification(load_fixture())
    subject = captured[0]["subject"]
    assert "4 financial flags found" in subject
    assert "Mama Fua Enterprises" in subject
    assert "May 2026" in subject


def test_send_filters_unset_recipients(monkeypatch):
    calls = []
    monkeypatch.setattr(notifier.resend.Emails, "send",
                        lambda params: calls.append(params) or {"id": "x"})
    monkeypatch.setenv("FOUNDER_EMAIL", "founder@example.com")
    monkeypatch.delenv("ACCOUNTANT_EMAIL", raising=False)
    notifier.send_notification(load_fixture())
    assert calls[0]["to"] == ["founder@example.com"]


def test_send_raises_when_no_recipients(monkeypatch):
    monkeypatch.setattr(notifier.resend.Emails, "send", lambda params: {"id": "x"})
    monkeypatch.delenv("FOUNDER_EMAIL", raising=False)
    monkeypatch.delenv("ACCOUNTANT_EMAIL", raising=False)
    with pytest.raises(RuntimeError):
        notifier.send_notification(load_fixture())
