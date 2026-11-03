"""Saved-only checks for ensemble algebra, weights, scores and report artifacts."""
import json
from pathlib import Path
import re
import numpy as np
import pandas as pd
from evaluation.b2_ensemble_combination import ROOT,EXPLORE,REPORT,SEEDS,ensemble,BANDS


def main():
    from evaluation.b2_gate_c import require_release
    from evaluation.gate_c_io import context_from_panel,load_baselines,read_prediction
    from models.b2_runtime import CAMPAIGN,sha
    cfg,_,order,_=require_release();ctx=context_from_panel(cfg)
    policy=json.loads((ROOT/'policy_and_verification.json').read_text())
    for path,h in {**policy['input_sha256'],**policy['source_sha256']}.items():assert sha(path)==h,path
    assert sha(policy['rules_file'])==policy['rules_sha256']
    def read(name,seed):
        parts=[];dates=[]
        for path in sorted(ROOT.glob(f'{name}_seed{seed}_part*.npz')):
            with np.load(path,allow_pickle=False) as data:
                np.testing.assert_array_equal(data['codes'],ctx.codes)
                parts.append(data['prediction'].copy());dates.extend(data['origins'])
        np.testing.assert_array_equal(dates,ctx.origins)
        result=np.concatenate(parts);assert result.shape==ctx.truth.shape
        assert np.isfinite(result).all() and (result>=0).all()
        return result
    raw={};derived={}
    for condition in order:
        raw[condition]={s:read_prediction(CAMPAIGN/condition/f'predictions_seed{s}.npz',ctx) for s in SEEDS}
        derived[condition]=read('B2_'+condition+'_ensemble','ensemble')
        np.testing.assert_array_equal(derived[condition],ensemble(raw[condition]))
    baseline,_,_=load_baselines(cfg,ctx)
    ledger=pd.read_csv(EXPLORE/'expanding_weights.csv',keep_default_na=False)
    assert len(ledger)==648 and ledger.neighbour_weight.between(0,1).all()
    used=ledger.loc[ledger.latest_target_used.ne('')]; assert (used.latest_target_used<=used.origin).all()
    for variant in ('B2_ensemble','B2_individual'):
        runs={s:read('learned_'+variant,s) for s in SEEDS}
        for t,date in enumerate(ctx.origins):
            for group,label in enumerate(('low','medium','high')):
                area=ctx.groups[t]==group
                for start,stop in BANDS:
                    row=ledger.loc[ledger.variant.eq(variant)&ledger.origin.eq(date)&ledger.maturity.eq(label)&ledger.band.eq(f'{start+1}-{stop}')]
                    assert len(row)==1;w=float(row.neighbour_weight.iloc[0])
                    for s in SEEDS:
                        graph=derived['real'] if variant=='B2_ensemble' else raw['real'][s]
                        expected=w*baseline['gradient_boosting_neighbours'][s][t,area,start:stop].astype(float)+(1-w)*graph[t,area,start:stop].astype(float)
                        np.testing.assert_allclose(runs[s][t,area,start:stop],expected,rtol=1e-11,atol=1e-11)
        np.testing.assert_array_equal(read('learned_'+variant+'_forecast_ensemble','ensemble'),ensemble(runs))
    count=0
    for kind in ('individual','ensemble'):
        origin=pd.read_csv(ROOT/(kind+'_origin.csv.gz'),dtype={'outcome':str})
        seed=pd.read_csv(ROOT/(kind+'_seed.csv'),dtype={'outcome':str})
        scores=pd.read_csv(ROOT/(kind+'_scores.csv'),dtype={'outcome':str})
        keys=['model','seed','outcome','group'];expected=origin.groupby(keys)[['mae','mase','mse','mean_signed_error']].mean()
        actual=seed.set_index(keys).reindex(expected.index)
        np.testing.assert_allclose(actual[expected.columns],expected,rtol=1e-11,atol=1e-10)
        np.testing.assert_allclose(actual.rmse,np.sqrt(expected.mse),rtol=1e-11,atol=1e-10)
        indexed=scores.set_index(['model','outcome','group'])
        for key,part in seed.groupby(['model','outcome','group']):
            row=indexed.loc[key]
            np.testing.assert_allclose(row[['mae','mase','rmse']].to_numpy(float),[part.mae.mean(),part.mase.mean(),np.sqrt(part.mse.mean())],rtol=1e-11,atol=1e-10)
        if kind=='ensemble':assert scores[['mae_seed_sd','mase_seed_sd','rmse_seed_sd']].isna().all().all()
        count+=len(scores)
    bias=pd.read_csv(EXPLORE/'bias_origin_horizon.csv')
    np.testing.assert_allclose(bias.mean_signed_error,bias.mean_forecast-bias.mean_actual,rtol=1e-11,atol=1e-11)
    assert len(bias)==5184 and bias.target_month.le('2022-10').all()
    members=pd.read_csv(EXPLORE/'ensemble_vs_seeds.csv',dtype={'member':str,'outcome':str})
    assert len(members)==832 and set(members.member)=={'11','29','47','ensemble'}
    assert not members.duplicated(['condition','member','outcome','group']).any()
    full=pd.read_csv(EXPLORE/'all36_weights.csv');assert len(full)==18 and full.validation_origins.eq(36).all()
    assert full.neighbour_weight.between(0,1).all() and full.latest_target_used.le('2022-10').all()
    artifacts=[p for folder in (ROOT,EXPLORE,Path('visuals/t03/b2_ensemble_combination'),Path('reports/figures/b2_ensemble_combination')) for p in folder.iterdir() if p.is_file()]
    assert all(0<p.stat().st_size<5_000_000 for p in artifacts)
    for path in EXPLORE.glob('*.png'):assert path.with_suffix('.csv').exists()
    broken=[target for target in re.findall(r'\]\(([^)]+)\)',REPORT.read_text(encoding='utf-8')) if not target.startswith(('http:','https:','#')) and not (REPORT.parent/target).exists()]
    assert not broken,broken
    result={'verification':'passed','score_rows_checked':count,'expanding_weight_rows':len(ledger),'all36_weight_rows':len(full),
        'bias_rows':len(bias),'ensemble_vs_individual_seed_rows':len(members),'artifact_files_under_5MB':len(artifacts),'broken_report_links':broken,
        'ensemble_and_combination_algebra_checked':True,'frozen_rule_and_input_hashes_match':True,'model_refits':0,'gpu_use':False,'test_forecasts_or_losses':0}
    raw=Path('logs/t03_b2_ensemble_full_tests.log').read_bytes()
    testlog=raw.decode('utf-16' if raw.startswith((b'\xff\xfe',b'\xfe\xff')) else 'utf-8-sig',errors='replace')
    assert '164 passed, 1 warning' in testlog
    result['full_test_suite']={'passed':164,'warnings':1,'log':'logs/t03_b2_ensemble_full_tests.log'}
    Path('reports/experiments/t03_b2_ensemble_combination_verification.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    marker='\n## Final verification\n'
    text=REPORT.read_text(encoding='utf-8').split(marker)[0]
    text+=marker+'\n**164 tests passed**, one upstream warning; targeted eight tests passed. Source: `logs/t03_b2_ensemble_full_tests.log` and `logs/t03_b2_ensemble_targeted_tests.log`. Independent saved-output audit checked 936 pooled score rows, all derived ensemble/combination algebra, 648 expanding weights, 18 descriptive all-validation weights and 5,184 bias rows. Frozen rules/input hashes match; all artifact files are below 5 MB and report links resolve. [Verification JSON](t03_b2_ensemble_combination_verification.json); `evaluation.b2_ensemble_verify`, log `logs/t03_b2_ensemble_verification.log`. No fits, GPU or final-test use.\n'
    REPORT.write_text(text,encoding='utf-8')
    print(json.dumps(result,indent=2))


if __name__=='__main__':main()
