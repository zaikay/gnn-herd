"""Audit completed CPU prerequisites and timings; no fits or predictions."""
import ast
import hashlib
from importlib.metadata import version
import json
from pathlib import Path
import re
from datetime import datetime,timedelta,timezone
import numpy as np
import pandas as pd
from models.screen_cpu import ROOT,OLD,extra_jobs,base_jobs,folder
from evaluation.protocol import training_calendar


def main():
    import joblib
    from threadpoolctl import threadpool_limits,threadpool_info
    from sklearn.ensemble import HistGradientBoostingRegressor  # load CPU backend only
    from evaluation.graph_diagnostics_report import table
    selected=json.loads((ROOT/'boosting_selection.json').read_text())
    from evaluation.frozen import frozen_protocol
    from evaluation.gate_c_io import context_from_panel
    from evaluation.gate_c_metrics import Context
    from evaluation.screen_baseline_comparison import load_anchor_baselines,band_scores
    from models.screen_cpu import ANCHORS
    cfg,_=frozen_protocol('protocol-v2'); full=context_from_panel(cfg)
    use=np.isin(full.origins,ANCHORS)
    ctx=Context(full.origins[use],full.codes,full.truth[use],full.scales[use],full.groups[use],full.edges,full.fit_origins[use])
    frozen_predictions,_=load_anchor_baselines(ctx)
    baseline_band_table=band_scores(frozen_predictions,ctx)
    old_manifest=json.loads((OLD/'run_manifest.json').read_text())
    manifest=json.loads((ROOT/'cpu_manifest.json').read_text())
    old=pd.read_csv(OLD/'fit_records.csv')
    old_parameters=old.parameters.map(ast.literal_eval)
    rows=[]
    for job in extra_jobs():
        record=json.loads((folder(job)/'complete.json').read_text())
        ref=old.loc[old.condition.eq(job['condition'])&old.fit_origin.eq(job['origin'])&old.seed.eq(11)&
                    old_parameters.map(lambda p:p['max_leaf_nodes']==job['parameters']['max_leaf_nodes'])]
        assert len(ref)==2
        _,eligible=training_calendar(job['origin'],'2011-01')
        expected_rows=int(eligible.sum())*2634
        assert ref.rows.eq(expected_rows).all()
        model=joblib.load(folder(job)/'model.joblib')
        assert model.n_iter_==300 and model.loss=='poisson' and not model.early_stopping
        assert all(model.get_params()[k]==v for k,v in job['parameters'].items())
        assert ref.features.eq(model.n_features_in_).all()
        rows.append({'condition':job['condition'],'anchor':job['origin'],'leaves':job['parameters']['max_leaf_nodes'],
            'new_fit_seconds':record['fit_seconds'],'historical_reference_seconds':ref.seconds.mean(),
            'ratio':record['fit_seconds']/ref.seconds.mean(),'historical_min_seconds':ref.seconds.min(),
            'historical_max_seconds':ref.seconds.max(),'expected_rows':expected_rows,'features':model.n_features_in_,
            'actual_iterations':model.n_iter_,'declared_threads':manifest['threads']})
    timing=pd.DataFrame(rows)
    overlaps=[]
    for name in ('t03_v3_screen_final_targeted_tests.log','t03_v3_screen_targeted_workspace_tests.log'):
        path=Path('logs')/name
        raw=path.read_bytes(); text=raw.decode('utf-16' if raw.startswith((b'\xff\xfe',b'\xfe\xff')) else 'utf-8-sig')
        duration=float(re.findall(r'in (\d+(?:\.\d+)?)s',text)[-1])
        end=datetime.fromtimestamp(path.stat().st_mtime,timezone.utc); start=end-timedelta(seconds=duration)
        for job in extra_jobs():
            marker=folder(job)/'complete.json'; record=json.loads(marker.read_text())
            fit_end=datetime.fromtimestamp(marker.stat().st_mtime,timezone.utc)
            fit_start=fit_end-timedelta(seconds=record['command_seconds'])
            seconds=max(0.,(min(end,fit_end)-max(start,fit_start)).total_seconds())
            if seconds>0:overlaps.append({'job':job['name'],'test_log':name,'approx_overlap_seconds':seconds})
    selection_rows=[]
    for condition,decision in selected.items():
        np.testing.assert_allclose(np.abs(frozen_predictions[f'{condition}_frozen']-ctx.truth).mean(),decision['old_tuning_mae'],rtol=1e-12)
        for choice in decision['extra']:
            anchor_losses=[]
            for anchor in ANCHORS:
                job=next(j for j in extra_jobs() if j['condition']==condition and j['origin']==anchor and j['parameters']==choice['parameters'])
                with np.load(folder(job)/'forecasts.npz',allow_pickle=False) as data:
                    np.testing.assert_array_equal(data['codes'],ctx.codes)
                    assert data['origins'].tolist()==[anchor]
                    anchor_losses.append(np.abs(data['prediction'][0].astype(float)-ctx.truth[list(ctx.origins).index(anchor)]).mean())
            np.testing.assert_allclose(np.mean(anchor_losses),choice['tuning_mae'],rtol=1e-12)
            selection_rows.append({'condition':condition,'frozen_tuning_mae':decision['old_tuning_mae'],
                'new_rate':choice['parameters']['learning_rate'],'new_leaves':choice['parameters']['max_leaf_nodes'],
                'extra_tuning_mae':choice['tuning_mae'],'beats_frozen':choice['tuning_mae']<decision['old_tuning_mae']})
    with threadpool_limits(limits=8):backends=threadpool_info()
    assert all(b['num_threads']==8 for b in backends)
    versions={name:version(name) for name in old_manifest['versions']}
    assert versions==old_manifest['versions'] and old_manifest['threads']==manifest['threads']==8
    original=json.loads(Path('logs/t03_graph_diagnostics_frozen_before.json').read_text())
    assert all(hashlib.sha256(Path(p).read_bytes()).hexdigest()==h for p,h in original.items())
    base_marker=json.loads((ROOT/'c_base_complete.json').read_text())
    with np.load(ROOT/'c_base_oos.npz',allow_pickle=False) as data:
        assert (data['fit_origins']<data['origins']).all()
        assert data['prediction'].shape==(114,2634,12)
        assert np.isfinite(data['prediction']).all() and (data['prediction']>0).all()
    assert hashlib.sha256((ROOT/'c_base_oos.npz').read_bytes()).hexdigest()==base_marker['prediction_sha256']
    all_records=[json.loads((folder(j)/'complete.json').read_text()) for j in extra_jobs()+base_jobs()]
    total=sum(r['fit_seconds'] for r in all_records)
    result={'cpu_jobs_completed':len(all_records),'new_cpu_fits':sum(r['new_fit'] for r in all_records),
        'new_cpu_fit_seconds':total,'new_cpu_fit_hours':total/3600,'both_frozen_selections_retained':not any(d['improved'] for d in selected.values()),
        'base_origins':114,'base_shape':[114,2634,12],'base_strict_prior_dates':True,
        'old_and_new_declared_threads':8,'current_backends_under_same_limit':backends,'versions_match_historical':True,
        'extra_tuning_scores_reproduced_from_forecasts':4,'frozen_tuning_scores_reproduced_from_forecasts':2,
        'timing_ratio_min':timing.ratio.min(),'timing_ratio_max':timing.ratio.max(),
        'aggregate_extra_timing_ratio':timing.new_fit_seconds.sum()/timing.historical_reference_seconds.sum(),
        'historical_background_load_or_clock_telemetry_available':False,'cause_established':False,
        'approx_test_command_overlaps_from_log_mtimes':overlaps,
        'protected_original_files_unchanged':len(original),'new_fits_this_audit':0,'gpu_use':False}
    out=Path('data/explore/t03/architecture_screen')
    timing.to_csv(out/'cpu_timing_review.csv',index=False)
    pd.DataFrame(selection_rows).to_csv(out/'cpu_selection_review.csv',index=False)
    pd.DataFrame(overlaps).to_csv(out/'cpu_test_overlaps.csv',index=False)
    baseline_band_table.to_csv(out/'cpu_anchor_baseline_bands.csv',index=False)
    Path('reports/experiments/t03_cpu_prerequisites_review.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    text=f'''# CPU prerequisites review — 31 October 2026

Read-only review of saved fits/forecasts, no refits, predictions, GPU operation or sealed-test access. All {len(all_records)} prerequisite jobs complete: eight extra anchor fits and 38 C-base quarterly jobs (31 new fits, seven reused). Total new fitting time {total/3600:.6f} CPU wall hours, excluding inference/serialization/startup. Gate C remains open; no screen GPU result exists.

## Extra configuration results

{table(pd.DataFrame(selection_rows))}

Neither new configuration beats its frozen selection. Retain own-lag rate 0.03 / 15 leaves and neighbour-lag rate 0.03 / 31 leaves, both L2=1, 300 iterations. No updated full-validation run is needed or claimed; their existing validation scores remain authoritative. Tuning score is systems/area/month, averaged equally across the two anchors and all twelve horizons. All four extra tuning scores and both frozen tuning scores were independently reproduced from saved forecasts against the anchor targets. [Baseline-only band preflight](../../data/explore/t03/architecture_screen/cpu_anchor_baseline_bands.csv) uses the new band calculations without opening any screen/GNN prediction.

C's base has 114 monthly origins, March 2011–August 2020, and 2,634 observed areas × twelve horizons. All fit dates are strictly earlier than their forecast origins; combined forecast hash matches its completion marker. Seven old base checkpoints are reused. Source: `c_base_complete.json` / `c_base_oos.npz`.

## Timing evidence

{table(timing)}

The 2.8–3.1× slowdown described earlier applies to the first two agent-run own-lag fits at August 2019. Across all eight fits, ratios span {timing.ratio.min():.3f}–{timing.ratio.max():.3f}; the ratio of total new seconds to total reference seconds is {result['aggregate_extra_timing_ratio']:.3f}. Later researcher-run own-lag August-2020 fits were faster than those historical references. This is not a uniform threefold penalty.

**Thread/settings checks:** both manifests request eight CPU threads. Both fitting implementations enter `threadpool_limits(8)` around fitting. Current loaded CPU backends report eight threads inside that context; this verifies today's configuration, not historical effective utilisation. Installed baseline-library versions match the historical manifest. All saved new estimators have 300 iterations, Poisson objective, early stopping disabled and their intended leaf limits. Horizon eligibility implies identical training row counts to their matched historical references; feature counts agree. The learning rate changes intentionally from 0.03/0.1 in the reference grid to 0.05, so these are not identical-model timing repeats. Different learned tree splits can have different costs.

**Timing boundaries:** new `fit_seconds` measures model.fit only. Old `seconds` also includes checkpoint compression/writing. Consequently the extra serialization in the reference cannot explain why a new fit was slower. The joblib missing-WMIC warning triggers logical-core discovery fallback; it does not remove the explicit eight-thread context. No evidence identifies that warning as the cause of a minutes-long fit difference.

**Known contention:** the agent launched targeted tests during the second initial own-lag fit. Approximate intervals reconstructed from log modification times and recorded durations confirm overlap; the [overlap table](../../data/explore/t03/architecture_screen/cpu_test_overlaps.csv) retains that evidence. This was avoidable concurrent CPU work and makes that timing less comparable. It does not establish its share of the slowdown, and cannot explain the first fit or all later timing variation.

**Single cause not established.** Historical per-process CPU utilisation, other concurrent workload, affinity, laptop power/thermal state and effective clock measurements were not recorded. Current process sampling cannot reconstruct those runs, so throttling or a sandbox effect cannot be asserted. No rerun was made to manufacture a diagnosis. Keep later timed CPU fits separate from test jobs and other fits; retain the eight-thread cap. Record threadpool state, process CPU/wall time and power/load context with future approved CPU jobs before interpreting timing ratios. No settings/environment changes are made now.

[Timing CSV](../../data/explore/t03/architecture_screen/cpu_timing_review.csv), [selection CSV](../../data/explore/t03/architecture_screen/cpu_selection_review.csv), [machine-readable audit](t03_cpu_prerequisites_review.json). Generator: `python -m evaluation.screen_cpu_review`. All {len(original)} protected original file hashes match. No frozen protocol change and no further CPU/GPU work is required before commit/tag and the researcher GPU screen.
'''
    Path('reports/experiments/t03_cpu_prerequisites_review.md').write_text(text,encoding='utf-8')
    index=out/'index.md'
    existing=index.read_text(encoding='utf-8')
    for name in ['cpu_timing_review.csv','cpu_selection_review.csv','cpu_test_overlaps.csv','cpu_anchor_baseline_bands.csv']:
        if f'[{name}]' not in existing:existing+=f'\n- [{name}]({name}): `evaluation.screen_cpu_review`.\n'
    index.write_text(existing,encoding='utf-8')
    print(json.dumps({k:v for k,v in result.items() if k!='current_backends_under_same_limit'},indent=2))


if __name__=='__main__':main()
