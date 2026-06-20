# test_chain.py — Owner: Person 5
# Tests for chain.py. No live Fuji transactions — Web3 is mocked.

import json
from types import SimpleNamespace

import pytest

import chain

FIXTURE = "tests/fixtures/sample_claude_response.json"


def load_fixture():
    with open(FIXTURE) as f:
        return json.load(f)


# ── _hash_report ─────────────────────────────────────────────────────────
def test_hash_is_sha256_hex():
    h = chain._hash_report({"test": True})
    assert len(h) == 64
    int(h, 16)  # raises if not valid hex


def test_hash_is_deterministic_regardless_of_key_order():
    a = chain._hash_report({"a": 1, "b": 2, "company": "X"})
    b = chain._hash_report({"company": "X", "b": 2, "a": 1})
    assert a == b  # sort_keys makes ordering irrelevant


def test_hash_changes_with_content():
    assert chain._hash_report({"x": 1}) != chain._hash_report({"x": 2})


def test_hash_matches_sort_keys_sha256():
    import hashlib
    report = load_fixture()
    expected = hashlib.sha256(
        json.dumps(report, sort_keys=True, ensure_ascii=False).encode()
    ).hexdigest()
    assert chain._hash_report(report) == expected


# ── _estimate_gas (mandatory 20% buffer) ──────────────────────────────────
def test_gas_formula_matches_spec():
    data = b"x" * 64
    assert chain._estimate_gas(data) == int((21000 + 64 * 68) * 1.2)


def test_gas_includes_20pct_buffer():
    data = b"x" * 64
    raw = 21000 + 64 * 68
    assert chain._estimate_gas(data) == int(raw * 1.2)
    assert chain._estimate_gas(data) > raw  # buffer present


# ── _build_transaction ─────────────────────────────────────────────────────
class FakeEth:
    gas_price = 25_000_000_000
    def get_transaction_count(self, address):
        return 7


def test_build_transaction_uses_fuji_and_zero_value():
    w3 = SimpleNamespace(eth=FakeEth())
    report_hash = chain._hash_report({"test": True})
    tx = chain._build_transaction(w3, "0xSENDER", report_hash)
    assert tx["chainId"] == 43113          # Fuji testnet, never mainnet
    assert tx["value"] == 0
    assert tx["from"] == "0xSENDER"
    assert tx["to"] == "0xSENDER"          # self-transfer anchor
    assert tx["nonce"] == 7
    assert tx["gasPrice"] == 25_000_000_000


def test_build_transaction_embeds_hash_and_gas():
    w3 = SimpleNamespace(eth=FakeEth())
    report_hash = chain._hash_report({"test": True})
    tx = chain._build_transaction(w3, "0xSENDER", report_hash)
    # data is "0x" + hex of the 64-byte hash string
    assert tx["data"] == "0x" + report_hash.encode().hex()
    assert tx["gas"] == chain._estimate_gas(report_hash.encode())


# ── anchor_report (full flow, Web3 mocked) ─────────────────────────────────
class FakeAccount:
    def from_key(self, key):
        return SimpleNamespace(address="0xFAKEADDRESS")
    def sign_transaction(self, tx, key):
        self.signed_tx = tx
        return SimpleNamespace(rawTransaction=b"raw-signed-bytes")


class FakeEthFull(FakeEth):
    def __init__(self):
        self.account = FakeAccount()
        self.sent_raw = None
    def send_raw_transaction(self, raw):
        self.sent_raw = raw
        return SimpleNamespace(hex=lambda: "deadbeef")


class FakeWeb3:
    last_instance = None
    def __init__(self, provider):
        self.provider = provider
        self.eth = FakeEthFull()
        FakeWeb3.last_instance = self
    @staticmethod
    def HTTPProvider(url):
        return ("provider", url)


@pytest.fixture
def fake_web3(monkeypatch):
    monkeypatch.setenv("AVAX_PRIVATE_KEY", "0x" + "1" * 64)
    monkeypatch.setattr(chain, "Web3", FakeWeb3)
    return FakeWeb3


def test_anchor_report_returns_prefixed_hash(fake_web3):
    tx = chain.anchor_report({"test": True})
    assert tx == "0xdeadbeef"
    assert tx.startswith("0x")


def test_anchor_report_signs_and_broadcasts(fake_web3):
    chain.anchor_report({"test": True})
    eth = FakeWeb3.last_instance.eth
    assert eth.sent_raw == b"raw-signed-bytes"      # actually broadcast
    assert eth.account.signed_tx["chainId"] == 43113
    assert eth.account.signed_tx["value"] == 0


def test_anchor_report_raises_without_key(monkeypatch):
    monkeypatch.setattr(chain, "Web3", FakeWeb3)
    monkeypatch.delenv("AVAX_PRIVATE_KEY", raising=False)
    with pytest.raises(RuntimeError):
        chain.anchor_report({"test": True})
