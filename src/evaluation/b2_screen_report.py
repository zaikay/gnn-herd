"""Saved B2 anchor forecasts/training curves only; no fit/GPU operations."""
import json
from pathlib import Path
import numpy as np
import pandas as pd


def report():
    from models.b2_screen import ROOT,path_for,grid
    from models.screen_cpu import ANCHORS
    from evaluation.frozen import frozen_protocol
    from evaluation.gate_c_io import context_from_panel
    from evaluation.gate_c_metrics import Context,evaluate
    from models.architecture_screen import output as old_output
    from evaluation.graph_diagnostics_report import table
    cfg,_=frozen_protocol('protocol-v2'); full=context_from_panel(cfg); use=np.isin(full.origins,ANCHORS)
    ctx=Context(full.origins[use],full.codes,full.truth[use],full.scales[use],full.groups[use],full.edges,full.fit_origins[use])
    selected=json.loads((ROOT/'selection.json').read_text()); chosen=selected['config_id']
    for i in range(6):
        for anchor in ANCHORS:
            if not (path_for(i,anchor,'real')/'complete.json').exists():raise RuntimeError('Complete B2 grid required')
    for anchor in ANCHORS:
        if not (path_for(chosen,anchor,'no_graph')/'complete.json').exists():raise RuntimeError('Selected no-graph fits incomplete')
    values={}; records=[]; curves=[]; scales=[]
    for epochs in (65,100):
        complete=all((path_for(chosen,a,c,epochs)/'complete.json').exists() for a in ANCHORS for c in ('real','no_graph'))
        if not complete:continue
        for condition in ('real','no_graph'):
            arrays=[]
            for anchor in ANCHORS:
                path=path_for(chosen,anchor,condition,epochs)
                with np.load(path/'prediction.npz',allow_pickle=False) as data:
                    np.testing.assert_array_equal(data['codes'],ctx.codes)
                    assert str(data['origin'])==anchor
                    arrays.append(data['prediction'].copy())
            values[f'B2_{condition}_e{epochs}']={11:np.stack(arrays)}
    for condition in ('real','no_graph'):
        arrays=[]
        for anchor in ANCHORS:
            with np.load(old_output('B',anchor,condition)/'prediction.npz',allow_pickle=False) as data:
                np.testing.assert_array_equal(data['codes'],ctx.codes); assert str(data['origin'])==anchor
                arrays.append(data['prediction'].copy())
        values[f'B_{condition}_e65']={11:np.stack(arrays)}
    bundle=evaluate(values,ctx,seeds=(11,)); bundle['origin']['rmse']=np.sqrt(bundle['origin'].mse)
    out=Path('data/explore/t03/b2_screen'); out.mkdir(parents=True,exist_ok=True)
    for key,value in bundle.items():value.to_csv(out/(f'{key}.csv.gz' if key=='areas' else f'{key}.csv'),index=False)
    for i in range(6):
        for anchor in ANCHORS:
            path=path_for(i,anchor,'real')
            record=json.loads((path/'complete.json').read_text()); records.append(record)
            curve=pd.read_csv(path/'training_curve.csv'); curve['config_id']=i; curve['anchor']=anchor
            curves.append(curve)
    for anchor in ANCHORS:
        records.append(json.loads((path_for(chosen,anchor,'no_graph',65)/'complete.json').read_text()))
        for condition in ('real','no_graph'):
            extension=path_for(chosen,anchor,condition,100)/'complete.json'
            if extension.exists():records.append(json.loads(extension.read_text()))
    for anchor in ANCHORS:
        with np.load(path_for(chosen,anchor,'real')/'prediction.npz',allow_pickle=False) as data:
            # The scale array includes unknown graph areas, while forecast codes include observed areas.
            scale=data['scale']; scales.append({'anchor':anchor,'graph_areas':len(scale),'minimum':scale.min(),'median':np.median(scale),'maximum':scale.max()})
    pd.DataFrame(records).to_csv(out/'grid_fits.csv',index=False)
    pd.concat(curves).to_csv(out/'grid_training_curves.csv',index=False)
    pd.DataFrame(scales).to_csv(out/'scales.csv',index=False)
    selected_curves=[]
    for epochs in (65,100):
        for anchor in ANCHORS:
            for condition in ('real','no_graph'):
                path=path_for(chosen,anchor,condition,epochs)/'training_curve.csv'
                if path.exists():
                    frame=pd.read_csv(path); frame['anchor']=anchor; frame['condition']=condition; frame['cap']=epochs
                    selected_curves.append(frame)
    pd.concat(selected_curves,ignore_index=True).to_csv(out/'selected_training_curves.csv',index=False)
    decision=json.loads((ROOT/'extension_decision.json').read_text())
    epoch_file=ROOT/'epoch_decision.json'
    epoch_decision=json.loads(epoch_file.read_text()) if epoch_file.exists() else {'selected_epochs':None,'pending_100':decision['trigger']}
    from visuals.b2_screen import render
    render(out)
    text=f'''# B2 scaling screen

Validation only; final test sealed. Selected configuration **{chosen}**, {selected['configuration']}, by minimum real-graph mean MAE over both anchors and horizons 1–12 at 65 epochs. No later 100-epoch result changes that selection. One seed (11); no seed-spread claim. Current B is its saved width-64/rate-0.003 65-epoch version, not refitted. B2 has an additional six-configuration search, so this is a development comparison rather than an isolated causal test of scaling.

Scale = 1 + each observed area's mean training target from January 2011 through fit origin, fixed for that fit. Divide raw count/base inputs before log1p; output rate multiplied back before the raw-count Poisson objective. Calendar/flags, masks, graph handling and objective unchanged. Unknown areas keep unit scale and masks. The numerical floor remains in raw-count units.

## Training-only extension decision

Trigger: **{decision['trigger']}**. Details: `{json.dumps(decision['anchors'])}`. Epoch decision: `{json.dumps(epoch_decision)}`. The configuration is selected at 65 epochs. Keep 100 only for at least 0.5% lower selected real MAE over both anchors/horizons 1–12; otherwise keep 65. The chosen count is shared by real, no graph, learned graph and identity control. Complete 100-epoch results, if present, are separately labelled. A pending continuation makes this report interim. This is a disclosed validation-based epoch choice, not an independent confirmatory comparison.

## Selected B2 and current B scores

{table(bundle['origin'][['model','origin','outcome','group','mae','mase','rmse','mean_signed_error']])}

## Scale distribution

{table(pd.DataFrame(scales))}

## Grid and costs

{table(pd.DataFrame(records))}

All twelve real-grid training curves are in [curves](../../data/explore/t03/b2_screen/grid_training_curves.png) / [CSV](../../data/explore/t03/b2_screen/grid_training_curves.csv). Selected real/no-graph 65/100 traces: [figure](../../data/explore/t03/b2_screen/selected_training_curves.png) / [CSV](../../data/explore/t03/b2_screen/selected_training_curves.csv). [Selected error curves](../../data/explore/t03/b2_screen/errors.png), [all metrics](../../data/explore/t03/b2_screen/origin.csv), [pooled anchors](../../data/explore/t03/b2_screen/scores.csv), [index](../../data/explore/t03/b2_screen/index.md). MAE/RMSE units systems/area/month or systems/area/window for total; MASE uses shared training-only seasonal scales, twelve times monthly scale for total. Dynamic maturity groups are unchanged.

No new DM family, full campaign, configuration reselection or test run. The one epoch decision follows the researcher's fixed 0.5% rule. Stop for researcher review. Generators: `models.b2_screen`, `evaluation.b2_screen_report`, `visuals.b2_screen`.
'''
    Path('reports/experiments/b2_screen.md').write_text(text,encoding='utf-8')
    print(json.dumps({'event':'B2_screen_report','selected_config_id':chosen,'extension_trigger':decision['trigger'],'report':'reports/experiments/b2_screen.md','test_forecasts_or_losses':0}),flush=True)


if __name__=='__main__':report()
