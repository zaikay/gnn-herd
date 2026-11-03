"""Researcher-only v7 fits. Every CLI mode requires protocol-v7-test first."""
import argparse
import gc
import json
import os
from pathlib import Path
import time
import numpy as np
import pandas as pd
from models.final_test_runtime import authorize,bind,calendar,ROOT,PANEL,write_json,sha,utc
from features.sealed_panel import load_prefix


def save_prediction(path,prediction,codes,origins):
    if not np.isfinite(prediction).all() or (prediction<0).any():raise RuntimeError('Invalid final forecast')
    temporary=path.with_suffix('.npz.tmp')
    with temporary.open('wb') as stream:
        np.savez_compressed(stream,prediction=prediction,codes=codes,origins=np.asarray(origins,dtype='U7'))
    temporary.replace(path)


def execute_calendar(rows,seeds,fit_predict):
    """Shared pure scheduler; tests inject synthetic fit/predict callbacks."""
    records=[];buffers={s:[] for s in seeds}
    for origin in rows.fit_origin.drop_duplicates():
        dates=rows.loc[rows.fit_origin.eq(origin),'origin'].tolist()
        for seed in seeds:
            prediction,record=fit_predict(origin,seed,dates)
            if prediction.shape[0]!=len(dates) or prediction.shape[-1]!=12:raise RuntimeError('Misaligned quarterly predictions')
            if not np.isfinite(prediction).all() or (prediction<0).any():raise RuntimeError('Invalid quarterly predictions')
            buffers[seed].append(prediction);records.append({**record,'seed':seed,'fit_origin':origin})
    return {s:np.concatenate(parts) for s,parts in buffers.items()},records


def completed(root,permit):
    path=root/'complete.json'
    if not path.exists():return False
    marker=json.loads(path.read_text())
    if marker['signature']!=permit.signature:raise RuntimeError('Completion signature changed')
    if marker['model']!=root.name or marker['fits']!=24 or marker['origins']!=24 or len(marker['artifact_sha256'])!=52:
        raise RuntimeError('Incomplete final-condition artifact inventory')
    for path,digest in marker['artifact_sha256'].items():
        if sha(path)!=digest:raise RuntimeError('Completed final artifacts changed')
    return True


def cpu_model(path,x,y,parameters,seed,permit,key):
    import joblib
    from sklearn.ensemble import HistGradientBoostingRegressor
    from threadpoolctl import threadpool_limits
    file=path/'model.joblib';path.mkdir(parents=True,exist_ok=True)
    identity={'signature':permit.signature,'model':key,'seed':seed,'parameters':parameters,'rows':len(y),'features':x.shape[1]}
    if file.exists():
        bundle=joblib.load(file)
        if bundle['identity']!=identity:raise RuntimeError('CPU fit identity changed')
        return bundle['model'],bundle['record']
    model=HistGradientBoostingRegressor(loss='poisson',random_state=seed,**parameters)
    started=time.perf_counter();outcome='interrupted'
    try:
        with threadpool_limits(limits=permit.spec['cpu_threads']):model.fit(x,y)
        seconds=time.perf_counter()-started
        if model.n_iter_!=parameters['max_iter']:raise RuntimeError('Boosting iteration budget changed')
        record={'fit_seconds':seconds,'device':'CPU','threads':permit.spec['cpu_threads'],'rows':len(y),'iterations':int(model.n_iter_)}
        temporary=file.with_suffix('.joblib.tmp')
        joblib.dump({'identity':identity,'record':record,'model':model},temporary,compress=3);temporary.replace(file)
        outcome='complete';return model,record
    finally:
        with (path/'sessions.jsonl').open('a',encoding='utf-8') as stream:
            stream.write(json.dumps({'ended_at':utc(),'seconds':time.perf_counter()-started,'outcome':outcome})+'\n')


