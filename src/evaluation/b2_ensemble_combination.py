"""Validation-only B2 seed averages, frozen-rule combinations and bias views."""
import json
from pathlib import Path
import numpy as np
import pandas as pd
from evaluation.expanding_weights import BANDS,convex_mae_weight,expanding_predictions

SEEDS=(11,29,47)
ROOT=Path('data/processed/t03_b2_ensemble_combination')
EXPLORE=Path('data/explore/t03/b2_ensemble_combination')
REPORT=Path('reports/experiments/b2_ensemble_and_combination.md')
RULES=Path('reports/protocol/learned_weight_rules.md')


def ensemble(predictions):
    if set(predictions)!=set(SEEDS):raise ValueError('Exactly seeds 11,29,47 required')
    arrays=[np.asarray(predictions[s],dtype=np.float64) for s in SEEDS]
    if any(a.shape!=arrays[0].shape or not np.isfinite(a).all() or (a<0).any() for a in arrays):
        raise ValueError('Aligned finite nonnegative seed forecasts required')
    return np.mean(arrays,axis=0,dtype=np.float64)


def combinations(neighbour,real,truth,origins,groups):
    """Same shared pooled-seed weights for individual and ensemble-B2 variants."""
    n=np.stack([neighbour[s] for s in SEEDS]); b=np.stack([real[s] for s in SEEDS])
    mean=ensemble(real)
    variants={'B2_ensemble':np.repeat(mean[None],len(SEEDS),axis=0),'B2_individual':b}
    outputs={}; ledgers=[]
    for variant,graph in variants.items():
        output,ledger=expanding_predictions(n,graph,truth,origins,groups)
        outputs[variant]=dict(zip(SEEDS,output)); ledger['variant']=variant; ledgers.append(ledger)
    return outputs,pd.concat(ledgers,ignore_index=True),variants


def all_validation_weights(neighbour,graph,truth,origins,groups):
    """Descriptive all-origin optima, NEVER substituted into expanding forecasts."""
    n=np.asarray(neighbour,dtype=float); b=np.asarray(graph,dtype=float); y=np.asarray(truth,dtype=float)
    if n.shape!=b.shape or n.ndim!=4 or n.shape[1:]!=y.shape or groups.shape!=y.shape[:2]:raise ValueError('Misaligned full-validation arrays')
    if n.shape[-1]!=12 or len(origins)!=len(y) or not np.isin(groups,[0,1,2]).all():raise ValueError('Invalid full-validation calendar/groups')
    if any(not np.isfinite(a).all() or (a<0).any() for a in (n,b,y)):raise ValueError('Invalid full-validation forecasts/targets')
    month=pd.PeriodIndex(origins,freq='M').asi8
    if len(set(month))!=len(month) or np.any(np.diff(month)<=0):raise ValueError('Unique chronological origins required')
    targets=np.broadcast_to((month[:,None]+np.arange(1,13))[...,None],(len(month),12,y.shape[1])).transpose(0,2,1)
    rows=[]
    for group,label in enumerate(('low','medium','high')):
        for start,stop in BANDS:
            use=(groups==group)[:,:,None]&np.broadcast_to((np.arange(12)>=start)&(np.arange(12)<stop),y.shape)
            if not use.any():raise ValueError('Empty maturity/band stratum')
            nn=n[:,use]; bb=b[:,use]; yy=np.broadcast_to(y[use],nn.shape)
            w=convex_mae_weight(nn,bb,yy)
            rows.append({'maturity':label,'band':f'{start+1}-{stop}','neighbour_weight':w,'graph_weight':1-w,
                'validation_origins':int(use.any(axis=(1,2)).sum()),'area_horizon_pairs_per_seed':int(use.sum()),
                'seed_pooled_cells':int(nn.size),'latest_target_used':str(pd.Period(ordinal=int(targets[use].max()),freq='M')),
                'pooled_MAE_at_optimum':float(np.abs(w*nn+(1-w)*bb-yy).mean()),
                'scope':'all 36 validation origins, descriptive in-sample; not used for scored expanding predictions'})
    return pd.DataFrame(rows)


