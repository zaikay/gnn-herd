"""Guarded saved-prediction IO. Baseline preflight never opens GNN forecasts."""
import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd

from evaluation.baselines import mase_scales, validation_rows
from evaluation.frozen import frozen_protocol
from evaluation.protocol import maturity_groups
from evaluation.result_report import completed_run
from evaluation.gate_c_metrics import Context, BASELINES
from features.panel import load_panel

CONDITIONS={'gnn_real':'real','gnn_shuffled':'within_state_shuffled',
            'gnn_no_graph':'no_graph','gnn_no_base':'real_without_installed_base'}


def campaign_path(signature):
    return Path('data/processed/t03_gnn/validation')/signature[:16]


def comparison_release(campaign,drop_decision=None):
    """Call before opening any GNN predictions or computing any GNN metric."""
    marker=Path(campaign)/CONDITIONS['gnn_no_base']/'condition_complete.json'
    if marker.exists():
        complete=json.loads(marker.read_text())
        if (complete.get('condition')!=CONDITIONS['gnn_no_base'] or complete.get('unique_fits')!=46
                or complete.get('seeds')!=[11,29,47] or complete.get('test_forecasts_or_losses')!=0):
            raise RuntimeError('Fourth-condition completion marker is invalid; comparisons withheld')
        return True,{'basis':'fourth condition complete','marker':marker.as_posix()}
    if drop_decision is not None and Path(drop_decision).exists():
        decision=json.loads(Path(drop_decision).read_text())
        if (decision.get('condition')==CONDITIONS['gnn_no_base'] and decision.get('decision')=='drop'
                and decision.get('approved_by')=='researcher' and str(decision.get('reason','')).strip()
                and decision.get('date')):
            pd.Timestamp(decision['date'])
            return False,{'basis':'formal researcher drop','decision_file':Path(drop_decision).as_posix(),**decision}
        raise RuntimeError('A dated, reasoned, researcher-approved drop decision is required')
    raise RuntimeError('GNN comparisons withheld: fourth condition incomplete and no formal researcher drop')


def context_from_panel(cfg):
    rows=validation_rows(cfg)
    if rows.last_target.max()>cfg['splits']['test']['first_origin'] or rows.last_target.max()>cfg['data']['evaluation_cutoff']:
        raise ValueError('Validation target crosses sealed boundary')
    panel=load_panel(through=rows.last_target.max())
    codes=panel.codes[panel.observed]
    truth=np.stack([panel.targets[panel.observed,panel.index(o)+1:panel.index(o)+13].astype(np.float64) for o in rows.origin])
    scales=np.stack([mase_scales(panel,fit,cfg) for fit in rows.fit_origin])
    base=np.cumsum(panel.inputs,axis=1,dtype=np.float64)
    groups=np.stack([maturity_groups(base[panel.observed,panel.index(o)],codes) for o in rows.origin])
    reindex={int(old):i for i,old in enumerate(np.flatnonzero(panel.observed))}
    edges=np.array([(reindex[int(a)],reindex[int(b)]) for a,b in panel.edges if int(a) in reindex and int(b) in reindex],dtype=int).reshape(-1,2)
    ctx=Context(rows.origin.to_numpy(dtype='U7'),codes,truth,scales,groups,edges,rows.fit_origin.to_numpy(dtype='U7'))
    ctx.validate()
    return ctx


def read_prediction(path,ctx,allow_legacy=False):
    with np.load(path,allow_pickle=False) as data:
        if ('codes' in data)!=('origins' in data):
            raise ValueError('Partially missing prediction identifiers')
        if 'codes' in data and 'origins' in data:
            np.testing.assert_array_equal(data['codes'],ctx.codes)
            np.testing.assert_array_equal(data['origins'],ctx.origins)
        elif not allow_legacy:
            raise ValueError('Prediction identifiers missing')
        values=data['prediction'].copy()
    if values.shape!=ctx.truth.shape or not np.isfinite(values).all() or (values<0).any():
        raise ValueError(f'Invalid/misaligned prediction file: {path}')
    return values