def cpu_callback(permit,key,root,rows):
    from features.builder import FeatureBuilder
    from threadpoolctl import threadpool_limits
    spatial=key=='gradient_boosting_neighbours';cache={}
    def callback(origin,seed,dates):
        # Cache one fit's X/y across seeds. Never construct targets after its fit origin.
        if cache.get('origin')!=origin:
            cache.clear();gc.collect()
            training=load_prefix(PANEL,origin,permit)
            x,y=FeatureBuilder(training,24).training(origin,permit.spec['training_first_target'],spatial)
            features=FeatureBuilder(load_prefix(PANEL,dates[-1],permit),24)
            cache.update(origin=origin,x=x,y=y,features=features,codes=training.codes[training.observed])
        path=root/f'seed{seed}_{origin}'
        model,record=cpu_model(path,cache['x'],cache['y'],permit.spec['boosting'][key],seed,permit,key)
        with threadpool_limits(limits=permit.spec['cpu_threads']):
            prediction=np.stack([np.stack([np.maximum(model.predict(cache['features'].at(date,h,spatial)),permit.cfg['objective']['rate_floor']) for h in range(1,13)],axis=1) for date in dates]).astype(np.float32)
        record={**record,'signature':permit.signature,'checkpoint':str(path/'model.joblib')}
        write_json(path/'fit.json',record)
        return prediction,record
    return callback


def b2_callback(permit,condition,root,rows):
    import torch
    from features.b2 import area_scale,B2Windows
    from models.b2_adaptive import make_model
    from models.gnn_checkpoint import run_epochs,train_epoch
    def callback(origin,seed,dates):
        training_panel=load_prefix(PANEL,origin,permit);scale=area_scale(training_panel,origin)
        training=B2Windows(training_panel,permit.cfg,scale)
        samples,targets,mask=training.training(origin)
        path=root/f'seed{seed}_{origin}';path.mkdir(parents=True,exist_ok=True)
        torch.manual_seed(seed);torch.cuda.manual_seed_all(seed)
        model=make_model(training_panel,condition,seed,scale).cuda()
        identity={'signature':permit.signature,'condition':condition,'seed':seed,'fit_origin':origin,'epochs':100}
        if (path/'fit.json').exists():
            record=json.loads((path/'fit.json').read_text())
            if any(record.get(k)!=v for k,v in identity.items()):raise RuntimeError('B2 fit identity changed')
            if sha(path/'checkpoint.pt')!=record['checkpoint_sha256']:raise RuntimeError('Retained checkpoint changed')
            saved=torch.load(path/'checkpoint.pt',map_location='cpu',weights_only=False)
            if saved['completed_epochs']!=100 or saved['total_epochs']!=100:raise RuntimeError('Incomplete retained final fit')
            model.load_state_dict(saved['model'],strict=True)
        else:
            optimiser=torch.optim.Adam(model.parameters(),lr=.003,weight_decay=.0001)
            channels=[0,2,3,4,5] if condition=='without_base' else None
            torch.cuda.synchronize();torch.cuda.reset_peak_memory_stats()
            records,seconds,peaks=run_epochs(model,optimiser,
                lambda epoch:train_epoch(model,optimiser,training,samples,targets,mask,epoch,seed,2,torch.device('cuda'),channels),
                100,path,torch.device('cuda'),interval=5,synchronise=torch.cuda.synchronize,
                metrics=lambda:{'allocated':torch.cuda.max_memory_allocated(),'reserved':torch.cuda.max_memory_reserved()},
                on_epoch=lambda r:print(json.dumps({'condition':condition,'seed':seed,'fit_origin':origin,**r}),flush=True))
            record={**identity,'fit_seconds':seconds,'training_loss':records[-1]['training_poisson_loss'],
                'peak_gpu_memory_bytes':peaks['allocated'],'peak_reserved_gpu_memory_bytes':peaks['reserved'],
                'parameter_count':sum(p.numel() for p in model.parameters()),'checkpoint':str(path/'checkpoint.pt'),
                'checkpoint_sha256':sha(path/'checkpoint.pt')}
            write_json(path/'fit.json',record);del optimiser
        model.eval();features=B2Windows(load_prefix(PANEL,dates[-1],permit),permit.cfg,scale)
        predictions=[]
        with torch.no_grad():
            for date in dates:
                x=features.at(date)[None]
                if condition=='without_base':x=x[:,:,:,[0,2,3,4,5]]
                predictions.append(model(torch.from_numpy(x).cuda())[0,training_panel.observed].cpu().numpy())
        del model;torch.cuda.empty_cache()
        return np.stack(predictions),record
    return callback


