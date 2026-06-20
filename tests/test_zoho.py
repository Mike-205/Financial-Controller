# test_zoho.py — Owner: Person 1
# Tests for zoho_client.py. Mock-only — never makes a live API call.

import asyncio
import os

import zoho_client
from demo_data import DEMO_TRANSACTIONS, COMPANY_NAME, REPORT_MONTH

REQUIRED_KEYS = {"date", "amount", "description", "vendor", "reference"}


def _run(coro):
    return asyncio.run(coro)


def _force_mock(monkeypatch):
    monkeypatch.setenv("ZOHO_MOCK", "true")


def test_fetch_returns_three_tuple(monkeypatch):
    _force_mock(monkeypatch)
    result = _run(zoho_client.fetch_transactions())
    assert isinstance(result, tuple)
    assert len(result) == 3


def test_fetch_returns_demo_data(monkeypatch):
    _force_mock(monkeypatch)
    transactions, company, month = _run(zoho_client.fetch_transactions())
    assert transactions == DEMO_TRANSACTIONS
    assert company == COMPANY_NAME
    assert month == REPORT_MONTH


def test_transactions_match_contract_shape(monkeypatch):
    _force_mock(monkeypatch)
    transactions, _, _ = _run(zoho_client.fetch_transactions())
    assert len(transactions) > 0
    for tx in transactions:
        missing = REQUIRED_KEYS - set(tx.keys())
        assert not missing, f"Missing keys {missing} in: {tx}"
        assert isinstance(tx["reference"], str)  # never None
        assert isinstance(tx["amount"], (int, float))


def test_mock_never_hits_network(monkeypatch):
    # If the mock branch is correct, refresh_access_token must not be called.
    _force_mock(monkeypatch)

    async def _boom():
        raise AssertionError("refresh_access_token was called under ZOHO_MOCK=true")

    monkeypatch.setattr(zoho_client, "refresh_access_token", _boom)
    transactions, _, _ = _run(zoho_client.fetch_transactions())
    assert transactions == DEMO_TRANSACTIONS


def test_mock_defaults_on_when_env_missing(monkeypatch):
    # Safety: an unset ZOHO_MOCK must default to mock-on, not live.
    monkeypatch.delenv("ZOHO_MOCK", raising=False)
    assert zoho_client._mock_enabled() is True


def test_map_expense_shape():
    raw = {
        "date": "2026-05-03",
        "total": 3500,
        "description": "Naivas Supermarket",
        "vendor_name": "Naivas",
        # no reference_number → must become ""
    }
    tx = zoho_client._map_expense(raw)
    assert set(tx.keys()) == REQUIRED_KEYS
    assert tx["reference"] == ""
    assert tx["amount"] == 3500.0
    assert isinstance(tx["amount"], float)
