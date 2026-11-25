"""Targeted EXPLORATORY checks for graph intervals and area summaries."""
from types import SimpleNamespace

import numpy as np
import pandas as pd

from evaluation.final_test_metrics import hac_interval
from evaluation.test_exploratory_graph_maturity import (
    BOUNDS, CANDIDATE, OUTCOMES, REFERENCES, area_sizes, graph_intervals, shuffled_summary,
)


def test_intervals_sort_origins_and_leave_h_equal_n_undefined():
    months = pd.period_range('2022-10', '2023-09', freq='M').astype(str)
    differences = np.arange(12) / 100 - 1
    rows = [dict(origin=month, model=model, outcome=outcome, group='low', mae=loss)
            for month, difference in zip(months, differences)
            for model, loss in [(CANDIDATE, 2 + difference), (REFERENCES[0], 2), (REFERENCES[1], 3)]
            for outcome in OUTCOMES]
    result = graph_intervals(pd.DataFrame(rows[::-1]), [('first_half', months[0], months[-1])], ['low'], .95)
    first = result.query("reference == @REFERENCES[0] and outcome == '1'").iloc[0]
    np.testing.assert_allclose(first[BOUNDS].astype(float), hac_interval(differences, 1))
    assert first.excludes_zero
    boundary = result.loc[result.outcome.isin(['12', 'total_12'])]
    assert len(boundary) == 4 and boundary.DM_h.eq(12).all()
    assert boundary[['lower95', 'upper95', 'excludes_zero']].isna().all().all()
    assert boundary.mean_MAE_difference.notna().all()


def test_area_means_exclude_masked_months_and_areas_and_keep_zeros():
    panel = SimpleNamespace(
        months=np.array(['2010-12', '2011-01', '2011-02', '2011-03']),
        targets=np.array([[100, 0, 4, 100], [100, np.nan, 8, 100], [99, 99, 99, 99]]),
        codes=np.array(['0001', '0002', '0003']), observed=np.array([True, True, False]))
    areas, summary = area_sizes(panel, '2011-02')
    assert areas.postcode.tolist() == ['0001', '0002']
    assert areas.observed_months.tolist() == [2, 1]
    assert areas.mean_monthly_count.tolist() == [2, 8]
    np.testing.assert_allclose(summary.mean_monthly_count, [2, 2.6, 5, 7.4, 8])


def test_shuffle_summary_uses_state_seed_extrema_and_counts():
    diagnostics = pd.DataFrame(dict(state_code=[1, 2, 1, 2], seed=[11, 11, 29, 29],
                                    original_edge_share=[.1, .2, .3, .4], target_swaps=[10]*4,
                                    accepted_swaps=[10, 9, 10, 10], target_reached=[True, False, True, True]))
    row = shuffled_summary(diagnostics, {'cross_state_edges_fixed': 190}, [11, 29]).iloc[0]
    assert (row.states_and_territories, row.seeds, row.cross_state_edges_fixed) == (2, 2, 190)
    assert (row.min_original_edge_share, row.max_original_edge_share) == (.1, .4)
    assert not row.all_swap_targets_reached
