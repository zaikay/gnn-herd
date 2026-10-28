import json
import sqlite3

from geography.inspect_poa import main


def test_inspection_reports_special_rows_without_changing_input(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    (tmp_path / "data/interim").mkdir(parents=True)
    (tmp_path / "reports/audit").mkdir(parents=True)
    source = tmp_path / "data/interim/fixture.gpkg"
    with sqlite3.connect(source) as connection:
        connection.execute("CREATE TABLE POA_2021_AUST_GDA2020 (POA_CODE_2021 TEXT, POA_NAME_2021 TEXT, geom BLOB)")
        connection.executemany("INSERT INTO POA_2021_AUST_GDA2020 VALUES (?, ?, ?)",
                               [("0800", "0800", b"geometry"), ("ZZZZ", "Outside Australia", None)])
    original = source.read_bytes()
    main()
    result = json.loads((tmp_path / "reports/audit/poa_inspection.json").read_text())
    assert result["row_count"] == 2
    assert result["special_or_null_geometry_rows"] == [
        {"code": "ZZZZ", "name": "Outside Australia", "geometry_is_null": 1}]
    assert not result["cer_panel_exists"]
    assert source.read_bytes() == original
