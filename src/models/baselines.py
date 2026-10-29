"""Researcher-only, CPU-only validation baselines under protocol-v1.

Resume from fingerprinted checkpoints. No test split option is provided.
Run after installing requirements-baselines.lock and passing leakage tests.
"""
import argparse
from datetime import datetime, timezone
import gc
import hashlib
from importlib.metadata import version
from itertools import product
import json
import os
import platform
from pathlib import Path
import time

import numpy as np
import pandas as pd

from evaluation.baselines import validation_rows, seasonal_predictions, evaluate, compare
from evaluation.frozen import frozen_protocol
from features.panel import load_panel
from features.builder import FeatureBuilder


def configurations(cfg):
    grid = cfg['tuning']['gradient_boosting_grid']
    return [{'learning_rate':lr, 'max_leaf_nodes':leaves, 'l2_regularization':l2,
             'max_iter':grid['max_iter'], 'early_stopping':False}
            for lr,leaves,l2 in product(grid['learning_rate'],grid['max_leaf_nodes'],grid['l2_regularization'])]


def validate_origin(origin, cfg):
    if origin not in set(validation_rows(cfg).origin):
        raise ValueError('Only frozen validation origins are permitted; final test is sealed')


def predict_origin(model, builder, origin, spatial, cfg):
    validate_origin(origin, cfg)
    values = np.stack([np.maximum(model.predict(builder.at(origin,h,spatial)), cfg['objective']['rate_floor'])
                       for h in range(1,13)], axis=1).astype(np.float32)
    if not np.isfinite(values).all():
        raise ValueError('Nonfinite validation predictions; stop before scoring')
    return values


def json_write(path, value):
    temporary = path.with_suffix(path.suffix+'.tmp')
    temporary.write_text(json.dumps(value, indent=2), encoding='utf-8')
    temporary.replace(path)


def fingerprint(protocol_hash, panel_hash, threads):
    sources = ['src/features/panel.py','src/features/builder.py','src/evaluation/protocol.py',
               'src/evaluation/baselines.py','src/models/baselines.py']
    hashes = {p:hashlib.sha256(Path(p).read_bytes()).hexdigest() for p in sources}
    info = {'protocol_sha256':protocol_hash, 'panel_sha256':panel_hash, 'source_sha256':hashes,'cpu_threads':threads,
            'versions':{name:version(name) for name in ('scikit-learn','numpy','scipy','joblib','threadpoolctl','dieboldmariano')}}
    return hashlib.sha256(json.dumps(info,sort_keys=True).encode()).hexdigest()[:16], info