def bias_table(point_predictions,ctx):
    """Single-forecast origin/horizon bias with means needed to interpret its sign."""
    rows=[]
    for model,prediction in point_predictions.items():
        if prediction.shape!=ctx.truth.shape:raise ValueError('Misaligned bias forecasts')
        for t,origin in enumerate(ctx.origins):
            for group,label in ((None,'all'),(0,'low'),(1,'medium'),(2,'high')):
                use=np.ones(len(ctx.codes),bool) if group is None else ctx.groups[t]==group
                for h in range(12):
                    forecast=prediction[t,use,h].astype(float); actual=ctx.truth[t,use,h]
                    rows.append({'model':model,'origin':origin,'horizon':h+1,
                        'target_month':str(pd.Period(origin,freq='M')+h+1),'maturity':label,'areas':int(use.sum()),
                        'mean_forecast':float(forecast.mean()),'mean_actual':float(actual.mean()),
                        'mean_signed_error':float((forecast-actual).mean())})
    return pd.DataFrame(rows)


def save_predictions(name,runs,ctx):
    for seed,prediction in runs.items():
        for part,indices in enumerate(np.array_split(np.arange(len(ctx.origins)),2)):
            path=ROOT/f'{name}_seed{seed}_part{part}.npz'
            np.savez_compressed(path,prediction=prediction[indices],codes=ctx.codes,origins=ctx.origins[indices])
            if path.stat().st_size>=5_000_000:raise ValueError('Derived forecast chunk exceeds 5 MB')


def compare_saved_scores(actual,path,rename):
    old=pd.read_csv(path,dtype={'outcome':str}).replace({'model':rename})
    use=old.model.isin(actual.model)
    keys=['model','outcome','group']; expected=old.loc[use].set_index(keys).sort_index()
    current=actual.set_index(keys).reindex(expected.index)
    columns=['mae','mase','rmse','mae_seed_sd','mase_seed_sd','rmse_seed_sd']
    np.testing.assert_allclose(current[columns],expected[columns],rtol=1e-10,atol=1e-10)
    return len(expected)


