"""Past-target-only convex MAE blending; saved validation forecasts, no model refits."""
import json
from pathlib import Path
import numpy as np
import pandas as pd

ROOT=Path('data/processed/t03_learned_combination')
BANDS=((0,3),(3,6),(6,12))
MIN_ORIGINS=3


def read_saved_predictions(ctx):
    values={}
    for seed in (11,29,47):
        pieces=[]; origins=[]
        for path in sorted(ROOT.glob(f'predictions_seed{seed}_part*.npz')):
            with np.load(path,allow_pickle=False) as data:
                np.testing.assert_array_equal(data['codes'],ctx.codes)
                pieces.append(data['prediction'].copy()); origins.extend(data['origins'])
        if not pieces:raise ValueError('Missing learned-weight forecast chunks')
        np.testing.assert_array_equal(origins,ctx.origins)
        result=np.concatenate(pieces)
        if result.shape!=ctx.truth.shape or not np.isfinite(result).all() or (result<0).any():raise ValueError('Invalid learned predictions')
        values[seed]=result
    return values


def convex_mae_weight(neighbour,graph,truth):
    n=np.asarray(neighbour,dtype=float).ravel(); b=np.asarray(graph,dtype=float).ravel(); y=np.asarray(truth,dtype=float).ravel()
    if n.shape!=b.shape or n.shape!=y.shape or not np.isfinite([n,b,y]).all():raise ValueError('Aligned finite weight data required')
    delta=n-b; use=delta!=0
    if not use.any():return .5
    ratios=(y[use]-b[use])/delta[use]; mass=np.abs(delta[use])
    order=np.argsort(ratios,kind='stable'); ratios=ratios[order]; mass=mass[order]
    cumulative=np.cumsum(mass); half=cumulative[-1]/2
    index=int(np.searchsorted(cumulative,half,side='left'))
    lower=ratios[index]; upper=lower
    if index+1<len(ratios) and np.isclose(cumulative[index],half,rtol=1e-12,atol=0):upper=ratios[index+1]
    # Any minimiser in a flat interval is valid; closest to equal weights is deterministic.
    return float(np.clip(.5,np.clip(lower,0,1),np.clip(upper,0,1)))


def expanding_predictions(neighbour,graph,truth,origins,groups,min_origins=MIN_ORIGINS):
    """Arrays seed x origin x area x horizon; common weights pooled across seeds."""
    n=np.asarray(neighbour,dtype=float); b=np.asarray(graph,dtype=float); y=np.asarray(truth,dtype=float)
    if n.shape!=b.shape or n.ndim!=4 or n.shape[1:]!=y.shape or groups.shape!=y.shape[:2]:raise ValueError('Misaligned expanding-weight arrays')
    if any(not np.isfinite(a).all() or (a<0).any() for a in (n,b,y)) or not np.isin(groups,[0,1,2]).all():raise ValueError('Invalid expanding-weight data')
    month=pd.PeriodIndex(origins,freq='M').asi8
    targets=month[:,None]+np.arange(1,13)[None,:]
    output=np.empty_like(n); ledger=[]
    for t,origin in enumerate(origins):
        for group in range(3):
            current=groups[t]==group
            for start,stop in BANDS:
                available=(np.arange(len(origins))[:,None]<t)&(targets<=month[t])
                available[:,:start]=False; available[:,stop:]=False
                eligible=available[:,None,:]&(groups==group)[:,:,None]
                prior_count=int((eligible.any(axis=(1,2))).sum())
                if prior_count<min_origins:
                    weight=.5; basis='equal-weight warm-up'
                else:
                    # Targets and all three seed errors enter symmetrically; one scalar per stratum/band.
                    weight=convex_mae_weight(n[:,eligible],b[:,eligible],np.broadcast_to(y[eligible],(n.shape[0],eligible.sum())))
                    basis='past-observed-target MAE'
                for h in range(start,stop):output[:,t,current,h]=weight*n[:,t,current,h]+(1-weight)*b[:,t,current,h]
                seen=np.broadcast_to(targets[:,None,:],y.shape)[eligible]
                assert not len(seen) or seen.max()<=month[t]
                ledger.append({'origin':str(origin),'maturity':['low','medium','high'][group],
                    'band':f'{start+1}-{stop}','neighbour_weight':weight,'graph_weight':1-weight,
                    'prior_origins_with_observed_targets':prior_count,'observed_area_horizon_pairs':int(eligible.sum()),
                    'latest_target_used':str(pd.Period(ordinal=int(seen.max()),freq='M')) if len(seen) and prior_count>=min_origins else '',
                    'basis':basis})
    return output,pd.DataFrame(ledger)