def run(threads):
    # Imports are lazy to keep tests and panel preparation independent of install.
    from sklearn.ensemble import HistGradientBoostingRegressor
    from threadpoolctl import threadpool_limits
    import joblib
    if version('scikit-learn') != '1.6.1' or version('dieboldmariano') != '1.1.0':
        raise RuntimeError('Install the pinned baseline dependency file first')
    cfg, protocol_hash = frozen_protocol()
    manifest = json.loads(Path('data/processed/t02_panel_manifest.json').read_text())
    actual_hash = hashlib.sha256(Path('data/processed/t02_panel.npz').read_bytes()).hexdigest()
    if manifest['protocol_sha256'] != protocol_hash or manifest['panel_sha256'] != actual_hash:
        raise RuntimeError('Panel/protocol provenance differs; review and rebuild preparation first')
    panel = load_panel(through=str(pd.Period(cfg['splits']['validation']['last_origin'],freq='M')+12))
    builder = FeatureBuilder(panel, cfg['splits']['lookback_months'])
    rows = validation_rows(cfg)
    run_id, provenance = fingerprint(protocol_hash, actual_hash, threads)
    root = Path('data/processed/t02_baselines')/run_id
    root.mkdir(parents=True, exist_ok=True)
    if (root/'complete.json').exists():
        Path('data/processed/t02_baselines/latest_complete.txt').write_text(run_id,encoding='utf-8')
        print(json.dumps({'event':'already_complete','run_id':run_id,'new_fits':0}),flush=True)
        return
    provenance.update(run_id=run_id, device='CPU', threads=threads, split='validation',
                      platform=platform.platform(),processor=platform.processor(),
                      started_at=datetime.now(timezone.utc).isoformat(), final_test_accessed=False)
    if not (root/'run_manifest.json').exists():
        json_write(root/'run_manifest.json', provenance)
    config_grid = configurations(cfg)
    if len(config_grid) != cfg['tuning']['configurations_per_tunable_condition']:
        raise RuntimeError('Configuration budget differs from frozen protocol')
    np.savez_compressed(root/'seasonal_naive.npz', prediction=seasonal_predictions(builder, rows.origin))
    predictions = {'seasonal_naive':{0:seasonal_predictions(builder, rows.origin)}}
    fit_records = []

    def fit_one(condition, config_id, seed, fit_origin, x, y):
        file = root/f'{condition}_c{config_id}_seed{seed}_{fit_origin}.joblib'
        metadata = file.with_suffix('.json')
        key = {'condition':condition,'config_id':config_id,'seed':seed,'fit_origin':fit_origin,
               'parameters':config_grid[config_id], 'rows':len(y),'features':x.shape[1]}
        if file.exists() and metadata.exists():
            saved = json.loads(metadata.read_text())
            if any(saved[k] != value for k,value in key.items()):
                raise RuntimeError('Incompatible checkpoint; no silent replacement')
            fit_records.append(saved)
            print(json.dumps({'event':'reuse_fit',**key}), flush=True)
            return joblib.load(file)
        if file.exists() or metadata.exists():
            raise RuntimeError('Incomplete checkpoint pair; review before any replacement fit')
        print(json.dumps({'event':'fit_start','device':'CPU',**key}), flush=True)
        start = time.perf_counter()
        model = HistGradientBoostingRegressor(loss='poisson', random_state=seed, **config_grid[config_id])
        with threadpool_limits(limits=threads):
            model.fit(x,y)
        if model.n_iter_ != cfg['tuning']['gradient_boosting_grid']['max_iter']:
            raise RuntimeError('Unexpected iteration count')
        temporary = file.with_suffix('.joblib.tmp')
        joblib.dump(model, temporary, compress=3)
        temporary.replace(file)
        record = {**key,'seconds':time.perf_counter()-start,'device':'CPU','threads':threads}
        json_write(metadata,record)
        fit_records.append(record)
        print(json.dumps({'event':'fit_complete',**record}), flush=True)
        return model

    for spatial,condition in ((False,'gradient_boosting_own'),(True,'gradient_boosting_neighbours')):
        scores = np.zeros(len(config_grid))
        for anchor in cfg['splits']['tuning_origins']:
            x,y = builder.training(anchor,cfg['splits']['training_first_target'],spatial)
            truth = builder.targets(anchor)
            for config_id in range(len(config_grid)):
                seed = cfg['tuning']['tuning_seeds'][0]
                model = fit_one(condition,config_id,seed,anchor,x,y)
                with threadpool_limits(limits=threads):
                    pred = predict_origin(model,builder,anchor,spatial,cfg)
                scores[config_id] += np.abs(pred-truth).mean()/len(cfg['splits']['tuning_origins'])
                del model
            del x,y
            gc.collect()
        selected = int(np.argmin(scores))
        json_write(root/f'{condition}_selection.json', {'configurations':config_grid,'anchor_scores_mae':scores.tolist(),
                   'selected_config_id':selected,'tie_break':'lowest index','device':'CPU'})
        predictions[condition] = {}
        buffers = {seed:np.empty((len(rows),int(panel.observed.sum()),12),dtype=np.float32) for seed in cfg['tuning']['seeds']}
        for fit_origin in rows.fit_origin.drop_duplicates():
            x,y = builder.training(fit_origin,cfg['splits']['training_first_target'],spatial)
            indices = np.flatnonzero(rows.fit_origin.to_numpy() == fit_origin)
            for seed in cfg['tuning']['seeds']:
                model = fit_one(condition,selected,seed,fit_origin,x,y)
                with threadpool_limits(limits=threads):
                    for index in indices:
                        buffers[seed][index] = predict_origin(model,builder,rows.origin.iloc[index],spatial,cfg)
                del model
            del x,y
            gc.collect()
        for seed, prediction in buffers.items():
            np.savez_compressed(root/f'{condition}_seed{seed}.npz',prediction=prediction,
                                codes=panel.codes[panel.observed],origins=rows.origin.to_numpy(dtype='U7'))
            predictions[condition][seed] = prediction
        # One selected seed at both fixed anchors; descriptive grouped permutation
        # only, no refitting, extra tuning or causal interpretation.
        if spatial:
            importance = []
            names = builder.names(True)
            sets = {'neighbour_lags': [i for i,name in enumerate(names) if name.startswith('neighbour_lag_')],
                    'neighbour_base':[names.index('neighbour_cumulative_base')],
                    'neighbour_flag':[names.index('has_observed_neighbour_flag')]}
            for anchor in cfg['splits']['tuning_origins']:
                model = joblib.load(root/f'{condition}_c{selected}_seed11_{anchor}.joblib')
                truth = builder.targets(anchor)
                base = np.abs(predictions[condition][11][rows.origin.tolist().index(anchor)]-truth).mean()
                for label,columns in sets.items():
                    for repeat in range(3):
                        permutation = np.random.default_rng(11+repeat).permutation(len(truth))
                        parts = []
                        with threadpool_limits(limits=threads):
                            for h in range(1,13):
                                xx = builder.at(anchor,h,True)
                                xx[:,columns] = xx[permutation][:,columns]
                                parts.append(np.maximum(model.predict(xx),cfg['objective']['rate_floor']))
                        score = np.abs(np.stack(parts,axis=1)-truth).mean()
                        importance.append({'origin':anchor,'seed':11,'group':label,'repeat':repeat,
                                           'mae_increase_systems':float(score-base),
                                           'interpretation':'descriptive sensitivity; correlated predictors; not causal'})
            pd.DataFrame(importance).to_csv(root/'neighbour_importance.csv',index=False)
    records = pd.DataFrame(fit_records).drop_duplicates(['condition','config_id','seed','fit_origin'])
    if records.groupby('condition').size().to_dict() != {'gradient_boosting_own':46,'gradient_boosting_neighbours':46}:
        raise RuntimeError('Completed fit budget is not exactly 46 per condition')
    records.to_csv(root/'fit_records.csv',index=False)
    origin,scores = evaluate(panel,builder,predictions,cfg,root)
    compare(origin,root)
    json_write(root/'complete.json', {'run_id':run_id,'split':'validation','cpu_fit_count':len(records),
              'fitting_seconds_recorded':float(records.seconds.sum()),'final_test_accessed':False})
    Path('data/processed/t02_baselines/latest_complete.txt').write_text(run_id,encoding='utf-8')
    print(json.dumps({'event':'complete','run_id':run_id,'cpu_fits':len(records),'scores':str(root/'scores.csv')}),flush=True)


def main():
    parser = argparse.ArgumentParser(__doc__)
    parser.add_argument('--threads',type=int,default=min(8,os.cpu_count() or 1))
    args = parser.parse_args()
    if args.threads < 1:
        raise ValueError('CPU thread count must be positive')
    run(args.threads)


if __name__ == '__main__':
    main()
