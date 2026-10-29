"""Researcher-run, resumable validation campaign. No test-block option."""
import argparse
from datetime import datetime, timezone
import hashlib
from itertools import product
import json
from pathlib import Path

import numpy as np
import pandas as pd

from evaluation.baselines import validation_rows
from evaluation.frozen import frozen_protocol
from evaluation.protocol import fit_budget
from features.gnn import GNNWindows
from features.panel import load_panel


def configurations(cfg):
    grid = cfg['tuning']['gnn_grid']
    return [dict(width=w,learning_rate=lr,weight_decay=wd) for w,lr,wd in
            product(grid['hidden_size'],grid['learning_rate'],grid['weight_decay'])]


def fit_name(config_id,seed,origin):
    return f'c{config_id}_seed{seed}_{origin}'


def selected_jobs(cfg,config_id):
    rows = validation_rows(cfg)
    return [(config_id,seed,origin) for origin in rows.fit_origin.drop_duplicates()
            for seed in cfg['tuning']['seeds']]


def select_configuration(anchor_scores,configuration_count):
    values = np.asarray(anchor_scores,dtype=np.float64)
    if values.shape!=(2,configuration_count) or not np.isfinite(values).all():
        raise ValueError('Two complete finite anchor scores per configuration required')
    return int(np.argmin(values.mean(axis=0)))


def json_write(path,value):
    path = Path(path)
    temporary = path.with_suffix(path.suffix+'.tmp')
    temporary.write_text(json.dumps(value,indent=2),encoding='utf-8')
    temporary.replace(path)


def campaign_root(signature):
    return Path('data/processed/t03_gnn/validation')/signature[:16]


def verify_inputs(cfg):
    # Data/geography were frozen before v2, whose changes do not alter them.
    old,_ = frozen_protocol('protocol-v1.1',require_working=False)
    for key in ('data','splits','features','objective','state_assignment'):
        if cfg[key]!=old[key]:
            raise ValueError(f'Unexpected change in approved panel/graph definition: {key}')
    evidence = json.loads(Path('reports/experiments/t03_preparation_checks.json').read_text())
    panel_hash = hashlib.sha256(Path('data/processed/t02_panel.npz').read_bytes()).hexdigest()
    pilot = json.loads(Path('data/processed/t03_gnn/pilot/real_seed11_width32_2020-08/manifest.json').read_text())
    if panel_hash!=pilot['panel']:
        raise ValueError('Model panel differs from approved pilot')
    states = json.loads(Path('data/explore/t03/state_assignment_summary.json').read_text())
    graph = json.loads(Path('data/explore/t03/graph_conditions_summary.json').read_text())
    if states['coverage_failures'] or graph['states_requiring_review']:
        raise ValueError('Unresolved geography review')
    for row in evidence['graph_checks']:
        path = Path(f"data/processed/t03_graphs/shuffled_seed{row['seed']}.npz")
        if hashlib.sha256(path.read_bytes()).hexdigest()!=row['sha256']:
            raise ValueError('Audited shuffled graph changed')
    return panel_hash


def plan(cfg,condition):
    rows = validation_rows(cfg)
    return {'condition':condition,'configurations':configurations(cfg),'tuning_origins':cfg['splits']['tuning_origins'],
        'epochs_per_fit':cfg['tuning']['max_gnn_epochs'],'budget':fit_budget(cfg),
        'validation_origins':len(rows),'last_validation_target':rows.last_target.max(),
        'checkpoint_interval_epochs':cfg['tuning']['checkpoints']['interval_epochs'],
        'switch_to_next_condition':False,'test_forecasts_or_losses':0}


