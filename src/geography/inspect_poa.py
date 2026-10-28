"""Read only POA attributes and geometry presence, without building a graph."""
import json
import re
import sqlite3
from pathlib import Path


def main():
    paths = list(Path("data/interim").glob("*.gpkg"))
    if len(paths) != 1:
        raise ValueError("Expected one extracted GeoPackage")
    with sqlite3.connect(paths[0].resolve().as_uri() + "?mode=ro", uri=True) as connection:
        connection.row_factory = sqlite3.Row
        rows = connection.execute(
            'SELECT POA_CODE_2021 AS code, POA_NAME_2021 AS name, '
            'geom IS NULL AS geometry_is_null FROM POA_2021_AUST_GDA2020'
        ).fetchall()
    special = [dict(row) for row in rows if not re.fullmatch(r"\d{4}", str(row["code"]))
               or row["code"] in {"9494", "9797"} or row["geometry_is_null"]]
    result = {"source": str(paths[0]), "layer": "POA_2021_AUST_GDA2020",
              "row_count": len(rows), "special_or_null_geometry_rows": special,
              "cer_panel_exists": Path("data/interim/cer_panel.csv").exists(),
              "cer_raw_files": [str(p) for p in Path("data/raw").glob("sgu_solar_*.csv")]}
    Path("reports/audit/poa_inspection.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
