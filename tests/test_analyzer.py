# test_analyzer.py — Owner: Person 2
# Tests for analyzer.py using fixture data. No live API calls.

import asyncio
import json, pytest

import analyzer
from demo_data import DEMO_TRANSACTIONS, COMPANY_NAME, REPORT_MONTH

FIXTURE = "tests/fixtures/sample_claude_response.json"

def load_fixture():
    with open(FIXTURE) as f:
        return json.load(f)

def test_fixture_has_required_keys():
    r = load_fixture()
    for key in ("flags", "summary", "company", "month", "total_transactions_reviewed"):
        assert key in r, f"Missing key: {key}"

def test_fixture_has_four_flags():
    assert len(load_fixture()["flags"]) == 4

def test_flag_types_are_valid():
    valid = {"MIXED_FUNDS", "DUPLICATE", "ROUND_NUMBER"}
    for flag in load_fixture()["flags"]:
        assert flag["type"] in valid

def test_all_flags_have_action_required():
    for flag in load_fixture()["flags"]:
        assert flag.get("action_required"), f"Missing action_required: {flag}"


# ── analyze() — mocked Claude call, no live API ────────────────────────
# These mock the async client so the test runs offline. We feed the real
# DEMO_TRANSACTIONS in and return the fixture as Claude's "response".

class _FakeBlock:
    def __init__(self, text):
        self.text = text

class _FakeResponse:
    def __init__(self, text):
        self.content = [_FakeBlock(text)]

class _FakeMessages:
    def __init__(self, text):
        self._text = text
        self.calls = []
    async def create(self, **kwargs):
        self.calls.append(kwargs)
        return _FakeResponse(self._text)

class _FakeClient:
    def __init__(self, text):
        self.messages = _FakeMessages(text)


def _patch_client(monkeypatch, response_text):
    fake = _FakeClient(response_text)
    monkeypatch.setattr(analyzer, "_get_client", lambda: fake)
    return fake


def _run_analyze():
    return asyncio.run(
        analyzer.analyze(DEMO_TRANSACTIONS, COMPANY_NAME, REPORT_MONTH)
    )


def test_analyze_returns_four_flags(monkeypatch):
    with open(FIXTURE) as f:
        _patch_client(monkeypatch, f.read())
    result = _run_analyze()
    assert len(result["flags"]) == 4


def test_analyze_strips_backtick_fences(monkeypatch):
    # Claude often wraps JSON in ```json ... ``` — analyze() must strip it.
    with open(FIXTURE) as f:
        fenced = "```json\n" + f.read() + "\n```"
    _patch_client(monkeypatch, fenced)
    result = _run_analyze()
    assert result["company"] == COMPANY_NAME
    assert result["month"] == REPORT_MONTH
    assert len(result["flags"]) == 4


def test_analyze_flag_types_valid(monkeypatch):
    with open(FIXTURE) as f:
        _patch_client(monkeypatch, f.read())
    result = _run_analyze()
    valid = {"MIXED_FUNDS", "DUPLICATE", "ROUND_NUMBER"}
    for flag in result["flags"]:
        assert flag["type"] in valid


def test_analyze_uses_sonnet_and_sends_transactions(monkeypatch):
    with open(FIXTURE) as f:
        fake = _patch_client(monkeypatch, f.read())
    _run_analyze()
    call = fake.messages.calls[0]
    assert call["model"] == "claude-sonnet-4-6"
    # The demo data must actually reach the prompt.
    assert "Naivas" in call["messages"][0]["content"]
    assert COMPANY_NAME in call["messages"][0]["content"]
