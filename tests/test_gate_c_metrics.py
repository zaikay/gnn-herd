import numpy as np
import pandas as pd
import pytest

from evaluation.gate_c_metrics import Context,evaluate,compare,moran,spatial_diagnostics,BASELINES,GNN_MODELS,REPORTED
from evaluation.gate_c_fixtures import synthetic_fixture


def hand_context():
    return Context(np.array(['2018-11','2018-12']),np.array(['0800','1000','2000']),
        np.ones((2,3,12),dtype=np.float64),np.array([[2,4,8],[1,2,4]],dtype=float),
        np.array([[0,1,2],[2,0,1]]),np.array([[0,1]]),np.array(['2018-11','2018-11']))


def test_hand_metrics_pool_squared_loss_before_root_and_seed_spread():
    ctx=hand_context()
    predictions={'toy':{seed:np.full((2,3,12),1+delta,dtype=np.float32) for seed,delta in ((11,1),(29,2),(47,3))}}
    bundle=evaluate(predictions,ctx)
    scores=bundle['scores'].set_index(['outcome','group'])
    row=scores.loc[('1','all')]
    assert row.mae==2 and row.mae_seed_sd==1
    assert row.rmse==pytest.approx(np.sqrt(14/3))
    assert row.rmse!=2  # neither seed-RMSE mean nor ensemble error
    assert row.rmse_seed_sd==1
    assert row.mase==pytest.approx(2*np.mean(1/ctx.scales))
    assert scores.loc[('1','low'),'mase']==1
    assert scores.loc[('1','medium'),'mase']==.5
    assert scores.loc[('total_12','all'),'mae']==24
    assert scores.loc[('total_12','all'),'mase']==pytest.approx(row.mase)
    assert scores.loc[('total_12','all'),'rmse']==pytest.approx(12*np.sqrt(14/3))
    assert len(bundle['scores'])==13*4
    assert set(bundle['areas'].postcode)=={'0800','1000','2000'}


def test_total_errors_allow_cancellation_before_absolute_or_square():
    ctx=hand_context(); ctx.truth[:]=2
    prediction=ctx.truth.astype(np.float32); prediction[:,:,0]+=1; prediction[:,:,1]-=1
    bundle=evaluate({'toy':{seed:prediction for seed in (11,29,47)}},ctx)
    total=bundle['scores'].loc[lambda f:f.outcome.eq('total_12')]
    assert (total[['mae','mase','rmse']]==0).all().all()


@pytest.mark.parametrize('bad',('negative','nan','shape','seed'))
def test_invalid_or_missing_predictions_rejected(bad):
    ctx=hand_context(); values=np.ones_like(ctx.truth,dtype=np.float32)
    predictions={seed:values.copy() for seed in (11,29,47)}
    if bad=='negative': predictions[11][0,0,0]=-1
    if bad=='nan': predictions[11][0,0,0]=np.nan
    if bad=='shape': predictions[11]=values[:1]
    if bad=='seed': del predictions[47]
    with pytest.raises(ValueError): evaluate({'toy':predictions},ctx)


@pytest.mark.parametrize('optional,size',[(False,16),(True,20)])
def test_whole_family_holm_after_origin_area_seed_average(optional,size):
    ctx,predictions=synthetic_fixture(optional)
    origin=evaluate(predictions,ctx)['origin']
    calls=[]
    def fake_dm(a,b,h):
        calls.append((a.copy(),b.copy(),h))
        return -1.,.001*len(calls)
    result=compare(origin,optional,dm=fake_dm)
    assert len(result)==size and result.family_size.eq(size).all()
    assert result.p_holm.iloc[0]==pytest.approx(size*.001)
    assert {c[2] for c in calls}=={1,6,12}
    expected=origin.loc[origin.model.eq('gnn_real') & origin.outcome.eq('1') & origin.group.eq('all')].groupby('origin').mae.mean()
    np.testing.assert_allclose(calls[0][0],expected.to_numpy())
    assert len(calls[0][0])==18  # origins, never areas or individual seed rows
    assert ('gnn_no_base' in set(result.model_b))==optional


def test_undefined_dm_keeps_the_full_holm_family():
    ctx,predictions=synthetic_fixture()
    origin=evaluate(predictions,ctx)['origin']; count=0
    def fake_dm(a,b,h):
        nonlocal count
        count+=1
        if count==1: raise ValueError('constant difference')
        return 0.,.001
    result=compare(origin,True,dm=fake_dm)
    assert len(result)==20 and np.isnan(result.p_holm.iloc[0])
    assert result.p_holm.iloc[1]==pytest.approx(.020)  # undefined slot stays reserved


def test_missing_origin_or_seed_cannot_silently_enter_dm():
    ctx,predictions=synthetic_fixture(); origin=evaluate(predictions,ctx)['origin']
    remove=origin.model.eq('gnn_real') & origin.seed.eq(11) & origin.outcome.eq('1') & origin.group.eq('all')
    with pytest.raises(ValueError,match='seed'): compare(origin.loc[~remove],True)
    invalid=origin.copy()
    invalid.loc[remove,'mae']=np.nan
    with pytest.raises(ValueError,match='finite'): compare(invalid,True)


def test_moran_hand_statistics_undefined_and_signed_difference():
    assert moran([0,2],[[0,1]])==-1
    assert moran([0,1,2],[[0,1],[1,2]])==0
    assert np.isnan(moran([1,1],[[0,1]]))
    assert np.isnan(moran([0,1],[]))
    with pytest.raises(ValueError): moran([np.nan,1],[[0,1]])
    ctx=hand_context()
    predictions={model:{seed:ctx.truth.astype(np.float32)+delta for seed in (11,29,47)} for model,delta in (('gnn_real',1),('gnn_shuffled',2))}
    bundle=evaluate(predictions,ctx)
    diagnostic,difference=spatial_diagnostics(bundle['areas'],ctx)
    assert set(diagnostic.error_type)=={'absolute','training_scaled_absolute','signed'}
    assert (difference.real_minus_shuffled_mase<0).all()
