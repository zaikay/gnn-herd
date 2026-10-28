"""Join and rook graph. Never repair geometry or connect isolates implicitly."""
import argparse
import json
import zipfile
from pathlib import Path

import networkx as nx
import pandas as pd


APPROVED_SPECIAL_CODES = {"9494", "9797", "ZZZZ"}


def spatial_areas(areas):
    """Researcher approved on 2026-10-28: omit only known NULL-geometry codes."""
    excluded = areas.postcode.isin(APPROVED_SPECIAL_CODES) & areas.geometry.isna()
    spatial = areas.loc[~excluded].copy()
    if not spatial.postcode.str.fullmatch(r"\d{4}").all():
        raise ValueError("Unexpected special POA code; researcher decision required")
    if spatial.geometry.isna().any():
        raise ValueError("Unexpected NULL geometry; researcher decision required")
    return spatial.reset_index(drop=True), areas.loc[excluded].copy()


def record_special_rows(special, output=Path("reports/audit")):
    output.mkdir(parents=True, exist_ok=True)
    attributes = pd.DataFrame(special.drop(columns=special.geometry.name))
    attributes["geometry_is_null"] = True
    attributes.to_csv(output / "abs_special_rows.csv", index=False)
    ledger = output / "exclusions.csv"
    existing = pd.read_csv(ledger, dtype=str, keep_default_na=False) if ledger.exists() else pd.DataFrame()
    entries = pd.DataFrame([{
        "source_file": "data/raw/abs_ed3_non_abs.zip:POA_2021_AUST_GDA2020",
        "postcode": code, "month": "", "scope": "spatial graph only",
        "reason": "ABS special-purpose row has NULL geometry; retained in abs_special_rows.csv; no CER records excluded",
        "approved_by": "researcher, conversation approval 2026-10-28",
    } for code in special.postcode])
    pd.concat([existing, entries], ignore_index=True).fillna("").drop_duplicates().to_csv(ledger, index=False)


def border_graph(areas):
    if areas.crs is None:
        raise ValueError("Missing CRS")
    if areas.geometry.isna().any() or areas.geometry.is_empty.any() or not areas.geometry.is_valid.all():
        raise ValueError("Missing/invalid geometries; no exclusion or repair authorised")
    if areas.postcode.duplicated().any():
        raise ValueError("Duplicate POA codes; review before dissolving")
    graph = nx.Graph()
    graph.add_nodes_from(areas.postcode)
    queen = []
    spatial = areas.sindex
    for i, geometry in enumerate(areas.geometry):
        for j in spatial.query(geometry, predicate="intersects"):
            if j <= i:
                continue
            other = areas.geometry.iloc[j]
            if not geometry.touches(other):
                raise ValueError("Overlapping Postal Area polygons; review required")
            pair = (areas.postcode.iloc[i], areas.postcode.iloc[j])
            if geometry.boundary.intersection(other.boundary).length > 0:
                graph.add_edge(*pair)
            else:
                queen.append(pair)
    return graph, queen


def join_panel(panel, codes):
    totals = panel.groupby("postcode")["count"].sum().rename("total_installations").reset_index()
    totals["matched"] = totals.postcode.isin(codes)
    return totals


def main():
    parser = argparse.ArgumentParser(__doc__)
    parser.add_argument("--layer", default="POA_2021_AUST_GDA2020")
    parser.add_argument("--prepare-only", action="store_true", help="Audit approved special rows without building graph")
    parser.add_argument("--join-only", action="store_true", help="Write postcode join without building graph")
    args = parser.parse_args()
    if not args.prepare_only and not Path("data/interim/cer_panel.csv").exists():
        raise FileNotFoundError("Run CER download and audit.profile before geography.graph")
    import geopandas as gpd
    import pyogrio
    interim = Path("data/interim")
    with zipfile.ZipFile("data/raw/abs_ed3_non_abs.zip") as archive:
        files = [n for n in archive.namelist() if n.lower().endswith(".gpkg")]
        if len(files) != 1:
            raise ValueError(f"Expected one GeoPackage: {files}")
        destination = interim / Path(files[0]).name
        if not destination.exists():
            with archive.open(files[0]) as source, destination.open("xb") as output:
                import shutil
                shutil.copyfileobj(source, output)
    layers = pyogrio.list_layers(destination)
    Path("reports/audit/abs_layers.json").write_text(json.dumps(layers.tolist(), indent=2), encoding="utf-8")
    areas = gpd.read_file(destination, layer=args.layer)
    if "POA_CODE_2021" not in areas:
        raise ValueError(f"Unexpected schema: {list(areas.columns)}")
    areas["postcode"] = areas.POA_CODE_2021.astype(str)
    areas, special = spatial_areas(areas)
    record_special_rows(special)
    if args.prepare_only:
        print(json.dumps({"spatial_rows": len(areas), "approved_graph_exclusions": special.postcode.tolist()}))
        return
    panel = pd.read_csv(interim / "cer_panel.csv", dtype={"postcode": str, "month": str})
    joined = join_panel(panel, set(areas.postcode))
    joined["abs_special_code"] = joined.postcode.isin(APPROVED_SPECIAL_CODES)
    joined.loc[joined.abs_special_code].to_csv("reports/audit/cer_special_codes.csv", index=False)
    joined.to_csv("reports/audit/postcode_poa_join.csv", index=False)
    join_summary = {
        "spatial_poas": len(areas), "cer_postcodes": len(joined),
        "matched_postcodes": int(joined.matched.sum()),
        "matched_postcode_share": float(joined.matched.mean()),
        "matched_installation_share": float(joined.loc[joined.matched, "total_installations"].sum() / joined.total_installations.sum()),
        "unmatched_postcodes": int((~joined.matched).sum()),
    }
    Path("reports/audit/join_summary.json").write_text(json.dumps(join_summary, indent=2), encoding="utf-8")
    if args.join_only:
        print(json.dumps(join_summary, indent=2))
        return
    graph, queen = border_graph(areas)
    pd.DataFrame(sorted(graph.edges()), columns=["source", "target"]).to_csv("data/processed/rook_edges.csv", index=False)
    pd.DataFrame(queen, columns=["source", "target"]).to_csv("reports/audit/queen_extra_edges.csv", index=False)
    components = {node: i for i, component in enumerate(nx.connected_components(graph)) for node in component}
    pd.DataFrame([{"postcode": node, "degree": degree, "component": components[node]}
                  for node, degree in sorted(graph.degree())]).to_csv("reports/audit/graph_nodes.csv", index=False)
    matched = joined.loc[joined.matched]
    summary = {"nodes": graph.number_of_nodes(), "edges": graph.number_of_edges(),
               "queen_extra_edges": len(queen), "components": nx.number_connected_components(graph),
               "isolates": sorted(nx.isolates(graph)),
               "degree_distribution": {int(k): int(v) for k, v in sorted(pd.Series(dict(graph.degree())).value_counts().items())},
               "matched_postcode_share": float(joined.matched.mean()),
               "matched_installation_share": float(matched.total_installations.sum() / joined.total_installations.sum()),
               "poas_with_observations": int(len(matched)), "months": int(panel.month.nunique()),
               "zero_share_observed_matched_cells": float(panel.loc[panel.postcode.isin(areas.postcode), "count"].eq(0).mean()),
               "poas_without_cer_records": sorted(set(areas.postcode) - set(panel.postcode)),
               "unmatched_postcodes": joined.loc[~joined.matched, "postcode"].tolist(),
               "isolate_proposal": "Retain isolates with degree zero; no artificial links. Researcher approval required."}
    Path("reports/audit/graph_summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
