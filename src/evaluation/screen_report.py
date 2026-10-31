"""Selection and reporting for protocol-v3-screen (no fitting)."""
import json
from pathlib import Path
import numpy as np
import pandas as pd


def select_candidate(summary):
    if set(summary.candidate)!={'A','B','C'} or not np.isfinite(summary[['mae','cost_seconds']]).all().all():
        raise ValueError('All three complete candidates and measured costs required')
    best=summary.mae.min()
    within=summary.loc[summary.mae<=best*1.02]
    return within.sort_values(['cost_seconds','mae','candidate']).iloc[0].candidate


def report():
    from models.screen_cpu import ROOT,OLD,ANCHORS,base_jobs,folder,write_json
    from models.architecture_screen import jobs,output,fingerprint,load_base
    from evaluation.gate_c_io import context_from_panel
    from evaluation.gate_c_metrics import Context,evaluate,OUTCOMES
    from evaluation.graph_diagnostics import neighbour_gap
    from features.panel import load_panel
    cfg,signature=fingerprint()
    if not all((output(*j)/'complete.json').exists() for j in jobs()):raise RuntimeError('All twelve GPU fits required before comparison/selection')
    manifest=json.loads((ROOT/'gpu_manifest.json').read_text())
    if any(manifest[k]!=v for k,v in signature.items()):raise RuntimeError('Screen provenance changed')
    context=context_from_panel(cfg); use=np.isin(context.origins,ANCHORS)
    ctx=Context(context.origins[use],context.codes,context.truth[use],context.scales[use],context.groups[use],context.edges,context.fit_origins[use])
    panel=load_panel(through=ANCHORS[-1]); base_origins,base_cube=load_base(panel)
    predictions={}; fit_records=[]; curves=[]
    for candidate,anchor,condition in jobs():
        path=output(candidate,anchor,condition)
        record=json.loads((path/'complete.json').read_text()); fit_records.append(record)
        curve=pd.read_csv(path/'training_curve.csv'); curve['candidate']=candidate; curve['condition']=condition; curve['anchor']=anchor; curves.append(curve)
        with np.load(path/'prediction.npz',allow_pickle=False) as data:
            np.testing.assert_array_equal(data['codes'],ctx.codes)
            if str(data['origin'])!=anchor:raise RuntimeError('Forecast origin mismatch')
            predictions.setdefault(f'{candidate}_{condition}',{})[anchor]=data['prediction'].copy()
    combined={name:{11:np.stack([values[a] for a in ANCHORS])} for name,values in predictions.items()}
    combined['C_base']={11:np.stack([base_cube[list(base_origins).index(a),panel.observed] for a in ANCHORS])}
    result=evaluate(combined,ctx,seeds=(11,))
    result['origin']['rmse']=np.sqrt(result['origin']['mse'])
    out=Path('data/explore/t03/architecture_screen'); out.mkdir(parents=True,exist_ok=True)
    for key,value in result.items():value.to_csv(out/(f'{key}.csv.gz' if key=='areas' else f'{key}.csv'),index=False)
    from evaluation.screen_baseline_comparison import write_comparisons
    comparison_text=write_comparisons(combined,ctx,out)
    fits=pd.DataFrame(fit_records); fits.to_csv(out/'fits.csv',index=False)
    pd.concat(curves).to_csv(out/'training_curves.csv',index=False)
    isolated=np.bincount(panel.edges.ravel(),minlength=len(panel.codes))[panel.observed]==0
    own=np.stack([panel.targets[panel.observed,panel.index(a)] for a in ANCHORS])
    gaps=neighbour_gap(own.astype(float),ctx.edges)
    isolation=[]; shifts=[]
    for model,seeds in combined.items():
        monthly=seeds[11].astype(float)-ctx.truth
        errors=np.concatenate([monthly,(seeds[11].sum(axis=2)-ctx.truth.sum(axis=2))[:,:,None]],axis=2)
        for t,anchor in enumerate(ANCHORS):
            for k,outcome in enumerate(OUTCOMES):
                isolation.append({'model':model,'anchor':anchor,'outcome':outcome,'mae':np.abs(errors[t,isolated,k]).mean(),'areas':int(isolated.sum())})
    for candidate in ('A','B','C'):
        real=combined[f'{candidate}_real'][11]; no=combined[f'{candidate}_no_graph'][11]
        delta=np.concatenate([real.astype(float)-no.astype(float),(real.sum(axis=2)-no.sum(axis=2))[:,:,None]],axis=2)
        for t,anchor in enumerate(ANCHORS):
            for k,outcome in enumerate(OUTCOMES):
                for i,code in enumerate(ctx.codes):
                    shifts.append({'candidate':candidate,'anchor':anchor,'outcome':outcome,'postcode':code,
                                   'neighbour_gap':gaps[t,i],'real_minus_no_graph':delta[t,i,k]})
    pd.DataFrame(isolation).to_csv(out/'isolates.csv',index=False)
    shift=pd.DataFrame(shifts); shift.to_csv(out/'neighbour_shift.csv.gz',index=False)
    correlations=[]
    for keys,part in shift.groupby(['candidate','anchor','outcome']):
        valid=part.dropna()
        defined=len(valid)>=3 and valid.neighbour_gap.nunique()>1 and valid.real_minus_no_graph.nunique()>1
        correlations.append(dict(zip(['candidate','anchor','outcome'],keys))|{'areas':len(valid),
            'cross_area_pearson':valid.neighbour_gap.corr(valid.real_minus_no_graph) if defined else np.nan,
            'cross_area_spearman':valid.neighbour_gap.corr(valid.real_minus_no_graph,method='spearman') if defined else np.nan,
            'status':'defined' if defined else 'insufficient_pairs_or_constant_series'})
    pd.DataFrame(correlations).to_csv(out/'neighbour_shift_summary.csv',index=False)
    # Charge C for all required base fits, including the original measured cost of reused fits.
    base_cost=0.; new_base_cost=0.
    for j in base_jobs():
        record=json.loads((folder(j)/'complete.json').read_text())
        if record['new_fit']:seconds=record['fit_seconds']; new_base_cost+=seconds
        else:seconds=json.loads(Path(record['reused']).with_suffix('.json').read_text())['seconds']
        base_cost+=seconds
    rows=[]
    origin=result['origin']
    for candidate in ('A','B','C'):
        part=origin.loc[origin.model.eq(f'{candidate}_real')&origin.group.eq('all')&origin.outcome.ne('total_12')]
        paired=[]
        for anchor in ANCHORS:
            real=part.loc[part.origin.eq(anchor)].mae.mean()
            control=origin.loc[origin.model.eq(f'{candidate}_no_graph')&origin.group.eq('all')&origin.outcome.ne('total_12')&origin.origin.eq(anchor)].mae.mean()
            paired.append(bool(real<control))
        times=fits.loc[fits.candidate.eq(candidate)].fit_seconds.sum()
        loss=fits.loc[fits.candidate.eq(candidate)].pivot(index='anchor',columns='condition',values='training_loss')
        rows.append({'candidate':candidate,'mae':part.mae.mean(),'gpu_fit_seconds':times,
            'allocated_base_cpu_seconds':base_cost if candidate=='C' else 0.,
            'cost_seconds':(times+(base_cost if candidate=='C' else 0))/4,
            'beats_own_no_graph_both_anchors':all(paired),
            'training_loss_worse_both_anchors':bool((loss.real>loss.no_graph).all())})
    selection=pd.DataFrame(rows); chosen=select_candidate(selection); selection['selected']=selection.candidate.eq(chosen)
    selection.to_csv(out/'selection.csv',index=False)
    no_success=not selection.beats_own_no_graph_both_anchors.any()
    # Projection uses measured epoch/window rates at the two screen anchors.
    from features.gnn import GNNWindows
    from evaluation.baselines import validation_rows
    projected=[]
    selected_fits=fits.loc[fits.candidate.eq(chosen)]
    for condition,reference in [('real','real'),('shuffled','real'),('no_graph','no_graph'),('optional_without_base','real')]:
        seconds=0.; fit_count=0
        for anchor in validation_rows(cfg).fit_origin.drop_duplicates():
            windows=GNNWindows(load_panel(through=anchor),cfg); dates,_,_=windows.training(anchor)
            if chosen=='C':dates=dates[dates>='2011-03']
            nearest=min(ANCHORS,key=lambda a:abs(pd.Period(a,freq='M').ordinal-pd.Period(anchor,freq='M').ordinal))
            ref=selected_fits.loc[selected_fits.anchor.eq(nearest)&selected_fits.condition.eq(reference)].iloc[0]
            seconds+=3*ref.fit_seconds*np.ceil(len(dates)/2)/np.ceil(ref.training_samples/2); fit_count+=3
        reused=selected_fits.loc[selected_fits.condition.eq(reference)].fit_seconds.sum() if condition in ('real','no_graph') else 0.
        projected.append({'condition':condition,'fits':fit_count,'projected_fit_hours':seconds/3600,
            'remaining_fits':fit_count-(2 if condition in ('real','no_graph') else 0),
            'remaining_projected_fit_hours':max(0.,seconds-reused)/3600,
            'reference':'measured screen batch-scaled; shuffled/ablation use real proxy',
            'already_completed_seed11_anchor_fits':2 if condition in ('real','no_graph') else 0})
    projection=pd.DataFrame(projected); projection.to_csv(out/'campaign_projection.csv',index=False)
    extension=[]
    if chosen=='C':
        # Five later seed-11 frozen own-lag models already exist in the original campaign.
        for q in pd.period_range('2020-08','2021-08',freq='3M').astype(str):
            meta=OLD/f'gradient_boosting_own_c0_seed11_{q}.json'
            if not meta.exists():raise RuntimeError('Missing CPU extension timing; review projection')
            saved=json.loads(meta.read_text())
            extension.append({'fit_origin':q,'measured_original_fit_seconds':saved['seconds'],
                              'exact_checkpoint_available':meta.with_suffix('.joblib').exists()})
    pd.DataFrame(extension,columns=['fit_origin','measured_original_fit_seconds','exact_checkpoint_available']).to_csv(out/'c_base_campaign_extension.csv',index=False)
    from visuals.architecture_screen import render
    render(out)
    from evaluation.graph_diagnostics_report import table
    text=f'''# Architecture screen — protocol v3 screen

Gate C remains open. Twelve seed-11 GPU fits completed. Selected by the fixed rule: **{chosen}**. This is an exploratory two-anchor screen, not a confirmatory gate decision. No sealed-test forecasts/losses.

## Selection and cost

{table(selection)}

Selection MAE averages the two anchors and all twelve monthly horizons. Candidates within 2% of the minimum use lower total measured cost per fit. C includes all necessary base-fit CPU seconds, including original measured cost of reused fits, allocated over its four GPU fits; CPU/GPU seconds are summed as elapsed compute cost, not converted to equivalent hardware work. Shared base fits are charged once across the four C fits. Newly executed base fit seconds: {new_base_cost:.3f}; total attributable base seconds: {base_cost:.3f}.

{'**No candidate real graph beats its own no graph at both anchors. No further architectures may be tried without researcher approval.**' if no_success else 'At least one candidate beats its own no graph at both anchors; flags in the table remain relevant. No full campaign is authorised by selection alone.'}

## Per-anchor metrics

MAE, MASE and RMSE are in the [complete per-anchor table](../../data/explore/t03/architecture_screen/origin.csv), every horizon 1–12 and the twelve-month total, all/low/medium/high maturity. C_base is the frozen v1.1 selected own-lag boosting base alone. [Pooled scores](../../data/explore/t03/architecture_screen/scores.csv). Single seed: no seed uncertainty estimate.

{table(origin.loc[origin.group.eq('all')&origin.outcome.isin(['1','6','12','total_12']),['model','origin','outcome','mae','mase','mse','mean_signed_error']].assign(rmse=lambda f:np.sqrt(f.mse)).drop(columns='mse'))}

{comparison_text}

## Saved training fit and spatial diagnostics

{table(fits)}

[Training curves](../../data/explore/t03/architecture_screen/training_curves.png), [signed errors by maturity](../../data/explore/t03/architecture_screen/signed_errors.png), [isolates every horizon](../../data/explore/t03/architecture_screen/isolates.csv), [isolate figure](../../data/explore/t03/architecture_screen/isolates.png), [neighbour shift figure](../../data/explore/t03/architecture_screen/neighbour_shift.png), [per-area shifts](../../data/explore/t03/architecture_screen/neighbour_shift.csv.gz), [correlations](../../data/explore/t03/architecture_screen/neighbour_shift_summary.csv).

Only two screen origins exist: neighbour-shift correlations here are cross-area **at each anchor**, not the previous within-area 36-origin statistic. The gap uses observed origin-month neighbours' mean minus own count. Isolates have undefined gaps. These are descriptive, not behavioural identification. C trains from March 2011 origins with strict prior-quarter boosting forecasts; A/B retain the original training calendar, which limits direct causal attribution between architectures.

## Full-campaign projection, not authorisation

{table(projection)}

This is a fixed-selected-configuration campaign: 12 quarterly refits × three seeds = 36 fits per condition, not a renewed six-configuration grid. Two seed-11 anchor fits can be reused for real and no graph only if the screen configuration and input fingerprints stay fixed. A full 46-fit retuning campaign is not specified by this screen; it would need an approved grid. Shuffled and optional five-channel ablation timings are unmeasured proxies. If C wins, its validation base extends with five strictly prior quarterly fits from August 2020 to August 2021, serving origins through October 2021. Their original measured cost and checkpoint availability are in [the CPU extension table](../../data/explore/t03/architecture_screen/c_base_campaign_extension.csv); existing exact checkpoints can be reused, but prediction time is additional. No test block access and no full campaign launched.

Sources: `models.architecture_screen`, `evaluation.screen_report`, `visuals.architecture_screen`. [Output index](../../data/explore/t03/architecture_screen/index.md). All report numbers come from saved artifacts. Frozen v2 files remain unchanged.
'''
    Path('reports/experiments/t03_architecture_screen.md').write_text(text,encoding='utf-8')
    write_json(ROOT/'selection.json',{'selected':chosen,'no_candidate_beats_control_both':no_success,'gpu_fits':12,'test_forecasts_or_losses':0})
    print(json.dumps({'event':'screen_report_complete','selected':chosen,'no_candidate_beats_control_both':no_success,
                      'report':'reports/experiments/t03_architecture_screen.md'}),flush=True)


if __name__=='__main__':report()
