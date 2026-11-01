"""Validation-only scale diagnostics from saved predictions, without fitting."""
import json
from pathlib import Path
import numpy as np
import pandas as pd
from evaluation.protocol import seasonal_scales


def robust_metrics(errors,seasonal,training_mean):
    """One origin/group/outcome's raw per-area absolute errors and denominators."""
    errors=np.asarray(errors,dtype=float); seasonal=np.asarray(seasonal,dtype=float)
    training_mean=np.asarray(training_mean,dtype=float)
    positive=seasonal>0; level_positive=training_mean>0
    scaled=errors[positive]/seasonal[positive]
    return {'areas':len(errors),'nonfallback_areas':int(positive.sum()),'fallback_areas':int((~positive).sum()),
        'mase_without_fallback':float(scaled.mean()) if len(scaled) else np.nan,
        'median_scaled_error_without_fallback':float(np.median(scaled)) if len(scaled) else np.nan,
        'positive_mean_areas':int(level_positive.sum()),'zero_mean_areas':int((~level_positive).sum()),
        'mean_level_scaled_error':float((errors[level_positive]/training_mean[level_positive]).mean()) if level_positive.any() else np.nan}


def main():
    from evaluation.b_gate_c import require_release,load_predictions
    from evaluation.gate_c_io import context_from_panel,load_baselines
    from evaluation.combination_validation import equal_weight
    from evaluation.gate_c_metrics import OUTCOMES
    from evaluation.graph_diagnostics_report import table
    from features.panel import load_panel
    cfg,_=require_release(); ctx=context_from_panel(cfg)
    b,_=load_predictions(ctx); baseline,_,_=load_baselines(cfg,ctx)
    predictions={**baseline,**b}
    predictions['half_own_B']=equal_weight(baseline['gradient_boosting_own'],b['gnn_real'])
    predictions['half_neighbour_B']=equal_weight(baseline['gradient_boosting_neighbours'],b['gnn_real'])
    from evaluation.expanding_weights import ROOT as WEIGHTS
    if (WEIGHTS/'policy_and_provenance.json').exists():
        from evaluation.expanding_weights import read_saved_predictions
        predictions['learned_neighbour_B']=read_saved_predictions(ctx)
    panel=load_panel(through='2022-10'); values=panel.targets[panel.observed]
    seasonal=np.stack([seasonal_scales(values,panel.months,fit,'2011-01') for fit in ctx.fit_origins])
    means=np.stack([values[:,panel.index('2011-01'):panel.index(fit)+1].mean(axis=1,dtype=float) for fit in ctx.fit_origins])
    records=[]
    for model,seeds in predictions.items():
        for seed,pred in seeds.items():
            monthly=np.abs(pred.astype(float)-ctx.truth)
            total=np.abs(pred.sum(axis=2).astype(float)-ctx.truth.sum(axis=2))
            errors=np.concatenate([monthly,total[:,:,None]],axis=2)
            for t,origin in enumerate(ctx.origins):
                for group,label in ((None,'all'),(0,'low'),(1,'medium'),(2,'high')):
                    use=np.ones(len(ctx.codes),bool) if group is None else ctx.groups[t]==group
                    for h,outcome in enumerate(OUTCOMES):
                        factor=12 if outcome=='total_12' else 1
                        record=robust_metrics(errors[t,use,h],seasonal[t,use]*factor,means[t,use]*factor)
                        record['median_scaled_error_with_fallback']=float(np.median(errors[t,use,h]/(ctx.scales[t,use]*factor)))
                        records.append({'model':model,'seed':seed,'origin':origin,'group':label,'outcome':outcome,**record})
    origin=pd.DataFrame(records)
    columns=['mase_without_fallback','median_scaled_error_without_fallback','median_scaled_error_with_fallback','mean_level_scaled_error']
    by_seed=origin.groupby(['model','seed','outcome','group'],as_index=False)[columns].mean()
    summaries=[]
    for keys,part in by_seed.groupby(['model','outcome','group']):
        row=dict(zip(['model','outcome','group'],keys))
        for metric in columns:row.update({metric:part[metric].mean(),metric+'_seed_sd':part[metric].std(ddof=1)})
        summaries.append(row)
    summary=pd.DataFrame(summaries)
    coverage=origin.loc[origin.model.eq('gnn_real')&origin.seed.eq(11)&origin.outcome.eq('1'),
        ['origin','group','areas','nonfallback_areas','fallback_areas','positive_mean_areas','zero_mean_areas']]
    out=Path('data/explore/t03/mase_robustness'); out.mkdir(parents=True,exist_ok=True)
    origin.to_csv(out/'origin_metrics.csv.gz',index=False); by_seed.to_csv(out/'seed_metrics.csv',index=False)
    summary.to_csv(out/'summary.csv',index=False); coverage.to_csv(out/'coverage.csv',index=False)
    text='''# MASE robustness — 1 November 2026

CPU-only, no model refits. Saved validation predictions, 36 origins and matched seeds 11/29/47; final test untouched. Aggregation definitions are explicit below. The learned expanding combination follows the concrete rules in reports/protocol/learned_weight_rules.md and is included when its saved validation forecasts are present.

Raw seasonal scale uses January 2011 through each scheduled fit origin. `mase_without_fallback` excludes only area/origin pairs with zero raw seasonal scale from this diagnostic; it does not remove data from any model or the accepted evaluation. Coverage below records all such pairs. No epsilon or replacement denominator is introduced.

Median scaled error is the within-origin/group median of per-area absolute scaled error, then an equal-origin and equal-seed average. Report both with the accepted fallback denominator and without fallback areas. This is explicitly an average of per-origin medians, not a median of per-area origin-mean errors. Mean-level-scaled error averages absolute error divided by each area's own mean target count from January 2011 through fit origin. Zero training means are undefined and excluded from that diagnostic with coverage reported, never changed to one. Total errors use twelve times each monthly denominator. Maturity groups remain origin-dependent. Seed SD is computed after origin aggregation.

These diagnostic filters affect metrics only, not panel membership or training. They are exploratory robustness views, not new confirmatory tests. The full monthly horizons and groups are in [summary](../../data/explore/t03/mase_robustness/summary.csv), [seeds](../../data/explore/t03/mase_robustness/seed_metrics.csv) and [coverage](../../data/explore/t03/mase_robustness/coverage.csv).

'''
    for group in ('all','low','medium','high'):
        text+=f'## {group} maturity\n\n'+table(summary.loc[summary.group.eq(group)&summary.outcome.isin(['1','6','12','total_12']),
            ['model','outcome',*columns]])+'\n\n'
    text+='## Coverage\n\n'+table(coverage)+'\n\nGenerator: `evaluation.mase_robustness`. No additional DM family is claimed.\n'
    Path('reports/experiments/mase_robustness.md').write_text(text,encoding='utf-8')
    (out/'index.md').write_text('# MASE robustness outputs\n\n'+'\n'.join(f'- [{p.name}]({p.name}): `evaluation.mase_robustness`.' for p in sorted(out.iterdir()) if p.name!='index.md')+'\n',encoding='utf-8')
    print(json.dumps({'models':len(predictions),'summary_rows':len(summary),'fallback_area_origin_pairs':int(coverage.loc[coverage.group.eq('all'),'fallback_areas'].sum()),
                      'zero_mean_area_origin_pairs':int(coverage.loc[coverage.group.eq('all'),'zero_mean_areas'].sum()),'fits':0,'test_forecasts_or_losses':0}))


if __name__=='__main__':main()
