"""Researcher-run GPU fitting and recovery; never invoked by agent checks."""
import hashlib
import json
import os
from pathlib import Path
import platform
import subprocess

import numpy as np
import torch
from filelock import FileLock

from features.gnn import GNNWindows
from models.core_gnn import CoreGNN, graph_operator
from models.gnn_checkpoint import run_epochs, train_epoch


def lock_machine(root):
    if platform.system()!='Windows' or not torch.cuda.is_available():
        raise RuntimeError('All GNN fits require the approved Windows RTX 4070 laptop with CUDA')
    if torch.__version__!='2.7.1+cu128':
        raise RuntimeError('Install the pinned torch 2.7.1+cu128 dependency')
    device = torch.cuda.get_device_properties(0)
    if '4070 Laptop' not in device.name or not 7*1024**3<device.total_memory<9*1024**3:
        raise RuntimeError('GPU does not match the approved RTX 4070 Laptop 8 GB')
    inventory = subprocess.run(['nvidia-smi','--query-gpu=uuid,name,memory.total,driver_version',
                                '--format=csv,noheader'],capture_output=True,text=True,check=True).stdout.strip()
    hardware = {'computer':platform.node(),'os':platform.platform(),'gpu_inventory':inventory,
                'torch':torch.__version__,'cuda_runtime':torch.version.cuda,
                'gpu_name':device.name,'gpu_memory_bytes':device.total_memory,'declared_system_ram_gb':32}
    root = Path(root); root.mkdir(parents=True,exist_ok=True)
    destination = root/'machine.json'
    if destination.exists():
        if json.loads(destination.read_text()) != hardware:
            raise RuntimeError('Machine/software differs from the pilot: all conditions must use the same laptop and environment')
    else:
        destination.write_text(json.dumps(hardware,indent=2),encoding='utf-8')
    return hardware


def fit(*args,**kwargs):
    root = Path('data/processed/t03_gnn')
    root.mkdir(parents=True,exist_ok=True)
    # OS-backed lock releases on interruption; never overlap GPU fits, including
    # separate shell invocations of different graph conditions.
    with FileLock(root/'gpu_fit.lock',timeout=0):
        return _fit(*args,**kwargs)


def _fit(panel,cfg,protocol_sha256,condition,seed,width,learning_rate,weight_decay,
        output,purpose='pilot',edges=None):
    """Checkpoint every five epochs/fit; reject changed fingerprints; no scoring."""
    if purpose not in {'pilot','approved_validation'}:
        raise ValueError('Sealed final-test fits are not implemented')
    optional = cfg['gnn_design'].get('optional_condition',{})
    allowed = list(cfg['gnn_design']['graph_conditions'])
    if optional.get('enabled'):
        allowed.append(optional['name'])
    if condition not in allowed:
        raise ValueError('Optional/unapproved graph condition is disabled')
    if condition=='within_state_shuffled' and edges is None:
        raise ValueError('Shuffled condition requires its audited seed-specific graph')
    if (width not in cfg['tuning']['gnn_grid']['hidden_size'] or
            learning_rate not in cfg['tuning']['gnn_grid']['learning_rate'] or
            weight_decay not in cfg['tuning']['gnn_grid']['weight_decay']):
        raise ValueError('Fit settings differ from frozen grid')
    os.environ['CUBLAS_WORKSPACE_CONFIG'] = ':4096:8'
    hardware = lock_machine('data/processed/t03_gnn')
    source_files = ['src/models/core_gnn.py','src/models/gnn_fit.py','src/models/gnn_checkpoint.py',
                    'src/features/gnn.py','src/features/panel.py','src/evaluation/protocol.py',
                    'requirements-gnn.lock']
    signature = {'protocol_sha256':protocol_sha256,'condition':condition,'seed':seed,'width':width,
        'learning_rate':learning_rate,'weight_decay':weight_decay,'epochs':cfg['tuning']['max_gnn_epochs'],
        'fit_origin':str(panel.months[-1]),'purpose':purpose,'hardware':hardware,
        'python':platform.python_version(),'numpy':np.__version__,
        'sources':{name:hashlib.sha256(Path(name).read_bytes()).hexdigest() for name in source_files},
        'panel':hashlib.sha256(Path('data/processed/t02_panel.npz').read_bytes()).hexdigest(),
        'edge_hash':hashlib.sha256(np.asarray(panel.edges if edges is None else edges,dtype=np.int32).tobytes()).hexdigest()}
    output = Path(output); output.mkdir(parents=True,exist_ok=True)
    manifest = output/'manifest.json'
    if manifest.exists() and json.loads(manifest.read_text())!=signature:
        raise RuntimeError('Existing checkpoint fingerprint differs; refusing overwrite/reuse')
    manifest.write_text(json.dumps(signature,indent=2),encoding='utf-8')
    if (output/'complete.json').exists():
        if purpose=='approved_validation' and not (output/'checkpoint.pt').exists():
            raise RuntimeError('Completed fit has no retained checkpoint; stop for review, do not refit')
        return json.loads((output/'complete.json').read_text())
    torch.manual_seed(seed); torch.cuda.manual_seed_all(seed)
    torch.use_deterministic_algorithms(True)
    torch.backends.cuda.matmul.allow_tf32 = False
    torch.backends.cudnn.allow_tf32 = False
    windows = GNNWindows(panel,cfg)
    origins,targets,mask = windows.training(panel.months[-1])
    channels = [0,2,3,4,5] if condition=='real_without_installed_base' else None
    graph_condition = 'real' if channels is not None else condition
    model = CoreGNN(graph_operator(panel.edges if edges is None else edges,panel.observed,graph_condition),
                    panel.observed,width,input_channels=5 if channels is not None else 6).cuda()
    optimiser = torch.optim.Adam(model.parameters(),lr=learning_rate,weight_decay=weight_decay)
    device = torch.device('cuda')
    torch.cuda.synchronize(); torch.cuda.reset_peak_memory_stats()
    records,wall_seconds,peaks = run_epochs(model,optimiser,
        lambda epoch:train_epoch(model,optimiser,windows,origins,targets,mask,epoch,seed,
                                 cfg['tuning']['full_graph_batch_origins'],device,channels),
        cfg['tuning']['max_gnn_epochs'],output,device,
        interval=cfg['tuning'].get('checkpoints',{}).get('interval_epochs',5),
        synchronise=torch.cuda.synchronize,
        metrics=lambda:{'allocated':torch.cuda.max_memory_allocated(),'reserved':torch.cuda.max_memory_reserved()},
        on_epoch=lambda event:print(json.dumps({'width':width,**event}),flush=True))
    torch.cuda.synchronize()
    result = {'condition':condition,'purpose':purpose,'seed':seed,'hidden_size':width,
        'fit_origin':str(panel.months[-1]),'epochs':len(records),
        'wall_seconds':wall_seconds,
        'mean_epoch_seconds':float(np.mean([r['epoch_seconds'] for r in records])),
        'peak_gpu_memory_bytes':peaks['allocated'],
        'peak_reserved_gpu_memory_bytes':peaks['reserved'],
        'parameter_count':sum(p.numel() for p in model.parameters()),'validation_or_test_scoring':False}
    completion_tmp = output/'complete.tmp'
    completion_tmp.write_text(json.dumps(result,indent=2),encoding='utf-8')
    completion_tmp.replace(output/'complete.json')
    # Protocol v2 retains the completed checkpoint. Existing historical pilot
    # weights were already discarded under v1.1 and are not recreated.
    return result
