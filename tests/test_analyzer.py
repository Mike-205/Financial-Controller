# test_analyzer.py — Owner: Person 2
# Tests for analyzer.py using fixture data. No live API calls.

import json, pytest

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

# TODO Person 2: add a test that mocks the Claude API call
# and asserts analyze() returns the correct shape
