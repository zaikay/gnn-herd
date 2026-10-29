"""Validate existing Task 1 artifacts and generate the Gate A report.

Does not rebuild the graph, change raw data, impute observations or apply an
isolate rule. Every reported measurement is computed here or read from audited
artifacts, with independent consistency checks.
"""
import hashlib
import json
import re
from datetime import datetime
from pathlib import Path

import networkx as nx
import pandas as pd
import yaml
from bs4 import BeautifulSoup

from audit.cer import validate_panel

OUT = Path("reports/audit")


def current_date(html):
    text = " ".join(BeautifulSoup(html, "html.parser").get_text(" ").split())
    match = re.search(r"current as at\s+(\d{1,2}\s+[A-Za-z]+\s+\d{4})", text, re.I)
    if not match:
        raise ValueError("CER current-as-at date not found in saved source page")
    return datetime.strptime(match.group(1), "%d %B %Y")


def validate_graph(nodes, edges, extra, summary):
    if nodes.postcode.duplicated().any() or not nodes.postcode.str.fullmatch(r"\d{4}").all():
        raise ValueError("Invalid or duplicate graph node codes")
    graph = nx.Graph()
    graph.add_nodes_from(nodes.postcode)
    pairs = [tuple(sorted(pair)) for pair in edges[["source", "target"]].itertuples(index=False, name=None)]
    if len(set(pairs)) != len(pairs) or any(a == b for a, b in pairs):
        raise ValueError("Duplicate edges or self loops")
    if any(a not in graph or b not in graph for a, b in pairs):
        raise ValueError("Unknown edge endpoint")
    graph.add_edges_from(pairs)
    queen = [tuple(sorted(pair)) for pair in extra[["source", "target"]].itertuples(index=False, name=None)]
    if len(set(queen)) != len(queen) or set(queen) & set(pairs):
        raise ValueError("Queen extras duplicated or already rook neighbours")
    if any(a == b or a not in graph or b not in graph for a, b in queen):
        raise ValueError("Invalid queen endpoint")
    degree = dict(graph.degree())
    if any(degree[row.postcode] != row.degree for row in nodes.itertuples()):
        raise ValueError("Saved degrees differ from edges")
    components = list(nx.connected_components(graph))
    saved = {frozenset(group.postcode) for _, group in nodes.groupby("component")}
    if saved != {frozenset(group) for group in components}:
        raise ValueError("Saved component assignments differ from edges")
    distribution = {str(k): int(v) for k, v in sorted(pd.Series(degree).value_counts().items())}
    checks = {"nodes": len(graph), "edges": graph.number_of_edges(), "components": len(components),
              "isolates": sorted(nx.isolates(graph)), "queen_extra_edges": len(queen),
              "degree_distribution": distribution}
    if any(summary[k] != value for k, value in checks.items()):
        raise ValueError("Saved graph summary differs from artifacts")
    return graph, sorted((len(c) for c in components), reverse=True)


