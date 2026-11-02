"""Conditional one-laptop B2 campaign. GPU runs belong to the researcher."""
import argparse
import json
import os
import numpy as np
import pandas as pd
from pathlib import Path
from models.b2_runtime import CAMPAIGN,SCREEN,ANCHORS,authority,bind_manifest,configure_gpu,screen_path,fit,require_screen,screen_artifact_hashes
from evaluation.b2_campaign_plan import CORE,OPTIONAL,SEEDS,job_plan,dm_family
from evaluation.baselines import validation_rows
from models.screen_cpu import write_json


def reuse_path(condition,seed,origin):
    if seed!=11 or origin not in ANCHORS:return None
    if condition in ('learned','identity'):return screen_path(condition,origin)
    if condition in ('real','no_graph'):
        from models.b2_screen import path_for
        return path_for(3,origin,condition,100)
    return None


def fit_path(condition,seed,origin):
    return reuse_path(condition,seed,origin) or CAMPAIGN/condition/f'seed{seed}_{origin}'


def conditions(decision):return CORE+(OPTIONAL if decision['include_learned_and_identity'] else ())


def run(condition):
    os.environ['CUBLAS_WORKSPACE_CONFIG']=':4096:8'
    import torch
    from filelock import FileLock
    from features.panel import load_panel
    from features.b2 import area_scale,B2Windows
    from models.b2_adaptive import make_model
    cfg,info=authority(); decision=require_screen(); order=conditions(decision)
    if condition not in order:raise RuntimeError('Condition excluded by predeclared screen rule')
    if json.loads((SCREEN/'manifest.json').read_text())!=info:raise RuntimeError('Screen provenance changed')
    for previous in order[:order.index(condition)]:
        if not (CAMPAIGN/previous/'condition_complete.json').exists():raise RuntimeError(f'Finish {previous} first')
    info={**info,'screen_decision':decision,'screen_artifacts':screen_artifact_hashes()}
    with FileLock('data/processed/t03_gnn/gpu_fit.lock',timeout=0):
        configure_gpu(info); bind_manifest(CAMPAIGN,info)
        root=CAMPAIGN/condition; root.mkdir(exist_ok=True)
        if (root/'condition_complete.json').exists():
            print(json.dumps({'event':'already_complete','condition':condition})); return
        rows=validation_rows(cfg); panel=load_panel(through=rows.last_target.max())
        buffers={s:np.zeros((len(rows),int(panel.observed.sum()),12),np.float32) for s in SEEDS}; records=[]
        for origin in rows.fit_origin.drop_duplicates():
            for seed in SEEDS:
                path=fit_path(condition,seed,origin); reuse=reuse_path(condition,seed,origin) is not None
                if reuse:
                    scale=area_scale(panel.through(origin),origin)
                    model=make_model(panel.through(origin),condition,seed,scale).cuda()
                    saved=torch.load(path/'checkpoint.pt',map_location='cpu',weights_only=False)
                    if saved['completed_epochs']!=100 or saved['total_epochs']!=100:raise RuntimeError('Reusable fit is not 100 epochs')
                    model.load_state_dict(saved['model'],strict=True)
                    record=json.loads((path/'complete.json').read_text())
                else:model,scale,record=fit(cfg,path,condition,seed,origin,info)
                windows=B2Windows(panel,cfg,scale); model.eval()
                with torch.no_grad():
                    for index in np.flatnonzero(rows.fit_origin.eq(origin).to_numpy()):
                        inputs=windows.at(rows.origin.iloc[index])[None]
                        if condition=='without_base':inputs=inputs[:,:,:,[0,2,3,4,5]]
                        buffers[seed][index]=model(torch.from_numpy(inputs).cuda())[0,panel.observed].cpu().numpy()
                records.append({**record,'condition':condition,'seed':seed,'fit_origin':origin,'reused_screen':reuse,'checkpoint':str(path/'checkpoint.pt')})
                pd.DataFrame(records).to_csv(root/'fit_records.csv',index=False)
                del model; torch.cuda.empty_cache()
        for seed,prediction in buffers.items():
            if not np.isfinite(prediction).all() or (prediction<0).any():raise RuntimeError('Invalid B2 forecast')
            np.savez_compressed(root/f'predictions_seed{seed}.npz',prediction=prediction,codes=panel.codes[panel.observed],origins=rows.origin.to_numpy(dtype='U7'))
        write_json(root/'condition_complete.json',{'condition':condition,'fits':36,'seeds':list(SEEDS),'epochs':100,
            'reused':sum(r['reused_screen'] for r in records),'validation_origins':36,'last_target':str(rows.last_target.max()),
            'test_forecasts_or_losses':0,'recorded_fit_hours':sum(r['fit_seconds'] for r in records)/3600,
            'new_fit_hours':sum(r['fit_seconds'] for r in records if not r['reused_screen'])/3600})
        print(json.dumps({'event':'B2_condition_complete','condition':condition,'fits':36}),flush=True)


def main():
    parser=argparse.ArgumentParser(__doc__); parser.add_argument('--condition',choices=CORE+OPTIONAL); parser.add_argument('--plan',action='store_true'); args=parser.parse_args()
    if args.condition:run(args.condition)
    else:
        from evaluation.frozen import frozen_protocol
        cfg,_=frozen_protocol('protocol-v2')
        decision=require_screen()
        jobs=job_plan(cfg,decision['include_learned_and_identity'])
        print(json.dumps({'decision':decision,'fits':len(jobs),'new_fits':int(jobs.new_fit.sum()),
            'order':conditions(decision),'dm_family_size':len(dm_family(decision['main'],decision['include_learned_and_identity'])),'machine_count':1,'gpu_use':False},indent=2))


if __name__=='__main__':main()
