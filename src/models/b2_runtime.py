"""Shared v6 provenance and researcher-only resumable B2 fit implementation."""
import hashlib
import json
from pathlib import Path
import subprocess
import numpy as np
from features.panel import load_panel
from features.b2 import area_scale,B2Windows
from models.screen_cpu import write_json

NOTE=Path('reports/protocol/protocol_v6_b2_graph_and_campaign.md')
TAG='protocol-v6-b2-graph-campaign'
SCREEN=Path('data/processed/t03_b2_graph_screen')
CAMPAIGN=Path('data/processed/t03_b2_validation')
ANCHORS=('2019-08','2020-08')
SOURCES=('src/models/b2_adaptive.py','src/models/b2_runtime.py','src/models/b2_graph_screen.py',
         'src/models/b2_validation.py','src/evaluation/b2_graph_screen_report.py','src/evaluation/b2_gate_c.py',
         'src/evaluation/b2_campaign_plan.py','src/models/b2.py','src/features/b2.py',
         'src/models/gnn_checkpoint.py','src/features/gnn.py','src/features/panel.py','src/models/screen_architectures.py',
         'src/evaluation/gate_c_metrics.py','src/evaluation/gate_c_io.py','src/evaluation/dm.py','src/evaluation/baselines.py')


def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def authority(require_tag=True):
    from evaluation.frozen import frozen_protocol
    from models.gnn_validation import verify_inputs
    cfg,v2=frozen_protocol('protocol-v2'); verify_inputs(cfg)
    if require_tag:
        result=subprocess.run(['git','show',f'{TAG}:{NOTE.as_posix()}'],capture_output=True,text=True)
        if result.returncode:raise RuntimeError(f'Commit the v6 note and create {TAG} before GPU runs; see STATUS.md')
        if result.stdout.replace('\r\n','\n')!=NOTE.read_text(encoding='utf-8').replace('\r\n','\n'):raise RuntimeError('V6 note differs from tag')
    old=json.loads(Path('data/processed/t03_b2_screen/manifest.json').read_text())
    if any(sha(p)!=h for p,h in old['sources'].items()):raise RuntimeError('Frozen B2 screen sources changed')
    if sha('data/processed/t02_panel.npz')!=old['panel_sha256']:raise RuntimeError('Panel changed')
    selection=json.loads(Path('data/processed/t03_b2_screen/selection.json').read_text())
    epoch=json.loads(Path('data/processed/t03_b2_screen/epoch_decision.json').read_text())
    if selection['config_id']!=3 or epoch['selected_epochs']!=100 or epoch['pending_100']:raise RuntimeError('Accepted B2 configuration/epochs differ')
    reuse={}
    for condition in ('real','no_graph'):
        for anchor in ANCHORS:
            from models.b2_screen import path_for
            path=path_for(3,anchor,condition,100)
            record=json.loads((path/'complete.json').read_text())
            if record['epochs']!=100 or record['config_id']!=3 or record['condition']!=condition or record['anchor']!=anchor:raise RuntimeError('Invalid B2 reuse')
            for filename in ('checkpoint.pt','prediction.npz','complete.json'):reuse[(path/filename).as_posix()]=sha(path/filename)
    info={'v2_sha256':v2,'note_sha256':sha(NOTE),'sources':{p:sha(p) for p in SOURCES},
          'panel_sha256':old['panel_sha256'],'hardware':old['hardware'],'reuse':reuse,
          'graphs':{str(p):sha(p) for p in sorted(Path('data/processed/t03_graphs').glob('shuffled_seed*.npz'))},
          'configuration_id':3,'width':64,'rate':.003,'decay':.0001,'epochs':100,'machine_count':1}
    return cfg,info


def bind_manifest(root,info):
    root.mkdir(parents=True,exist_ok=True); path=root/'manifest.json'
    if path.exists() and json.loads(path.read_text())!=info:raise RuntimeError(f'Provenance changed: {root}')
    write_json(path,info)


def screen_path(condition,anchor):return SCREEN/f'{condition}_seed11_{anchor}_e100'


