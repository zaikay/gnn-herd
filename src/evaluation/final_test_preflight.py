"""Preparation only: synthetic pipeline plus saved validation-date inference.

This is not a final-test CLI: no tag bypass or final-date option is exposed.
"""
import json
import os
from pathlib import Path
import numpy as np
import pandas as pd
from threadpoolctl import threadpool_limits


def main():
    os.environ['LOKY_MAX_CPU_COUNT']='1'
    from models.final_test_runtime import SPEC,CODE,NOTE,INVENTORY,PANEL,sha,validate_spec,calendar
    from features.sealed_panel import load_prefix
    from evaluation.final_test_metrics import analyse
    from evaluation.final_test_report import write_outputs
    from evaluation.gate_c_metrics import Context
    from evaluation.frozen import frozen_protocol
    spec=json.loads(SPEC.read_text());validate_spec(spec);cfg,_=frozen_protocol('protocol-v2')
    out=Path('data/explore/t03/v7_execution_preflight');out.mkdir(parents=True,exist_ok=True)
    rng=np.random.default_rng(711)
    dates=pd.period_range('2018-11',periods=36,freq='M').astype(str).to_numpy()
    truth=rng.poisson(10,(36,6,12)).astype(float)
    ctx=Context(dates,np.array([f'{i:04}' for i in range(1,7)]),truth,np.ones((36,6))*2,np.tile([0,0,1,1,2,2],(36,1)),np.array([[0,1],[2,3]]),dates)
    models=list(spec['boosting'])+['B2_'+c for c in spec['conditions']]
    values={m:{s:np.maximum(truth+rng.normal(0,1+i/5,truth.shape),.01) for s in spec['seeds']} for i,m in enumerate(models)}
    with threadpool_limits(limits=1):
        bundle,_=analyse(values,ctx,spec)
        artifacts,report=write_outputs(bundle,ctx,spec,out/'synthetic',scope='synthetic_validation_preflight')
        # Validation history only. The sealed reader materialises no target after Oct 2019.
        historical=load_prefix(PANEL,'2019-10')
        fit_panel=historical.through('2019-08')
        from features.builder import FeatureBuilder
        from features.b2 import B2Windows,area_scale
        from models.b2_adaptive import make_model
        import torch,joblib
        torch.set_num_threads(1)
        recorded={}
        dates=['2019-08','2019-09','2019-10']
        base=Path('data/processed/t02_baselines/be4f68799849cb4c')
        for model,cid,spatial in [('gradient_boosting_own',0,False),('gradient_boosting_neighbours',1,True)]:
            fitted=joblib.load(base/f'{model}_c{cid}_seed11_2019-08.joblib')
            features=FeatureBuilder(historical,24)
            prediction=np.stack([np.stack([np.maximum(fitted.predict(features.at(date,h,spatial)),cfg['objective']['rate_floor']) for h in range(1,13)],axis=1) for date in dates]).astype(np.float32)
            with np.load(base/f'{model}_seed11.npz',allow_pickle=False) as saved:
                use=np.isin(saved['origins'],dates);expected=saved['prediction'][use]
            np.testing.assert_allclose(prediction,expected,rtol=1e-7,atol=1e-7)
            recorded[model]={'max_absolute_difference':float(np.abs(prediction-expected).max()),'dates':dates,'new_fits':0}
        scale=area_scale(fit_panel,'2019-08');network=make_model(fit_panel,'real',11,scale)
        checkpoint=Path('data/processed/t03_b2_screen/c3_real_seed11_2019-08_e100/checkpoint.pt')
        saved=torch.load(checkpoint,map_location='cpu',weights_only=False);network.load_state_dict(saved['model'],strict=True);network.eval()
        features=B2Windows(historical,cfg,scale)
        with torch.no_grad():prediction=np.stack([network(torch.from_numpy(features.at(date)[None]))[0,historical.observed].numpy() for date in dates])
        with np.load('data/processed/t03_b2_validation/real/predictions_seed11.npz',allow_pickle=False) as saved:expected=saved['prediction'][np.isin(saved['origins'],dates)]
        np.testing.assert_allclose(prediction,expected,rtol=2e-4,atol=2e-4)
        recorded['B2_real']={'max_absolute_difference':float(np.abs(prediction-expected).max()),'CPU_GPU_tolerance':2e-4,'dates':dates,'new_fits':0}
    result={'scope':'synthetic pipeline and validation-date inference only','synthetic_models':6,'synthetic_ensemble_scores':len(bundle['ensemble']['scores']),
        'synthetic_chain_rows':len(bundle['chains']),'synthetic_interval_rows':len(bundle['intervals']),
        'synthetic_figure_table_files':len(artifacts),'validation_inference_replay':recorded,
        'latest_real_target_materialised':'2019-10','test_targets_materialised':0,'GPU_operations':0,'new_model_fits':0,
        'tag_created':False,'source_sha256':{p:sha(p) for p in CODE},'spec_sha256':sha(SPEC),'inventory_sha256':sha(INVENTORY),'note_sha256':sha(NOTE)}
    # Calendar-only projection: no additional data values are loaded.
    from evaluation.protocol import training_calendar
    validation=calendar('2018-11','2021-10');final=calendar(spec['first_origin'],spec['last_origin'])
    val_work=sum(int(np.ceil(len(training_calendar(o)[0])/2)) for o in validation.fit_origin.unique())
    final_work=sum(int(np.ceil(len(training_calendar(o)[0])/2)) for o in final.fit_origin.unique())
    reference=json.loads(Path('reports/experiments/t03_b2_session_progress.json').read_text())
    estimates={r['condition']:r['recorded_fit_hours_including_reuse']*final_work/val_work for r in reference['conditions']}
    cpu=pd.read_csv('data/processed/t03_combination_validation/final_test_cost_summary.csv').query("device=='CPU boosting'")
    result['resource_projection']={'validation_minibatches_per_epoch_per_seed':val_work,'test_minibatches_per_epoch_per_seed':final_work,
        'GPU_hours_by_condition':estimates,'GPU_hours_total':sum(estimates.values()),'CPU_hours_total':float(cpu.hours_central.sum()),
        'scope':'calendar arithmetic and saved fit times only; excludes final feature/prediction/evaluation overhead'}
    destination=Path('reports/experiments/t03_v7_execution_preparation_checks.json')
    destination.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    (out/'index.md').write_text('# V7 execution preparation - not test results\n\n- synthetic/: synthetic end-to-end tables, chain stops, intervals and figure CSVs; `evaluation.final_test_preflight`.\n- Validation inference replay uses August-October 2019 only, no new fits.\n',encoding='utf-8')
    print(json.dumps({k:v for k,v in result.items() if k!='source_sha256'},indent=2))


if __name__=='__main__':main()
