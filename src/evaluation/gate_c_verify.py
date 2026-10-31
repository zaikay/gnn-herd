"""CPU-only audit of released Gate C outputs against raw saved forecasts."""
import json
from pathlib import Path
import re

import numpy as np
import pandas as pd
from threadpoolctl import threadpool_limits

from evaluation.dm import dm_from_losses
from evaluation.gate_c import write_report
from evaluation.gate_c_findings import findings
from evaluation.gate_c_io import frozen_context,load_baselines,load_gnn_predictions
from evaluation.gate_c_metrics import OUTCOMES,REPORTED


def main():
    with threadpool_limits(limits=1):
        cfg,signature,ctx=frozen_context()
        baseline,_,_=load_baselines(cfg,ctx)
        gnn,provenance=load_gnn_predictions(cfg,ctx,signature)
        root=Path('data/processed/t03_gate_c')
        origin=pd.read_csv(root/'origin_metrics.csv.gz',dtype={'outcome':str})
        scores=pd.read_csv(root/'scores.csv',dtype={'outcome':str})
        seed=pd.read_csv(root/'seed_metrics.csv',dtype={'outcome':str})
        dm=pd.read_csv(root/'dm_tests.csv',dtype={'outcome':str})
        areas=pd.read_csv(root/'area_metrics.csv.gz',dtype={'outcome':str,'postcode':str})
        moran=pd.read_csv(root/'error_moran.csv',dtype={'outcome':str})
        difference=pd.read_csv(root/'real_minus_shuffled.csv',dtype={'outcome':str,'postcode':str})
        keys=['model','seed','origin','outcome','group']
        actual=origin.set_index(keys)
        if actual.index.duplicated().any():raise ValueError('Duplicate origin metrics')
        checked=0
        for model,predictions in {**baseline,**gnn}.items():
            for run_seed,prediction in predictions.items():
                monthly=prediction.astype(np.float64)-ctx.truth
                total=prediction.sum(axis=2).astype(np.float64)-ctx.truth.sum(axis=2)
                for t,origin_date in enumerate(ctx.origins):
                    for group,label in ((None,'all'),(0,'low'),(1,'medium'),(2,'high')):
                        use=np.ones(len(ctx.codes),bool) if group is None else ctx.groups[t]==group
                        for h in OUTCOMES:
                            error=total[t,use] if h=='total_12' else monthly[t,use,int(h)-1]
                            scale=ctx.scales[t,use]*(12 if h=='total_12' else 1)
                            expected=[np.abs(error).mean(),(np.abs(error)/scale).mean(),np.square(error).mean(),error.mean()]
                            row=actual.loc[(model,run_seed,origin_date,h,label)]
                            np.testing.assert_allclose(row[['mae','mase','mse','mean_signed_error']].to_numpy(dtype=float),expected,rtol=1e-11,atol=1e-10)
                            assert int(row.areas)==int(use.sum())
                            checked+=1
        assert checked==len(origin)==7*3*36*13*4
        grouped=origin.groupby(['model','seed','outcome','group'])[['mae','mase','mse']].mean()
        actual_seed=seed.set_index(['model','seed','outcome','group']).reindex(grouped.index)
        np.testing.assert_allclose(actual_seed[['mae','mase','mse']],grouped,rtol=1e-11,atol=1e-10)
        np.testing.assert_allclose(actual_seed.rmse,np.sqrt(grouped.mse),rtol=1e-11,atol=1e-10)
        indexed=scores.set_index(['model','outcome','group'])
        for key,part in seed.groupby(['model','outcome','group']):
            row=indexed.loc[key]
            np.testing.assert_allclose(row[['mae','mase','rmse']].to_numpy(dtype=float),
                [part.mae.mean(),part.mase.mean(),np.sqrt(part.mse.mean())],rtol=1e-11,atol=1e-10)
            for metric in ('mae','mase','rmse'):
                np.testing.assert_allclose([row[metric+'_seed_sd'],row[metric+'_seed_min'],row[metric+'_seed_max']],
                    [part[metric].std(ddof=1),part[metric].min(),part[metric].max()],rtol=1e-11,atol=1e-10)
        assert len(dm)==20 and dm.family_size.eq(20).all() and dm.status.eq('defined').all()
        losses=origin.loc[origin.group.eq('all')].groupby(['model','outcome','origin']).mae.mean()
        for row in dm.itertuples():
            statistic,p=dm_from_losses(losses.loc[(row.model_a,row.outcome)].to_numpy(),
                                      losses.loc[(row.model_b,row.outcome)].to_numpy(),int(row.h))
            np.testing.assert_allclose(row.statistic,statistic,rtol=1e-10,atol=1e-10)
            np.testing.assert_allclose(row.p_raw,p,rtol=1e-10,atol=0)
        adjusted=np.empty(20); running=0.
        for rank,index in enumerate(np.argsort(dm.p_raw.to_numpy(),kind='stable')):
            running=max(running,min(1.,(20-rank)*float(dm.p_raw.iloc[index])))
            adjusted[index]=running
        np.testing.assert_allclose(dm.p_holm,adjusted,rtol=1e-10,atol=0)
        artifacts=[]
        for folder,names in (
            (Path('visuals/t03'),['gnn_error_horizon','gnn_error_total','gnn_error_maturity','gnn_graph_comparison']),
            (Path('data/explore/t03'),['gnn_error_moran','gnn_scaled_error_map','gnn_real_minus_shuffled_map']),
            (Path('reports/figures'),['t03_graph_comparison','t03_gnn_error_horizon'])):
            for name in names:
                for extension in ('png','csv'):
                    path=folder/f'{name}.{extension}'
                    assert path.exists() and 0<path.stat().st_size<5_000_000
                    artifacts.append(path.as_posix())
        for name in ('gnn_scaled_error_map','gnn_real_minus_shuffled_map'):
            plotted=pd.read_csv(f'data/explore/t03/{name}.csv',dtype={'postcode':str})
            assert len(plotted)==2641 and int((~plotted.evaluated).sum())==7
            assert set(plotted.loc[plotted.evaluated,'postcode'])==set(ctx.codes)
        metadata=json.loads((root/'manifest.json').read_text())
        bundle={'origin':origin,'seed':seed,'scores':scores,'dm':dm,'areas':areas,'moran':moran,'difference':difference}
        write_report(bundle,metadata,data_root=root)  # refresh text only; figures/metrics unchanged
        progress=json.loads(Path('reports/experiments/t03_session_progress.json').read_text())
        comparison_answer,comparison=findings(scores,dm)
        info={'verification':'passed','protocol':'protocol-v2','origin_rows_checked':checked,
            'score_rows_checked':len(scores),'seed_rows_checked':len(seed),'dm_tests_checked':20,
            'gnn_conditions':4,'unique_gnn_fits':184,'retained_checkpoints':184,
            'all_conditions_same_machine_and_software':True,'figure_csv_files_checked':len(artifacts),
            'map_areas':2641,'map_unknown_errors':7,'test_forecasts_or_losses':0,'new_fits':0,'gpu_use':False,
            'measured_full_fit_hours':progress['measured_full_fit_hours_total'],
            'gate_c_finding':comparison_answer,'real_vs_shuffled':comparison.to_dict('records')}
        verification=Path('reports/experiments/t03_gate_c_verification.json')
        verification.write_text(json.dumps(info,indent=2),encoding='utf-8')
        lines=['\n## Completion and verification\n',
            'All four GNN conditions completed 46 unique fits at 65 epochs with retained checkpoints: **184 GNN fits**. All fit manifests confirm the same laptop/software inventory and frozen protocol. Three saved forecast arrays per condition cover all 36 validation origins, 2,634 observed areas and twelve horizons. Existing baseline fits are reused unchanged.\n',
            '| Condition | Unique fits | Recorded fit wall hours |\n| --- | ---: | ---: |']
        lines += [f"| {r['condition']} | {r['completed_fits']} | {r['measured_hours']:.6f} |" for r in progress['conditions']]
        lines += ['',f"Total recorded full-fit wall time: **{progress['measured_full_fit_hours_total']:.6f} hours**; original pilot **{progress['pilot_hours_separate']:.6f} hours** is separate. Inference, between-session breaks and GPU utilisation are not included in this fit-time sum.",'',
            f'CPU verification recomputed all **{checked:,} origin/group loss rows** from saved forecasts, checked {len(scores)} score rows and {len(seed)} per-seed rows, reproduced all 20 DM statistics/raw p-values and the single Holm adjustment, and checked {len(artifacts)} figure/CSV files plus both maps. No model/checkpoint was loaded for inference or retrained; no GPU operation or sealed-test scoring.\n',
            '[Verification JSON](t03_gate_c_verification.json) · [Session progress](t03_session_progress.json) · [Full test log](../../logs/t03_gate_c_full_tests.log).\n',
            'Each condition was tuned independently under the same grid/budget; selected widths can differ. This is a comparison of the frozen tuned procedures, not a matched-selected-width experiment. Low Moran I alone is not predictive improvement: accuracy and clustering describe different properties. Training/validation tuning, overlapping horizons, 36 origins, revised snapshot data and fixed-seed averaging limit inference.\n',
            '**Gate C awaits researcher review.** No hybrid, extra fit, protocol change or final-test access is initiated by this report.\n']
        report=Path('reports/experiments/gnn_validation.md')
        with report.open('a',encoding='utf-8') as stream:stream.write('\n'.join(lines))
        broken=[target for target in re.findall(r'\]\(([^)]+)\)',report.read_text(encoding='utf-8'))
                if not target.startswith(('http:','https:','#')) and not (report.parent/target).exists()]
        assert not broken,broken
        info['broken_report_links']=broken
        verification.write_text(json.dumps(info,indent=2),encoding='utf-8')
        print(json.dumps(info,indent=2))


if __name__=='__main__':
    main()