def load_baselines(cfg,ctx):
    root,old,manifest,complete=completed_run()
    for key in ('data','splits','features','horizons','objective'):
        if cfg[key]!=old[key]:
            raise ValueError(f'Baseline evaluation authority differs: {key}')
    actual=hashlib.sha256(Path('data/processed/t02_panel.npz').read_bytes()).hexdigest()
    if actual!=manifest['panel_sha256']:
        raise ValueError('Saved baseline panel provenance mismatch')
    result={}; hashes={}
    for model in BASELINES:
        result[model]={}
        for seed in cfg['tuning']['seeds']:
            path=root/'seasonal_naive.npz' if model=='seasonal_naive' else root/f'{model}_seed{seed}.npz'
            result[model][seed]=read_prediction(path,ctx,allow_legacy=model=='seasonal_naive')
            hashes[path.as_posix()]=hashlib.sha256(path.read_bytes()).hexdigest()
    return result,root,{'baseline_run':manifest['run_id'],'prediction_sha256':hashes,
                       'legacy_seasonal_identifiers':'inherited from verified common panel and identical origin calendar'}


def load_gnn_predictions(cfg,ctx,signature,drop_decision=None,campaign=None):
    campaign=campaign_path(signature) if campaign is None else Path(campaign)
    include_optional,release=comparison_release(campaign,drop_decision)  # before any forecast read
    models=list(CONDITIONS) if include_optional else list(CONDITIONS)[:-1]
    result={}; provenance={'release':release,'include_optional':include_optional,'conditions':{}}
    panel_hash=hashlib.sha256(Path('data/processed/t02_panel.npz').read_bytes()).hexdigest()
    common_hardware=None
    for model in models:
        root=campaign/CONDITIONS[model]
        complete=json.loads((root/'condition_complete.json').read_text())
        if (complete.get('condition')!=CONDITIONS[model] or complete['unique_fits']!=46 or complete['seeds']!=cfg['tuning']['seeds']
                or complete['validation_origins']!=len(ctx.origins) or complete['last_target']!='2022-10'
                or complete['test_forecasts_or_losses']):
            raise ValueError('Incomplete or misaligned GNN condition')
        manifest=json.loads((root/'run_manifest.json').read_text())
        if manifest['protocol_sha256']!=signature or manifest.get('condition')!=CONDITIONS[model]:
            raise ValueError('GNN condition uses different frozen protocol')
        if manifest['panel_sha256']!=panel_hash:
            raise ValueError('GNN condition uses a different panel')
        for filename,expected in manifest['source_sha256'].items():
            if hashlib.sha256(Path(filename).read_bytes()).hexdigest()!=expected:
                raise ValueError(f'GNN fit source changed: {filename}')
        folders=list(root.glob('c*_seed*/complete.json'))
        if (len(folders)!=46 or any(not (p.parent/'checkpoint.pt').exists() for p in folders)
                or any(json.loads(p.read_text())['epochs']!=cfg['tuning']['max_gnn_epochs'] for p in folders)):
            raise ValueError('Missing completed fit/checkpoint')
        chosen=json.loads((root/'selection.json').read_text())['configuration_id']
        if chosen not in range(cfg['tuning']['configurations_per_tunable_condition']):
            raise ValueError('Invalid selected configuration')
        expected={f'c{i}_seed11_{a}' for i in range(6) for a in cfg['splits']['tuning_origins']}
        rows=validation_rows(cfg)
        expected|={f'c{chosen}_seed{seed}_{fit}' for fit in rows.fit_origin.drop_duplicates() for seed in cfg['tuning']['seeds']}
        if {p.parent.name for p in folders}!=expected:
            raise ValueError('GNN unique fit/reuse schedule differs')
        for path in folders:
            fit_manifest=json.loads((path.parent/'manifest.json').read_text())
            if common_hardware is None: common_hardware=fit_manifest['hardware']
            if fit_manifest['hardware']!=common_hardware or fit_manifest['protocol_sha256']!=signature:
                raise ValueError('GNN fits used different machine/software or protocol')
        result[model]={}; hashes={}
        for seed in cfg['tuning']['seeds']:
            path=root/f'predictions_seed{seed}.npz'
            result[model][seed]=read_prediction(path,ctx)
            hashes[path.name]=hashlib.sha256(path.read_bytes()).hexdigest()
        provenance['conditions'][model]={'completion':complete,'prediction_sha256':hashes}
    return result,provenance


def frozen_context():
    cfg,signature=frozen_protocol('protocol-v2')
    return cfg,signature,context_from_panel(cfg)
