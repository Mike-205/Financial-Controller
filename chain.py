# chain.py — Avalanche Fuji C-Chain audit trail
# Owner: Person 5 (feat/chain)
#
# Responsibilities:
#   - SHA-256 hash the full report JSON (deterministic — use sort_keys=True)
#   - Send a 0 AVAX transaction to Fuji testnet with hash in the data field
#   - Return the transaction hash as proof of timestamp
#
# GOTCHA: Gas estimation needs a 20% buffer or the tx fails silently.
#         Formula: gas = 21000 + len(data_bytes) * 68, then multiply by 1.2
#
# Network: Avalanche Fuji C-Chain
#   RPC:      https://api.avax-test.network/ext/bc/C/rpc
#   Chain ID: 43113
#   Explorer: https://testnet.snowtrace.io
#   Faucet:   https://faucet.avax.network (free test AVAX)

import os, json, hashlib
from web3 import Web3
from dotenv import load_dotenv

load_dotenv()

RPC_URL  = os.getenv("AVAX_FUJI_RPC", "https://api.avax-test.network/ext/bc/C/rpc")
CHAIN_ID = 43113


def _hash_report(report: dict) -> str:
    """SHA-256 hash of deterministically serialized report JSON."""
    serialized = json.dumps(report, sort_keys=True, ensure_ascii=False)
    return hashlib.sha256(serialized.encode()).hexdigest()


def _estimate_gas(data_bytes: bytes) -> int:
    """Base 21000 + 68 per data byte, with a mandatory 20% buffer.
    Without the buffer the tx can fail silently (see GOTCHA above)."""
    return int((21000 + len(data_bytes) * 68) * 1.2)


def _build_transaction(w3: "Web3", address: str, report_hash: str) -> dict:
    """Build a 0-value self-transfer carrying the report hash in `data`."""
    data_bytes = report_hash.encode()  # 64-byte hex string → bytes
    return {
        "from":     address,
        "to":       address,            # send to self; this is an anchor, not a transfer
        "value":    0,
        "nonce":    w3.eth.get_transaction_count(address),
        "gas":      _estimate_gas(data_bytes),
        "gasPrice": w3.eth.gas_price,
        "chainId":  CHAIN_ID,           # 43113 — Fuji testnet only, never mainnet
        "data":     "0x" + data_bytes.hex(),
    }


def _raw_tx(signed) -> bytes:
    """The raw signed bytes, across web3 v6 (rawTransaction) and v7 (raw_transaction)."""
    return getattr(signed, "rawTransaction", None) or signed.raw_transaction


def anchor_report(report: dict) -> str:
    """
    Write the report hash to Avalanche Fuji as a 0-value transaction.
    Returns the transaction hash (store this alongside the report).
    """
    w3 = Web3(Web3.HTTPProvider(RPC_URL))

    private_key = os.getenv("AVAX_PRIVATE_KEY")
    if not private_key:
        raise RuntimeError("AVAX_PRIVATE_KEY is not set — cannot sign the anchor tx.")

    account = w3.eth.account.from_key(private_key)
    report_hash = _hash_report(report)

    tx = _build_transaction(w3, account.address, report_hash)
    signed = w3.eth.account.sign_transaction(tx, private_key)
    tx_hash = w3.eth.send_raw_transaction(_raw_tx(signed))

    tx_hex = tx_hash.hex()
    return tx_hex if tx_hex.startswith("0x") else "0x" + tx_hex
