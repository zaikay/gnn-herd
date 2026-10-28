"""Profile immutable CER inputs and preserve all discrepancies for review."""
import json
from pathlib import Path

import pandas as pd
from bs4 import BeautifulSoup

from audit.cer import dates_in, historical_check, read_wide, validate_panel

OUT = Path("reports/audit")


def national_tables(html):
    soup = BeautifulSoup(html, "html.parser")
    tables = []
    for table in soup.find_all("table"):
        rows = [[cell.get_text(" ", strip=True) for cell in row.find_all(["th", "td"])]
                for row in table.find_all("tr")]
        if not rows or not any("Solar PV systems" in cell for cell in rows[0]):
            continue
        col = next(i for i, cell in enumerate(rows[0]) if "Solar PV systems" in cell)
        for row in rows[1:]:
            if row and row[0].strip("*").isdigit() and len(row) > col:
                tables.append({"year": int(row[0].strip("*")),
                               "cer_page_count": int(row[col].replace(",", "").strip())})
    if not tables:
        raise ValueError("No national annual Solar PV table in saved CER page")
    return pd.DataFrame(tables)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    panels, summaries, issues, wides = [], [], [], []
    for period in ("early", "recent"):
        wide, panel, issue, summary = read_wide(f"data/raw/sgu_solar_{period}.csv")
        panels.append(panel)
        summaries.append(summary)
        issue["source_file"] = summary["file"]
        issues.append(issue)
        wides.append(wide)
    pd.concat(issues).to_csv(OUT / "validation_issues.csv", index=False)
    # Empty ledger: no exclusions have been applied, including unmatched codes.
    if not (OUT / "exclusions.csv").exists():
        pd.DataFrame(columns=["source_file", "postcode", "month", "reason", "approved_by"]).to_csv(OUT / "exclusions.csv", index=False)
    (OUT / "cer_profile.json").write_text(json.dumps(summaries, indent=2), encoding="utf-8")
    panel = pd.concat(panels, ignore_index=True).sort_values(["postcode", "month"])
    validate_panel(panel)
    if any(s["missing_month_columns"] for s in summaries):
        raise ValueError("Missing month columns: researcher review required")
    historical_check(wides[1], panels[0]).to_csv(OUT / "historical_totals.csv", index=False)
    annual = panel.assign(year=panel.month.str[:4].astype(int)).groupby("year")["count"].sum().rename("csv_count").reset_index()
    html = Path("data/raw/cer_page.html").read_text(encoding="utf-8")
    annual = annual.merge(national_tables(html), on="year", how="outer", validate="one_to_one")
    annual["difference"] = annual.csv_count - annual.cer_page_count
    annual.to_csv(OUT / "annual_national_comparison.csv", index=False)
    (OUT / "cer_page_dates.json").write_text(json.dumps(dates_in(BeautifulSoup(html, "html.parser").get_text(" "))), encoding="utf-8")
    Path("data/interim").mkdir(parents=True, exist_ok=True)
    panel[["postcode", "month", "count"]].to_csv("data/interim/cer_panel.csv", index=False)
    print(json.dumps({"rows": len(panel), "postcodes": panel.postcode.nunique(),
                      "months": panel.month.nunique(), "zero_share": panel["count"].eq(0).mean(),
                      "annual_mismatch_years": annual.loc[annual.difference.ne(0), "year"].tolist()}))


if __name__ == "__main__":
    main()
