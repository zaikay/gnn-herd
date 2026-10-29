"""Shared CPU/GPU epoch loop, five-epoch recovery and session timing journal."""
import json
from datetime import datetime, timezone
from pathlib import Path
import random
import time
import uuid

import numpy as np
import pandas as pd
import torch

from models.core_gnn import poisson_loss


def train_epoch(model,optimiser,windows,origins,targets,mask,epoch,seed,batch_size,device,channels=None):
    numerator = 0.0; cells = 0
    order = np.random.default_rng(seed+epoch).permutation(len(origins))
    for start in range(0,len(order),batch_size):
        use = order[start:start+batch_size]
        inputs = np.stack([windows.at(origins[i]) for i in use])
        if channels is not None:
            inputs = inputs[:,:,:,channels]
        x = torch.from_numpy(inputs).to(device)
        y = torch.from_numpy(targets[use]).to(device)
        eligible = torch.from_numpy(mask[use]).to(device)
        optimiser.zero_grad(set_to_none=True)
        loss = poisson_loss(model(x),y,eligible)
        if not torch.isfinite(loss):
            raise RuntimeError('Nonfinite training loss; stop without changing protocol settings')
        loss.backward(); optimiser.step()
        count = int(eligible.sum().item()); numerator += loss.item()*count; cells += count
    return {'training_poisson_loss':numerator/cells,'eligible_cells':cells}


def journal_event(output,event):
    event = {**event,'recorded_at':datetime.now(timezone.utc).isoformat()}
    with (Path(output)/'sessions.jsonl').open('a',encoding='utf-8') as stream:
        stream.write(json.dumps(event)+'\n')


def measured_seconds(output):
    """Sum the latest elapsed observation per attempt, including replay work."""
    path = Path(output)/'sessions.jsonl'
    if not path.exists():
        return 0.0
    attempts = {}
    lines = path.read_text(encoding='utf-8').splitlines()
    for i,line in enumerate(lines):
        try:
            row = json.loads(line)
        except json.JSONDecodeError:
            if i==len(lines)-1:
                break  # interrupted final write; last recorded epoch is a lower bound
            raise
        attempts[row['session_id']] = max(attempts.get(row['session_id'],0),row.get('attempt_seconds',0))
    return sum(attempts.values())


def run_epochs(model,optimiser,one_epoch,total_epochs,output,device,interval=5,
               stop_after_epoch=None,synchronise=lambda:None,metrics=lambda:{},on_epoch=None):
    """The synthetic CPU resume test calls this exact production engine."""
    output = Path(output); output.mkdir(parents=True,exist_ok=True)
    checkpoint = output/'checkpoint.pt'
    records = []; first_epoch = 0; prior_metrics = {}
    if checkpoint.exists():
        saved = torch.load(checkpoint,map_location='cpu',weights_only=False)
        model.load_state_dict(saved['model']); optimiser.load_state_dict(saved['optimiser'])
        first_epoch,records = saved['completed_epochs'],saved['epoch_records']
        if saved['total_epochs']!=total_epochs:
            raise RuntimeError('Checkpoint epoch cap differs from fixed protocol')
        random.setstate(saved['python_rng']); np.random.set_state(saved['numpy_rng'])
        torch.set_rng_state(saved['cpu_rng'])
        if device.type=='cuda':
            torch.cuda.set_rng_state_all(saved['cuda_rng'])
        prior_metrics = saved.get('metrics',{})
    session_id = uuid.uuid4().hex
    started = time.perf_counter(); checkpoint_epoch = first_epoch
    journal_event(output,{'event':'attempt_start','session_id':session_id,'attempt_seconds':0,'checkpoint_epoch':first_epoch})
    try:
        for epoch in range(first_epoch,total_epochs):
            epoch_start = time.perf_counter()
            result = one_epoch(epoch)
            synchronise()
            records.append({'epoch':epoch+1,**result,'epoch_seconds':time.perf_counter()-epoch_start})
            pd.DataFrame(records).to_csv(output/'training_curve.csv',index=False)
            if (epoch+1)%interval==0 or epoch+1==total_epochs:
                snapshot_metrics = {key:max(prior_metrics.get(key,0),value) for key,value in metrics().items()}
                temporary = output/'checkpoint.tmp'
                torch.save({'schema_version':2,'model':model.state_dict(),'optimiser':optimiser.state_dict(),
                    'completed_epochs':epoch+1,'total_epochs':total_epochs,'epoch_records':records.copy(),
                    'python_rng':random.getstate(),'numpy_rng':np.random.get_state(),'cpu_rng':torch.get_rng_state(),
                    'cuda_rng':torch.cuda.get_rng_state_all() if device.type=='cuda' else [],
                    'metrics':snapshot_metrics},temporary)
                temporary.replace(checkpoint); checkpoint_epoch = epoch+1
            event = {'event':'epoch_end','session_id':session_id,'attempt_seconds':time.perf_counter()-started,
                     'epoch':epoch+1,'checkpoint_epoch':checkpoint_epoch,**records[-1]}
            journal_event(output,event)
            if on_epoch is not None:
                on_epoch(event)
            if stop_after_epoch is not None and epoch+1==stop_after_epoch:
                raise KeyboardInterrupt('Synthetic/user session stop')
    finally:
        journal_event(output,{'event':'attempt_end','session_id':session_id,
            'attempt_seconds':time.perf_counter()-started,'checkpoint_epoch':checkpoint_epoch})
    combined_metrics = {key:max(prior_metrics.get(key,0),value) for key,value in metrics().items()}
    return records,measured_seconds(output),combined_metrics
