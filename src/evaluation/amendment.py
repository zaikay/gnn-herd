"""Protocol v1.1 diagnostics from saved validation predictions, without fitting."""
import json
from pathlib import Path

import numpy as np
import pandas as pd

from evaluation.baselines import validation_rows, mase_scales, MODELS, OUTCOMES
from evaluation.protocol import maturity_groups
from evaluation.result_report import completed_run, table, write_report
from features.panel import load_panel


def pooled_rmse(mse_values):
    return float(np.sqrt(np.mean(np.asarray(mse_values,dtype=np.float64))))


def error_arrays(prediction, truth):
    """Keep v1 saved forecast/total conventions; accumulate squares in float64."""
    monthly = prediction.astype(np.float64)-truth.astype(np.float64)
    total = prediction.sum(axis=2).astype(np.float64)-truth.sum(axis=2,dtype=np.float64)
    return monthly,total


def row_moran(values, edges):
    values = np.asarray(values,dtype=np.float64)
    edges = np.asarray(edges,dtype=int).reshape(-1,2)
    source = np.r_[edges[:,0],edges[:,1]]
    target = np.r_[edges[:,1],edges[:,0]]
    degree = np.bincount(source,minlength=len(values))
    z = values-values.mean()
    s0 = int((degree>0).sum())
    if not s0 or np.dot(z,z)==0:
        return None
    return float(len(z)/s0*np.sum(z[source]*z[target]/degree[source])/np.dot(z,z))


def national_revision(frame, reference=174204):
    selected = frame.loc[frame.month.between('2025-01','2025-09')]
    if (selected.month.nunique()!=9 or selected.duplicated(['postcode','month']).any()
            or not selected.groupby('postcode').month.nunique().eq(9).all()):
        raise ValueError('Incomplete or duplicated January-September 2025 source window')
    if selected['count'].isna().any() or (selected['count']<0).any() or (selected['count']%1!=0).any():
        raise ValueError('National counts must be nonnegative integers')
    total = int(selected['count'].sum())
    return {'installation_window':'2025-01 to 2025-09','current_as_at':'2026-09-30',
            'current_count_systems':total,'reference_as_at':'2025-09-30',
            'reference_count_systems':reference,'increase_systems':total-reference,
            'growth_percent':(total/reference-1)*100,
            'reference_source':'researcher-supplied CER figure at Gate B, 29 October 2026; archive not downloaded',
            'interpretation':'same installation months across two snapshots, not year-on-year installation growth',
            'scope':'national CER SGU Solar, all postcodes including unmatched; not model evaluation'}