def run(condition,cfg,signature,panel_hash):
    # All torch imports and device operations are confined to researcher execution.
    import torch
    from filelock import FileLock
    from models.core_gnn import CoreGNN, graph_operator
    from models.gnn_fit import fit, lock_machine
    base = campaign_root(signature); base.mkdir(parents=True,exist_ok=True)
    with FileLock(base/'session.lock',timeout=0):
        root = base/condition
        order = cfg['gnn_design']['run_order']
        for previous in order[:order.index(condition)]:
            if not (base/previous/'condition_complete.json').exists():
                raise ValueError(f'Finish {previous} before starting {condition}')
        root.mkdir(exist_ok=True)
        sources = ['src/models/gnn_validation.py','src/models/core_gnn.py','src/models/gnn_fit.py',
                   'src/models/gnn_checkpoint.py','src/features/gnn.py','src/features/panel.py',
                   'src/evaluation/protocol.py']
        manifest = {'protocol_sha256':signature,'condition':condition,'panel_sha256':panel_hash,
                    'source_sha256':{p:hashlib.sha256(Path(p).read_bytes()).hexdigest() for p in sources},
                    'device':'CUDA','split':'validation','epochs':cfg['tuning']['max_gnn_epochs']}
        path = root/'run_manifest.json'
        if path.exists() and json.loads(path.read_text())!=manifest:
            raise ValueError('Campaign fingerprint changed; existing fits are not silently replaced')
        json_write(path,manifest)
        lock_machine('data/processed/t03_gnn')
        if (root/'condition_complete.json').exists():
            print(json.dumps({'event':'already_complete','condition':condition,'new_fits':0}),flush=True)
            return
        rows = validation_rows(cfg)
        panel = load_panel(through=rows.last_target.max())
        windows = GNNWindows(panel,cfg)
        grid = configurations(cfg)
        if len(grid)!=cfg['tuning']['configurations_per_tunable_condition']:
            raise ValueError('Configuration count differs from protocol')
        channels = [0,2,3,4,5] if condition=='real_without_installed_base' else None

        def graph_edges(seed):
            if condition!='within_state_shuffled':
                return None
            with np.load(f'data/processed/t03_graphs/shuffled_seed{seed}.npz',allow_pickle=False) as saved:
                np.testing.assert_array_equal(saved['codes'],panel.codes)
                np.testing.assert_array_equal(saved['observed'],panel.observed)
                return saved['edges'].copy()

        def fit_one(config_id,seed,origin):
            destination = root/fit_name(config_id,seed,origin)
            print(json.dumps({'event':'fit_or_resume','condition':condition,'config_id':config_id,
                              'seed':seed,'fit_origin':origin,'checkpoint_every_epochs':5}),flush=True)
            fit(panel.through(origin),cfg,signature,condition,seed,**grid[config_id],
                output=destination,purpose='approved_validation',edges=graph_edges(seed))
            return destination

        def predict(destination,config_id,seed,origins,filename):
            origins = list(origins)
            if not set(origins).issubset(set(rows.origin)):
                raise ValueError('Only approved validation origins may be forecast')
            path = destination/filename
            if path.exists():
                with np.load(path,allow_pickle=False) as data:
                    np.testing.assert_array_equal(data['origins'],np.array(origins,dtype='U7'))
                    np.testing.assert_array_equal(data['codes'],panel.codes[panel.observed])
                    values = data['prediction'].copy()
                if values.shape!=(len(origins),int(panel.observed.sum()),12) or not np.isfinite(values).all() or (values<0).any():
                    raise ValueError('Invalid cached validation forecasts')
                return values
            edges = graph_edges(seed)
            operator = graph_operator(panel.edges if edges is None else edges,panel.observed,
                                      'real' if channels is not None else condition)
            model = CoreGNN(operator,panel.observed,grid[config_id]['width'],input_channels=5 if channels is not None else 6).cuda()
            saved = torch.load(destination/'checkpoint.pt',map_location='cpu',weights_only=False)
            if saved['completed_epochs']!=cfg['tuning']['max_gnn_epochs']:
                raise ValueError('Forecast requested from incomplete fit')
            model.load_state_dict(saved['model']); model.eval()
            values = []
            with torch.no_grad():
                for origin in origins:
                    x = windows.at(origin)[None,...]
                    if channels is not None:
                        x = x[:,:,:,channels]
                    values.append(model(torch.from_numpy(x).cuda())[0].cpu().numpy()[panel.observed])
            values = np.stack(values).astype(np.float32)
            if not np.isfinite(values).all() or (values<0).any():
                raise ValueError('Invalid validation forecast')
            temporary = path.with_suffix('.tmp')
            with temporary.open('wb') as stream:
                np.savez_compressed(stream,prediction=values,codes=panel.codes[panel.observed],origins=np.array(origins,dtype='U7'))
            temporary.replace(path)
            return values

        scores = []
        for anchor in cfg['splits']['tuning_origins']:
            truth = panel.targets[panel.observed,panel.index(anchor)+1:panel.index(anchor)+13].astype(np.float64)
            anchor_scores = []
            for config_id in range(len(grid)):
                destination = fit_one(config_id,11,anchor)
                forecast = predict(destination,config_id,11,[anchor],'anchor_prediction.npz')[0]
                anchor_scores.append(float(np.abs(forecast-truth).mean()))
            scores.append(anchor_scores)
        chosen = select_configuration(scores,len(grid))
        json_write(root/'selection.json',{'configuration_id':chosen,'configuration':grid[chosen],
            'anchor_mae':scores,'score':'equal-area, equal-horizon, equal-anchor mean MAE; seed 11',
            'tie_break':'lowest configuration index'})
        buffers = {seed:np.empty((len(rows),int(panel.observed.sum()),12),dtype=np.float32) for seed in cfg['tuning']['seeds']}
        for config_id,seed,origin in selected_jobs(cfg,chosen):
            destination = fit_one(config_id,seed,origin)
            indices = np.flatnonzero(rows.fit_origin.eq(origin).to_numpy())
            buffers[seed][indices] = predict(destination,config_id,seed,rows.origin.iloc[indices],'validation_predictions.npz')
        for seed,values in buffers.items():
            path = root/f'predictions_seed{seed}.npz'
            with path.with_suffix('.tmp').open('wb') as stream:
                np.savez_compressed(stream,prediction=values,codes=panel.codes[panel.observed],origins=rows.origin.to_numpy(dtype='U7'))
            path.with_suffix('.tmp').replace(path)
        actual = list(root.glob('c*_seed*/complete.json'))
        if len(actual)!=46:
            raise ValueError('Completed condition does not have exactly 46 unique fits')
        json_write(root/'condition_complete.json',{'condition':condition,'unique_fits':46,'seeds':cfg['tuning']['seeds'],
            'validation_origins':len(rows),'last_target':rows.last_target.max(),'test_forecasts_or_losses':0,
            'completed_at':datetime.now(timezone.utc).isoformat()})
        print(json.dumps({'event':'condition_complete','condition':condition,'unique_fits':46,
                          'next':'STOP; no automatic transition to another condition'}),flush=True)


def main():
    parser = argparse.ArgumentParser(__doc__)
    parser.add_argument('--condition',required=True,choices=['real','within_state_shuffled','no_graph','real_without_installed_base'])
    parser.add_argument('--plan-only',action='store_true',help='CPU-only inspection; never imports torch or starts fits')
    args = parser.parse_args()
    cfg,signature = frozen_protocol('protocol-v2')
    if args.condition=='real_without_installed_base' and not cfg['gnn_design']['optional_condition']['enabled']:
        raise ValueError('Optional fourth condition is disabled')
    panel_hash = verify_inputs(cfg)
    if args.plan_only:
        print(json.dumps(plan(cfg,args.condition),indent=2))
        return
    try:
        run(args.condition,cfg,signature,panel_hash)
    except KeyboardInterrupt:
        print('Session stopped. Completed fits retained; current fit resumes from its last five-epoch checkpoint.',flush=True)
    finally:
        from evaluation.gnn_progress import write_progress
        write_progress(cfg,signature)


if __name__=='__main__':
    main()
