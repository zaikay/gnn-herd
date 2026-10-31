"""One resumable, bounded CPU fit per invocation for the authorised v3 screen."""
import argparse
import gc
import hashlib
import json
from pathlib import Path
import time
import numpy as np
import pandas as pd
from evaluation.frozen import frozen_protocol
from evaluation.baselines import validation_rows
from features.builder import FeatureBuilder
from features.panel import load_panel

ROOT=Path('data/processed/t03_screen_v3')
OLD=Path('data/processed/t02_baselines/be4f68799849cb4c')
ANCHORS=('2019-08','2020-08')
CONDITIONS=('gradient_boosting_own','gradient_boosting_neighbours')
THREADS=8


def write_json(path,data):
    path=Path(path); path.parent.mkdir(parents=True,exist_ok=True)
    temporary=path.with_suffix('.tmp'); temporary.write_text(json.dumps(data,indent=2),encoding='utf-8'); temporary.replace(path)


def base_schedule():
    return pd.period_range('2011-02','2020-05',freq='3M').astype(str).tolist()


def base_fit_for(origin):
    eligible=[q for q in base_schedule() if q<str(origin)]
    return eligible[-1] if eligible else None


def selected_parameters(condition):
    selection=json.loads((OLD/f'{condition}_selection.json').read_text())
    return selection['configurations'][selection['selected_config_id']]


def extra_parameters(leaves):
    return dict(learning_rate=.05,max_leaf_nodes=int(leaves),l2_regularization=1.,max_iter=300,early_stopping=False)


def initialise():
    cfg,signature=frozen_protocol('protocol-v2')
    source=['src/models/screen_cpu.py','src/features/builder.py','src/features/panel.py','src/evaluation/protocol.py']
    manifest={'v2_sha256':signature,'panel_sha256':hashlib.sha256(Path('data/processed/t02_panel.npz').read_bytes()).hexdigest(),
        'sources':{p:hashlib.sha256(Path(p).read_bytes()).hexdigest() for p in source},
        'threads':THREADS,'seed':11,'base_configuration':selected_parameters(CONDITIONS[0]),
        'first_c_origin':'2011-03','first_c_target':'2011-04','base_fit_rule':'strictly before forecast origin'}
    ROOT.mkdir(parents=True,exist_ok=True)
    destination=ROOT/'cpu_manifest.json'
    if destination.exists() and json.loads(destination.read_text())!=manifest:
        previous=json.loads(destination.read_text())
        old_core={k:v for k,v in previous.items() if k!='sources'}
        new_core={k:v for k,v in manifest.items() if k!='sources'}
        changed=[p for p in source if previous['sources'].get(p)!=manifest['sources'][p]]
        # One explicit pre-GPU correction expands reused anchor forecasts to
        # their other two validation origins; fitting/feature definitions unchanged.
        approved_old='ca3bed82b5a5bb640bf0fc17249681c8205b271300b9498e4a22bd7820678560'
        if (old_core!=new_core or changed!=['src/models/screen_cpu.py'] or
                previous['sources']['src/models/screen_cpu.py']!=approved_old or (ROOT/'gpu_manifest.json').exists()):
            raise RuntimeError('CPU screen provenance changed; no overwrite')
        archive=ROOT/'cpu_manifest_before_anchor_expansion_fix.json'
        if archive.exists():raise RuntimeError('Provenance archive already exists; review')
        archive.write_bytes(destination.read_bytes())
        write_json(ROOT/'cpu_source_revision.json',{'reason':'Expand reused selected tuning-anchor predictions to all three quarterly validation origins; no refit/settings change',
            'previous_manifest_sha256':hashlib.sha256(archive.read_bytes()).hexdigest(),
            'old_source':previous['sources']['src/models/screen_cpu.py'],'new_source':manifest['sources']['src/models/screen_cpu.py']})
    write_json(destination,manifest)
    return cfg


def extra_jobs():
    return [dict(kind='extra',condition=c,origin=a,seed=11,parameters=extra_parameters(l),
                 name=f'extra_{c}_l{l}_seed11_{a}') for c in CONDITIONS for a in ANCHORS for l in (31,63)]


def base_jobs():
    return [dict(kind='base',condition=CONDITIONS[0],origin=q,seed=11,parameters=selected_parameters(CONDITIONS[0]),
                 name=f'base_seed11_{q}') for q in base_schedule()]


def folder(job):return ROOT/'cpu'/job['name']


