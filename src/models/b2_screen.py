"""Researcher-run B2 scaling grid screen, with separately retained extensions."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import numpy as np
import pandas as pd
from evaluation.frozen import frozen_protocol
from models.screen_cpu import ANCHORS,write_json
from features.panel import load_panel
from features.b2 import area_scale,B2Windows

ROOT=Path('data/processed/t03_b2_screen')
NOTE=Path('reports/protocol/protocol_v5_b2_screen.md')
TAG='protocol-v5-b2-screen'
CONTINUATION_EVIDENCE=Path('reports/experiments/t03_b2_continuation_check.json')


def grid(cfg):
    g=cfg['tuning']['gnn_grid']
    return [{'width':w,'rate':r,'decay':.0001} for w in g['hidden_size'] for r in g['learning_rate']]


def path_for(config_id,anchor,condition,epochs=65):return ROOT/f'c{config_id}_{condition}_seed11_{anchor}_e{epochs}'


def still_falling(curve):
    if curve.epoch.tolist()!=list(range(1,66)):raise ValueError('Complete 65-epoch curve required')
    losses=curve.training_poisson_loss.to_numpy()
    if not np.isfinite(losses).all():raise ValueError('Nonfinite curve')
    recent=float(losses[60:65].mean()); prior=float(losses[55:60].mean())
    decrease=float(losses[0]-recent)
    return {'trigger':bool(decrease>0 and prior-recent>.01*decrease),
            'recent5_loss':recent,'prior5_loss':prior,'last5_decrease':prior-recent,'total_decrease':decrease}


def select(scores):
    scores=np.asarray(scores,dtype=float)
    if scores.shape!=(2,6) or not np.isfinite(scores).all():raise ValueError('Two anchors x six finite configuration scores required')
    return int(np.argmin(scores.mean(axis=0)))


def continuation_snapshot(saved):
    if saved['completed_epochs']!=65 or saved['total_epochs']!=65:raise RuntimeError('Invalid continuation source')
    return {**saved,'total_epochs':100}


def continuation_allowed():
    try:
        proof=json.loads(CONTINUATION_EVIDENCE.read_text())
        flags=('bit_exact_weights','bit_exact_adam','bit_exact_losses','rng_restored','source_checkpoint_unchanged')
        return (all(proof.get(k) is True for k in flags) and proof.get('scheduler') is None
                and set(proof['source_sha256'])=={'src/models/b2.py','src/models/b2_screen.py','src/models/gnn_checkpoint.py','src/features/b2.py'}
                and all(Path(p).exists() and hashlib.sha256(Path(p).read_bytes()).hexdigest()==h for p,h in proof['source_sha256'].items()))
    except (OSError,KeyError,ValueError):return False


def choose_epochs(mae65,mae100=None):
    if not np.isfinite(mae65) or mae65<0:raise ValueError('Invalid 65-epoch MAE')
    if mae100 is None:return 65
    if not np.isfinite(mae100) or mae100<0:raise ValueError('Invalid 100-epoch MAE')
    return 100 if mae65>0 and mae100<=.995*mae65 else 65


def selected_real_mae(config_id,epochs):
    panel=load_panel(through='2021-08'); scores=[]
    for anchor in ANCHORS:
        truth=panel.targets[panel.observed,panel.index(anchor)+1:panel.index(anchor)+13].astype(float)
        with np.load(path_for(config_id,anchor,'real',epochs)/'prediction.npz',allow_pickle=False) as data:
            np.testing.assert_array_equal(data['codes'],panel.codes[panel.observed])
            scores.append(np.abs(data['prediction'].astype(float)-truth).mean())
    return float(np.mean(scores))


def write_epoch_decision(config_id,trigger):
    mae65=selected_real_mae(config_id,65)
    complete100=all((path_for(config_id,a,c,100)/'complete.json').exists() for a in ANCHORS for c in ('real','no_graph'))
    pending=bool(trigger and not complete100)
    mae100=selected_real_mae(config_id,100) if trigger and complete100 else None
    result={'selected_epochs':None if pending else choose_epochs(mae65,mae100),'pending_100':pending,
            'mae65':mae65,'mae100':mae100,'minimum_relative_improvement':.005,
            'applies_to':['real','no_graph','learned_graph','identity_control']}
    write_json(ROOT/'epoch_decision.json',result)
    return result


def authority():
    cfg,v2=frozen_protocol('protocol-v2')
    tagged=subprocess.run(['git','show',f'{TAG}:{NOTE.as_posix()}'],capture_output=True,check=True)
    if tagged.stdout.decode('utf-8').replace('\r\n','\n')!=NOTE.read_text(encoding='utf-8').replace('\r\n','\n'):raise RuntimeError('B2 screen note differs from tag')
    from models.b_validation import authority as b_authority
    _,base=b_authority()
    files=['src/models/b2_screen.py','src/models/b2.py','src/features/b2.py','src/features/gnn.py','src/models/screen_architectures.py','src/models/gnn_checkpoint.py']
    info={'v2_sha256':v2,'note_sha256':hashlib.sha256(NOTE.read_bytes()).hexdigest(),
          'sources':{p:hashlib.sha256(Path(p).read_bytes()).hexdigest() for p in files},
          'panel_sha256':base['panel_sha256'],'hardware':base['hardware'],'grid':grid(cfg),'seed':11}
    manifest=ROOT/'manifest.json'; ROOT.mkdir(parents=True,exist_ok=True)
    if manifest.exists() and json.loads(manifest.read_text())!=info:raise RuntimeError('B2 sources/data/hardware changed')
    write_json(manifest,info)
    return cfg,info


def fit_one(cfg,config_id,anchor,condition,epochs):
    import torch
    from models.b2 import B2Network
    from models.gnn_checkpoint import run_epochs,train_epoch
    destination=path_for(config_id,anchor,condition,epochs); destination.mkdir(parents=True,exist_ok=True)
    if (destination/'complete.json').exists():
        if not (destination/'checkpoint.pt').exists():raise RuntimeError('Missing retained B2 checkpoint')
        return json.loads((destination/'complete.json').read_text())
    panel=load_panel(through=anchor); scale=area_scale(panel,anchor)
    windows=B2Windows(panel,cfg,scale); samples,targets,mask=windows.training(anchor)
    conf=grid(cfg)[config_id]
    torch.manual_seed(11); torch.cuda.manual_seed_all(11)
    model=B2Network(panel.edges,panel.observed,conf['width'],scale,condition=='real').cuda()
    optimiser=torch.optim.Adam(model.parameters(),lr=conf['rate'],weight_decay=conf['decay'])
    base_seconds=0.
    mode='primary65'
    if epochs==100:
        original=path_for(config_id,anchor,condition,65)
        mode='continuation65' if ((destination/'continuation.json').exists() or
            (not (destination/'fresh100.json').exists() and continuation_allowed())) else 'fresh100'
        if mode=='continuation65':base_seconds=json.loads((original/'complete.json').read_text())['fit_seconds']
        if not (destination/'checkpoint.pt').exists():
            if mode=='continuation65':
                # Explicit authorised continuation; source checkpoint/65-epoch cap is unchanged.
                saved=torch.load(original/'checkpoint.pt',map_location='cpu',weights_only=False)
                write_json(destination/'continuation.json',{'source':str(original/'checkpoint.pt'),
                    'sha256':hashlib.sha256((original/'checkpoint.pt').read_bytes()).hexdigest(),'epoch':65,
                    'proof':str(CONTINUATION_EVIDENCE)})
                torch.save(continuation_snapshot(saved),destination/'checkpoint.pt')
            else:
                write_json(destination/'fresh100.json',{'reason':'Continuation proof unavailable or no longer matches; fresh deterministic 100 epochs'})
    torch.cuda.synchronize(); torch.cuda.reset_peak_memory_stats()
    records,seconds,peaks=run_epochs(model,optimiser,
        lambda epoch:train_epoch(model,optimiser,windows,samples,targets,mask,epoch,11,2,torch.device('cuda')),
        epochs,destination,torch.device('cuda'),interval=5,synchronise=torch.cuda.synchronize,
        metrics=lambda:{'allocated':torch.cuda.max_memory_allocated(),'reserved':torch.cuda.max_memory_reserved()},
        on_epoch=lambda e:print(json.dumps({'config_id':config_id,'anchor':anchor,'condition':condition,'cap':epochs,**e}),flush=True))
    with torch.no_grad():prediction=model(torch.from_numpy(windows.at(anchor)[None]).cuda())[0,panel.observed].cpu().numpy()
    if not np.isfinite(prediction).all() or (prediction<0).any():raise RuntimeError('Invalid B2 prediction')
    np.savez_compressed(destination/'prediction.npz',prediction=prediction,codes=panel.codes[panel.observed],origin=anchor,scale=scale)
    result={'config_id':config_id,'anchor':anchor,'condition':condition,'epochs':epochs,'mode':mode,**conf,
            'fit_seconds':seconds+base_seconds,'new_segment_seconds':seconds,'peak_gpu_memory_bytes':peaks['allocated'],
            'peak_reserved_gpu_memory_bytes':peaks['reserved'],'parameter_count':sum(p.numel() for p in model.parameters()),
            'training_loss':records[-1]['training_poisson_loss'],'scale_min':float(scale[panel.observed].min()),
            'scale_max':float(scale[panel.observed].max()),'test_forecasts_or_losses':0}
    write_json(destination/'complete.json',result)
    del model,optimiser; torch.cuda.empty_cache()
    return result


def run(extend=False):
    import torch
    from filelock import FileLock
    from models.gnn_fit import lock_machine
    os.environ['CUBLAS_WORKSPACE_CONFIG']=':4096:8'
    cfg,info=authority()
    with FileLock('data/processed/t03_gnn/gpu_fit.lock',timeout=0):
        if lock_machine('data/processed/t03_gnn')!=info['hardware']:raise RuntimeError('B2 must use same laptop/software')
        torch.set_num_threads(1); torch.use_deterministic_algorithms(True)
        torch.backends.cuda.matmul.allow_tf32=False; torch.backends.cudnn.allow_tf32=False
        if not extend:
            scores=np.zeros((2,6))
            # Validation targets are loaded only through the anchors' permitted twelve months.
            truth_panel=load_panel(through='2021-08')
            for t,anchor in enumerate(ANCHORS):
                truth=truth_panel.targets[truth_panel.observed,truth_panel.index(anchor)+1:truth_panel.index(anchor)+13].astype(float)
                for i in range(6):
                    fit_one(cfg,i,anchor,'real',65)
                    with np.load(path_for(i,anchor,'real')/'prediction.npz',allow_pickle=False) as data:scores[t,i]=np.abs(data['prediction'].astype(float)-truth).mean()
            chosen=select(scores)
            write_json(ROOT/'selection.json',{'config_id':chosen,'configuration':grid(cfg)[chosen],'anchor_scores':scores.tolist(),'criterion':'65-epoch real graph mean MAE, both anchors/horizons 1-12'})
            for anchor in ANCHORS:fit_one(cfg,chosen,anchor,'no_graph',65)
            checks=[still_falling(pd.read_csv(path_for(chosen,a,'real')/'training_curve.csv')) for a in ANCHORS]
            write_json(ROOT/'extension_decision.json',{'trigger':any(c['trigger'] for c in checks),'anchors':dict(zip(ANCHORS,checks))})
            trigger=any(c['trigger'] for c in checks)
            write_epoch_decision(chosen,trigger)
        else:
            chosen=json.loads((ROOT/'selection.json').read_text())['config_id']
            trigger=json.loads((ROOT/'extension_decision.json').read_text())['trigger']
            if trigger:
                for anchor in ANCHORS:
                    for condition in ('real','no_graph'):fit_one(cfg,chosen,anchor,condition,100)
            else:print('Training-only extension rule not triggered; no 100-epoch fits.',flush=True)
            write_epoch_decision(chosen,trigger)
    from evaluation.b2_screen_report import report
    report()


def main():
    parser=argparse.ArgumentParser(__doc__); parser.add_argument('--run',action='store_true'); parser.add_argument('--extend-if-needed',action='store_true'); args=parser.parse_args()
    if args.run or args.extend_if_needed:run(args.extend_if_needed)
    else:print(json.dumps({'real_grid_fits':12,'selected_no_graph_fits':2,'conditional_35_epoch_continuations':4,'gpu_use':False}))


if __name__=='__main__':main()
