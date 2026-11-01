import numpy as np
import pandas as pd
from evaluation.expanding_weights import convex_mae_weight,expanding_predictions


def test_exact_convex_mae_solution_and_flat_tie():
    assert convex_mae_weight([8,8],[2,2],[6.5,6.5])==.75
    assert convex_mae_weight([1,1],[0,0],[0,1])==.5
    assert convex_mae_weight([1],[0],[-2])==0
    assert convex_mae_weight([1],[0],[3])==1
    assert convex_mae_weight([2],[2],[3])==.5


def fixture():
    origins=pd.period_range('2018-01',periods=12,freq='M').astype(str).to_numpy()
    truth=np.full((12,3,12),6.5)
    n=np.full((3,12,3,12),8.); b=np.full_like(n,2.)
    groups=np.tile([0,1,2],(12,1))
    return n,b,truth,origins,groups


def test_warm_up_and_horizon_availability():
    result,ledger=expanding_predictions(*fixture())
    first=ledger.loc[ledger.origin.eq('2018-01')]
    assert first.neighbour_weight.eq(.5).all()
    april=ledger.loc[ledger.origin.eq('2018-04')&ledger.band.eq('1-3')]
    assert april.neighbour_weight.eq(.75).all()
    assert ledger.loc[ledger.origin.eq('2018-04')&ledger.band.eq('4-6'),'neighbour_weight'].eq(.5).all()
    assert result.shape==(3,12,3,12)
    assert (ledger.loc[ledger.latest_target_used.ne(''),'latest_target_used']<=ledger.loc[ledger.latest_target_used.ne(''),'origin']).all()


def test_mutating_unobserved_targets_cannot_change_current_weights():
    n,b,y,origins,groups=fixture()
    output,weights=expanding_predictions(n,b,y,origins,groups)
    dates=pd.PeriodIndex(origins,freq='M').asi8
    future=dates[:,None]+np.arange(1,13)>pd.Period('2018-06',freq='M').ordinal
    changed=y.copy(); changed[np.broadcast_to(future[:,None,:],y.shape)]=10000
    alternate,other=expanding_predictions(n,b,changed,origins,groups)
    np.testing.assert_array_equal(output[:,:6],alternate[:,:6])
    np.testing.assert_array_equal(weights.loc[weights.origin<='2018-06','neighbour_weight'],other.loc[other.origin<='2018-06','neighbour_weight'])


def test_chunked_prediction_storage_is_lossless(tmp_path,monkeypatch):
    from types import SimpleNamespace
    from evaluation import expanding_weights as module
    monkeypatch.setattr(module,'ROOT',tmp_path)
    n,b,y,origins,groups=fixture(); codes=np.array(['0001','0002','0003'])
    for i,seed in enumerate((11,29,47)):
        for part,indices in enumerate(np.array_split(np.arange(len(origins)),2)):
            np.savez_compressed(tmp_path/f'predictions_seed{seed}_part{part}.npz',prediction=n[i,indices],origins=np.asarray(origins[indices],dtype='U7'),codes=codes)
    saved=module.read_saved_predictions(SimpleNamespace(codes=codes,origins=origins,truth=y))
    for i,seed in enumerate((11,29,47)):np.testing.assert_array_equal(saved[seed],n[i])