def main():
    config = yaml.safe_load(Path("configs/sources.yaml").read_text(encoding="utf-8"))
    verified = []
    for name, metadata in config["files"].items():
        path = Path(name)
        digest = hashlib.sha256()
        with path.open("rb") as stream:
            while chunk := stream.read(1024 * 1024):
                digest.update(chunk)
        if path.stat().st_size != metadata["size_bytes"] or digest.hexdigest() != metadata["sha256"]:
            raise ValueError(f"Source checksum/size mismatch: {path}")
        verified.append({"file": name, **metadata})
    as_at = current_date(Path("data/raw/cer_page.html").read_text(encoding="utf-8"))
    safe_month = (pd.Timestamp(as_at) - pd.DateOffset(months=12)).strftime("%Y-%m")
    panel = pd.read_csv("data/interim/cer_panel.csv", dtype={"postcode": str, "month": str})
    validate_panel(panel)
    profiles = json.loads((OUT / "cer_profile.json").read_text())
    nodes = pd.read_csv(OUT / "graph_nodes.csv", dtype={"postcode": str})
    edges = pd.read_csv("data/processed/rook_edges.csv", dtype=str)
    extra = pd.read_csv(OUT / "queen_extra_edges.csv", dtype=str)
    summary = json.loads((OUT / "graph_summary.json").read_text())
    graph, component_sizes = validate_graph(nodes, edges, extra, summary)
    # Check each saved edge's geometric meaning without rebuilding all adjacency.
    import geopandas as gpd
    from geography.graph import spatial_areas
    gpkg = next(Path("data/interim").glob("*.gpkg"))
    areas = gpd.read_file(gpkg, layer="POA_2021_AUST_GDA2020")
    areas["postcode"] = areas.POA_CODE_2021.astype(str)
    areas, special = spatial_areas(areas)
    if set(areas.postcode) != set(nodes.postcode) or not areas.geometry.is_valid.all() or areas.geometry.is_empty.any():
        raise ValueError("Spatial graph nodes/geometry differ from the ABS layer")
    geometries = areas.set_index("postcode").geometry
    for is_rook, pairs in ((True, edges), (False, extra)):
        for a, b in pairs[["source", "target"]].itertuples(index=False, name=None):
            left, right = geometries[a], geometries[b]
            if not left.touches(right) or (left.boundary.intersection(right.boundary).length > 0) != is_rook:
                raise ValueError(f"Invalid saved contiguity link: {a}, {b}")
    joined = pd.read_csv(OUT / "postcode_poa_join.csv", dtype={"postcode": str})
    totals = panel.groupby("postcode")["count"].sum()
    if set(joined.postcode) != set(totals.index) or joined.postcode.duplicated().any():
        raise ValueError("Postcode join has lost or duplicated records")
    indexed = joined.set_index("postcode").reindex(totals.index)
    if not indexed.total_installations.eq(totals).all() or not indexed.matched.eq(indexed.index.isin(graph)).all():
        raise ValueError("Postcode join totals or matches differ")
    observed = panel.loc[panel.postcode.isin(graph)]
    coverage = nodes[["postcode", "degree", "component"]].merge(
        observed.groupby("postcode").agg(observed_months=("month", "size"),
            first_month=("month", "min"), last_month=("month", "max"),
            zero_months=("count", lambda s: int(s.eq(0).sum()))).reset_index(), how="left", on="postcode")
    # These are observation counts, not imputed installation counts.
    for col in ("observed_months", "zero_months"):
        coverage[col] = coverage[col].fillna(0).astype(int)
    coverage["missing_observation_months"] = panel.month.nunique() - coverage.observed_months
    coverage.to_csv(OUT / "poa_month_coverage.csv", index=False)
    hist = pd.read_csv(OUT / "historical_totals.csv", dtype={"postcode": str})
    discrepancies = hist.loc[~hist.matches]
    discrepancies.to_csv(OUT / "historical_total_discrepancies.csv", index=False)
    annual = pd.read_csv(OUT / "annual_national_comparison.csv")
    if not annual.difference.eq(0).all():
        raise ValueError("National annual discrepancies require review")
    actual_annual = panel.assign(year=panel.month.str[:4].astype(int)).groupby("year")["count"].sum()
    if not annual.set_index("year").csv_count.reindex(actual_annual.index).eq(actual_annual).all():
        raise ValueError("Annual comparison does not match panel")
    tail = pd.read_csv(OUT / "reporting_lag.csv", dtype={"month": str})
    expected_tail = panel.groupby("month")["count"].sum().sort_index().tail(24)
    if not tail.set_index("month")["count"].equals(expected_tail):
        raise ValueError("Reporting-lag series does not match panel")
    ledger = pd.read_csv(OUT / "exclusions.csv", dtype=str)
    graph_ledger = ledger.loc[ledger.scope.eq('spatial graph only')]
    if len(graph_ledger) != len(special) or set(graph_ledger.postcode) != set(special.postcode):
        raise ValueError("Exclusion ledger does not match approved special rows")
    matched_share = float(joined.loc[joined.matched, "total_installations"].sum() / joined.total_installations.sum())
    result = {"checksums_verified": len(verified), "as_at": as_at.strftime("%Y-%m-%d"),
        "last_safe_test_month": safe_month, "graph_validated": True,
        "edge_geometry_checks": len(edges) + len(extra), "component_sizes": component_sizes,
        "panel_rows": len(panel), "matched_observed_cells": len(observed),
        "spatial_poas": len(nodes), "poas_with_observations": int(coverage.observed_months.gt(0).sum()),
        "months": int(panel.month.nunique()), "missing_spatial_poa_month_cells": int(coverage.missing_observation_months.sum()),
        "complete_observed_poas": int(coverage.observed_months.eq(panel.month.nunique()).sum()),
        "zero_share_observed_matched_cells": float(observed["count"].eq(0).mean()),
        "historical_discrepancies": json.loads(discrepancies.to_json(orient="records")), "matched_installation_share": matched_share,
        "verdict": "CONDITIONAL GO"}
    (OUT / "final_validation.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
    lines = ["# Task 1 audit — Gate A review", "", "**Verdict: CONDITIONAL GO.** The files support observed monthly postcode counts and a validated rook graph. Acceptance remains with the researcher. Coverage gaps, unmatched postcodes and the isolate policy need explicit review before Task 2. This is a data-feasibility assessment, not a scientific conclusion.", "",
        "## Provenance and dates", "", f"Saved CER page current as at **{as_at:%d %B %Y}**. The CSV header preambles contain no embedded current-as-at date; it is not inferred from retrieval or last-modified dates. The last month permitted by the task's data-date-minus-12-month rule is **{safe_month}**. This is a reporting-lag cutoff, not evidence of historical data vintages: no archived as-of snapshots were obtained.", "",
        "All raw sizes and SHA256 checksums were independently verified by `python -m audit.finalize`.", "",
        "| Raw file | Bytes | Retrieved (UTC) | SHA256 |", "| --- | ---: | --- | --- |"]
    for f in verified:
        lines.append(f"| [{f['file']}]({f['url']}) | {f['size_bytes']} | {f['retrieved_at']} | `{f['sha256']}` |")
    lines += ["", "ABS Edition 3 GDA2020 Non ABS Structures is used. [Edition 4 Postal Areas](https://www.abs.gov.au/statistics/standards/australian-statistical-geography-standard-asgs/edition-4-july-2026-june-2031/non-abs-structures/postal-areas) were released on 14 October 2026, as checked during preparation; no edition switch was made.", "", "## CER layout and quality", "",
        "Target: monthly certificate backed solar PV installations, including upgrades and off-grid systems. Units are systems, not adopters. Both files are wide. Monthly headers are month/year plus Installation(s) Quantity; the first field is Small Unit Installation Postcode. The recent file also has historical and overall totals. Full column lists are in `cer_profile.json`.", "",
        "| File | Postcode rows | Months | First | Last | Duplicate postcode rows | Invalid monthly cells | Blank monthly cells |", "| --- | ---: | ---: | --- | --- | ---: | ---: | ---: |"]
    for p in profiles:
        lines.append(f"| {p['file']} | {p['rows']} | {len(p['months'])} | {p['months'][0]} | {p['months'][-1]} | {p['duplicate_postcode_rows']} | {p['issue_cells']} | {p['blank_cells']} |")
    lines += ["", "Monthly keys are unique, postcodes remain four-character strings, counts are nonnegative integers and months are ordered. Explicit zeros are present; blanks are not converted to zeros. No internal month-column gaps were found. January–March 2001 are absent from the early file and have not been invented.", "",
        f"Annual national sums match every year in the saved CER Solar PV national table ({len(annual)} years). See `annual_national_comparison.csv`; this comparison uses the snapshot at download, not a later live page.", "",
        f"Historical-total comparison: {int(hist.matches.sum())} matching postcodes and {len(discrepancies)} nonmatching comparisons. Details are in `historical_total_discrepancies.csv`. Nonmatching codes are " + ", ".join(discrepancies.postcode) + ". Their reported historical totals are zero, but neither has an early-file row. Their missing monthly sums remain missing; no zero is imputed.", "",
        "## Panel and postcode join", "",
        f"The observed panel has {len(panel):,} postcode-month cells, {panel.postcode.nunique():,} postcodes and {panel.month.nunique()} distinct months. The graph has {len(nodes):,} spatial Postal Areas; {result['poas_with_observations']:,} have CER observations. Matched observations comprise {len(observed):,} cells. {result['complete_observed_poas']:,} Postal Areas have every covered month; {result['missing_spatial_poa_month_cells']:,} cells are missing relative to the spatial-POA-by-covered-month rectangle. No missing count is imputed.", "",
        f"Zero share among observed matched Postal Area-month cells: **{result['zero_share_observed_matched_cells']:.6%}**. Denominator excludes missing observations; see `poa_month_coverage.csv` for every node's months, zeros and missing observation count.", "",
        f"Matched CER postcodes: **{int(joined.matched.sum()):,}/{len(joined):,} ({joined.matched.mean():.6%})**. Matched installation share: **{matched_share:.6%}**. Unmatched postcodes: **{int((~joined.matched).sum())}**, all retained with installation totals in `postcode_poa_join.csv`. No location is assigned to unmatched codes. Any special CER codes are separately listed in `cer_special_codes.csv`.", "",
        "Postal Areas are approximations of postcodes. This audit checks code equality, not exact postal-boundary correspondence. It does not establish stable geographic definitions over the full historical period.", "",
        "## Border graph", "",
        f"Validated artifacts: **{len(graph):,} nodes, {graph.number_of_edges():,} undirected rook edges, {len(extra)} additional queen-only edges, {len(component_sizes)} connected components and {len(summary['isolates'])} isolates**. No self loops, duplicate edges or unknown endpoints. Saved degrees and components agree with the edge list. Every saved rook edge shares a positive-length boundary and every queen-only edge is point contact. All raw hashes and node geometry checks passed. This validates the existing artifacts without rebuilding the graph; completeness relies on the spatial-index candidate enumeration in `geography.graph`.", "",
        f"Component sizes, largest first: {component_sizes}.", "",
        "| Degree | Postal Areas |", "| ---: | ---: |"]
    lines += [f"| {degree} | {count} |" for degree, count in summary["degree_distribution"].items()]
    lines += ["", "Isolated Postal Areas: " + ", ".join(summary["isolates"]) + ".", "",
        "**Proposed rule, not applied:** retain isolated areas as nodes with no geographic neighbours. Do not invent mainland or nearest-neighbour edges for islands. Future modelling must define their own-history path and the representation of an empty neighbour set in Task 2; no such feature or model is implemented here. Retain all connected components. Researcher approval is required.", "",
        "Approved special-row treatment is separate: ABS 9494, 9797 and ZZZZ have NULL geometry. Their attributes are in `abs_special_rows.csv`; only graph membership is excluded, with approval and reasons in `exclusions.csv`. No CER records have been excluded.", "",
        "## Reporting lag", "", "![National recent monthly counts](../figures/reporting_lag.png)", "",
        f"The figure contains {len(tail)} national monthly counts ending {tail.month.iloc[-1]}. Values are in `reporting_lag.csv`. Counts in the recent tail can still rise under the certificate creation period. No correction or nowcast is applied.", "",
        "## Gate A decisions", "", "1. Accept the join rate and retained unmatched-code ledger, or request further investigation.", "2. Approve the proposed isolate rule: retain nodes with no artificial geographic links.", "3. Accept the observed panel coverage provisionally. Missing early months, postcodes absent from the early file, and graph nodes without CER records remain missing; no zero-filling policy is approved.", "4. Accept CONDITIONAL GO for Task 1, or request revisions. Task 2 must resolve modelling eligibility and vintage leakage before a protocol is frozen. No forecasting work starts here.", "",
        "## Reproduction", "", "From a fresh clone, the researcher runs `scripts/setup.ps1` for the pinned environment. Download commands below are researcher commands when sizes are unknown or exceed the configured limit. Raw downloads use exclusive creation and must not be repeated over existing files. Approval for the three special graph rows is documented in STATUS.md and the exclusion ledger.", "", "```powershell", "& .\\scripts\\setup.ps1", "# Remaining commands use the installed environment's Python:", "& .venv\\Scripts\\python.exe -m download.fetch cer 2>&1 | Tee-Object logs/t01_download_cer.log", "& .venv\\Scripts\\python.exe -m download.fetch abs 2>&1 | Tee-Object logs/t01_download_abs.log", "& .venv\\Scripts\\python.exe -m audit.profile 2>&1 | Tee-Object logs/t01_profile.log", "& .venv\\Scripts\\python.exe -m geography.graph 2>&1 | Tee-Object logs/t01_graph.log", "& .venv\\Scripts\\python.exe -m audit.lag 2>&1 | Tee-Object logs/t01_lag.log", "& .venv\\Scripts\\python.exe -m audit.finalize 2>&1 | Tee-Object logs/t01_finalize.log", "& .venv\\Scripts\\python.exe -m pytest -q 2>&1 | Tee-Object logs/t01_tests_gate_a.log", "```", "",
        "All measurements in this report are generated or validated by `audit.finalize`; the profile and graph artifacts are produced by the commands above. `final_validation.json` holds machine-readable checks. A fresh download may contain revisions and will not necessarily reproduce the historical snapshot's values; exact reproduction requires the recorded raw hashes. The graph terminal log was lost through the incomplete Tee-Object filename, so the existing saved artifacts were checked independently rather than rerun.", ""]
    (OUT / "audit_week1.md").write_text("\n".join(lines), encoding="utf-8")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
