from types import SimpleNamespace
import numpy as np
import pytest
from scipy.stats import t
from evaluation.v7_chain_evidence import candidate_test,origin_losses,CANDIDATES


def test_pooled_horizons_are_absolute_losses_not_total_error_or_extra_origins():
    truth=np.full((6,3,12),10.);pred=truth.copy();pred[:,:,0]=13;pred[:,:,1]=7;pred[:,:,2]=13
    ctx=SimpleNamespace(truth=truth,origins=np.arange(6),groups=np.tile([0,1,2],(6,1)),scales=np.ones((6,3))*2)
    runs={11:pred,29:pred,47:pred}
    loss=origin_losses(runs,ctx,'mae','1-3','all')
    assert loss.shape==(6,) and np.allclose(loss,3)
    assert np.allclose(origin_losses(runs,ctx,'mae','total_12','all'),3)
    assert np.allclose(origin_losses(runs,ctx,'mase','1-3','low'),1.5)
    # Three-month absolute total would be 3, then dividing by three gives 1: different from pooled MAE=3.
    assert np.allclose(np.abs((pred[:,:,:3]-truth[:,:,:3]).sum(2)).mean(1)/3,1)


def test_two_sided_DM_and_lower_tail_against_hand_statistic():
    a=[2,4,3,5,5,7];b=[1,2,2,2,3,4]
    row=candidate_test(a,b,2)
    assert row['dm_statistic']==pytest.approx(np.sqrt(80/3),rel=1e-12)
    assert row['p_lower_loss']==pytest.approx(t.cdf(row['dm_statistic'],5),rel=1e-10)
    reverse=candidate_test(b,a,2)
    assert reverse['p_two_sided']==pytest.approx(row['p_two_sided'])
    assert reverse['p_lower_loss']==pytest.approx(1-row['p_lower_loss'])
    assert row['p_same_convention']==row['p_two_sided']


def test_NI_is_shifted_loss_not_superiority_or_constant_margin_variance():
    b=np.array([10.,12,9,11,13,8]);a=1.005*b+np.array([.001,-.001,.002,-.002,.001,-.001])
    ni=candidate_test(a,b,1,True);zero=candidate_test(a,b,1)
    assert zero['mean_test_differential']>0 and ni['mean_test_differential']<0
    assert ni['noninferiority_margin_slack']>0
    assert ni['p_same_convention']==ni['p_lower_loss']<.025
    expected=candidate_test(a,1.01*b,1)
    assert ni['dm_statistic']==pytest.approx(expected['dm_statistic'])
    assert ni['relative_excess_percent']<1


def test_low_maturity_uses_current_origin_membership_and_seed_losses():
    truth=np.zeros((6,3,12));pred=np.ones_like(truth);pred[:,0]=2;pred[:,1]=4;pred[:,2]=8
    groups=np.tile([0,1,2],(6,1));groups[1]=[1,0,2]
    ctx=SimpleNamespace(truth=truth,origins=np.arange(6),groups=groups,scales=np.ones((6,3)))
    loss=origin_losses({11:pred,29:2*pred,47:3*pred},ctx,'mae','1','low')
    assert loss[0]==4 and loss[1]==8
    assert len(CANDIDATES)==11 and len({c[0] for c in CANDIDATES})==11


def test_undefined_dm_is_not_silently_a_rejection():
    row=candidate_test(np.ones(6),np.ones(6),1)
    assert row['status'].startswith('undefined') and np.isnan(row['p_same_convention'])
