# test_report.py — Owner: Person 3
# Tests for report.py. No live Google Sheets calls — _get_sheet is mocked.

import json
import pytest

import report

FIXTURE = "tests/fixtures/sample_claude_response.json"


def load_fixture():
    with open(FIXTURE) as f:
        return json.load(f)


# ── Fake gspread objects ───────────────────────────────────────────────
class FakeWorksheet:
    def __init__(self, title, values=None):
        self.title = title
        self._values = list(values or [])
        self.batch_calls = []
        self.append_row_calls = 0

    def get_all_values(self):
        return self._values

    def batch_update(self, data, **kwargs):
        self.batch_calls.append(data)
        # Mimic Sheets: write each block's rows starting at its range row.
        for block in data:
            for row in block["values"]:
                self._values.append(row)
        return {"ok": True}

    def append_row(self, *args, **kwargs):
        # If this is ever called, the rule (no append_row) was violated.
        self.append_row_calls += 1
        raise AssertionError("append_row must not be used — use batch_update")


class FakeSpreadsheet:
    def __init__(self):
        self.worksheets = {}

    def worksheet(self, title):
        if title not in self.worksheets:
            from gspread.exceptions import WorksheetNotFound
            raise WorksheetNotFound(title)
        return self.worksheets[title]

    def add_worksheet(self, title, rows, cols):
        ws = FakeWorksheet(title)
        self.worksheets[title] = ws
        return ws


@pytest.fixture
def fake_sheet(monkeypatch):
    monkeypatch.setenv("SHEET_ENV", "dev")
    ss = FakeSpreadsheet()
    monkeypatch.setattr(report, "_get_sheet", lambda: ss)
    return ss


# ── Tests ───────────────────────────────────────────────────────────────
def test_writes_four_flag_rows(fake_sheet):
    result = report.write_report(load_fixture())
    assert result["flags_written"] == 4
    flags_ws = fake_sheet.worksheets[report.FLAGS_TAB]
    # header + 4 flag rows
    assert flags_ws.get_all_values()[0] == report.FLAGS_HEADER
    assert len(flags_ws.get_all_values()) == 5


def test_uses_batch_update_not_append_row(fake_sheet):
    report.write_report(load_fixture())
    for ws in fake_sheet.worksheets.values():
        assert ws.append_row_calls == 0
        assert ws.batch_calls, f"{ws.title} never got a batch_update"


def test_flag_row_shape_and_content(fake_sheet):
    report.write_report(load_fixture())
    flags_ws = fake_sheet.worksheets[report.FLAGS_TAB]
    first_data_row = flags_ws.get_all_values()[1]  # row after header
    assert len(first_data_row) == len(report.FLAGS_HEADER)
    # First fixture flag is the Naivas MIXED_FUNDS one.
    assert first_data_row[3] == "MIXED_FUNDS"
    assert first_data_row[0] == "2026-05-03"
    assert first_data_row[1] == 3500
    # Tx Hash column is blank (chain.py fills it later).
    assert first_data_row[6] == ""


def test_summary_row(fake_sheet):
    result = report.write_report(load_fixture())
    summary_ws = fake_sheet.worksheets[report.SUMMARY_TAB]
    assert summary_ws.get_all_values()[0] == report.SUMMARY_HEADER
    row = result["summary_row"]
    assert row[0] == "Mama Fua Enterprises"  # company
    assert row[1] == "May 2026"              # month
    assert row[2] == 15                      # total_transactions_reviewed
    assert row[3] == 4                       # flags found


def test_runs_accumulate_below_existing_rows(fake_sheet):
    report.write_report(load_fixture())
    report.write_report(load_fixture())
    flags_ws = fake_sheet.worksheets[report.FLAGS_TAB]
    # header + 4 + 4
    assert len(flags_ws.get_all_values()) == 9
    summary_ws = fake_sheet.worksheets[report.SUMMARY_TAB]
    # header + 2 summary rows
    assert len(summary_ws.get_all_values()) == 3


# ── SHEET_ENV safety guard ──────────────────────────────────────────────
def test_refuses_when_env_unset(monkeypatch):
    monkeypatch.delenv("SHEET_ENV", raising=False)
    monkeypatch.setattr(report, "_get_sheet", lambda: FakeSpreadsheet())
    with pytest.raises(RuntimeError):
        report.write_report(load_fixture())


def test_refuses_on_prod(monkeypatch):
    monkeypatch.setenv("SHEET_ENV", "prod")
    monkeypatch.setattr(report, "_get_sheet", lambda: FakeSpreadsheet())
    with pytest.raises(RuntimeError):
        report.write_report(load_fixture())
