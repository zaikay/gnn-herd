"""Authorised fixed-configuration B campaign; GPU execution is researcher-only."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import numpy as np
import pandas as pd
from evaluation.frozen import frozen_protocol
from evaluation.baselines import validation_rows
from features.panel import load_panel
from features.gnn import GNNWindows
from models.screen_cpu import write_json,ANCHORS

ROOT=Path('data/processed/t03_b_validation')
NOTE=Path('reports/protocol/protocol_v4_b_validation.md')
TAG='protocol-v4-b-validation'
ORDER=('real','shuffled','no_graph','without_base')
SEEDS=(11,29,47)
ALIASES={'real':'gnn_real','shuffled':'gnn_shuffled','no_graph':'gnn_no_graph','without_base':'gnn_no_base'}


def channels(condition):return [0,2,3,4,5] if condition=='without_base' else None


def reused_fit(condition,seed,origin):
    if condition in ('real','no_graph') and seed==11 and origin in ANCHORS:
        from models.architecture_screen import output
        return output('B',origin,condition)
    return None


def fit_path(condition,seed,origin):
    old=reused_fit(condition,seed,origin)
    return old if old is not None else ROOT/condition/f'seed{seed}_{origin}'


def graph_edges(panel,condition,seed):
    if condition!='shuffled':return panel.edges
    with np.load(f'data/processed/t03_graphs/shuffled_seed{seed}.npz',allow_pickle=False) as data:
        return data['edges'].copy()


def make_model(panel,condition,seed):
    from models.screen_architectures import ScreenNetwork
    return ScreenNetwork('B',graph_edges(panel,condition,seed),panel.observed,64,
                         condition!='no_graph',channels=5 if condition=='without_base' else 6)


def authority(require_tag=False):
    cfg,signature=frozen_protocol('protocol-v2')
    from models.gnn_validation import verify_inputs
    verify_inputs(cfg)
    if require_tag:
        tagged=subprocess.run(['git','show',f'{TAG}:{NOTE.as_posix()}'],capture_output=True,check=True)
        if tagged.stdout.decode('utf-8').replace('\r\n','\n')!=NOTE.read_text(encoding='utf-8').replace('\r\n','\n'):
            raise RuntimeError('Working B note differs from its tag')
    sources=['src/models/b_validation.py','src/models/screen_architectures.py','src/models/gnn_checkpoint.py',
             'src/models/core_gnn.py','src/features/gnn.py','src/features/panel.py','src/evaluation/protocol.py',
             'src/evaluation/b_gate_c.py','src/evaluation/gate_c_metrics.py','src/evaluation/gate_c_io.py',
             'src/evaluation/dm.py','src/evaluation/baselines.py']
    graphs={f'data/processed/t03_graphs/shuffled_seed{s}.npz':None for s in SEEDS}
    from models.architecture_screen import fingerprint,ROOT as SCREEN
    _,screen_expected=fingerprint(); screen_saved=json.loads((SCREEN/'gpu_manifest.json').read_text())
    if any(screen_saved[k]!=v for k,v in screen_expected.items()):raise RuntimeError('Screen reuse provenance changed')
    reused={}
    for condition in ('real','no_graph'):
        for anchor in ANCHORS:
            path=reused_fit(condition,11,anchor)
            record=json.loads((path/'complete.json').read_text())
            if record['candidate']!='B' or record['epochs']!=65 or record['training_samples'] not in (115,127):raise RuntimeError('Ineligible screen fit')
            reused[(path/'checkpoint.pt').as_posix()]=hashlib.sha256((path/'checkpoint.pt').read_bytes()).hexdigest()
    info={'v2_sha256':signature,'note_sha256':hashlib.sha256(NOTE.read_bytes()).hexdigest(),
          'sources':{p:hashlib.sha256(Path(p).read_bytes()).hexdigest() for p in sources},
          'panel_sha256':hashlib.sha256(Path('data/processed/t02_panel.npz').read_bytes()).hexdigest(),
          'graphs':{p:hashlib.sha256(Path(p).read_bytes()).hexdigest() for p in graphs},
          'reused_checkpoint_sha256':reused,'hardware':screen_saved['hardware'],
          'width':64,'learning_rate':.003,'weight_decay':.0001,'epochs':65,'seeds':list(SEEDS),
          'order':list(ORDER),'fits_per_condition':36,'new_fits':140,'dm_family_size':20}
    return cfg,info


def plan(cfg):
    origins=validation_rows(cfg).fit_origin.drop_duplicates()
    return [{'condition':c,'fits':len(origins)*3,
             'reused':sum(reused_fit(c,s,o) is not None for o in origins for s in SEEDS),
             'new':sum(reused_fit(c,s,o) is None for o in origins for s in SEEDS)} for c in ORDER]


def require_previous(condition):
    for previous in ORDER[:ORDER.index(condition)]:
        if not (ROOT/previous/'condition_complete.json').exists():raise RuntimeError(f'Finish {previous} first')


def run(condition):
    import torch
    from filelock import FileLock
    from models.gnn_fit import lock_machine
    from models.gnn_checkpoint import run_epochs,train_epoch
    cfg,info=authority(require_tag=True)
    require_previous(condition)
    ROOT.mkdir(parents=True,exist_ok=True)
    with FileLock('data/processed/t03_gnn/gpu_fit.lock',timeout=0):
        os.environ['CUBLAS_WORKSPACE_CONFIG']=':4096:8'
        hardware=lock_machine('data/processed/t03_gnn')
        if hardware!=info['hardware']:raise RuntimeError('Screen/full campaign machine mismatch')
        manifest=ROOT/'campaign_manifest.json'
        if manifest.exists() and json.loads(manifest.read_text())!=info:raise RuntimeError('B campaign fingerprints changed')
        write_json(manifest,info)
        root=ROOT/condition; root.mkdir(exist_ok=True)
        if (root/'condition_complete.json').exists():
            print(json.dumps({'event':'already_complete','condition':condition,'new_fits':0})); return
        torch.set_num_threads(1); torch.use_deterministic_algorithms(True)
        torch.backends.cuda.matmul.allow_tf32=False; torch.backends.cudnn.allow_tf32=False
        rows=validation_rows(cfg); panel=load_panel(through=rows.last_target.max())
        windows=GNNWindows(panel,cfg)
        buffers={s:np.zeros((len(rows),int(panel.observed.sum()),12),dtype=np.float32) for s in SEEDS}
        records=[]
        for origin in rows.fit_origin.drop_duplicates():
            truncated=panel.through(origin); training=GNNWindows(truncated,cfg)
            samples,targets,mask=training.training(origin)
            for seed in SEEDS:
                path=fit_path(condition,seed,origin); reuse=reused_fit(condition,seed,origin) is not None
                torch.manual_seed(seed); torch.cuda.manual_seed_all(seed)
                model=make_model(truncated,condition,seed).cuda()
                if reuse:
                    saved=torch.load(path/'checkpoint.pt',map_location='cpu',weights_only=False)
                    if saved['completed_epochs']!=65:raise RuntimeError('Incomplete reusable fit')
                    model.load_state_dict(saved['model'],strict=True)
                    complete=json.loads((path/'complete.json').read_text())
                else:
                    path.mkdir(parents=True,exist_ok=True)
                    if not (path/'complete.json').exists():
                        optimiser=torch.optim.Adam(model.parameters(),lr=.003,weight_decay=.0001)
                        torch.cuda.synchronize(); torch.cuda.reset_peak_memory_stats()
                        curves,seconds,peaks=run_epochs(model,optimiser,
                            lambda epoch:train_epoch(model,optimiser,training,samples,targets,mask,epoch,seed,2,torch.device('cuda'),channels(condition)),
                            65,path,torch.device('cuda'),interval=5,synchronise=torch.cuda.synchronize,
                            metrics=lambda:{'allocated':torch.cuda.max_memory_allocated(),'reserved':torch.cuda.max_memory_reserved()},
                            on_epoch=lambda e:print(json.dumps({'condition':condition,'seed':seed,'fit_origin':origin,**e}),flush=True))
                        complete={'condition':condition,'seed':seed,'fit_origin':origin,'epochs':65,'fit_seconds':seconds,
                            'peak_gpu_memory_bytes':peaks['allocated'],'peak_reserved_gpu_memory_bytes':peaks['reserved'],
                            'parameter_count':sum(p.numel() for p in model.parameters()),'training_loss':curves[-1]['training_poisson_loss']}
                        write_json(path/'complete.json',complete); del optimiser
                    else:
                        if not (path/'checkpoint.pt').exists():raise RuntimeError('Missing completed checkpoint')
                        saved=torch.load(path/'checkpoint.pt',map_location='cpu',weights_only=False)
                        if saved['completed_epochs']!=65:raise RuntimeError('Bad completed checkpoint')
                        model.load_state_dict(saved['model'],strict=True)
                        complete=json.loads((path/'complete.json').read_text())
                model.eval()
                indices=np.flatnonzero(rows.fit_origin.eq(origin).to_numpy())
                with torch.no_grad():
                    for index in indices:
                        inputs=windows.at(rows.origin.iloc[index])[None]
                        if channels(condition) is not None:inputs=inputs[:,:,:,channels(condition)]
                        buffers[seed][index]=model(torch.from_numpy(inputs).cuda())[0,panel.observed].cpu().numpy()
                records.append({**complete,'condition':condition,'seed':seed,'fit_origin':origin,'reused_screen':reuse,
                                'checkpoint':(path/'checkpoint.pt').as_posix()})
                pd.DataFrame(records).to_csv(root/'fit_records.csv',index=False)
                if reuse:write_json(root/f'reuse_seed{seed}_{origin}.json',{'checkpoint':(path/'checkpoint.pt').as_posix(),'reuse':True})
                del model; torch.cuda.empty_cache()
        for seed,prediction in buffers.items():
            if not np.isfinite(prediction).all() or (prediction<0).any():raise RuntimeError('Invalid B forecasts')
            np.savez_compressed(root/f'predictions_seed{seed}.npz',prediction=prediction,codes=panel.codes[panel.observed],origins=rows.origin.to_numpy(dtype='U7'))
        write_json(root/'condition_complete.json',{'condition':condition,'fits':36,'seeds':list(SEEDS),
            'reused':sum(r['reused_screen'] for r in records),'validation_origins':len(rows),'last_target':rows.last_target.max(),
            'test_forecasts_or_losses':0,'recorded_fit_hours':sum(r['fit_seconds'] for r in records)/3600,
            'new_fit_hours':sum(r['fit_seconds'] for r in records if not r['reused_screen'])/3600})
        print(json.dumps({'event':'B_condition_complete','condition':condition,'fits':36,'test_forecasts_or_losses':0}),flush=True)


def main():
    parser=argparse.ArgumentParser(__doc__); parser.add_argument('--condition',choices=ORDER); parser.add_argument('--plan',action='store_true'); args=parser.parse_args()
    cfg,_=frozen_protocol('protocol-v2')
    if args.plan:print(json.dumps({'plan':plan(cfg),'dm_family_size':20,'gpu_use':False},indent=2))
    elif args.condition:run(args.condition)
    else:parser.error('Choose --plan or --condition')


if __name__=='__main__':main()
