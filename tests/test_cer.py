import pandas as pd
import pytest

from audit.cer import historical_check, month_label, read_wide, validate_panel
from audit.profile import national_tables


def test_month_labels():
    assert month_label("Jan 2011") == "2011-01"
    assert month_label("January-2011") == "2011-01"
    assert month_label("2001-2010 total") is None
    assert month_label("Apr 2001 - Installations Quantity") == "2001-04"
    assert month_label("Jan 2011 - Installation Quantity") == "2011-01"


def test_live_cer_column_naming(tmp_path):
    path = tmp_path / "fixture.csv"
    path.write_text("Small Unit Installation Postcode,Apr 2001 - Installations Quantity\n0800,0\n", encoding="utf-8")
    _, panel, issues, _ = read_wide(path)
    validate_panel(panel)
    assert panel.month.tolist() == ["2001-04"]
    assert issues.empty


def test_preserves_codes_zeros_and_months(tmp_path):
    path = tmp_path / "fixture.csv"
    path.write_text("SGU Solar Installations current as at 30 September 2026\nPostcode,Jan 2011,Feb 2011\n0800,0,2\n2000,3,4\n", encoding="utf-8")
    _, panel, issues, summary = read_wide(path)
    panel = panel.sort_values(["postcode", "month"])
    validate_panel(panel)
    assert panel.postcode.iloc[0] == "0800"
    assert summary["explicit_zero_cells"] == 1
    assert summary["current_as_at_candidates"] == ["30 September 2026"]
    assert issues.empty


@pytest.mark.parametrize("value", ["", "-1", "abc", "1.5"])
def test_bad_counts_retained_and_rejected(tmp_path, value):
    path = tmp_path / "fixture.csv"
    path.write_text(f"Postcode,Jan 2011\n0800,{value}\n", encoding="utf-8")
    _, panel, issues, _ = read_wide(path)
    assert len(panel) == len(issues) == 1
    with pytest.raises(ValueError, match="Invalid counts"):
        validate_panel(panel)


def test_duplicate_key_and_month_order():
    panel = pd.DataFrame({"postcode": ["0800", "0800"], "month": ["2011-02", "2011-01"], "count": [1, 0]})
    with pytest.raises(ValueError, match="ordered"):
        validate_panel(panel)
    panel.month = "2011-01"
    with pytest.raises(ValueError, match="Duplicate"):
        validate_panel(panel)
    panel.postcode = [800, "2000"]
    with pytest.raises(ValueError, match="four character"):
        validate_panel(panel)


def test_swh_rejected(tmp_path):
    path = tmp_path / "swh.csv"
    path.write_text("SWH Solar Installations\nPostcode,Jan 2011\n0800,1\n", encoding="utf-8")
    with pytest.raises(ValueError, match="Wrong product"):
        read_wide(path)


def test_historical_total_reports_missing_codes():
    recent = pd.DataFrame({"postcode": ["0800", "2000"], "2001-2010 total": ["3", "4"]})
    early = pd.DataFrame({"postcode": ["0800", "3000"], "count": [3, 8]})
    result = historical_check(recent, early)
    assert len(result) == 3
    assert result.matches.sum() == 1


def test_saved_page_national_table():
    html = "<table><tr><th>Installation year</th><th>Solar PV systems (deemed)</th></tr><tr><td>2025*</td><td>1,234</td></tr></table>"
    assert national_tables(html).iloc[0].to_dict() == {"year": 2025, "cer_page_count": 1234}
