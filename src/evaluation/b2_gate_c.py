"""Conditional 20/28-test B2 Gate C report, saved validation forecasts only."""
import json
from pathlib import Path
import numpy as np
import pandas as pd
from evaluation.b2_campaign_plan import dm_family,SEEDS
from models.b2_runtime import CAMPAIGN,SCREEN,authority,require_screen,sha,screen_artifact_hashes

OUT=Path('data/processed/t03_b2_gate_c')


def compare(origin,decision):
    from evaluation.dm import dm_from_losses
    from evaluation.baselines import holm
    rows=[]
    for main,opponent,outcome in dm_family(decision['main'],decision['include_learned_and_identity']):
        part=origin.loc[origin.group.eq('all')&origin.outcome.eq(outcome)]
        losses=part.groupby(['origin','model']).mae.mean().unstack('model').sort_index()
        record={'model_a':main,'model_b':opponent,'outcome':outcome,'statistic':np.nan,'p_raw':np.nan,'status':'defined'}
        try:
            statistic,p=dm_from_losses(losses[main].to_numpy(),losses[opponent].to_numpy(),12 if outcome=='total_12' else int(outcome))
            if not np.isfinite([statistic,p]).all() or not 0<=p<=1:raise ValueError('Invalid DM result')
            record.update(statistic=float(statistic),p_raw=float(p))
        except (ArithmeticError,ValueError) as error:record['status']='undefined: '+str(error)
        rows.append(record)
    result=pd.DataFrame(rows)
    result['family_size']=len(result)
    result['p_holm']=holm(result.p_raw.to_numpy())
    return result


def require_release():
    # Do not read campaign forecasts until every retained condition has finished.
    from models.b2_validation import conditions
    cfg,info=authority(); decision=require_screen(); order=conditions(decision)
    expected={**info,'screen_decision':decision,'screen_artifacts':screen_artifact_hashes()}
    for condition in order:
        path=CAMPAIGN/condition/'condition_complete.json'
        if not path.exists():raise RuntimeError(f'B2 comparisons withheld: {condition} incomplete')
        marker=json.loads(path.read_text())
        if (marker['condition']!=condition or marker['fits']!=36 or marker['seeds']!=list(SEEDS)
            or marker['epochs']!=100 or marker['validation_origins']!=36 or marker['last_target']!='2022-10'
            or marker['test_forecasts_or_losses']):raise RuntimeError('Invalid B2 completion marker')
    if json.loads((CAMPAIGN/'manifest.json').read_text())!=expected:raise RuntimeError('B2 campaign provenance changed')
    return cfg,decision,order,expected


def run():
    from threadpoolctl import threadpool_limits
    from evaluation.gate_c_io import context_from_panel,load_baselines,read_prediction
    from evaluation.gate_c_metrics import evaluate,spatial_diagnostics
    from evaluation.graph_diagnostics_report import table
    from models.b2_validation import fit_path
    cfg,decision,order,info=require_release()
    with threadpool_limits(limits=1):
        ctx=context_from_panel(cfg); baseline,_,base_info=load_baselines(cfg,ctx)
        values=dict(baseline); hashes={}
        expected={(s,o) for s in SEEDS for o in dict.fromkeys(ctx.fit_origins)}
        for condition in order:
            root=CAMPAIGN/condition
            records=pd.read_csv(root/'fit_records.csv',dtype={'fit_origin':str})
            if len(records)!=36 or set(zip(records.seed,records.fit_origin))!=expected:raise RuntimeError('Missing/duplicate fit identities')
            for seed,origin in expected:
                path=fit_path(condition,seed,origin)
                if not (path/'checkpoint.pt').exists() or json.loads((path/'complete.json').read_text())['epochs']!=100:raise RuntimeError('Missing retained 100-epoch fit')
            values[condition]={}
            for seed in SEEDS:
                path=root/f'predictions_seed{seed}.npz'; values[condition][seed]=read_prediction(path,ctx); hashes[str(path)]=sha(path)
        bundle=evaluate(values,ctx); bundle['dm']=compare(bundle['origin'],decision)
        spatial_areas=bundle['areas'].replace({'model':{'real':'gnn_real','shuffled':'gnn_shuffled'}})
        bundle['moran'],bundle['difference']=spatial_diagnostics(spatial_areas,ctx)
        bundle['moran']=bundle['moran'].replace({'model':{'gnn_real':'real','gnn_shuffled':'shuffled'}})
        OUT.mkdir(parents=True,exist_ok=True)
        for name,frame in bundle.items():frame.to_csv(OUT/(name+'.csv.gz' if name in ('areas','origin') else name+'.csv'),index=False)
        (OUT/'manifest.json').write_text(json.dumps({'authority':info,'baselines':base_info,'prediction_sha256':hashes,
            'dm_family':dm_family(decision['main'],decision['include_learned_and_identity']),'gpu_use':False,'test_forecasts_or_losses':0},indent=2)+'\n')
        from visuals.b2_gate_c import render,study_geometry
        render(bundle,ctx,'released_gnn_validation',geometry=study_geometry(cfg),release={'B2':True})
    text='# B2 full validation: Gate C review\n\nAll retained conditions complete. Final test sealed. Main model: **'+decision['main']+'**. Screen choice and inclusion were fixed before campaign fitting. No refits in this evaluation. Validation p-values are descriptive after model development.\n\n'
    text+='## Metrics and seed spread\n\nEqual area/origin/seed losses, not seed-ensemble forecasts. MAE primary; seasonal MASE unitless; RMSE roots pooled squared error. Monthly units systems/area/month, total systems/area/window. Dynamic maturity terciles and pooled zero-scale fallback unchanged.\n\n'
    text+=table(bundle['scores'])+'\n\n## One predeclared MAE DM/Holm family\n\n'
    shown=bundle['dm'].copy()
    for col in ('p_raw','p_holm'):shown[col]=shown[col].map(lambda v:f'{v:.6g}' if np.isfinite(v) else 'undefined')
    text+=table(shown)+'\n\nTwo-sided HLN/Bartlett tests; origin losses averaged over three seeds, h=12 for total. Undefined slots retained in the single '+str(len(shown))+'-test Holm family. No MASE/RMSE test family.\n\n'
    text+='[Error horizons, total, maturity and graph comparison](../../visuals/t03/b2_validation/index.md); [scaled-error/difference maps and Moran I](../../data/explore/t03/b2_validation/index.md); [full numeric scores](../../data/processed/t03_b2_gate_c/scores.csv), per-seed scores and losses in the same folder. Each figure has a plotted CSV; paper candidates are private in reports/figures/b2_validation/. Unknown areas masked; isolates retained. No individual behavioural mechanism is identified. Researcher Gate C review is required; no further fitting or test work follows.\n'
    Path('reports/experiments/b2_validation.md').write_text(text,encoding='utf-8')
    print(json.dumps({'event':'B2_gate_c_complete','main':decision['main'],'dm_family_size':len(bundle['dm']),'test_forecasts_or_losses':0}))


if __name__=='__main__':run()
