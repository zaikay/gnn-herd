"""Researcher-run GPU fitting and recovery; never invoked by agent checks."""
import hashlib
import json
import os
from pathlib import Path
import platform
import subprocess
import time

import numpy as np
import pandas as pd
import torch
from filelock import FileLock

from features.gnn import GNNWindows
from models.core_gnn import CoreGNN, graph_operator, poisson_loss


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
    """Checkpoint every epoch/fit; reject changed fingerprints; no scoring."""
    if purpose not in {'pilot','approved_validation'}:
        raise ValueError('Sealed final-test fits are not implemented')
    if condition not in cfg['gnn_design']['graph_conditions']:
        raise ValueError('Optional/unapproved graph condition is disabled')
    if condition=='within_state_shuffled' and edges is None:
        raise ValueError('Shuffled condition requires its audited seed-specific graph')
    if (width not in cfg['tuning']['gnn_grid']['hidden_size'] or
            learning_rate not in cfg['tuning']['gnn_grid']['learning_rate'] or
            weight_decay not in cfg['tuning']['gnn_grid']['weight_decay']):
        raise ValueError('Fit settings differ from frozen grid')
    os.environ['CUBLAS_WORKSPACE_CONFIG'] = ':4096:8'
    hardware = lock_machine('data/processed/t03_gnn')
    source_files = ['src/models/core_gnn.py','src/models/gnn_fit.py','src/models/gnn_pilot.py',
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
        if purpose=='pilot' and (output/'checkpoint.pt').exists():
            (output/'checkpoint.pt').unlink()
        return json.loads((output/'complete.json').read_text())
    torch.manual_seed(seed); torch.cuda.manual_seed_all(seed)
    torch.use_deterministic_algorithms(True)
    torch.backends.cuda.matmul.allow_tf32 = False
    torch.backends.cudnn.allow_tf32 = False
    windows = GNNWindows(panel,cfg)
    origins,targets,mask = windows.training(panel.months[-1])
    model = CoreGNN(graph_operator(panel.edges if edges is None else edges,panel.observed,condition),panel.observed,width).cuda()
    optimiser = torch.optim.Adam(model.parameters(),lr=learning_rate,weight_decay=weight_decay)
    checkpoint = output/'checkpoint.pt'
    first_epoch = 0; records = []; previous_seconds = 0.0; previous_peak = 0; previous_reserved = 0
    if checkpoint.exists():
        saved = torch.load(checkpoint,map_location='cpu',weights_only=False)
        model.load_state_dict(saved['model']); optimiser.load_state_dict(saved['optimiser'])
        first_epoch,records = saved['completed_epochs'],saved['epoch_records']
        previous_seconds = saved['wall_seconds']; previous_peak = saved['peak_gpu_memory_bytes']
        previous_reserved = saved.get('peak_reserved_gpu_memory_bytes',0)
    torch.cuda.synchronize(); torch.cuda.reset_peak_memory_stats(); started = time.perf_counter()
    for epoch in range(first_epoch,cfg['tuning']['max_gnn_epochs']):
        epoch_start = time.perf_counter(); numerator = 0.0; cells = 0
        order = np.random.default_rng(seed+epoch).permutation(len(origins))
        for start in range(0,len(order),cfg['tuning']['full_graph_batch_origins']):
            use = order[start:start+cfg['tuning']['full_graph_batch_origins']]
            x = torch.from_numpy(np.stack([windows.at(origins[i]) for i in use])).cuda()
            y = torch.from_numpy(targets[use]).cuda(); eligible = torch.from_numpy(mask[use]).cuda()
            optimiser.zero_grad(set_to_none=True)
            loss = poisson_loss(model(x),y,eligible)
            if not torch.isfinite(loss):
                raise RuntimeError('Nonfinite training loss; no configuration/epoch/objective adjustment authorised')
            loss.backward(); optimiser.step()
            count = int(eligible.sum().item()); numerator += loss.item()*count; cells += count
        torch.cuda.synchronize()
        records.append({'epoch':epoch+1,'training_poisson_loss':numerator/cells,
                        'eligible_cells':cells,'epoch_seconds':time.perf_counter()-epoch_start})
        elapsed = previous_seconds+time.perf_counter()-started
        peak = max(previous_peak,torch.cuda.max_memory_allocated())
        temporary = output/'checkpoint.tmp'
        torch.save({'model':model.state_dict(),'optimiser':optimiser.state_dict(),'completed_epochs':epoch+1,
                    'epoch_records':records,'wall_seconds':elapsed,'peak_gpu_memory_bytes':peak,
                    'peak_reserved_gpu_memory_bytes':max(previous_reserved,torch.cuda.max_memory_reserved())},temporary)
        temporary.replace(checkpoint)
        pd.DataFrame(records).to_csv(output/'training_curve.csv',index=False)
        print(json.dumps({'width':width,**records[-1]}),flush=True)
    torch.cuda.synchronize()
    result = {'condition':condition,'purpose':purpose,'seed':seed,'hidden_size':width,
        'fit_origin':str(panel.months[-1]),'epochs':len(records),
        'wall_seconds':previous_seconds+time.perf_counter()-started,
        'mean_epoch_seconds':float(np.mean([r['epoch_seconds'] for r in records])),
        'peak_gpu_memory_bytes':max(previous_peak,torch.cuda.max_memory_allocated()),
        'peak_reserved_gpu_memory_bytes':max(previous_reserved,torch.cuda.max_memory_reserved()),
        'parameter_count':sum(p.numel() for p in model.parameters()),'validation_or_test_scoring':False}
    completion_tmp = output/'complete.tmp'
    completion_tmp.write_text(json.dumps(result,indent=2),encoding='utf-8')
    completion_tmp.replace(output/'complete.json')
    # Pilot weights cannot be used for tuning or later forecasts. Completed
    # measurement records/curves are retained; partial fits remain resumable.
    if purpose=='pilot':
        checkpoint.unlink()
    return result