def choose_extras():
    if not all((folder(j)/'complete.json').exists() for j in extra_jobs()):return None
    result={}
    for condition in CONDITIONS:
        old=json.loads((OLD/f'{condition}_selection.json').read_text())
        current=float(old['anchor_scores_mae'][old['selected_config_id']])
        choices=[]
        for leaves in (31,63):
            scores=[json.loads((folder(j)/'complete.json').read_text())['anchor_mae'] for j in extra_jobs()
                    if j['condition']==condition and j['parameters']['max_leaf_nodes']==leaves]
            choices.append({'parameters':extra_parameters(leaves),'tuning_mae':float(np.mean(scores))})
        winner=min(choices,key=lambda x:x['tuning_mae'])
        result[condition]={'old_tuning_mae':current,'extra':choices,'improved':winner['tuning_mae']<current,
                           'winner':winner,'old_configuration':selected_parameters(condition)}
    write_json(ROOT/'boosting_selection.json',result)
    return result


def full_jobs(cfg,selection):
    jobs=[]
    for condition,decision in (selection or {}).items():
        if not decision['improved']:continue
        for origin in validation_rows(cfg).fit_origin.drop_duplicates():
            for seed in (11,29,47):
                # Selected seed-11 anchor fits already exist among the eight extras.
                leaves=decision['winner']['parameters']['max_leaf_nodes']
                name=f'extra_{condition}_l{leaves}_seed11_{origin}' if seed==11 and origin in ANCHORS else f'full_{condition}_seed{seed}_{origin}'
                jobs.append(dict(kind='full',condition=condition,origin=origin,seed=seed,
                                 parameters=decision['winner']['parameters'],name=name))
    return jobs


def predict(model,builder,origin,spatial):
    value=np.stack([np.maximum(model.predict(builder.at(origin,h,spatial)),1e-6) for h in range(1,13)],axis=1).astype(np.float32)
    if not np.isfinite(value).all():raise RuntimeError('Nonfinite CPU predictions')
    return value


def execute(job,cfg):
    import joblib
    from sklearn.ensemble import HistGradientBoostingRegressor
    from threadpoolctl import threadpool_limits
    destination=folder(job); destination.mkdir(parents=True,exist_ok=True)
    marker=destination/'complete.json'
    if marker.exists():return json.loads(marker.read_text())
    panel=load_panel(through='2022-10')
    builder=FeatureBuilder(panel,24)
    spatial=job['condition']==CONDITIONS[1]
    start=time.perf_counter(); reused=None
    modelpath=destination/'model.joblib'
    with threadpool_limits(limits=THREADS):
        if modelpath.exists():
            meta=json.loads((destination/'fit.json').read_text())
            if meta['job']!=job:raise RuntimeError('CPU checkpoint job differs')
            model=joblib.load(modelpath)
        else:
            if job['kind']=='base':
                old_selection=json.loads((OLD/f'{CONDITIONS[0]}_selection.json').read_text())
                candidate=OLD/f"{CONDITIONS[0]}_c{old_selection['selected_config_id']}_seed11_{job['origin']}.joblib"
                if candidate.exists():
                    metadata=json.loads(candidate.with_suffix('.json').read_text())
                    if metadata['parameters']!=job['parameters'] or metadata['fit_origin']!=job['origin']:raise RuntimeError('Old base checkpoint mismatch')
                    model=joblib.load(candidate); reused=str(candidate)
            if reused is None:
                x,y=builder.training(job['origin'],'2011-01',spatial)
                fit_start=time.perf_counter()
                model=HistGradientBoostingRegressor(loss='poisson',random_state=job['seed'],**job['parameters']).fit(x,y)
                fit_seconds=time.perf_counter()-fit_start
                del x,y; gc.collect()
                temporary=modelpath.with_suffix('.tmp'); joblib.dump(model,temporary,compress=3); temporary.replace(modelpath)
                write_json(destination/'fit.json',{'job':job,'fit_seconds':fit_seconds,'new_fit':True})
            else:
                write_json(destination/'fit.json',{'job':job,'fit_seconds':0.,'new_fit':False,'reused':reused,
                    'reused_sha256':hashlib.sha256(Path(reused).read_bytes()).hexdigest()})
        if job['kind']=='base':
            origins=[o for o in pd.period_range('2011-03','2020-08',freq='M').astype(str) if base_fit_for(o)==job['origin']]
            assert all(job['origin']<o for o in origins)
        elif job['kind']=='extra':origins=[job['origin']]
        else:origins=validation_rows(cfg).loc[lambda f:f.fit_origin.eq(job['origin']),'origin'].tolist()
        values=np.stack([predict(model,builder,o,spatial) for o in origins])
        np.savez_compressed(destination/'forecasts.npz',prediction=values,origins=np.array(origins,dtype='U7'),codes=panel.codes[panel.observed])
        record={**json.loads((destination/'fit.json').read_text()),'command_seconds':time.perf_counter()-start,
                'origin_count':len(origins),'test_forecasts_or_losses':0}
        if job['kind']=='extra':record['anchor_mae']=float(np.abs(values[0].astype(np.float64)-builder.targets(job['origin'])).mean())
        write_json(marker,record)
        print(json.dumps({'event':'cpu_job_complete','job':job['name'],'fit_seconds':record['fit_seconds'],
                          'command_seconds':record['command_seconds'],'new_fit':record['new_fit']}),flush=True)
    return record


