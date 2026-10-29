"""P7 degree-preserving within-state controls, with fixed cross-state edges."""
import json
from pathlib import Path

import numpy as np
import pandas as pd

from evaluation.frozen import frozen_protocol
from features.panel import load_panel


def edge_set(edges):
    return {tuple(sorted((int(a),int(b)))) for a,b in edges}


def shuffle_graph(edges, states, seed, swaps_per_edge=10, attempt_multiplier=100):
    original = edge_set(edges)
    if len(original)!=len(edges) or any(a==b for a,b in original):
        raise ValueError('Invalid original edges')
    rng = np.random.default_rng(seed)
    output = {edge for edge in original if states[edge[0]]!=states[edge[1]]}
    records = []
    for state in sorted(set(states)):
        initial = {edge for edge in original if states[edge[0]]==states[edge[1]]==state}
        pool = sorted(initial); current = set(initial)
        target = swaps_per_edge*len(pool)
        accepted = attempts = 0
        while accepted<target and attempts<max(1,target*attempt_multiplier):
            if len(pool)<2:
                break
            attempts += 1
            i,j = rng.choice(len(pool),2,replace=False)
            a,b = pool[i]; c,d = pool[j]
            if len({a,b,c,d})!=4:
                continue
            if rng.integers(2):
                c,d = d,c
            first,second = tuple(sorted((a,c))),tuple(sorted((b,d)))
            if first in current or second in current:
                continue
            current.remove(pool[i]); current.remove(pool[j])
            current.update((first,second)); pool[i],pool[j] = first,second
            accepted += 1
        retained = len(initial & current)
        records.append({'state_code':state,'seed':seed,'within_state_edges':len(initial),
            'target_swaps':target,'attempted_swaps':attempts,'accepted_swaps':accepted,
            'original_edges_retained':retained,'original_edge_share':retained/len(initial) if initial else None,
            'target_reached':accepted==target,'mixing_review_required':bool(initial) and (accepted<target or retained==len(initial))})
        output.update(current)
    result = np.array(sorted(output),dtype=np.int32).reshape(-1,2)
    if len(result)!=len(edges):
        raise AssertionError('Shuffle changed edge count')
    np.testing.assert_array_equal(np.bincount(result.ravel(),minlength=len(states)),
                                  np.bincount(np.asarray(edges).ravel(),minlength=len(states)))
    fixed = {edge for edge in original if states[edge[0]]!=states[edge[1]]}
    if {edge for edge in output if states[edge[0]]!=states[edge[1]]}!=fixed:
        raise AssertionError('Shuffle changed cross-state edges')
    return result,pd.DataFrame(records)


def main():
    cfg,signature = frozen_protocol('protocol-v1.1')
    out = Path('data/explore/t03'); saved = Path('data/processed/t03_graphs')
    states = pd.read_csv(out/'state_assignment.csv',dtype={'postcode':str,'state_code':str})
    if not states.coverage_ok.all() or states.state_code.isna().any():
        raise ValueError('State coverage has not passed; researcher review required before shuffling')
    panel = load_panel(through=cfg['splits']['validation']['first_origin'])
    state = states.set_index('postcode').loc[panel.codes,'state_code'].to_numpy()
    saved.mkdir(parents=True,exist_ok=True)
    records = []
    for seed in cfg['state_assignment']['graph_seeds']:
        shuffled,diagnostics = shuffle_graph(panel.edges,state,seed)
        records.append(diagnostics)
        np.savez_compressed(saved/f'shuffled_seed{seed}.npz',edges=shuffled,codes=panel.codes,
                            observed=panel.observed,protocol_sha256=signature)
    diagnostics = pd.concat(records,ignore_index=True)
    diagnostics.to_csv(out/'graph_swap_diagnostics.csv',index=False)
    summary = {'protocol_sha256':signature,'real_edges':len(panel.edges),
               'cross_state_edges_fixed':int(np.sum(state[panel.edges[:,0]]!=state[panel.edges[:,1]])),
               'states_requiring_review':diagnostics.loc[diagnostics.mixing_review_required,['state_code','seed']].to_dict('records'),
               'review_rule':'ten accepted swaps per intra-state edge; flag unmet target or completely unchanged nonempty state graph; no silently relaxed null'}
    (out/'graph_conditions_summary.json').write_text(json.dumps(summary,indent=2),encoding='utf-8')
    print(json.dumps(summary,indent=2))
    if diagnostics.mixing_review_required.any():
        raise ValueError('State graph cannot mix adequately: stop for researcher review')


if __name__=='__main__':
    main()
