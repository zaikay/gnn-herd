"""CPU screen/base status and updated baseline metrics, without fitting."""
import hashlib
import json
from pathlib import Path
import numpy as np
import pandas as pd
from models.screen_cpu import ROOT,OLD,ANCHORS,CONDITIONS,base_jobs,extra_jobs,folder,choose_extras,initialise,full_jobs,write_json


def report():
    from models.screen_architectures import ScreenNetwork
    from features.panel import load_panel
    from evaluation.graph_diagnostics_report import table
    cfg=initialise(); panel=load_panel(through=ANCHORS[-1])
    counts=[]
    for candidate in 'ABC':
        for condition in ('real','no_graph'):
            model=ScreenNetwork(candidate,panel.edges,panel.observed,64,condition=='real')
            counts.append({'candidate':candidate,'condition':condition,'parameters':sum(p.numel() for p in model.parameters())})
    out=Path('data/explore/t03/architecture_screen'); out.mkdir(parents=True,exist_ok=True)
    pd.DataFrame(counts).to_csv(out/'parameter_counts.csv',index=False)
    selection=choose_extras(); jobs=extra_jobs()+base_jobs()+full_jobs(cfg,selection)
    jobs=list({j['name']:j for j in jobs}.values())
    records=[]
    for j in jobs:
        path=folder(j)/'complete.json'
        if path.exists():
            r=json.loads(path.read_text()); records.append({'job':j['name'],'kind':j['kind'],'complete':True,
                'new_fit':r['new_fit'],'fit_seconds':r['fit_seconds'],'command_seconds':r['command_seconds']})
        else:records.append({'job':j['name'],'kind':j['kind'],'complete':False,'new_fit':False,'fit_seconds':0,'command_seconds':0})
    frame=pd.DataFrame(records); frame.to_csv(out/'cpu_progress.csv',index=False)
    if selection is not None:
        from evaluation.gate_c_io import context_from_panel
        from evaluation.gate_c_metrics import evaluate
        for condition,decision in selection.items():
            marker=ROOT/f'{condition}_updated_complete.json'
            if decision['improved'] and marker.exists():
                predictions={condition:{}}
                for seed in (11,29,47):
                    with np.load(ROOT/f'{condition}_updated_seed{seed}.npz',allow_pickle=False) as data:predictions[condition][seed]=data['prediction'].copy()
                result=evaluate(predictions,context_from_panel(cfg))
                for key,value in result.items():value.to_csv(out/f'{condition}_updated_{key}.csv',index=False)
    text=f'''# Architecture screen preparation — 31 October 2026

Gate C is open. The three-candidate screen is approved, but no GPU fit has been run by the agent. Results and selection are pending all twelve fits. The future completed report is `t03_architecture_screen.md`; this is a preparation/CPU-progress report, not a screen result.

Full pre-run suite: 114 passed, one upstream deprecation warning (`logs/t03_v3_full_tests.log`). The CPU job ledger below is refreshed from completion markers. A source-revision record and original CPU manifest are retained for the anchor-forecast expansion fix; fitting settings and original frozen sources were unchanged.

## Parameter counts

{table(pd.DataFrame(counts))}

Counts include inactive neighbour weights in no graph. C does not include the separately fitted boosting trees in its neural parameter count; base fit costs are charged separately. Tests: `logs/t03_v3_screen_pre_run_tests.log`; full-suite result is recorded in STATUS.md after final preparation. CPU toy forward tests use no optimisation.

## CPU progress

{table(frame.groupby('kind',as_index=False).agg(jobs=('job','size'),completed=('complete','sum'),new_fits=('new_fit','sum'),fit_seconds=('fit_seconds','sum')))}

The C base needs 38 quarterly fits, of which seven exact existing own-lag seed-11 fits can be reused. Earliest C sample March 2011; first target April 2011. Each base fit precedes its forecast origin strictly. Source and panel hashes are cached in `data/processed/t03_screen_v3/cpu_manifest.json`. Original baseline/GNN forecasts are never overwritten. The separate extra search cannot alter C's frozen base configuration.

## Extra boosting selection

'''
    if selection is None:text+='Pending: all eight extra anchor fits are required before choosing a baseline configuration. No partial-search winner is reported.\n'
    else:
        choices=[]
        for condition,decision in selection.items():
            choices.append({'condition':condition,'old_score':decision['old_tuning_mae'],'new_score':decision['winner']['tuning_mae'],
                'new_leaves':decision['winner']['parameters']['max_leaf_nodes'],'improved':decision['improved'],
                'full_validation_complete':(ROOT/f'{condition}_updated_complete.json').exists()})
        text+=table(pd.DataFrame(choices))+'\n\nAn improvement requires full validation with the new configuration, preserving all origins, quarterly refits and three seeds. Exact ties retain the old choice. Completed updated metrics are linked through the output index; any pending validation is not silently treated as complete.\n'
    text+='''
## Next commands and stop point

Exact CPU prerequisite and GPU commands are in `internal/STATUS.md`. All GPU fits use the same laptop, run A/B/C in one resumable session and save five-epoch checkpoints. The GPU command writes the final screen report automatically after twelve fits. No further architecture or full campaign starts. The screen remains exploratory and the final test sealed.

[Parameter counts](../../data/explore/t03/architecture_screen/parameter_counts.csv), [CPU job ledger](../../data/explore/t03/architecture_screen/cpu_progress.csv), [screen note](../protocol/protocol_v3_screen.md). Generator: `evaluation.screen_cpu_report`.
'''
    Path('reports/experiments/t03_architecture_screen_preparation.md').write_text(text,encoding='utf-8')
    existing=out/'index.md'
    lines=['# Architecture screen preparation outputs','','`evaluation.screen_cpu_report` produces counts and CPU progress. Results remain pending.','']
    for p in sorted(out.iterdir()):
        if p.name!='index.md':lines.append(f'- [{p.name}]({p.name}): `evaluation.screen_cpu_report` (tables), `visuals.architecture_screen` (figures).')
    existing.write_text('\n'.join(lines)+'\n',encoding='utf-8')
    print(json.dumps({'cpu_jobs_complete':int(frame.complete.sum()),'cpu_jobs_total':len(frame),
                      'new_cpu_fit_seconds':float(frame.fit_seconds.sum()),'parameter_counts':counts,'gpu_fits_by_agent':0}),flush=True)


if __name__=='__main__':report()