def assemble_base():
    jobs=base_jobs()
    if not all((folder(j)/'complete.json').exists() for j in jobs):return False
    predictions=[]; origins=[]; fit_origins=[]; hashes={}
    for job in jobs:
        path=folder(job)/'forecasts.npz'
        with np.load(path,allow_pickle=False) as data:
            predictions.extend(data['prediction']); origins.extend(data['origins']); codes=data['codes'].copy()
            fit_origins.extend([job['origin']]*len(data['origins']))
        hashes[path.as_posix()]=hashlib.sha256(path.read_bytes()).hexdigest()
    assert all(q<o for q,o in zip(fit_origins,origins))
    assert origins==pd.period_range('2011-03','2020-08',freq='M').astype(str).tolist()
    np.savez_compressed(ROOT/'c_base_oos.npz',prediction=np.stack(predictions),origins=np.array(origins,dtype='U7'),
                        fit_origins=np.array(fit_origins,dtype='U7'),codes=codes)
    write_json(ROOT/'c_base_complete.json',{'first_origin':origins[0],'last_origin':origins[-1],
        'refits':len(jobs),'strictly_prior_fit_dates':True,'sources':hashes,
        'prediction_sha256':hashlib.sha256((ROOT/'c_base_oos.npz').read_bytes()).hexdigest()})
    return True


def assemble_full(cfg,selection):
    import joblib
    from threadpoolctl import threadpool_limits
    for condition,decision in (selection or {}).items():
        if not decision['improved']:continue
        jobs=[j for j in full_jobs(cfg,selection) if j['condition']==condition]
        if not all((folder(j)/'complete.json').exists() for j in jobs):continue
        rows=validation_rows(cfg)
        for seed in (11,29,47):
            pieces={}
            for j in jobs:
                if j['seed']!=seed:continue
                with np.load(folder(j)/'forecasts.npz',allow_pickle=False) as data:
                    pieces.update(zip(data['origins'],data['prediction'])); codes=data['codes'].copy()
                expected=rows.loc[rows.fit_origin.eq(j['origin']),'origin'].tolist()
                missing=[o for o in expected if o not in pieces]
                if missing:
                    # Selected tuning anchors have one cached forecast but their
                    # retained model also serves the next two validation origins.
                    if j['origin'] not in ANCHORS or seed!=11:raise RuntimeError('Incomplete full-validation forecast cache')
                    builder=FeatureBuilder(load_panel(through='2022-10'),24)
                    model=joblib.load(folder(j)/'model.joblib')
                    with threadpool_limits(limits=THREADS):
                        extension=np.stack([predict(model,builder,o,condition==CONDITIONS[1]) for o in missing])
                    pieces.update(zip(missing,extension))
                    np.savez_compressed(folder(j)/'validation_expansion.npz',prediction=extension,origins=np.array(missing,dtype='U7'),codes=codes)
            np.savez_compressed(ROOT/f'{condition}_updated_seed{seed}.npz',prediction=np.stack([pieces[o] for o in rows.origin]),
                                origins=rows.origin.to_numpy(dtype='U7'),codes=codes)
        write_json(ROOT/f'{condition}_updated_complete.json',{'fits':36,'reused_extra_anchor_fits':2,'test_forecasts_or_losses':0,
                    'parameters':decision['winner']['parameters']})


def status(cfg):
    selection=choose_extras()
    jobs=extra_jobs()+full_jobs(cfg,selection)+base_jobs()
    # Deduplicate anchor reuse for display.
    jobs=list({j['name']:j for j in jobs}.values())
    pending=[j for j in jobs if not (folder(j)/'complete.json').exists()]
    result={'jobs':len(jobs),'completed':len(jobs)-len(pending),'pending':len(pending),
            'next_job':pending[0]['name'] if pending else None,'base_ready':(ROOT/'c_base_complete.json').exists()}
    print(json.dumps(result),flush=True)
    return pending


def main():
    parser=argparse.ArgumentParser(__doc__)
    parser.add_argument('--next',action='store_true',help='One natural CPU job only; never a campaign loop')
    parser.add_argument('--all',action='store_true',help='Researcher command when total exceeds agent time limit')
    args=parser.parse_args(); cfg=initialise()
    while True:
        pending=status(cfg)
        if not pending or not(args.next or args.all):break
        execute(pending[0],cfg)
        selection=choose_extras(); assemble_full(cfg,selection)
        if all((folder(j)/'complete.json').exists() for j in base_jobs()):assemble_base()
        if not args.all:break
    status(cfg)


if __name__=='__main__':main()

