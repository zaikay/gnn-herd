"""Targeted checks for EXPLORATORY section 9."""
import numpy as np
import pandas as pd
import pytest

from evaluation.test_exploratory_offsets import (
    GROUPS, METRICS, NEIGH, OWN, PERIODS, decompose, robustness, verified_calendar,
)


def test_decomposition_uses_original_members_for_both_references():
    boost = np.array([4., 4., 0., -2.])
    network = np.array([-2., 2., 4., 0.])
    own = np.array([-3., 2., 5., -4.])
    weights = np.array([.5, .25, .75, .5])
    hybrid = weights * boost + (1 - weights) * network
    for reference in (boost, own):
        weighting, shift, cancelling, gain = decompose(boost, network, hybrid, weights, reference)
        np.testing.assert_allclose(cancelling, [2, 0, 0, 0], atol=1e-10, rtol=0)
        np.testing.assert_allclose(weighting + shift + cancelling, gain, atol=1e-10, rtol=0)
        np.testing.assert_allclose(gain, abs(reference) - abs(hybrid), atol=1e-10, rtol=0)


def test_boosting_ties_count_as_not_lower():
    rows = [
        dict(model=model, period=period, group=group, outcome=outcome, **dict.fromkeys(METRICS, loss))
        for model, loss in [(OWN, 2), (NEIGH, 1), ('tie', 1), ('lower', .5)]
        for period, _, _ in PERIODS for group in GROUPS
        for outcome in [str(h) for h in range(1, 13)] + ['total_12']
    ]
    results = robustness(pd.DataFrame(rows))['robustness_cells']
    assert results.query("model == 'tie'").not_lower.all()
    assert not results.query("model == 'lower'").not_lower.any()


@pytest.fixture
def test_spec():
    return dict(first_origin='2022-10', last_origin='2024-09',
                last_target='2025-09', refit_interval_months=3)


def test_origin_boundaries(test_spec):
    rows = verified_calendar(test_spec)
    assert rows.origin.iloc[[0, 11, 12, 23]].tolist() == ['2022-10', '2023-09', '2023-10', '2024-09']


def test_no_target_after_september_2025(test_spec):
    rows = verified_calendar(test_spec)
    assert rows.last_target.max() == '2025-09'
    with pytest.raises(ValueError, match='September 2025'):
        verified_calendar(dict(test_spec, last_target='2025-10'))
    with pytest.raises(ValueError, match='September 2025|period'):
        verified_calendar(dict(test_spec, last_origin='2024-10'))
