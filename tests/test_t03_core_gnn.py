import numpy as np
import pytest

torch = pytest.importorskip('torch',reason='Pinned GPU dependencies are researcher-installed')
from models.core_gnn import CoreGNN, graph_operator, poisson_loss


def test_identity_only_same_parameters_and_deterministic_cpu():
    observed = np.array([True,False,True])
    edges = np.array([[0,1],[0,2]])
    counts = []
    for condition in ('real','no_graph','within_state_shuffled'):
        torch.manual_seed(11)
        op = graph_operator(edges,observed,condition)
        model = CoreGNN(op,observed,32)
        counts.append(sum(p.numel() for p in model.parameters()))
        x = torch.ones(2,24,3,6)
        output = model(x)
        assert output.shape == (2,3,12)
        assert (output[:,1]==0).all()
        if condition=='no_graph':
            torch.testing.assert_close(op.to_dense(),torch.eye(3))
        torch.manual_seed(11)
        repeat = CoreGNN(op,observed,32)
        torch.testing.assert_close(output,repeat(x),rtol=0,atol=0)
    assert counts == [4140]*3


def test_unknown_nodes_cannot_send_messages_and_loss_ignores_nan():
    observed = np.array([True,False,True])
    model = CoreGNN(graph_operator([[0,1],[1,2]],observed),observed,32)
    x = torch.ones(1,24,3,6)
    initial = model(x)
    x[:,:,1,:] = 1e6
    torch.testing.assert_close(initial,model(x),rtol=0,atol=0)
    mask = torch.tensor([True,False])
    loss = poisson_loss(torch.tensor([2.,0.]),torch.tensor([3.,float('nan')]),mask)
    assert loss.item() == pytest.approx(2-3*np.log(2))


@pytest.mark.parametrize('width,expected',[(32,4140),(64,14412),(96,30828)])
def test_all_frozen_widths_parameter_count(width,expected):
    model = CoreGNN(graph_operator([],np.array([True]),'no_graph'),np.array([True]),width)
    assert sum(p.numel() for p in model.parameters()) == expected
