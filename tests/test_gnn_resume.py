import numpy as np
import pandas as pd
import pytest
torch = pytest.importorskip('torch',reason='Pinned GNN dependencies are researcher-installed')

from evaluation.protocol import config
from features.gnn import GNNWindows
from features.panel import Panel
from models.core_gnn import CoreGNN, graph_operator
from models.gnn_checkpoint import run_epochs, train_epoch, measured_seconds


def test_stopped_cpu_fit_resumes_bit_exactly_including_adam(tmp_path):
    """User-authorised synthetic CPU fit test; same engine as production GPU fits."""
    old_threads = torch.get_num_threads()
    torch.set_num_threads(1)
    try:
        months = pd.period_range('2008-01','2011-02',freq='M').astype(str).to_numpy()
        counts = np.arange(len(months))%5+1
        panel = Panel(np.array(['0800','1000','2000']),months,
            np.stack([counts,np.full(len(months),np.nan),counts*2]).astype(np.float32),
            np.array([True,False,True]),np.array([[0,1],[0,2]]))
        windows = GNNWindows(panel,config())
        origins,targets,mask = windows.training('2011-02')
        device = torch.device('cpu')

        def setup(seed):
            torch.manual_seed(seed)
            model = CoreGNN(graph_operator(panel.edges,panel.observed),panel.observed,32)
            optimiser = torch.optim.Adam(model.parameters(),lr=.001,weight_decay=.0001)
            callback = lambda epoch:train_epoch(model,optimiser,windows,origins,targets,mask,epoch,11,2,device)
            return model,optimiser,callback

        full,full_opt,callback = setup(11)
        full_records,_,_ = run_epochs(full,full_opt,callback,10,tmp_path/'full',device)
        expected_rng = torch.rand(5)
        partial,partial_opt,callback = setup(11)
        with pytest.raises(KeyboardInterrupt):
            run_epochs(partial,partial_opt,callback,10,tmp_path/'resumed',device,stop_after_epoch=7)
        saved = torch.load(tmp_path/'resumed/checkpoint.pt',weights_only=False)
        assert saved['completed_epochs']==5  # epochs 6/7 are replayed, not silently reused
        resumed,resumed_opt,callback = setup(999)
        resumed_records,_,_ = run_epochs(resumed,resumed_opt,callback,10,tmp_path/'resumed',device)
        for key,value in full.state_dict().items():
            actual = resumed.state_dict()[key]
            if value.is_sparse:
                value,actual = value.to_dense(),actual.to_dense()
            torch.testing.assert_close(value,actual,rtol=0,atol=0)
        for parameter,state in full_opt.state_dict()['state'].items():
            for key,value in state.items():
                torch.testing.assert_close(value,resumed_opt.state_dict()['state'][parameter][key],rtol=0,atol=0)
        assert [r['training_poisson_loss'] for r in full_records]==[r['training_poisson_loss'] for r in resumed_records]
        torch.testing.assert_close(expected_rng,torch.rand(5),rtol=0,atol=0)
        assert measured_seconds(tmp_path/'resumed')>0
        assert (tmp_path/'resumed/checkpoint.pt').exists()
    finally:
        torch.set_num_threads(old_threads)


def test_final_checkpoint_saved_between_five_epoch_boundaries(tmp_path):
    model = torch.nn.Linear(1,1)
    optimiser = torch.optim.Adam(model.parameters())
    run_epochs(model,optimiser,lambda epoch:{'training_poisson_loss':0.,'eligible_cells':1},
               7,tmp_path,torch.device('cpu'))
    assert torch.load(tmp_path/'checkpoint.pt',weights_only=False)['completed_epochs']==7