def fit(cfg,path,condition,seed,origin,info):
    # Invoked exclusively by researcher GPU commands under the shared GPU lock.
    import torch
    from models.b2_adaptive import make_model
    from models.gnn_checkpoint import run_epochs,train_epoch
    panel=load_panel(through=origin); scale=area_scale(panel,origin)
    training=B2Windows(panel,cfg,scale); samples,targets,mask=training.training(origin)
    torch.manual_seed(seed); torch.cuda.manual_seed_all(seed)
    model=make_model(panel,condition,seed,scale).cuda()
    path.mkdir(parents=True,exist_ok=True)
    if (path/'complete.json').exists():
        saved=torch.load(path/'checkpoint.pt',map_location='cpu',weights_only=False)
        if saved['completed_epochs']!=100 or saved['total_epochs']!=100:raise RuntimeError('Invalid completed checkpoint')
        model.load_state_dict(saved['model'],strict=True)
        result=json.loads((path/'complete.json').read_text())
        if result['condition']!=condition or result['seed']!=seed or result['fit_origin']!=origin or result['epochs']!=100:raise RuntimeError('Fit identity mismatch')
    else:
        optimiser=torch.optim.Adam(model.parameters(),lr=.003,weight_decay=.0001)
        channels=[0,2,3,4,5] if condition=='without_base' else None
        torch.cuda.synchronize(); torch.cuda.reset_peak_memory_stats()
        records,seconds,peaks=run_epochs(model,optimiser,
            lambda epoch:train_epoch(model,optimiser,training,samples,targets,mask,epoch,seed,2,torch.device('cuda'),channels),
            100,path,torch.device('cuda'),interval=5,synchronise=torch.cuda.synchronize,
            metrics=lambda:{'allocated':torch.cuda.max_memory_allocated(),'reserved':torch.cuda.max_memory_reserved()},
            on_epoch=lambda e:print(json.dumps({'condition':condition,'seed':seed,'fit_origin':origin,**e}),flush=True))
        result={'condition':condition,'seed':seed,'fit_origin':origin,'epochs':100,'configuration_id':3,
                'fit_seconds':seconds,'peak_gpu_memory_bytes':peaks['allocated'],'peak_reserved_gpu_memory_bytes':peaks['reserved'],
                'parameter_count':sum(p.numel() for p in model.parameters()),'training_loss':records[-1]['training_poisson_loss'],
                'test_forecasts_or_losses':0}
        write_json(path/'complete.json',result)
        del optimiser
    model.eval()
    return model,scale,result


def configure_gpu(info):
    import torch
    from models.gnn_fit import lock_machine
    if lock_machine('data/processed/t03_gnn')!=info['hardware']:raise RuntimeError('Use the original laptop/software for every seed and condition')
    torch.set_num_threads(1); torch.use_deterministic_algorithms(True)
    torch.backends.cuda.matmul.allow_tf32=False; torch.backends.cudnn.allow_tf32=False


def require_screen():
    # Refuse campaign access until four new screen fits and the saved comparisons exist.
    for condition in ('learned','identity'):
        for anchor in ANCHORS:
            path=screen_path(condition,anchor)
            for name in ('complete.json','checkpoint.pt','prediction.npz'):
                if not (path/name).exists():raise RuntimeError('Complete the four-fit learned/identity screen first')
    decision_path=SCREEN/'decision.json'
    if not decision_path.exists():raise RuntimeError('Generate and review the graph screen report first')
    from evaluation.b2_graph_screen_report import compute_decision
    decision=compute_decision()
    if decision!=json.loads(decision_path.read_text()):raise RuntimeError('Screen decision no longer matches forecasts')
    if decision['requires_researcher_review']:raise RuntimeError('Identity improves real by at least 2%; STOP for researcher review')
    return decision


def screen_artifact_hashes():
    return {str(path/name):sha(path/name) for condition in ('learned','identity') for anchor in ANCHORS
            for path in (screen_path(condition,anchor),) for name in ('checkpoint.pt','prediction.npz','complete.json','training_curve.csv')}