def main():
    root,cfg,manifest,completion = completed_run()
    rows = validation_rows(cfg)
    panel = load_panel(through=rows.last_target.max())
    truth = np.stack([panel.targets[panel.observed,panel.index(o)+1:panel.index(o)+13].astype(np.float64) for o in rows.origin])
    scales = np.stack([mase_scales(panel,r,cfg) for r in rows.fit_origin])
    base = np.cumsum(panel.inputs,axis=1,dtype=np.float64)
    codes = panel.codes[panel.observed]
    groups = np.stack([maturity_groups(base[panel.observed,panel.index(o)],codes) for o in rows.origin])
    source_indices = np.flatnonzero(panel.observed)
    reindex = {int(old):new for new,old in enumerate(source_indices)}
    edges = np.array([(reindex[int(a)],reindex[int(b)]) for a,b in panel.edges
                      if int(a) in reindex and int(b) in reindex],dtype=int)
    destination = root/'amendment_v1_1'
    destination.mkdir(exist_ok=True)
    explore = Path('data/explore/t02')
    origin_rows, signed_rows, area_rows, moran_rows = [],[],[],[]
    for model in MODELS:
        errors_all = []
        total_all = []
        for seed in cfg['tuning']['seeds']:
            path = root/'seasonal_naive.npz' if model=='seasonal_naive' else root/f'{model}_seed{seed}.npz'
            with np.load(path,allow_pickle=False) as data:
                prediction = data['prediction']
                if model!='seasonal_naive':
                    np.testing.assert_array_equal(data['codes'],codes)
                    np.testing.assert_array_equal(data['origins'],rows.origin.to_numpy(dtype='U7'))
            if prediction.shape != truth.shape:
                raise ValueError('Saved predictions have wrong validation shape')
            monthly,total = error_arrays(prediction,truth)
            errors_all.append(monthly); total_all.append(total)
            for t,origin in enumerate(rows.origin):
                for group_id,label in ((None,'all'),(0,'low'),(1,'medium'),(2,'high')):
                    use = np.ones(len(codes),bool) if group_id is None else groups[t]==group_id
                    for h in range(1,13):
                        error = monthly[t,use,h-1]
                        signed_rows.append({'model':model,'seed':seed,'origin':origin,'horizon':str(h),'group':label,
                                            'mean_signed_error_systems':float(error.mean()),'areas':int(use.sum())})
                    signed_rows.append({'model':model,'seed':seed,'origin':origin,'horizon':'total_12','group':label,
                                        'mean_signed_error_systems':float(total[t,use].mean()),'areas':int(use.sum())})
                    for outcome in OUTCOMES:
                        error = total[t,use] if outcome=='total_12' else monthly[t,use,int(outcome)-1]
                        origin_rows.append({'model':model,'seed':seed,'origin':origin,'outcome':outcome,'group':label,
                                            'mean_squared_error_systems2':float(np.mean(error*error)),'areas':int(use.sum())})
        error12 = np.stack(errors_all)[:,:,:,11]
        absolute = np.abs(error12).mean(axis=(0,1))
        scaled = (np.abs(error12)/scales[None,:,:]).mean(axis=(0,1))
        signed = error12.mean(axis=(0,1))
        for i,code in enumerate(codes):
            area_rows.append({'model':model,'postcode':code,'horizon':12,'absolute_error_systems':float(absolute[i]),
                             'scaled_absolute_error_unitless':float(scaled[i]),'signed_error_systems':float(signed[i])})
        for label,values in (('absolute',absolute),('scaled_absolute',scaled),('signed',signed)):
            moran_rows.append({'model':model,'horizon':12,'error_type':label,'moran_i':row_moran(values,edges),
                'observed_areas':len(codes),'weights':'row-standardised rook, isolates zero rows',
                'interpretation':'descriptive, no permutation p-value; scaling by training error is not dwelling normalisation'})
    origin = pd.DataFrame(origin_rows)
    summary = origin.groupby(['model','outcome','group'],as_index=False).mean_squared_error_systems2.mean()
    summary['rmse'] = np.sqrt(summary.mean_squared_error_systems2)
    summary.to_csv(destination/'rmse_summary.csv',index=False)
    per_seed = origin.groupby(['model','seed','outcome','group'],as_index=False).mean_squared_error_systems2.mean()
    per_seed['rmse'] = np.sqrt(per_seed.mean_squared_error_systems2)
    per_seed.to_csv(destination/'rmse_by_seed.csv',index=False)
    origin.to_csv(destination/'origin_squared_errors.csv',index=False)
    signed = pd.DataFrame(signed_rows)
    signed.groupby(['model','horizon','group'],as_index=False).mean_signed_error_systems.mean().to_csv(explore/'mean_signed_error.csv',index=False)
    pd.DataFrame(area_rows).to_csv(explore/'per_area_error_diagnostics.csv',index=False)
    morans = pd.DataFrame(moran_rows)
    morans.to_csv(explore/'error_moran_comparison.csv',index=False)
    old = pd.read_csv(explore/'validation_error_moran.csv').moran_i.iloc[0]
    new = morans.loc[morans.model.eq('gradient_boosting_own') & morans.error_type.eq('absolute'),'moran_i'].iloc[0]
    np.testing.assert_allclose(old,new,rtol=1e-10)
    cer = pd.read_csv('data/interim/cer_panel.csv',dtype={'postcode':str,'month':str})
    revision = national_revision(cer)
    pd.DataFrame([revision]).to_csv(explore/'pv_2025_snapshot_comparison.csv',index=False)
    pd.DataFrame([revision]).to_csv(destination/'pv_2025_snapshot_comparison.csv',index=False)
    info = {'amendment':'protocol-v1.1','approved_on':'2026-10-29','original_run':manifest['run_id'],
            'original_training_protocol_sha256':manifest['protocol_sha256'],'new_fits':0,'test_forecasts_or_losses':0,
            'metric':'RMSE = sqrt(mean squared loss over equal-weight observed areas, origins and seeds); no prediction ensemble',
            'total_rule':'sum the same saved twelve monthly forecasts before squaring; float64 squares/means',
            'snapshot_comparison':revision,'moran_rows':moran_rows}
    (destination/'summary.json').write_text(json.dumps(info,indent=2),encoding='utf-8')
    amend = Path('reports/protocol/protocol_v1_1.md')
    amend.parent.mkdir(exist_ok=True)
    text = ['# Protocol v1.1 amendment — 29 October 2026','',
        '**Approved by the researcher at Gate B; pending commit and `protocol-v1.1` tag.** Applies before any GNN run. It supersedes only the items listed below; protocol-v1 remains the immutable authority for the completed baseline fitting run. No refitting or final-test forecast/error evaluation is authorised by this amendment. Task 3 has not started.','',
        '## Gate B accepted','',
        'Neighbour lags give no clear overall MAE gain, but lower MASE than own-history boosting for all reported horizons and the twelve-month total, with important differences in the low-maturity tercile. Its twelve-month-total MAE is about 3.89 versus 4.32 systems in that tercile. Both boosting models improve over seasonal naive at horizons 1 and 6 in the corrected DM comparisons; there is no such evidence at horizon 12 or for the twelve-month total, even where raw MAE is numerically lower. The spatial model relies chiefly on neighbours installed base and hardly on recent neighbour counts in the saved grouped-permutation diagnostic. Reliance is not added value and is not causal evidence.','',
        '## A. Add RMSE, retain the objective and primary metric','',
        'MAE remains primary. Secondary metrics are MASE and RMSE for every model, including seasonal naive and all approved GNN conditions. MAE is minimised by a conditional median; squared error is minimised by a conditional mean. Fitted Poisson models predict a mean, so RMSE adds a mean-aligned view without changing the frozen Poisson training objective, tuning selection by MAE, dates, seeds or budget. This does not guarantee calibration or improvements.','',
        'RMSE is the square root of equally weighted mean squared errors across evaluated areas within each origin/maturity group, then across origins and seeds. Take the square root after pooling squared losses, not before, and do not evaluate an ensemble of averaged predictions. For the twelve-month total, sum predicted and observed monthly counts first, then square their difference. Units are systems per area/month for monthly horizons and systems per area/twelve-month window for the total. Compute origin-specific maturity membership from history only, as before.','',
        'Existing baseline RMSE is computed solely from saved validation predictions. Original model files, forecasts, MAE/MASE files and v1 DM results are retained unchanged. New metric files are a labelled amendment overlay.','',
        '## B. Extend the Task 3 DM/Holm family','',
        'Compare real-graph GNN against (1) no-graph GNN, (2) within-state shuffled GNN, (3) own-history boosting and (4) neighbour-history boosting. Apply one Holm adjustment across the entire four-pair x four-outcome family: 16 tests for outcomes 1, 6, 12 and twelve-month total. Keep the v1 origin-level area/seed-averaged MAE loss, Bartlett estimator, HLN correction and two-sided testing. RMSE is an added secondary score; this amendment does not add an unrequested squared-loss DM family. Validation p-values remain descriptive; the final test is still sealed.','',
        '## C. Optional installed-base-channel condition','',
        'A fourth GNN condition may use the real graph with the explicit installed-base input channel removed. All other approved inputs, objective, masks, architecture settings and tuning rules stay the same. Compare it against the real-graph GNN. It is disabled now and runs only if the researcher explicitly approves it after the Task 3 pilot. If enabled, include its four outcome comparisons in the same Holm family, making 20 tests. Do not introduce a separate more favourable testing family. Its extra compute must be presented for approval; no such fit is run now.','',
        '## D. What remains unchanged','',
        'The April 2001 panel, ASGS Edition 3, matching ledger, unknown-area masks, isolate rule, target definition, target-availability mask, split dates, 24-month input window, horizons, Poisson loss, MAE tuning rule, configuration budget, quarterly refits, seeds and Task 3 timing/24-GPU-hour stop remain as v1. July–September 2025 remains in the sealed test calendar with the recorded battery-eligibility timing limitation. Exploratory 2025 source counts and the paper map are descriptive outputs explicitly requested at Gate B, not final-test model evaluation or a basis for additional tuning.','',
        '## Existing-baseline RMSE (no refit)','',table(summary[['model','outcome','group','rmse']]),'',
        'Generated by `python -m evaluation.amendment`; original run: '+manifest['run_id']+'. New RMSE, signed-error and spatial diagnostics link from reports/experiments/baselines_validation.md and data/explore/t02/index.md. Plotting outputs and generators remain local-only under the researcher policy. No model/GPU command was run.','']
    amend.write_text('\n'.join(text),encoding='utf-8')
    with amend.open('a',encoding='utf-8') as stream:
        stream.write('\n[Baseline report and RMSE](../experiments/baselines_validation.md) · [Exploration index](../../data/explore/t02/index.md) · [Albers paper map](../figures/cumulative_sep2025.png) / [POA values](../figures/cumulative_sep2025.csv) / [Inset bounds](../figures/cumulative_sep2025_insets.csv).\n')
    write_report(root,cfg,manifest,completion)
    print(json.dumps(info,indent=2))


if __name__=='__main__':
    main()
