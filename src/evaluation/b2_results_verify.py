"""Independent saved-forecast audit and dated B2 validation handover."""
import json
from pathlib import Path
import re
import numpy as np
import pandas as pd
from threadpoolctl import threadpool_limits


def main():
    from evaluation.b2_gate_c import require_release,OUT
    from evaluation.gate_c_io import context_from_panel,load_baselines,read_prediction
    from evaluation.gate_c_metrics import OUTCOMES,spatial_diagnostics
    from evaluation.dm import dm_from_losses
    from evaluation.b2_campaign_plan import dm_family
    from evaluation.graph_diagnostics_report import table
    from models.b2_runtime import CAMPAIGN,sha
    cfg,decision,order,info=require_release()
    with threadpool_limits(limits=1):
        ctx=context_from_panel(cfg); values,_,_=load_baselines(cfg,ctx)
        metadata=json.loads((OUT/'manifest.json').read_text())
        assert metadata['authority']==info and metadata['test_forecasts_or_losses']==0
        fit_progress=[]
        for condition in order:
            evidence=json.loads(Path(f'reports/experiments/t03_b2_{condition}_completion_verification.json').read_text())
            assert evidence['unique_fits']==36 and evidence['epochs']==100 and evidence['source_and_reuse_provenance_match']
            for path,expected in evidence['artifact_sha256'].items():assert sha(path)==expected,path
            marker=json.loads((CAMPAIGN/condition/'condition_complete.json').read_text())
            fit_progress.append({'condition':condition,'completed_fit_identities':36,
                'new_campaign_fit_hours':marker['new_fit_hours'],'recorded_fit_hours_including_reuse':marker['recorded_fit_hours'],
                'estimated_remaining_fit_hours':0,'basis':'verified complete'})
            values[condition]={}
            for seed in (11,29,47):
                path=CAMPAIGN/condition/f'predictions_seed{seed}.npz'
                assert metadata['prediction_sha256'][str(path)]==sha(path)
                values[condition][seed]=read_prediction(path,ctx)
        tables={name:pd.read_csv(OUT/(name+'.csv.gz' if name in ('origin','areas') else name+'.csv'),dtype={'outcome':str,'postcode':str})
                for name in ('origin','seed','scores','areas','dm','moran','difference')}
        origin=tables['origin']; keys=['model','seed','origin','outcome','group']; actual=origin.set_index(keys)
        assert not actual.index.duplicated().any()
        checked=0
        for model,runs in values.items():
            for seed,prediction in runs.items():
                monthly=prediction.astype(float)-ctx.truth
                total=prediction.sum(axis=2).astype(float)-ctx.truth.sum(axis=2)
                for t,date in enumerate(ctx.origins):
                    for group,label in ((None,'all'),(0,'low'),(1,'medium'),(2,'high')):
                        use=np.ones(len(ctx.codes),bool) if group is None else ctx.groups[t]==group
                        for h in OUTCOMES:
                            error=total[t,use] if h=='total_12' else monthly[t,use,int(h)-1]
                            scale=ctx.scales[t,use]*(12 if h=='total_12' else 1)
                            expected=[np.abs(error).mean(),(np.abs(error)/scale).mean(),np.square(error).mean(),error.mean()]
                            row=actual.loc[(model,seed,date,h,label)]
                            np.testing.assert_allclose(row[['mae','mase','mse','mean_signed_error']].to_numpy(float),expected,rtol=1e-11,atol=1e-10)
                            assert row.areas==use.sum(); checked+=1
        assert checked==len(origin)==39312
        seed_keys=['model','seed','outcome','group']
        grouped=origin.groupby(seed_keys)[['mae','mase','mse','mean_signed_error']].mean()
        seed=tables['seed'].set_index(seed_keys).reindex(grouped.index)
        np.testing.assert_allclose(seed[grouped.columns],grouped,rtol=1e-11,atol=1e-10)
        np.testing.assert_allclose(seed.rmse,np.sqrt(seed.mse),rtol=1e-11,atol=1e-10)
        scores=tables['scores']; indexed=scores.set_index(['model','outcome','group'])
        for key,part in tables['seed'].groupby(['model','outcome','group']):
            row=indexed.loc[key]
            np.testing.assert_allclose(row[['mae','mase','rmse']].to_numpy(float),[part.mae.mean(),part.mase.mean(),np.sqrt(part.mse.mean())],rtol=1e-11,atol=1e-10)
            for metric in ('mae','mase','rmse'):
                np.testing.assert_allclose([row[metric+'_seed_sd'],row[metric+'_seed_min'],row[metric+'_seed_max']],
                    [part[metric].std(ddof=1),part[metric].min(),part[metric].max()],rtol=1e-11,atol=1e-10)
        dm=tables['dm']; family=dm_family(decision['main'],False)
        assert len(dm)==20 and list(zip(dm.model_a,dm.model_b,dm.outcome))==family
        assert metadata['dm_family']==[list(x) for x in family]
        losses=origin.loc[origin.group.eq('all')].groupby(['model','outcome','origin']).mae.mean()
        for row in dm.itertuples():
            stat,p=dm_from_losses(losses.loc[(row.model_a,row.outcome)].to_numpy(),losses.loc[(row.model_b,row.outcome)].to_numpy(),12 if row.outcome=='total_12' else int(row.outcome))
            np.testing.assert_allclose([row.statistic,row.p_raw],[stat,p],rtol=1e-10,atol=1e-12)
        adjusted=np.empty(20); running=0.
        for rank,index in enumerate(np.argsort(dm.p_raw.to_numpy(),kind='stable')):
            running=max(running,min(1.,(20-rank)*float(dm.p_raw.iloc[index]))); adjusted[index]=running
        np.testing.assert_allclose(dm.p_holm,adjusted,rtol=1e-10,atol=1e-12)
        areas=tables['areas'].replace({'model':{'real':'gnn_real','shuffled':'gnn_shuffled'}})
        moran,difference=spatial_diagnostics(areas,ctx)
        moran=moran.replace({'model':{'gnn_real':'real','gnn_shuffled':'shuffled'}})
        for expected,actual_frame in ((moran,tables['moran']),(difference,tables['difference'])):
            pd.testing.assert_frame_equal(actual_frame,expected,check_dtype=False,rtol=1e-10,atol=1e-11)
    artifacts=[]
    for folder,names in ((Path('visuals/t03/b2_validation'),['gnn_error_horizon','gnn_error_total','gnn_error_maturity','gnn_graph_comparison']),
                         (Path('data/explore/t03/b2_validation'),['gnn_error_moran','gnn_scaled_error_map','gnn_real_minus_shuffled_map']),
                         (Path('reports/figures/b2_validation'),['t03_graph_comparison','t03_gnn_error_horizon'])):
        for name in names:
            for ext in ('png','csv'):
                path=folder/f'{name}.{ext}'; assert path.exists() and 0<path.stat().st_size<5_000_000
                artifacts.append(str(path))
    for name in ('gnn_scaled_error_map','gnn_real_minus_shuffled_map'):
        frame=pd.read_csv(f'data/explore/t03/b2_validation/{name}.csv',dtype={'postcode':str})
        assert len(frame)==2641 and (~frame.evaluated).sum()==7
        assert set(frame.loc[frame.evaluated,'postcode'])==set(ctx.codes)
    result={'verification':'passed','fits':144,'new_fits_in_campaign':140,'reused_screen_fits':4,
        'new_campaign_fit_hours':sum(r['new_campaign_fit_hours'] for r in fit_progress),
        'recorded_fit_hours_including_reuse':sum(r['recorded_fit_hours_including_reuse'] for r in fit_progress),
        'origin_rows_checked':checked,'score_rows_checked':len(scores),'seed_rows_checked':len(seed),'dm_tests_checked':20,
        'significant_tests_at_005':int((dm.p_holm<.05).sum()),'minimum_Holm_p':float(dm.p_holm.min()),
        'figure_csv_files_checked':len(artifacts),'conditions':fit_progress,'gpu_use':False,'new_fits_by_agent':0,'test_forecasts_or_losses':0}
    report=Path('reports/experiments/b2_validation.md')
    text=report.read_text(encoding='utf-8'); marker='\n## Verified completion and review summary\n'; text=text.split(marker)[0]
    selected=scores.loc[scores.group.eq('all')&scores.outcome.isin(['1','6','12','total_12'])]
    text+=marker+'\n3 November 2026. All four conditions and the combined evaluation are verified complete. **B2 Gate C awaits researcher review.** The accepted earlier B Gate C is unchanged. No further model run is needed now.\n\n'
    text+='Real has lower MAE than shuffled at all four reported outcomes, but none of the 20 predeclared Holm-adjusted tests is below 0.05. Real beats no graph on MAE at horizon 1 only; no graph is lower at horizons 6, 12 and total. These results do not establish a geographic forecast gain for B2.\n\n'
    text+='Real has lower MAE than both boosting baselines at horizon 1; both boosting baselines are lower at horizons 6, 12 and total. Real has lower MASE than own-lag boosting at all four outcomes. Real beats seasonal naive on MAE at horizons 1 and 6, but not at 12 or total.\n\n'
    text+='Removing installed base worsens MAE and MASE at all four reported outcomes. The closest adjusted comparison is real versus without-base at horizon 1, Holm p '+f"{result['minimum_Holm_p']:.6g}"+', which remains above 0.05. Lack of significance is not equivalence. Validation-based configuration/epoch/model selection, 36 overlapping origins and three fixed seeds limit inference. No individual behavioural mechanism is identified.\n\n'
    text+=table(selected[['model','outcome','mae','mase','rmse']])+'\n\n'
    text+=f"Independent CPU audit reproduced {checked:,} origin loss rows, {len(scores)} pooled scores, {len(seed)} seed scores and every DM statistic/raw p-value plus the full Holm adjustment. Spatial statistics/differences reproduce; {len(artifacts)} figure/CSV files and seven unknown map areas checked. All condition checkpoint/forecast hashes match their completion audits.\n\n"
    text+=table(pd.DataFrame(fit_progress))+'\n\n'
    text+=f"Campaign new-fit time: **{result['new_campaign_fit_hours']:.6f} hours**; including four reused screen fits: **{result['recorded_fit_hours_including_reuse']:.6f} hours**. Reused fit hours were not run again. These sums exclude inference, breaks and other screens. No fit remains.\n\n"
    text+='[Verification JSON](t03_b2_results_verification.json), [progress](t03_b2_session_progress.json); `evaluation.b2_results_verify`, log `logs/t03_b2_results_verification.log`. No new fit, GPU use, frozen-file change, protocol amendment, combination search or final-test work follows this review report.\n'
    report.write_text(text,encoding='utf-8')
    broken=[target for target in re.findall(r'\]\(([^)]+)\)',text) if not target.startswith(('http:','https:','#')) and not (report.parent/target).exists()]
    # The two JSON outputs below are written by this audit.
    broken=[target for target in broken if target not in ('t03_b2_results_verification.json','t03_b2_session_progress.json')]
    assert not broken,broken
    result['broken_report_links']=broken
    Path('reports/experiments/t03_b2_results_verification.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    Path('reports/experiments/t03_b2_session_progress.json').write_text(json.dumps({'conditions':fit_progress,'remaining_estimated_fit_hours':0,
        'new_campaign_fit_hours':result['new_campaign_fit_hours'],'recorded_fit_hours_including_reuse':result['recorded_fit_hours_including_reuse'],
        'test_forecasts_or_losses':0,'gpu_use':False},indent=2)+'\n',encoding='utf-8')
    pd.DataFrame(fit_progress).to_csv('data/explore/t03/b2_validation_progress/session_progress.csv',index=False)
    print(json.dumps(result,indent=2))


if __name__=='__main__':main()
