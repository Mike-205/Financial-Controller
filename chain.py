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


def anchor_report(report: dict) -> str:
    """
    Write the report hash to Avalanche Fuji as a 0-value transaction.
    Returns the transaction hash (store this alongside the report).
    """
    # TODO Person 5: implement
    # 1. w3 = Web3(Web3.HTTPProvider(RPC_URL))
    # 2. Load private key from env, derive sender address
    # 3. report_hash = _hash_report(report)
    # 4. Build tx with data=report_hash, value=0, chainId=CHAIN_ID
    # 5. Sign + send, return tx hash
    raise NotImplementedError("Person 5: implement anchor_report()")