def main():
    from threadpoolctl import threadpool_limits
    from evaluation.b2_gate_c import require_release
    from models.b2_runtime import CAMPAIGN,sha
    from evaluation.gate_c_io import context_from_panel,load_baselines,read_prediction
    from evaluation.gate_c_metrics import evaluate
    from evaluation.expanding_weights import read_saved_predictions,ROOT as EARLIER
    cfg,decision,order,authority=require_release()
    ROOT.mkdir(parents=True,exist_ok=True); EXPLORE.mkdir(parents=True,exist_ok=True)
    with threadpool_limits(limits=1):
        ctx=context_from_panel(cfg); baseline,_,base_provenance=load_baselines(cfg,ctx)
        paired={m:baseline[m] for m in ('gradient_boosting_own','gradient_boosting_neighbours')}
        hashes={}; points={}
        for condition in order:
            name='B2_'+condition; runs={}
            for seed in SEEDS:
                path=CAMPAIGN/condition/f'predictions_seed{seed}.npz'
                runs[seed]=read_prediction(path,ctx); hashes[str(path)]=sha(path)
            paired[name]=runs; points[name+'_ensemble']={'ensemble':ensemble(runs)}
            save_predictions(name+'_ensemble',points[name+'_ensemble'],ctx)
        earlier=read_saved_predictions(ctx); paired['earlier_learned_B']=earlier
        for path in EARLIER.glob('predictions_seed*_part*.npz'):hashes[str(path)]=sha(path)
        outputs,weights,variants=combinations(baseline['gradient_boosting_neighbours'],paired['B2_real'],ctx.truth,ctx.origins,ctx.groups)
        full=[]; n=np.stack([baseline['gradient_boosting_neighbours'][s] for s in SEEDS])
        for variant,runs in outputs.items():
            name='learned_'+variant; paired[name]=runs; save_predictions(name,runs,ctx)
            points[name+'_forecast_ensemble']={'ensemble':ensemble(runs)}
            save_predictions(name+'_forecast_ensemble',points[name+'_forecast_ensemble'],ctx)
            frame=all_validation_weights(n,variants[variant],ctx.truth,ctx.origins,ctx.groups)
            frame['variant']=variant; full.append(frame)
        for name in ('gradient_boosting_own','gradient_boosting_neighbours','earlier_learned_B'):
            points[name+'_ensemble']={'ensemble':ensemble(paired[name])}
        paired_bundle=evaluate(paired,ctx)
        point_bundle=evaluate(points,ctx,seeds=('ensemble',))
        for label,bundle in (('individual',paired_bundle),('ensemble',point_bundle)):
            for name,frame in bundle.items():
                frame.to_csv(ROOT/(label+'_'+name+('.csv.gz' if name in ('origin','areas') else '.csv')),index=False)
        b2_rows=compare_saved_scores(paired_bundle['scores'],Path('data/processed/t03_b2_gate_c/scores.csv'),
            {'real':'B2_real','shuffled':'B2_shuffled','no_graph':'B2_no_graph','without_base':'B2_without_base'})
        earlier_rows=compare_saved_scores(paired_bundle['scores'],EARLIER/'scores.csv',{'learned_neighbour_B':'earlier_learned_B'})
        full=pd.concat(full,ignore_index=True)
        weights.to_csv(EXPLORE/'expanding_weights.csv',index=False); full.to_csv(EXPLORE/'all36_weights.csv',index=False)
        used=weights.loc[weights.latest_target_used.ne('')]
        assert (used.latest_target_used<=used.origin).all() and weights.groupby('variant').size().eq(324).all()
        assert full.validation_origins.eq(36).all() and full.latest_target_used.le('2022-10').all()
        # Ensembling convex losses may not worsen the mean individual monthly loss.
        for condition in order:
            single=paired_bundle['scores'].loc[paired_bundle['scores'].model.eq('B2_'+condition)].set_index(['outcome','group'])
            avg=point_bundle['scores'].loc[point_bundle['scores'].model.eq('B2_'+condition+'_ensemble')].set_index(['outcome','group'])
            monthly=avg.index.get_level_values('outcome')!='total_12'
            for metric in ('mae','mase','rmse'):assert (avg.loc[monthly,metric]<=single.reindex(avg.index).loc[monthly,metric]+1e-10).all()
        bias=bias_table({'B2_real_ensemble':points['B2_real_ensemble']['ensemble'],
            'gradient_boosting_own_ensemble':points['gradient_boosting_own_ensemble']['ensemble'],
            'gradient_boosting_neighbours_ensemble':points['gradient_boosting_neighbours_ensemble']['ensemble']},ctx)
        assert bias.target_month.le('2022-10').all()
        bias.to_csv(EXPLORE/'bias_origin_horizon.csv',index=False)
        policy={'date':'2026-11-03','rules_file':str(RULES),'rules_sha256':sha(RULES),
            'acceptance':'B2 review accepted by researcher 3 November 2026',
            'ensemble':'arithmetic mean of forecasts over seeds 11,29,47 before scoring; float64',
            'ensemble_combination':'one common weight pooled over three boosting seeds, each paired with the same B2 ensemble',
            'individual_combination':'one common weight pooled over three matched boosting/B2 seeds; no per-seed weight optimisation',
            'combination_ensemble':'average three resulting combination forecasts; these use pooled-seed weights, not weights reoptimised on averages',
            'all36_weights':'descriptive in-sample only, all 36 origins and 12 targets through October 2022; never applied to expanding forecasts',
            'b2_authority':authority,'baseline_provenance':base_provenance,'input_sha256':hashes,
            'source_sha256':{p:sha(p) for p in ('src/evaluation/b2_ensemble_combination.py','src/evaluation/expanding_weights.py','src/evaluation/gate_c_metrics.py')},
            'saved_B2_baseline_score_rows_reproduced':b2_rows,'earlier_reference_score_rows_reproduced':earlier_rows,
            'expanding_weight_rows':len(weights),'all36_weight_rows':len(full),'bias_rows':len(bias),
            'model_refits':0,'gpu_use':False,'test_forecasts_or_losses':0}
        from visuals.b2_ensemble_combination import render
        render(paired_bundle['scores'],point_bundle['scores'],weights,full,bias,EXPLORE)
        write_report(paired_bundle,point_bundle,weights,full,bias,policy)
        (ROOT/'policy_and_verification.json').write_text(json.dumps(policy,indent=2)+'\n',encoding='utf-8')
        Path('reports/experiments/t03_b2_ensemble_combination_checks.json').write_text(json.dumps(policy,indent=2)+'\n',encoding='utf-8')
        print(point_bundle['scores'].loc[lambda f:f.group.eq('all')&f.outcome.isin(['1','6','12','total_12']),['model','outcome','mae','mase','rmse']].to_string(index=False))
        print(full[['variant','maturity','band','neighbour_weight','latest_target_used']].to_string(index=False))
        print(json.dumps({k:v for k,v in policy.items() if k.endswith('_rows') or k.endswith('_reproduced') or k in ('model_refits','gpu_use','test_forecasts_or_losses')}))


