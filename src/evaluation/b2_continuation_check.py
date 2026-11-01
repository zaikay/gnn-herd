"""User-requested synthetic CPU proof: fresh B2 100 epochs equals 65+35."""
import hashlib
import json
from pathlib import Path
import random
import tempfile
import numpy as np
import torch
from models.b2 import B2Network
from models.b2_screen import continuation_snapshot
from models.gnn_checkpoint import run_epochs,train_epoch


def verify(directory):
    torch.set_num_threads(1); device=torch.device('cpu')
    rng=np.random.default_rng(11)
    inputs=rng.normal(size=(3,24,4,6)).astype(np.float32); inputs[:,:,3]=0
    targets=rng.poisson(3,size=(3,4,12)).astype(np.float32)
    mask=np.ones_like(targets,dtype=bool); mask[:,3]=False
    origins=np.array(['a','b','c'])
    class Windows:
        def at(self,origin):return inputs[list(origins).index(origin)].copy()
    windows=Windows(); observed=np.array([True,True,True,False])
    def setup(seed):
        random.seed(seed); np.random.seed(seed); torch.manual_seed(seed)
        model=B2Network(np.array([[0,1],[1,3]]),observed,32,np.array([2.,3.,1.,1.]))
        optimiser=torch.optim.Adam(model.parameters(),lr=.003,weight_decay=.0001)
        callback=lambda epoch:train_epoch(model,optimiser,windows,origins,targets,mask,epoch,11,2,device)
        return model,optimiser,callback
    directory=Path(directory)
    fresh,fresh_opt,callback=setup(11)
    complete,_,_=run_epochs(fresh,fresh_opt,callback,100,directory/'fresh',device)
    next_torch=torch.rand(3); next_numpy=np.random.rand(3); next_python=random.random()
    first,first_opt,callback=setup(11)
    run_epochs(first,first_opt,callback,65,directory/'first65',device)
    # Production performs deterministic prediction before a later continuation.
    with torch.no_grad():first(torch.from_numpy(inputs[:1]))
    source=directory/'first65/checkpoint.pt'; before=hashlib.sha256(source.read_bytes()).hexdigest()
    snapshot=torch.load(source,map_location='cpu',weights_only=False)
    continuation=directory/'continued'; continuation.mkdir()
    torch.save(continuation_snapshot(snapshot),continuation/'checkpoint.pt')
    resumed,resumed_opt,callback=setup(999)
    continued,_,_=run_epochs(resumed,resumed_opt,callback,100,continuation,device)
    for name,expected in fresh.state_dict().items():
        actual=resumed.state_dict()[name]
        if expected.is_sparse:expected,actual=expected.to_dense(),actual.to_dense()
        torch.testing.assert_close(expected,actual,rtol=0,atol=0)
    for parameter,items in fresh_opt.state_dict()['state'].items():
        for name,expected in items.items():torch.testing.assert_close(expected,resumed_opt.state_dict()['state'][parameter][name],rtol=0,atol=0)
    assert [r['training_poisson_loss'] for r in complete]==[r['training_poisson_loss'] for r in continued]
    torch.testing.assert_close(next_torch,torch.rand(3),rtol=0,atol=0)
    np.testing.assert_array_equal(next_numpy,np.random.rand(3)); assert next_python==random.random()
    assert hashlib.sha256(source.read_bytes()).hexdigest()==before
    return {'fresh_epochs':100,'source_epochs':65,'continued_epochs':35,'bit_exact_weights':True,
        'bit_exact_adam':True,'bit_exact_losses':True,'rng_restored':True,'source_checkpoint_unchanged':True,
        'constant_learning_rate':.003,'scheduler':None,'data_order':'seed11 + epoch, production train_epoch',
        'scope':'synthetic CPU only; same-device deterministic GPU continuation required, no cross-device claim',
        'study_fits':0,'gpu_use':False,'test_forecasts_or_losses':0}


def main():
    root=Path('logs'); root.mkdir(exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='b2_continue_',dir=root) as temporary:result=verify(temporary)
    result['source_sha256']={p:hashlib.sha256(Path(p).read_bytes()).hexdigest() for p in ('src/models/b2.py','src/models/b2_screen.py','src/models/gnn_checkpoint.py','src/features/b2.py')}
    Path('reports/experiments/t03_b2_continuation_check.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(result,indent=2))


if __name__=='__main__':main()
