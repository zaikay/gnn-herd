"""Saved-only B2 learned/identity screen; no fitting or test-block access."""
import json
from pathlib import Path
import numpy as np
import pandas as pd
from models.b2_runtime import SCREEN,ANCHORS,screen_path
from evaluation.b2_campaign_plan import graph_screen_decision


def paths(condition,anchor):
    if condition in ('real','no_graph'):
        from models.b2_screen import path_for
        return path_for(3,anchor,condition,100)
    return screen_path(condition,anchor)


def load_screen():
    from evaluation.frozen import frozen_protocol
    from evaluation.gate_c_io import context_from_panel
    from evaluation.gate_c_metrics import Context
    cfg,_=frozen_protocol('protocol-v2'); full=context_from_panel(cfg); use=np.isin(full.origins,ANCHORS)
    ctx=Context(full.origins[use],full.codes,full.truth[use],full.scales[use],full.groups[use],full.edges,full.fit_origins[use])
    values={}; records=[]; curves=[]
    for condition in ('real','no_graph','learned','identity'):
        arrays=[]
        for anchor in ANCHORS:
            path=paths(condition,anchor)
            record=json.loads((path/'complete.json').read_text())
            if record['epochs']!=100:raise RuntimeError('All screen controls must use 100 epochs')
            with np.load(path/'prediction.npz',allow_pickle=False) as data:
                np.testing.assert_array_equal(data['codes'],ctx.codes)
                if str(data['origin'])!=anchor:raise RuntimeError('Wrong anchor')
                arrays.append(data['prediction'].copy())
            records.append({**record,'condition':condition,'anchor':anchor})
            curve=pd.read_csv(path/'training_curve.csv')
            # A continued curve may contain only epochs 66..100: restore the retained 1..65 trace.
            if curve.epoch.min()>1 and condition in ('real','no_graph'):
                from models.b2_screen import path_for
                curve=pd.concat([pd.read_csv(path_for(3,anchor,condition,65)/'training_curve.csv'),curve]).drop_duplicates('epoch',keep='last').sort_values('epoch')
            if curve.epoch.tolist()!=list(range(1,101)):raise RuntimeError('Incomplete 100-epoch curve')
            curve['condition']=condition; curve['anchor']=anchor; curves.append(curve)
        values[condition]={11:np.stack(arrays)}
    return cfg,ctx,values,pd.DataFrame(records),pd.concat(curves,ignore_index=True)


def decision_from_arrays(values,truth):
    scores={name:float(np.abs(values[name][11].astype(float)-truth).mean()) for name in ('real','learned','identity')}
    return graph_screen_decision(scores['real'],scores['learned'],scores['identity'])


def compute_decision():
    _,ctx,values,_,_=load_screen()
    return decision_from_arrays(values,ctx.truth)


def summarise(values,ctx):
    from evaluation.gate_c_metrics import evaluate
    bundle=evaluate(values,ctx,seeds=(11,))
    bundle['origin']['rmse']=np.sqrt(bundle['origin'].mse)
    return bundle,decision_from_arrays(values,ctx.truth)


def report():
    from models.b2_runtime import authority
    from evaluation.graph_diagnostics_report import table
    from models.screen_cpu import write_json
    cfg,info=authority()
    if json.loads((SCREEN/'manifest.json').read_text())!=info:raise RuntimeError('Graph screen provenance changed')
    _,ctx,values,records,curves=load_screen(); bundle,decision=summarise(values,ctx)
    out=Path('data/explore/t03/b2_graph_screen'); out.mkdir(parents=True,exist_ok=True)
    for name,frame in bundle.items():frame.to_csv(out/(name+'.csv.gz' if name=='areas' else name+'.csv'),index=False)
    records.to_csv(out/'fit_costs.csv',index=False); curves.to_csv(out/'training_curves.csv',index=False)
    from evaluation.b2_campaign_plan import CORE,OPTIONAL
    projection=[]
    for condition in CORE+(OPTIONAL if decision['include_learned_and_identity'] else ()):
        reference=condition if condition in ('real','no_graph','learned','identity') else 'real'
        seconds=float(records.loc[records.condition.eq(reference),'fit_seconds'].mean())
        reuse=2 if condition in ('real','no_graph','learned','identity') else 0
        projection.append({'condition':condition,'new_fits':36-reuse,'reused_fits':reuse,
            'reference_condition':reference,'reference_mean_fit_seconds':seconds,'estimated_new_fit_hours':seconds*(36-reuse)/3600,
            'basis':'two anchor means; other refit sizes and conditions may differ'})
    projection=pd.DataFrame(projection); projection.to_csv(out/'campaign_projection.csv',index=False)
    write_json(SCREEN/'decision.json',decision)
    from visuals.b2_graph import screen_figures
    screen_figures(bundle,curves,out)
    text='# B2 learned graph and identity screen\n\nProtocol v6; 2 November 2026 specification. Four new GPU fits; saved B2 real/no graph at 100 epochs. Configuration 3, seed 11, August 2019/2020. Validation development evidence only; final test sealed.\n\n'
    text+='## Fixed selection decision\n\n```json\n'+json.dumps(decision,indent=2)+'\n```\n\n'
    text+='Identity improving real by at least 2% stops the campaign for review. Otherwise learned enters only if it beats both real and identity; real is main when learned fails identity. No graph is a control. Exact ties retain real.\n\n'
    text+='## Each anchor: all horizons, total and maturity\n\nMAE/RMSE: systems per area/month, or per twelve-month window. MASE: unitless seasonal training scales; total denominator is twelve times monthly scale. Signed error is forecast minus actual. One seed; no seed-spread inference.\n\n'
    text+=table(bundle['origin'][['model','origin','outcome','group','mae','mase','rmse','mean_signed_error']])+'\n\n## Costs and final training losses\n\n'+table(records)+'\n\n'
    text+='## Full campaign planning estimate\n\n'+table(projection)+'\n\nAnchor-based fit-hour projection, excluding inference and breaks. Shuffled/ablation use real as an unmeasured proxy. This does not override an identity-review stop.\n\n'
    text+='[Training curves](../../data/explore/t03/b2_graph_screen/training_curves.png) and [CSV](../../data/explore/t03/b2_graph_screen/training_curves.csv); [MAE horizons](../../data/explore/t03/b2_graph_screen/errors.png); [all tables](../../data/explore/t03/b2_graph_screen/index.md). Dense learned adjacency masks self and unknown source columns, including for isolated receivers. Identity has equal embedding count, not equal total parameter count. Embeddings are trained only on training loss. No extra configuration/epoch search or test access.\n'
    Path('reports/experiments/b2_graph_screen.md').write_text(text,encoding='utf-8')
    print(json.dumps({'event':'B2_graph_screen_report','decision':decision,'report':'reports/experiments/b2_graph_screen.md','gpu_use':False}),flush=True)


if __name__=='__main__':report()
