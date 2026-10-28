import pandas as pd
import pytest

from audit.finalize import current_date, validate_graph


def test_as_at_ignores_other_dates():
    assert current_date('<p>Updated 20 October 2026</p><p>This data is current as at <b>30 September 2026</b>.</p>').strftime('%Y-%m-%d') == '2026-09-30'
    with pytest.raises(ValueError):
        current_date('<p>Updated 20 October 2026</p>')


def test_graph_artifact_validation_detects_tampered_degrees():
    nodes = pd.DataFrame({'postcode': ['0800', '2000', '3000'], 'degree': [1, 1, 0], 'component': [0, 0, 1]})
    edges = pd.DataFrame({'source': ['0800'], 'target': ['2000']})
    extra = pd.DataFrame(columns=['source', 'target'])
    summary = {'nodes': 3, 'edges': 1, 'components': 2, 'isolates': ['3000'], 'queen_extra_edges': 0, 'degree_distribution': {'0': 1, '1': 2}}
    graph, sizes = validate_graph(nodes, edges, extra, summary)
    assert len(graph) == 3 and sizes == [2, 1]
    nodes.loc[0, 'degree'] = 2
    with pytest.raises(ValueError, match='degrees'):
        validate_graph(nodes, edges, extra, summary)