def run_one(permit,key):
    rows=calendar(permit.spec['first_origin'],permit.spec['last_origin'])
    root=ROOT/key;root.mkdir(parents=True,exist_ok=True)
    if completed(root,permit):
        print(json.dumps({'event':'already_complete','model':key}),flush=True);return
    if key in permit.spec['boosting']:callback=cpu_callback(permit,key,root,rows)
    else:callback=b2_callback(permit,key.removeprefix('B2_'),root,rows)
    progress={}
    if (root/'fit_records.csv').exists():
        previous=pd.read_csv(root/'fit_records.csv',dtype={'fit_origin':str})
        progress={(int(r['seed']),r['fit_origin']):r for r in previous.to_dict('records')}
    def with_log(origin,seed,dates):
        print(json.dumps({'event':'fit_or_resume_start','model':key,'seed':seed,'fit_origin':origin}),flush=True)
        result,record=callback(origin,seed,dates)
        progress[seed,origin]={**record,'seed':seed,'fit_origin':origin}
        temporary=root/'fit_records.csv.tmp';pd.DataFrame(progress.values()).to_csv(temporary,index=False);temporary.replace(root/'fit_records.csv')
        print(json.dumps({'event':'fit_complete','model':key,'seed':seed,'fit_origin':origin,**record}),flush=True)
        return result,record
    buffers,records=execute_calendar(rows,permit.spec['seeds'],with_log)
    metadata=load_prefix(PANEL,rows.origin.iloc[0],permit)
    for seed,prediction in buffers.items():save_prediction(root/f'predictions_seed{seed}.npz',prediction,metadata.codes[metadata.observed],rows.origin)
    pd.DataFrame(records).to_csv(root/'fit_records.csv',index=False)
    paths=[root/f'predictions_seed{s}.npz' for s in permit.spec['seeds']]+[root/'fit_records.csv']
    paths += [Path(r['checkpoint']) for r in records]
    paths += [root/f"seed{r['seed']}_{r['fit_origin']}"/('fit.json') for r in records]
    write_json(root/'complete.json',{'signature':permit.signature,'model':key,'fits':len(records),'origins':len(rows),
        'fit_hours':sum(r['fit_seconds'] for r in records)/3600,'completed_at':utc(),
        'artifact_sha256':{str(p):sha(p) for p in paths}})
    print(json.dumps({'event':'final_condition_complete','model':key,'fits':len(records)}),flush=True)


def main():
    parser=argparse.ArgumentParser(__doc__);options=parser.add_mutually_exclusive_group(required=True)
    options.add_argument('--boosting',action='store_true');options.add_argument('--condition',choices=('real','shuffled','no_graph','without_base'));options.add_argument('--plan',action='store_true')
    args=parser.parse_args();permit=authorize()
    if args.plan:
        print(json.dumps({'tag':permit.manifest['tag'],'signature':permit.signature,'CPU_fits':48,'GPU_fits':96,'test_values_opened':False}));return
    os.environ['LOKY_MAX_CPU_COUNT']=str(permit.spec['cpu_threads'])
    from filelock import FileLock
    ROOT.mkdir(parents=True,exist_ok=True)
    with FileLock(str(ROOT/'workflow.lock'),timeout=0):
        bind(permit)
        if args.boosting:
            for key in permit.spec['boosting']:run_one(permit,key)
        else:
            os.environ['CUBLAS_WORKSPACE_CONFIG']=':4096:8'
            import torch
            from models.gnn_fit import lock_machine
            if lock_machine('data/processed/t03_gnn')!=permit.manifest['inventory']['hardware']:raise RuntimeError('Original GPU inventory differs')
            order=list(permit.spec['boosting'])+['B2_'+c for c in permit.spec['conditions']]
            for previous in order[:order.index('B2_'+args.condition)]:
                if not completed(ROOT/previous,permit):raise RuntimeError(f'Finish {previous} first')
            from filelock import FileLock as GPUFileLock
            with GPUFileLock('data/processed/t03_gnn/gpu_fit.lock',timeout=0):
                torch.set_num_threads(1);torch.use_deterministic_algorithms(True)
                torch.backends.cuda.matmul.allow_tf32=False;torch.backends.cudnn.allow_tf32=False
                run_one(permit,'B2_'+args.condition)


if __name__=='__main__':main()
