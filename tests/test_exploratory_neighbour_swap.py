"""Checks for the EXPLORATORY fixed-weight member swap."""
import numpy as np
import pandas as pd

from evaluation.gate_c_metrics import Context
from evaluation.test_exploratory_neighbour_swap import (
    METRICS, NEIGH, ORIGINAL, OWN, REAL, SWAP, contrasts, score_saved,
)


def test_score_saved_averages_seeds_before_swapping_and_routes_weights(tmp_path):
    origins = np.array(['2022-10', '2022-11'])
    codes = np.array(['0001', '0002', '0003'])
    groups = np.array([[0, 1, 2], [2, 1, 0]])
    truth = np.full((2, 3, 12), 10.)
    ctx = Context(origins, codes, truth, np.ones((2, 3)), groups, np.empty((0, 2), int), origins)
    seeds = [11, 29, 47]
    values = {OWN: [2., 20., 20.], NEIGH: [0., 18., 18.], REAL: [10., 10., 10.]}
    paths = {}
    for model, predictions in values.items():
        paths[model] = {}
        for seed, value in zip(seeds, predictions):
            path = tmp_path / f'{model}_{seed}.npz'
            np.savez(path, origins=origins, codes=codes, prediction=np.full_like(truth, value))
            paths[model][seed] = path
    weights = {g: dict(zip(['1-3', '4-6', '7-12'], ws)) for g, ws in
               zip(['low', 'medium', 'high'], [[.1, .2, .3], [.4, .5, .6], [.7, .8, .9]])}
    result = score_saved(paths, ctx, {'seeds': seeds, 'weights': weights}, {})
    assert set(result.model) == {OWN, NEIGH, REAL, ORIGINAL, SWAP}
    indexed = result.set_index(['model', 'origin', 'group', 'outcome']).mae
    for origin in origins:
        np.testing.assert_allclose(indexed.loc[(SWAP, origin, 'low', '4')], 4 * .2)
        np.testing.assert_allclose(indexed.loc[(ORIGINAL, origin, 'high', '12')], 2 * .9)
        np.testing.assert_allclose(indexed.loc[(SWAP, origin, 'low', 'total_12')], 4 * (3*.1 + 3*.2 + 6*.3))


def test_contrasts_preserve_sign_and_use_metric_scores_directly():
    frame = pd.DataFrame([
        dict(period='full_test', group='all', outcome='total_12', model=model, **dict(zip(METRICS, losses)))
        for model, losses in [(SWAP, (3, 1, 5)), (ORIGINAL, (2, 2, 3)),
                              (OWN, (6, 3, 8)), (NEIGH, (3, 2, 4))]
    ])
    result = contrasts(frame).set_index(['comparison', 'metric']).difference
    assert result.loc[('hybrids', 'mae')] == 1
    assert result.loc[('hybrids', 'mase')] == -1
    assert result.loc[('boosting', 'rmse')] == 4
