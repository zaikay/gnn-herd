import numpy as np
import pandas as pd
import pytest

from evaluation.protocol import config
from features.gnn import GNNWindows
from features.panel import Panel


def toy_panel():
    months = pd.period_range('2008-01','2012-01',freq='M').astype(str).to_numpy()
    targets = np.stack([np.arange(len(months)),np.full(len(months),np.nan),np.arange(len(months))*2]).astype(np.float32)
    return Panel(np.array(['0800','1000','2000']),months,targets,np.array([True,False,True]),np.array([[0,1]],dtype=np.int32))


def test_gnn_window_shape_channels_masks_and_future_leakage():
    panel = toy_panel(); cfg = config()
    before = GNNWindows(panel,cfg).at('2011-02')
    assert before.shape == (24,3,6)
    assert (before[:,1]==0).all()
    assert (before[:,2,5]==1).all()
    t = panel.index('2011-02')
    assert before[-1,0,0] == pytest.approx(np.log1p(panel.targets[0,t]))
    assert before[-1,0,1] == pytest.approx(np.log1p(panel.targets[0,:t+1].sum()))
    panel.targets[:,panel.months>'2011-02'] = 100000
    panel.targets[~panel.observed] = np.nan
    np.testing.assert_array_equal(before,GNNWindows(panel,cfg).at('2011-02'))


def test_gnn_training_horizon_eligibility_and_no_unknown_targets():
    panel = toy_panel().through('2011-02'); cfg = config()
    origins,targets,mask = GNNWindows(panel,cfg).training('2011-02')
    assert not mask[:,1,:].any()
    for i,sample in enumerate(origins):
        for h in range(1,13):
            month = pd.Period(sample,freq='M')+h
            eligible = pd.Period('2011-01',freq='M')<=month<=pd.Period('2011-02',freq='M')
            assert mask[i,0,h-1] == eligible
            if eligible:
                assert targets[i,0,h-1] == panel.targets[0,panel.index(str(month))]
    with pytest.raises(ValueError,match='truncated'):
        GNNWindows(toy_panel(),cfg).training('2011-02')
