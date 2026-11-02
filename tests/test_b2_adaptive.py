import numpy as np
import torch
from models.b2_adaptive import AdaptiveB2,B2WithoutBase,parameter_counts


def model(condition):
    torch.manual_seed(11)
    return AdaptiveB2(np.array([[0,1]]),np.array([True,True,True,False]),8,np.array([1.,2.,3.,1.]),condition)


def test_learned_mask_rows_and_geographic_isolate():
    m=model('learned'); a=m.adjacency()
    assert torch.equal(a.diagonal(),torch.zeros(4))
    assert torch.equal(a[:,3],torch.zeros(4))
    torch.testing.assert_close(a.sum(1),torch.ones(4))
    assert a[2,0]>0 and a[2,1]>0
    assert not m.has_neighbour[2]


def test_unknown_sources_do_not_change_observed_outputs_and_A_once(monkeypatch):
    m=model('learned'); m.neighbour_head.weight.data.fill_(.1)
    calls=[]; adjacency=m.adjacency
    monkeypatch.setattr(m,'adjacency',lambda:(calls.append(1) or adjacency()))
    x=torch.randn(2,3,4,6); expected=m(x)
    assert len(calls)==1
    x[:,:,3]=9999
    assert torch.equal(expected,m(x))
    assert torch.equal(expected[:,3],torch.zeros(2,12))


def test_embeddings_train_jointly_and_identity_is_local():
    for condition in ('learned','identity'):
        m=model(condition); x=torch.randn(1,2,4,6)
        if condition=='learned':m.neighbour_head.weight.data.fill_(.1)
        m(x).sum().backward()
        assert m.E1.grad is not None and m.E2.grad is not None
        if condition=='identity':
            assert not hasattr(m,'neighbour_head')
            y=m(x).detach(); x[:,:,1]+=20
            assert torch.equal(y[:,0],m(x)[:,0])


def test_parameter_counts_and_base_ablation_shape():
    counts=parameter_counts()
    assert counts['learned']=={'total':68000,'embeddings':52820}
    assert counts['identity']=={'total':71072,'embeddings':52820}
    m=B2WithoutBase(np.array([[0,1]]),np.ones(3,bool),8,np.ones(3))
    assert m(torch.zeros(1,2,3,5)).shape==(1,3,12)
