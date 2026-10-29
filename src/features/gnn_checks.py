"""CPU-only real-panel leakage and graph-identity checks; never import torch."""
import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd

from evaluation.frozen import frozen_protocol
from features.gnn import GNNWindows
from features.panel import load_panel, Panel
from geography.conditions import edge_set


def main():
    cfg,signature = frozen_protocol('protocol-v1.1')
    panel = load_panel(through=cfg['splits']['validation']['last_origin'])
    states = pd.read_csv('data/explore/t03/state_assignment.csv',dtype={'postcode':str,'state_code':str}).set_index('postcode').loc[panel.codes,'state_code'].to_numpy()
    checks = []
    for origin in ('2018-11','2020-08','2021-10'):
        before = GNNWindows(panel,cfg).at(origin)
        changed = panel.targets.copy()
        changed[:,panel.months>origin] = 1e6
        changed[~panel.observed] = np.nan
        after = GNNWindows(Panel(panel.codes,panel.months,changed,panel.observed,panel.edges),cfg).at(origin)
        np.testing.assert_array_equal(before,after)
        assert np.all(before[:,~panel.observed,:]==0)
        checks.append({'origin':origin,'window_shape':list(before.shape),'future_mutation_unchanged':True,'unknown_inputs_zero':True})
    graph_checks = []
    original = edge_set(panel.edges)
    cross = {edge for edge in original if states[edge[0]]!=states[edge[1]]}
    for seed in cfg['state_assignment']['graph_seeds']:
        path = Path(f'data/processed/t03_graphs/shuffled_seed{seed}.npz')
        with np.load(path,allow_pickle=False) as saved:
            np.testing.assert_array_equal(saved['codes'],panel.codes)
            np.testing.assert_array_equal(saved['observed'],panel.observed)
            assert saved['protocol_sha256'].item()==signature
            edges = saved['edges']
        np.testing.assert_array_equal(np.bincount(edges.ravel(),minlength=len(panel.codes)),
                                      np.bincount(panel.edges.ravel(),minlength=len(panel.codes)))
        shuffled = edge_set(edges)
        assert len(shuffled)==len(original) and not any(a==b for a,b in shuffled)
        assert {edge for edge in shuffled if states[edge[0]]!=states[edge[1]]}==cross
        graph_checks.append({'seed':seed,'edges':len(edges),'cross_state_edges_fixed':len(cross),
                             'degrees_and_missing_mask_preserved':True,'sha256':hashlib.sha256(path.read_bytes()).hexdigest()})
    report = {'protocol':'protocol-v1.1','protocol_sha256':signature,'leakage_checks':checks,
              'graph_checks':graph_checks,'latest_loaded_month':str(panel.months[-1]),
              'training_or_gpu_use':False,'test_forecasts_or_losses':0,
              'torch_tensor_tests':'researcher must run after pinned dependency installation'}
    destination = Path('reports/experiments/t03_preparation_checks.json')
    destination.write_text(json.dumps(report,indent=2),encoding='utf-8')
    print(json.dumps(report,indent=2))


if __name__=='__main__':
    main()
