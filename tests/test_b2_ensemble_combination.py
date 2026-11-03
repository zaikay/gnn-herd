import numpy as np
import pandas as pd
import pytest
from evaluation.b2_ensemble_combination import ensemble,combinations,all_validation_weights,bias_table
from evaluation.gate_c_metrics import Context


def fixture():
    origins=pd.period_range('2018-01',periods=12,freq='M').astype(str).to_numpy()
    n={s:np.full((12,3,12),8.) for s in (11,29,47)}
    b={s:np.full((12,3,12),float(i)) for i,s in enumerate((11,29,47),1)}
    return n,b,np.full((12,3,12),6.5),origins,np.tile([0,1,2],(12,1))


def test_mean_forecast_is_scored_not_average_seed_error():
    values={11:np.array([0.]),29:np.array([3.]),47:np.array([6.])}
    mean=ensemble(values)
    assert mean[0]==3 and mean.dtype==np.float64
    assert abs(mean[0]-3)==0 and np.mean([abs(p[0]-3) for p in values.values()])==2
    with pytest.raises(ValueError):ensemble({11:np.array([1.])})


def test_shared_weights_and_future_target_invariance_for_both_variants():
    n,b,y,origins,groups=fixture(); outputs,weights,variants=combinations(n,b,y,origins,groups)
    assert len(weights)==216 and set(weights.variant)=={'B2_ensemble','B2_individual'}
    np.testing.assert_array_equal(variants['B2_ensemble'][0],ensemble(b))
    np.testing.assert_array_equal(variants['B2_ensemble'][0],variants['B2_ensemble'][2])
    months=pd.PeriodIndex(origins,freq='M').asi8
    future=months[:,None]+np.arange(1,13)>pd.Period('2018-06',freq='M').ordinal
    changed=y.copy();changed[np.broadcast_to(future[:,None,:],y.shape)]=10000
    other,ledger,_=combinations(n,b,changed,origins,groups)
    for variant in outputs:
        for seed in (11,29,47):np.testing.assert_array_equal(outputs[variant][seed][:6],other[variant][seed][:6])
    np.testing.assert_array_equal(weights.loc[weights.origin<='2018-06','neighbour_weight'],ledger.loc[ledger.origin<='2018-06','neighbour_weight'])
    assert weights.loc[weights.origin.eq('2018-01'),'neighbour_weight'].eq(.5).all()


def test_full_origin_weights_are_separate_and_exact_minimisers():
    n,b,y,origins,groups=fixture()
    b={s:np.full_like(y,2.) for s in (11,29,47)}
    outputs,weights,variants=combinations(n,b,y,origins,groups)
    before=weights.copy(deep=True)
    full=all_validation_weights(np.stack(list(n.values())),variants['B2_ensemble'],y,origins,groups)
    assert len(full)==9 and full.neighbour_weight.eq(.75).all() and full.validation_origins.eq(12).all()
    assert np.allclose(full.pooled_MAE_at_optimum,0)
    pd.testing.assert_frame_equal(weights,before)
    assert weights.loc[weights.origin.eq('2018-01'),'neighbour_weight'].eq(.5).all()


def test_bias_dates_signs_groups_and_mean_forecast_identity():
    n,b,y,origins,groups=fixture()
    ctx=Context(origins,np.array(['0001','0002','0003']),y,np.ones((12,3)),groups,np.empty((0,2),int),origins)
    frame=bias_table({'toy':ensemble(n)},ctx)
    assert len(frame)==12*12*4 and np.allclose(frame.mean_signed_error,1.5)
    assert np.allclose(frame.mean_forecast-frame.mean_actual,frame.mean_signed_error)
    assert frame.target_month.max()=='2019-12'
