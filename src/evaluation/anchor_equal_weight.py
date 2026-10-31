"""Authorised descriptive equal-weight combinations of saved anchor forecasts."""
import hashlib
import json
from pathlib import Path
import numpy as np
import pandas as pd
from evaluation.screen_baseline_comparison import band_scores,load_anchor_baselines


def combinations(own,neighbour,b_real,c_real):
    arrays=[np.asarray(v,dtype=np.float64) for v in (own,neighbour,b_real,c_real)]
    if len({v.shape for v in arrays})!=1 or any(not np.isfinite(v).all() or (v<0).any() for v in arrays):
        raise ValueError('Aligned finite nonnegative saved forecasts required')
    own,neighbour,b_real,c_real=arrays
    return {'half_own_B':.5*own+.5*b_real,'half_neighbour_B':.5*neighbour+.5*b_real,
            'half_own_C':.5*own+.5*c_real}


def main():
    from evaluation.frozen import frozen_protocol
    from evaluation.gate_c_io import context_from_panel
    from evaluation.gate_c_metrics import Context
    from evaluation.graph_diagnostics_report import table
    from models.screen_cpu import ANCHORS
    from models.architecture_screen import ROOT,output
    cfg,_=frozen_protocol('protocol-v2'); full=context_from_panel(cfg)
    use=np.isin(full.origins,ANCHORS)
    ctx=Context(full.origins[use],full.codes,full.truth[use],full.scales[use],full.groups[use],full.edges,full.fit_origins[use])
    baseline,provenance=load_anchor_baselines(ctx)
    sources={}
    for candidate in ('B','C'):
        pieces=[]
        for anchor in ANCHORS:
            path=output(candidate,anchor,'real')/'prediction.npz'
            with np.load(path,allow_pickle=False) as data:
                np.testing.assert_array_equal(data['codes'],ctx.codes)
                assert str(data['origin'])==anchor
                pieces.append(data['prediction'].copy())
            provenance['prediction_sha256'][path.as_posix()]=hashlib.sha256(path.read_bytes()).hexdigest()
        sources[candidate]=np.stack(pieces)
    own=baseline['gradient_boosting_own_frozen']; neighbour=baseline['gradient_boosting_neighbours_frozen']
    mixed=combinations(own,neighbour,sources['B'],sources['C'])
    scores=band_scores({**baseline,**mixed},ctx)
    paired=[]
    for name in mixed:
        for reference in baseline:
            joined=scores.loc[scores.model.eq(name)].merge(scores.loc[scores.model.eq(reference)],
                on=['anchor','band','group'],suffixes=('_combination','_baseline'),validate='one_to_one')
            for row in joined.to_dict('records'):
                record={k:row[k] for k in ('anchor','band','group')}|{'combination':name,'reference':reference}
                for metric in ('mae','mase','rmse'):
                    x=row[metric+'_combination']; y=row[metric+'_baseline']
                    record.update({metric+'_combination':x,metric+'_baseline':y,metric+'_gain':y-x})
                paired.append(record)
    out=Path('data/explore/t03/equal_weight'); out.mkdir(parents=True,exist_ok=True)
    scores.to_csv(out/'scores.csv',index=False); pd.DataFrame(paired).to_csv(out/'comparisons.csv',index=False)
    (out/'provenance.json').write_text(json.dumps(provenance,indent=2)+'\n',encoding='utf-8')
    text='''# Equal-weight anchor combinations — 31 October 2026

**Descriptive and exploratory.** CPU-only arithmetic on saved seed-11 forecasts. No fits, estimated weights, model selection change, GPU use, DM tests or sealed-test access. Weights are exactly 0.5/0.5 on forecast counts, computed in float64. Own/neighbour boosting uses the frozen selection fitted at each anchor. C real retains its original strict-prior base internally.

`half_own_B` = own-lag boosting + B real; `half_neighbour_B` = neighbour-lag boosting + B real; `half_own_C` = own-lag boosting + C real. Each is an equal-weight arithmetic average. Bands pool monthly errors, not band totals. MASE uses the same training-only anchor scales. RMSE roots pooled squared errors. Origin-dependent maturity groups are unchanged.

'''
    for anchor in [*ANCHORS,'both_anchors']:
        text+=f'## {anchor}\n\n'
        text+=table(scores.loc[scores.anchor.eq(anchor),['model','band','group','mae','mase','rmse']])+'\n\n'
    text+='''[Every combination against both baselines, per anchor/band/tercile](../../data/explore/t03/equal_weight/comparisons.csv); [scores](../../data/explore/t03/equal_weight/scores.csv); [source hashes](../../data/explore/t03/equal_weight/provenance.json); [figure](../../data/explore/t03/equal_weight/overall_mae.png). Positive gain means lower combination error. The 1–12 band supplies the overall monthly summary in addition to the requested three bands. No claim of out-of-sample confirmation follows from inspecting already-used anchors.

Generator: `python -m evaluation.anchor_equal_weight`; figure: `visuals.equal_weight`. These combinations are not part of the authorised B campaign or its DM family.
'''
    Path('reports/experiments/t03_equal_weight_anchors.md').write_text(text,encoding='utf-8')
    from visuals.equal_weight import render
    render(scores,out)
    print(scores.loc[scores.anchor.eq('both_anchors')&scores.band.eq('1-12')&scores.group.eq('all'),['model','mae','mase','rmse']].to_string(index=False))


if __name__=='__main__':main()