def write_report(individual,point,weights,full,bias,policy):
    from evaluation.graph_diagnostics_report import table
    text='''# B2 seed ensembles and learned combinations

3 November 2026. **Descriptive and exploratory, validation only.** B2 review accepted by the researcher. No model fits, GPU operations or final-test access. Validation origins November 2018 to October 2021; targets through October 2022 only.

## Accepted B2 findings

- B2 real has the lowest MAE at horizon 1 (not significant) but trails both boosting baselines from horizon 6, with growing overprediction at longer horizons.
- With per-area scaling, the graph adds no forecast value: no graph matches or beats real except at horizon 1, and real does not beat shuffled. The learned graph was excluded at the screen. The full-validation real/shuffled point scores differ, but no predeclared adjusted comparison is significant.
- Removing installed base worsens MAE and MASE at every reported outcome (minimum Holm p 0.056), consistent with the original B.

## Definitions and comparisons

Each B2 seed ensemble averages the three saved forecasts per origin/area/horizon **before** scoring. It is one forecast, not an average of three scores. Individual tables retain each seed's score and mean/SD/min/max. Ensemble tables have no seed SD: they contain one forecast. MAE/RMSE units are systems per area/month or per twelve-month window; MASE uses the unchanged training-only seasonal scales/fallback and twelve times the monthly denominator for total. Maturity groups remain origin-dependent. Float64 is used for means and new combinations; existing individual float32 total-sum conventions are preserved.

Learned combinations follow [the existing rules](../protocol/learned_weight_rules.md) unchanged: w times neighbour boosting plus (1-w) times B2, convex raw-MAE weights per maturity tercile and bands 1-3/4-6/7-12. One shared weight pools seeds 11/29/47; never optimise separately per seed. For the B2-ensemble variant, each boosting seed is paired with the SAME B2 mean forecast. For the individual variant, the matching B2 seed is used. Each variant therefore has three boosting-seed-paired combination forecasts. Their average is additionally scored as a single forecast ensemble. This preserves the pooled-seed objective; no weight is reoptimised against a mean forecast instead.

Only earlier origins and targets observed by the current origin enter expanding weights, including partially observed bands. Historical maturity remains attached to the historical origin. Three eligible prior origins are required; otherwise w=0.5. Warm-up origins remain scored. Exact weighted-median optimisation uses [0,1], choosing the minimiser nearest 0.5 on flat optima. Earlier learned-B combination forecasts are reused unchanged; they are not re-estimated. Both individual-seed and seed-mean boosting/earlier-combination references are shown, so the comparison basis is explicit. This adds no DM family and establishes no final-test protocol.

## Ensemble scores beside individual-seed scores

Full monthly/total/maturity scores and every individual seed are linked below. The following tables use horizons 1, 6, 12 and total for readability.

'''
    score=point['scores'].loc[point['scores'].group.eq('all')].set_index(['model','outcome'])
    means=bias.groupby(['model','maturity','horizon']).mean_signed_error.mean()
    key='learned_B2_ensemble_forecast_ensemble'
    summary='## Descriptive summary\n\n'
    summary+='The combination using B2 ensemble inputs, averaged across its three boosting-seed pairs, has MAE '
    summary+=', '.join(f"{score.loc[(key,h),'mae']:.6f}" for h in ('1','6','12','total_12'))+' at horizons 1, 6, 12 and total. '
    summary+='It improves on the B2 real ensemble at all four outcomes. Against both boosting forecast ensembles, it is lower at horizons 1 and 6 and total, but higher at horizon 12. The total advantage over own-lag boosting is small. The matched-individual-B2 combination forecast average is shown separately; no variant is selected or proposed for the final test here.\n\n'
    summary+='The added bias diagnostic qualifies the accepted review shorthand about growing overprediction. Across all 36 origins, B2 real ensemble signed error is '
    summary+=', '.join(f"{means.loc[('B2_real_ensemble','all',h)]:+.6f}" for h in (1,6,12))+' systems/area/month at horizons 1, 6 and 12. Overprediction is time-dependent, not a uniform monotonic horizon effect: earlier underprediction offsets large overpredictions at later forecast origins. The origin-year table and full heatmaps below retain both signs. No causal explanation is inferred.\n\n'
    insertion='## Ensemble scores beside individual-seed scores'
    text=text.replace(insertion,summary+insertion)
    members=[]
    for frame,kind in ((individual['seed'],'individual_seed'),(point['seed'],'forecast_ensemble')):
        selected=frame.loc[frame.model.isin(['B2_'+c+('_ensemble' if kind=='forecast_ensemble' else '') for c in ('real','shuffled','no_graph','without_base')])].copy()
        selected['condition']=selected.model.str.removesuffix('_ensemble')
        selected['forecast_type']=kind
        selected=selected.rename(columns={'seed':'member'})
        members.append(selected[['condition','forecast_type','member','outcome','group','mae','mase','rmse']])
    members=pd.concat(members,ignore_index=True).sort_values(['condition','group','outcome','forecast_type','member'],key=lambda s:s.astype(str))
    members.to_csv(EXPLORE/'ensemble_vs_seeds.csv',index=False)
    text+='### Each seed alongside its forecast ensemble\n\n[Every horizon/total and maturity group: 832 rows](../../data/explore/t03/b2_ensemble_combination/ensemble_vs_seeds.csv). The following comparison uses all areas and the four reported outcomes. Members 11, 29 and 47 are individual forecasts; member ensemble is their arithmetic forecast average, scored once.\n\n'
    text+=table(members.loc[members.group.eq('all')&members.outcome.isin(['1','6','12','total_12'])])+'\n\n'
    for group in ('all','low','medium','high'):
        text+='### '+group+' maturity: single forecast ensembles\n\n'
        frame=point['scores'].loc[point['scores'].group.eq(group)&point['scores'].outcome.isin(['1','6','12','total_12'])]
        text+=table(frame[['model','outcome','mae','mase','rmse','mean_signed_error']])+'\n\n'
        text+='### '+group+' maturity: individual seed means and spread\n\n'
        frame=individual['scores'].loc[individual['scores'].group.eq(group)&individual['scores'].outcome.isin(['1','6','12','total_12'])]
        text+=table(frame[['model','outcome','mae','mae_seed_sd','mase','mase_seed_sd','rmse','rmse_seed_sd']])+'\n\n'
    text+='''## Weights over time and all 36 validation origins

The expanding [weight paths](../../data/explore/t03/b2_ensemble_combination/weights_over_time.png) / [plotted CSV](../../data/explore/t03/b2_ensemble_combination/weights_over_time.csv) show both variants by maturity and horizon band, with availability and warm-up ledger. Weight w is the share assigned to neighbour boosting; 1-w is assigned to B2. Dashed full-validation reference lines are descriptive only.

The following weights use **all 36 validation origins and their full twelve-month targets**, through October 2022 at the latest. They are in-sample descriptive estimates, not a leakage-free validation forecast, not the weights used for any reported expanding score, and not an approved final-test specification. No score is supplied for applying these weights retrospectively. [Full-validation figure](../../data/explore/t03/b2_ensemble_combination/all36_weights.png) / [CSV](../../data/explore/t03/b2_ensemble_combination/all36_weights.csv).

'''
    text+=table(full[['variant','maturity','band','neighbour_weight','graph_weight','validation_origins','seed_pooled_cells','latest_target_used']])+'\n\n'
    text+='''## Bias by forecast origin and horizon

Mean signed error is forecast minus actual, averaged over observed areas. The three main series are B2 real's seed ensemble and both boosting seed ensembles. Averaging signed errors over seeds is equivalent to using the mean forecast. Positive is overprediction. [Origin/horizon heatmaps](../../data/explore/t03/b2_ensemble_combination/bias_origin_horizon.png) / [CSV](../../data/explore/t03/b2_ensemble_combination/bias_origin_horizon.csv) include target month, mean forecast, mean actual and maturity group. [Horizon/maturity summary](../../data/explore/t03/b2_ensemble_combination/bias_horizon_maturity.png) / [CSV](../../data/explore/t03/b2_ensemble_combination/bias_horizon_maturity.csv). These localise error patterns, not causal drivers.

'''
    summaries=bias.groupby(['model','maturity','horizon'],as_index=False)[['mean_forecast','mean_actual','mean_signed_error']].mean()
    text+=table(summaries.loc[summaries.maturity.eq('all')&summaries.horizon.isin([1,6,12])])+'\n\n'
    years=bias.loc[bias.maturity.eq('all')].assign(origin_year=lambda f:f.origin.str[:4]).groupby(['model','origin_year','horizon'],as_index=False)[['mean_forecast','mean_actual','mean_signed_error']].mean()
    years.to_csv(EXPLORE/'bias_origin_year.csv',index=False)
    text+='Horizon-12 signed error by forecast-origin year (all areas, all available origins in that calendar year; descriptive grouping):\n\n'+table(years.loc[years.horizon.eq(12)])+'\n\n[All origin-year/horizon values](../../data/explore/t03/b2_ensemble_combination/bias_origin_year.csv).\n\n'
    worst=bias.loc[bias.model.eq('B2_real_ensemble')&bias.maturity.eq('all')&bias.horizon.eq(12)].nlargest(6,'mean_signed_error')
    text+='Largest six horizon-12 overprediction origins (display selection only; all origins remain scored):\n\n'+table(worst)+'\n\n'
    text+='''## Outputs and verification

[All individual score rows](../../data/processed/t03_b2_ensemble_combination/individual_scores.csv), [individual seeds](../../data/processed/t03_b2_ensemble_combination/individual_seed.csv), [ensemble score rows](../../data/processed/t03_b2_ensemble_combination/ensemble_scores.csv), [ensemble origin losses](../../data/processed/t03_b2_ensemble_combination/ensemble_origin.csv.gz), [weight/availability ledger](../../data/explore/t03/b2_ensemble_combination/expanding_weights.csv), [combination error curves](../../data/explore/t03/b2_ensemble_combination/combination_errors.png) / [CSV](../../data/explore/t03/b2_ensemble_combination/combination_errors.csv), [B2 seed-average curves](../../data/explore/t03/b2_ensemble_combination/ensemble_errors.png) / [CSV](../../data/explore/t03/b2_ensemble_combination/ensemble_errors.csv), [index](../../data/explore/t03/b2_ensemble_combination/index.md). Private paper candidates and visual copies use the same values. Full verification and input/source hashes: [checks](t03_b2_ensemble_combination_checks.json).

'''
    text+=f"Reproduced {policy['saved_B2_baseline_score_rows_reproduced']} existing B2/baseline pooled score rows and {policy['earlier_reference_score_rows_reproduced']} earlier-B/reference rows. There are {len(weights)} expanding weight records (324 per variant), {len(full)} all-validation weights and {len(bias)} origin/horizon/maturity bias rows. All expanding latest-target dates are no later than their forecast origin; warm-ups remain included. Model/source/protocol/input hashes are retained. No model refits, GPU use or test forecasts/losses.\n\n"
    text+='Generators: `evaluation.b2_ensemble_combination`, `visuals.b2_ensemble_combination`. Stop for researcher review; no further combination, architecture, weight selection or final-test work is initiated.\n'
    REPORT.write_text(text,encoding='utf-8')


if __name__=='__main__':main()
