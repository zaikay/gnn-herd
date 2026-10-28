import pandas as pd
import pytest

from geography.graph import border_graph, join_panel, spatial_areas, record_special_rows


def test_join_keeps_unmatched_and_leading_zero():
    panel = pd.DataFrame({"postcode": ["0800", "9999"], "count": [3, 2]})
    result = join_panel(panel, {"0800"})
    assert result.postcode.tolist() == ["0800", "9999"]
    assert result.matched.tolist() == [True, False]
    assert result.total_installations.sum() == 5


def test_rook_queen_isolate_and_components():
    gpd = pytest.importorskip("geopandas")
    from shapely.geometry import box
    import networkx as nx
    areas = gpd.GeoDataFrame({"postcode": ["0800", "0801", "0802", "0803"]},
                             geometry=[box(0, 0, 1, 1), box(1, 0, 2, 1), box(2, 1, 3, 2), box(8, 8, 9, 9)], crs=7844)
    graph, queen = border_graph(areas)
    assert set(graph.edges()) == {("0800", "0801")}
    assert queen == [("0801", "0802")]
    assert set(nx.isolates(graph)) == {"0802", "0803"}
    assert nx.number_connected_components(graph) == 3


def test_overlap_rejected():
    gpd = pytest.importorskip("geopandas")
    from shapely.geometry import box
    areas = gpd.GeoDataFrame({"postcode": ["0800", "0801"]}, geometry=[box(0, 0, 2, 2), box(1, 1, 3, 3)], crs=7844)
    with pytest.raises(ValueError, match="Overlapping"):
        border_graph(areas)


def test_approved_special_rows_audited_and_ledger_idempotent(tmp_path):
    gpd = pytest.importorskip("geopandas")
    from shapely.geometry import box
    original = gpd.GeoDataFrame({"postcode": ["0800", "9494", "9797", "ZZZZ"]},
                                geometry=[box(0, 0, 1, 1), None, None, None], crs=7844)
    spatial, special = spatial_areas(original)
    assert spatial.postcode.tolist() == ["0800"]
    assert special.postcode.tolist() == ["9494", "9797", "ZZZZ"]
    assert len(original) == 4
    record_special_rows(special, tmp_path)
    record_special_rows(special, tmp_path)
    ledger = pd.read_csv(tmp_path / "exclusions.csv", dtype=str)
    assert len(ledger) == 3
    assert ledger.scope.eq("spatial graph only").all()
    joined = join_panel(pd.DataFrame({"postcode": ["0800", "9494"], "count": [2, 5]}), set(spatial.postcode))
    assert joined.total_installations.sum() == 7
    assert joined.matched.tolist() == [True, False]


def test_unknown_null_geometry_still_stops():
    gpd = pytest.importorskip("geopandas")
    original = gpd.GeoDataFrame({"postcode": ["2000"]}, geometry=[None], crs=7844)
    with pytest.raises(ValueError, match="Unexpected NULL"):
        spatial_areas(original)