def main():
    from evaluation.b_gate_c import require_release,load_predictions
    from evaluation.gate_c_io import context_from_panel,load_baselines
    from evaluation.gate_c_metrics import evaluate
    from evaluation.combination_validation import equal_weight
    from evaluation.gate_c import write_tables
    from evaluation.graph_diagnostics_report import table
    cfg,_=require_release(); ctx=context_from_panel(cfg)
    b,b_provenance=load_predictions(ctx); baseline,_,base_provenance=load_baselines(cfg,ctx)
    seeds=(11,29,47)
    prediction,weights=expanding_predictions(np.stack([baseline['gradient_boosting_neighbours'][s] for s in seeds]),
        np.stack([b['gnn_real'][s] for s in seeds]),ctx.truth,ctx.origins,ctx.groups)
    ROOT.mkdir(parents=True,exist_ok=True)
    for i,seed in enumerate(seeds):
        for part,indices in enumerate(np.array_split(np.arange(len(ctx.origins)),2)):
            path=ROOT/f'predictions_seed{seed}_part{part}.npz'
            np.savez_compressed(path,prediction=prediction[i,indices],codes=ctx.codes,origins=ctx.origins[indices])
            if path.stat().st_size>=5_000_000:raise ValueError('Learned prediction chunk exceeds 5 MB')
        # Replace only this script's older oversized derived cache, never source data.
        previous=ROOT/f'predictions_seed{seed}.npz'
        if previous.exists():previous.unlink()
    values={'learned_neighbour_B':dict(zip(seeds,prediction)),'half_neighbour_B':equal_weight(baseline['gradient_boosting_neighbours'],b['gnn_real']),
            'gradient_boosting_neighbours':baseline['gradient_boosting_neighbours'],'gradient_boosting_own':baseline['gradient_boosting_own'],'gnn_real':b['gnn_real']}
    bundle=evaluate(values,ctx); write_tables(bundle,ROOT)
    out=Path('data/explore/t03/learned_weights'); out.mkdir(parents=True,exist_ok=True)
    weights.to_csv(out/'weights.csv',index=False)
    policy={'objective':'pooled raw MAE','neighbour_weight_bounds':[0,1],'update':'every validation origin',
            'strata':'origin-dependent maturity tercile x horizons 1-3/4-6/7-12','minimum_prior_origins':MIN_ORIGINS,
            'warm_up_weight':.5,'seed_policy':'one common weight, objective pooled over seeds 11/29/47',
            'availability':'earlier forecast origins only; target month <= current origin; partial observed horizons allowed',
            'ties':'minimiser closest to 0.5','test_forecasts_or_losses':0,'model_refits':0,'B':b_provenance,'baselines':base_provenance}
    (ROOT/'policy_and_provenance.json').write_text(json.dumps(policy,indent=2)+'\n',encoding='utf-8')
    from visuals.learned_weights import render
    render(weights,bundle['scores'],out)
    text='''# Expanding learned combination — 1 November 2026

**Descriptive and exploratory, validation only.** No neural/boosting refits, GPU use or test-block evaluation. The earlier detailed message could not be found; the following concrete rules are newly documented implementation choices, not a claim to recover an unavailable specification.

At each validation forecast origin r, predict `w × neighbour boosting + (1−w) × B real`. Estimate one w in [0,1] for each origin-dependent maturity tercile and band 1–3, 4–6, 7–12, by minimising pooled raw MAE across all three matched seeds. Use only earlier forecast origins s<r and targets s+h<=r, including partially observed bands. Past samples retain their maturity at their own forecast origin; apply the resulting weight to the current origin's group. This uses the study's revised-data/month-availability convention, not historical CER release vintages.

Require three distinct prior forecast origins with at least one observed target in that band/group; otherwise w=0.5. Exact convex MAE minimisation uses a weighted median; flat optima choose the minimiser closest to 0.5. Bounds prevent extrapolation. These rules are fixed before computing these weights and are not selected from the final result. No estimated weight uses its own current/future target. No pooled in-sample full-validation weight is substituted for the expanding procedure.

All 36 origins and seeds are scored; warm-up periods stay in the evaluation. Weight estimation alone is performed on saved forecasts. This is an additional development procedure, not a confirmatory performance claim or final-test protocol. No new DM family is added here.

'''
    for group in ('all','low','medium','high'):
        text+=f'## {group} maturity\n\n'+table(bundle['scores'].loc[bundle['scores'].group.eq(group),['model','outcome','mae','mae_seed_sd','mase','mase_seed_sd','rmse','rmse_seed_sd']])+'\n\n'
    text+='''[Weights/availability ledger](../../data/explore/t03/learned_weights/weights.csv), [weight paths](../../data/explore/t03/learned_weights/weights.png), [horizon metrics](../../data/explore/t03/learned_weights/errors.png), [full tables](../../data/processed/t03_learned_combination/index.md), [policy/provenance](../../data/processed/t03_learned_combination/policy_and_provenance.json). Median/fallback/training-mean robustness views are in [the robustness report](mase_robustness.md). Seed spread describes the fixed base-model seeds; it is not weight-estimation uncertainty.

Generators: `evaluation.expanding_weights`, `visuals.learned_weights`. Stop for researcher review; no final-test weights are fitted or applied.
'''
    Path('reports/experiments/learned_combination_validation.md').write_text(text,encoding='utf-8')
    print(bundle['scores'].loc[bundle['scores'].group.eq('all')&bundle['scores'].outcome.isin(['1','6','12','total_12']),['model','outcome','mae','mase','rmse']].to_string(index=False))
    print(weights.groupby(['maturity','band']).neighbour_weight.agg(['min','median','max']).to_string())


if __name__=='__main__':main()
