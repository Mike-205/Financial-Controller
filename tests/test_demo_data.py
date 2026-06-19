# test_demo_data.py — validates demo_data.py shape for the pipeline

from demo_data import DEMO_TRANSACTIONS, COMPANY_NAME, REPORT_MONTH

REQUIRED_KEYS = {"date", "amount", "description", "vendor", "reference"}

def test_not_empty():
    assert len(DEMO_TRANSACTIONS) > 0

def test_all_have_required_keys():
    for tx in DEMO_TRANSACTIONS:
        missing = REQUIRED_KEYS - set(tx.keys())
        assert not missing, f"Missing keys {missing} in: {tx}"

def test_company_and_month_defined():
    assert COMPANY_NAME
    assert REPORT_MONTH

def test_mixed_funds_trigger():
    assert any("Naivas" in tx["description"] for tx in DEMO_TRANSACTIONS)

def test_round_number_trigger():
    assert any("John Kamau" in tx["description"] for tx in DEMO_TRANSACTIONS)

def test_duplicate_trigger():
    supplier = [tx for tx in DEMO_TRANSACTIONS if tx["vendor"] == "Supplier XYZ"]
    assert len(supplier) == 2, "Need 2x Supplier XYZ to trigger DUPLICATE flag"
