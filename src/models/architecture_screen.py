"""Researcher-only, twelve-fit v3 architecture session with five-epoch recovery."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import numpy as np
import pandas as pd
from evaluation.frozen import frozen_protocol
from features.gnn import GNNWindows
from features.panel import load_panel
from models.screen_cpu import ROOT,ANCHORS,write_json

NOTE=Path('reports/protocol/protocol_v3_screen.md')


def jobs():return [(candidate,anchor,condition) for candidate in ('A','B','C') for anchor in ANCHORS for condition in ('real','no_graph')]


def output(candidate,anchor,condition):return ROOT/'gpu'/f'{candidate}_{condition}_seed11_{anchor}'


def load_base(panel):
    marker=ROOT/'c_base_complete.json'
    if not marker.exists():raise RuntimeError('Finish the CPU OOS base prerequisites before GPU screening')
    record=json.loads(marker.read_text())
    if hashlib.sha256((ROOT/'c_base_oos.npz').read_bytes()).hexdigest()!=record['prediction_sha256']:raise RuntimeError('Base forecasts changed')
    with np.load(ROOT/'c_base_oos.npz',allow_pickle=False) as data:
        np.testing.assert_array_equal(data['codes'],panel.codes[panel.observed])
        assert (data['fit_origins']<data['origins']).all()
        origins=data['origins'].copy()
        cube=np.zeros((len(origins),len(panel.codes),12),dtype=np.float32)
        cube[:,panel.observed]=data['prediction']
    if origins[0]!='2011-03' or origins[-1]!='2020-08':raise RuntimeError('C origin calendar differs from screen note')
    return origins,cube


def fingerprint():
    cfg,signature=frozen_protocol('protocol-v2')
    files=['src/models/architecture_screen.py','src/models/screen_architectures.py','src/models/screen_cpu.py',
           'src/models/gnn_checkpoint.py','src/models/core_gnn.py','src/features/gnn.py','src/features/panel.py',
           'src/evaluation/protocol.py','reports/protocol/protocol_v3_screen.md']
    return cfg,{'v2_sha256':signature,'source_sha256':{p:hashlib.sha256(Path(p).read_bytes()).hexdigest() for p in files},
                'cpu_manifest_sha256':hashlib.sha256((ROOT/'cpu_manifest.json').read_bytes()).hexdigest(),
                'c_base_sha256':hashlib.sha256((ROOT/'c_base_oos.npz').read_bytes()).hexdigest(),
                'panel_sha256':hashlib.sha256(Path('data/processed/t02_panel.npz').read_bytes()).hexdigest(),
                'seed':11,'width':64,'learning_rate':.003,'weight_decay':.0001,'epochs':65,'gpu_fits':12}


def train_epoch(model,optimiser,windows,origins,targets,mask,base,epoch,device):
    import torch
    from models.core_gnn import poisson_loss
    order=np.random.default_rng(11+epoch).permutation(len(origins))
    numerator=0.; cells=0
    for start in range(0,len(order),2):
        use=order[start:start+2]
        x=torch.from_numpy(np.stack([windows.at(origins[i]) for i in use])).to(device)
        y=torch.from_numpy(targets[use]).to(device); eligible=torch.from_numpy(mask[use]).to(device)
        b=None if base is None else torch.from_numpy(base[use]).to(device)
        optimiser.zero_grad(set_to_none=True)
        prediction=model(x,b)
        if not torch.isfinite(prediction).all():raise RuntimeError('Nonfinite screen rates; no silent clipping or objective change')
        loss=poisson_loss(prediction,y,eligible)
        if not torch.isfinite(loss):raise RuntimeError('Nonfinite screen loss')
        loss.backward(); optimiser.step()
        count=int(eligible.sum().item()); numerator+=loss.item()*count; cells+=count
    return {'training_poisson_loss':numerator/cells,'eligible_cells':cells}


def run():
    import subprocess
    import torch
    from filelock import FileLock
    from models.gnn_fit import lock_machine
    from models.gnn_checkpoint import run_epochs
    from models.screen_architectures import ScreenNetwork
    from models.screen_cpu import extra_jobs,full_jobs,choose_extras,folder
    # A dated approved note must be committed and tagged before the GPU session.
    tagged=subprocess.run(['git','show','protocol-v3-screen:reports/protocol/protocol_v3_screen.md'],capture_output=True,check=True)
    if tagged.stdout.decode('utf-8').replace('\r\n','\n')!=NOTE.read_text(encoding='utf-8').replace('\r\n','\n'):
        raise RuntimeError('Working screen note differs from protocol-v3-screen tag')
    cfg,signature=fingerprint()
    selection=choose_extras()
    if selection is None or not all((folder(j)/'complete.json').exists() for j in extra_jobs()+full_jobs(cfg,selection)):
        raise RuntimeError('Complete the eight extra CPU fits and any required updated baseline validation before GPU screening')
    with FileLock('data/processed/t03_gnn/gpu_fit.lock',timeout=0):
        os.environ['CUBLAS_WORKSPACE_CONFIG']=':4096:8'
        hardware=lock_machine('data/processed/t03_gnn')
        signature['hardware']=hardware
        manifest=ROOT/'gpu_manifest.json'
        if manifest.exists() and json.loads(manifest.read_text())!=signature:raise RuntimeError('Screen source/data/machine changed; no overwrite')
        write_json(manifest,signature)
        torch.set_num_threads(1); torch.use_deterministic_algorithms(True)
        torch.backends.cuda.matmul.allow_tf32=False; torch.backends.cudnn.allow_tf32=False
        for candidate,anchor,condition in jobs():
            destination=output(candidate,anchor,condition); destination.mkdir(parents=True,exist_ok=True)
            if (destination/'complete.json').exists():
                if not (destination/'checkpoint.pt').exists() or not (destination/'prediction.npz').exists():raise RuntimeError('Completed screen fit missing retained artifacts')
                continue
            panel=load_panel(through=anchor); windows=GNNWindows(panel,cfg)
            origins,targets,mask=windows.training(anchor)
            base=None; forecast_base=None
            if candidate=='C':
                base_origins,cube=load_base(panel)
                keep=origins>='2011-03'; origins=origins[keep]; targets=targets[keep]; mask=mask[keep]
                lookup={o:i for i,o in enumerate(base_origins)}
                base=cube[[lookup[o] for o in origins]]; forecast_base=cube[lookup[anchor]]
            torch.manual_seed(11); torch.cuda.manual_seed_all(11)
            model=ScreenNetwork(candidate,panel.edges,panel.observed,64,condition=='real').cuda()
            optimiser=torch.optim.Adam(model.parameters(),lr=.003,weight_decay=.0001)
            torch.cuda.synchronize(); torch.cuda.reset_peak_memory_stats()
            print(json.dumps({'event':'screen_fit_start','candidate':candidate,'anchor':anchor,'condition':condition,'samples':len(origins)}),flush=True)
            records,seconds,peaks=run_epochs(model,optimiser,
                lambda epoch:train_epoch(model,optimiser,windows,origins,targets,mask,base,epoch,torch.device('cuda')),
                65,destination,torch.device('cuda'),interval=5,synchronise=torch.cuda.synchronize,
                metrics=lambda:{'allocated':torch.cuda.max_memory_allocated(),'reserved':torch.cuda.max_memory_reserved()},
                on_epoch=lambda event:print(json.dumps({'candidate':candidate,'anchor':anchor,'condition':condition,**event}),flush=True))
            with torch.no_grad():
                x=torch.from_numpy(windows.at(anchor)[None]).cuda()
                b=None if forecast_base is None else torch.from_numpy(forecast_base[None]).cuda()
                prediction=model(x,b)[0,panel.observed].cpu().numpy()
            if not np.isfinite(prediction).all() or (prediction<0).any():raise RuntimeError('Invalid screen prediction')
            np.savez_compressed(destination/'prediction.npz',prediction=prediction,codes=panel.codes[panel.observed],origin=anchor)
            write_json(destination/'complete.json',{'candidate':candidate,'anchor':anchor,'condition':condition,
                'epochs':len(records),'parameter_count':sum(p.numel() for p in model.parameters()),'fit_seconds':seconds,
                'peak_gpu_memory_bytes':peaks['allocated'],'peak_reserved_gpu_memory_bytes':peaks['reserved'],
                'training_loss':records[-1]['training_poisson_loss'],'training_samples':len(origins),'test_forecasts_or_losses':0})
            del model,optimiser; torch.cuda.empty_cache()
        write_json(ROOT/'screen_complete.json',{'gpu_fits':12,'seed':11,'test_forecasts_or_losses':0})
    from evaluation.screen_report import report
    report()


def main():
    parser=argparse.ArgumentParser(__doc__); parser.add_argument('--run',action='store_true'); args=parser.parse_args()
    if args.run:run()
    else:print(json.dumps({'gpu_fits':len(jobs()),'jobs':jobs(),'c_base_ready':(ROOT/'c_base_complete.json').exists(),'gpu_use':False}))


if __name__=='__main__':main()
