"""Light CPU-only synthetic/provenance preflight for B2 protocol v6."""
import json
from pathlib import Path
import numpy as np
import pandas as pd
from threadpoolctl import threadpool_limits


def main():
    from models.b2_runtime import authority,sha,SOURCES,NOTE
    from models.b2_adaptive import parameter_counts
    from evaluation.b2_campaign_plan import job_plan,graph_screen_decision
    from evaluation.gate_c_metrics import Context,evaluate,spatial_diagnostics
    from evaluation.b2_gate_c import compare
    from visuals.b2_gate_c import render,synthetic_geometry
    cfg,info=authority(require_tag=False)
    out=Path('data/explore/t03/b2_v6_synthetic'); out.mkdir(parents=True,exist_ok=True)
    rng=np.random.default_rng(123)
    origins=pd.period_range('2018-11',periods=36,freq='M').astype(str).to_numpy()
    codes=np.array([f'{i:04}' for i in range(1,7)])
    truth=rng.poisson(10,(36,6,12)).astype(float)
    ctx=Context(origins,codes,truth,np.ones((36,6))*2,np.tile([0,0,1,1,2,2],(36,1)),np.array([[0,1],[1,2],[3,4]]),origins)
    checks={}
    with threadpool_limits(limits=1):
        for include in (False,True):
            names=['seasonal_naive','gradient_boosting_own','gradient_boosting_neighbours','real','shuffled','no_graph','without_base']
            if include:names+=['learned','identity']
            predictions={name:{seed:np.maximum(truth+rng.normal(0,1+i*.2,truth.shape),0) for seed in (11,29,47)} for i,name in enumerate(names)}
            bundle=evaluate(predictions,ctx)
            decision=graph_screen_decision(4.,3.8,3.95) if include else graph_screen_decision(4.,4.1,4.2)
            bundle['dm']=compare(bundle['origin'],decision)
            bundle['moran'],bundle['difference']=spatial_diagnostics(bundle['areas'].replace({'model':{'real':'gnn_real','shuffled':'gnn_shuffled'}}),ctx)
            bundle['moran']=bundle['moran'].replace({'model':{'gnn_real':'real','gnn_shuffled':'shuffled'}})
            case=out/('extended28' if include else 'core20')
            roots={kind:case/kind for kind in ('visual','explore','paper')}
            paths=render(bundle,ctx,'synthetic',geometry=synthetic_geometry(ctx),roots=roots)
            bundle['dm'].to_csv(case/'dm_tests.csv',index=False)
            checks[str(len(bundle['dm']))]={'scores':len(bundle['scores']),'dm_tests':len(bundle['dm']),'figures_and_csvs':len(paths),
                'all_files_under_5MB':all(p.stat().st_size<5_000_000 for p in case.rglob('*') if p.is_file())}
    counts=parameter_counts(); plans={}
    for include in (False,True):
        jobs=job_plan(cfg,include,1)
        plans[str(4+2*include)]={'identities':len(jobs),'new_fits':int(jobs.new_fit.sum()),'reuse':int(jobs.reuse_screen.sum())}
    evidence={'scope':'synthetic only; no new study forecast evaluation','source_sha256':{p:sha(p) for p in SOURCES},
        'note_sha256':sha(NOTE),'frozen_B2_sources_and_data_match':True,'synthetic_cases':checks,
        'parameter_counts':counts,'campaign_counts':plans,'machine_count':1,'gpu_use':False,'study_fits':0,'test_forecasts_or_losses':0}
    dest=Path('reports/experiments/t03_b2_v6_preparation_checks.json'); dest.write_text(json.dumps(evidence,indent=2)+'\n',encoding='utf-8')
    (out/'index.md').write_text('# Synthetic B2 v6 test fixtures\n\nAll numbers are fictional fixtures, not study results.\n\n- core20/: seven-model synthetic 20-test pipeline.\n- extended28/: nine-model synthetic 28-test pipeline.\n\nGenerator: `evaluation.b2_graph_preflight`. No actual learned/identity forecasts exist yet.\n',encoding='utf-8')
    print(json.dumps(evidence,indent=2))


if __name__=='__main__':main()
