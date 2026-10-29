from math import sqrt
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from evaluation.baselines import mase_scales, seasonal_predictions, evaluate, holm, validation_rows
from evaluation.dm import dm_from_losses
from evaluation.protocol import config
from features.panel import Panel, assemble
from features.builder import FeatureBuilder
from models.baselines import configurations, predict_origin


@pytest.fixture
def panel():
    months = pd.period_range('2008-01','2022-10',freq='M').astype(str).to_numpy()
    t = np.arange(1,len(months)+1,dtype=np.float32)
    targets = np.stack([t,2*t,np.zeros_like(t),np.full_like(t,np.nan),3*t])
    return Panel(np.array(['0800','1000','2000','3000','4000']), months, targets,
                 np.array([True,True,True,False,True]), np.array([[0,1],[0,3],[1,3]]))


def test_exact_own_neighbour_features_and_unknown_node_mask(panel):
    builder = FeatureBuilder(panel)
    x = builder.at('2018-11',6,True,False)
    names = builder.names(True)
    t = panel.index('2018-11')
    assert x[0,names.index('own_lag_1')] == pytest.approx(np.log1p(t+1))
    assert x[0,names.index('own_lag_24')] == pytest.approx(np.log1p(t-22))
    assert x[0,names.index('own_rolling_3')] == pytest.approx(np.log1p(t))
    assert x[0,names.index('own_cumulative_base')] == pytest.approx(np.log1p((t+1)*(t+2)/2))
    assert x[0,names.index('neighbour_lag_1')] == pytest.approx(np.log1p(2*(t+1)))
    assert x[1,names.index('neighbour_lag_1')] == pytest.approx(np.log1p(t+1))
    assert x[2,names.index('has_observed_neighbour_flag')] == 0
    assert x[2,names.index('isolate_flag')] == 1
    assert x[2,names.index('neighbour_cumulative_base')] == 0
    assert np.all(x[3] == 0)
    assert x[:,names.index('horizon')].tolist() == [6,6,6,0,6]
    # No geographic identifier or forbidden covariate appears among predictors.
    assert not any('postcode' in name or 'state' in name or 'policy' in name for name in names)


@pytest.mark.parametrize('origin',['2010-01','2018-11','2021-08'])
def test_all_features_invariant_to_own_and_neighbour_future_counts(panel,origin):
    future = panel.targets.copy()
    future[:,panel.months > origin] = 1234567
    changed = Panel(panel.codes,panel.months,future,panel.observed,panel.edges)
    a,b = FeatureBuilder(panel),FeatureBuilder(changed)
    for spatial in (False,True):
        for horizon in (1,6,12):
            np.testing.assert_array_equal(a.at(origin,horizon,spatial,False),b.at(origin,horizon,spatial,False))


def test_training_mask_excludes_future_and_preserves_all_observed_targets(panel):
    first,fit = '2011-01','2011-03'
    a = FeatureBuilder(panel)
    x,y = a.training(fit,first,True)
    assert len(y) == 3*12*4
    assert np.bincount(x[:,a.names(True).index('horizon')].astype(int))[1:].tolist() == [12]*12
    future = panel.targets.copy()
    future[:,panel.months > fit] = 9876543
    b = FeatureBuilder(Panel(panel.codes,panel.months,future,panel.observed,panel.edges))
    xx,yy = b.training(fit,first,True)
    np.testing.assert_array_equal(x,xx)
    np.testing.assert_array_equal(y,yy)
    own_x,own_y = a.training(fit,first,False)
    np.testing.assert_array_equal(own_x,x[:,:own_x.shape[1]])
    np.testing.assert_array_equal(own_y,y)


def test_unknown_sources_suppressed_even_if_placeholder_is_poisoned(panel):
    target = panel.targets.copy()
    target[~panel.observed] = 999999
    a,b = FeatureBuilder(panel),FeatureBuilder(Panel(panel.codes,panel.months,target,panel.observed,panel.edges))
    np.testing.assert_array_equal(a.at('2018-11',1,True,False),b.at('2018-11',1,True,False))


def test_panel_preserves_strings_unknowns_and_all_graph_nodes():
    cer = pd.DataFrame({'postcode':['0800','0800','9999','9999'], 'month':['2011-01','2011-02']*2,'count':[0,2,7,9]})
    nodes = pd.DataFrame({'postcode':['0800','2000']})
    edges = pd.DataFrame({'source':['0800'],'target':['2000']})
    panel = assemble(cer,nodes,edges,'2011-01','2011-02')
    assert panel.codes.tolist() == ['0800','2000']
    assert panel.observed.tolist() == [True,False]
    assert np.isnan(panel.targets[1]).all() and np.all(panel.inputs[1] == 0)
    with pytest.raises(ValueError,match='four-character'):
        assemble(cer,pd.DataFrame({'postcode':[800]}),edges,'2011-01','2011-02')


def test_seasonal_naive_and_cpu_configuration_budget_without_fitting(panel):
    builder = FeatureBuilder(panel)
    pred = seasonal_predictions(builder,['2018-11'])
    t = panel.index('2018-11')
    np.testing.assert_array_equal(pred[0,:,0],panel.inputs[panel.observed,t-11])
    np.testing.assert_array_equal(pred[0,:,11],panel.inputs[panel.observed,t])
    configs = configurations(config())
    assert len(configs) == 6
    assert all(c['max_iter']==300 and not c['early_stopping'] for c in configs)
    class ConstantPredictor:
        def predict(self,x):
            return np.ones(len(x))
    with pytest.raises(ValueError,match='test is sealed'):
        predict_origin(ConstantPredictor(),builder,'2022-10',False,config())


def test_mase_zero_scale_fallback_and_aggregate_error(panel,tmp_path):
    cfg = config()
    scale = mase_scales(panel,'2018-11',cfg)
    # Observed nonconstant areas have seasonal differences 12,24,36; pooled=24.
    np.testing.assert_allclose(scale,[12,24,24,36])
    constant = Panel(panel.codes,panel.months,np.where(panel.observed[:,None],np.zeros_like(panel.targets),np.nan),panel.observed,panel.edges)
    np.testing.assert_array_equal(mase_scales(constant,'2018-11',cfg),np.ones(4))
    builder = FeatureBuilder(panel)
    rows = validation_rows(cfg)
    truth = np.stack([builder.targets(o) for o in rows.origin])
    # Signed errors cancel in the twelve-month total: total MAE must be zero.
    pred = truth.copy(); pred[:,:,0] += 1; pred[:,:,1] -= 1
    # Zero-count area cannot have a negative expected count; leave it exact.
    pred[:,2] = truth[:,2]
    predictions = {model:{0:pred} for model in ('seasonal_naive','gradient_boosting_own','gradient_boosting_neighbours')}
    origin,scores = evaluate(panel,builder,predictions,cfg,tmp_path)
    assert scores.loc[scores.outcome.eq('total_12'),'mae'].eq(0).all()
    assert (scores.loc[scores.outcome.eq('1'),'mae'] > 0).any()
    assert np.isfinite(origin.mase).all()


def test_holm_keeps_full_family_when_some_dm_tests_undefined():
    np.testing.assert_allclose(holm([.01,.04,.03]),[.03,.06,.06])
    actual = holm([.01,np.nan,.04])
    assert actual[0] == pytest.approx(.03) and actual[2] == pytest.approx(.08)
    assert np.isnan(actual[1])


def test_installed_dm_package_adapter_matches_hand_computation():
    pytest.importorskip('dieboldmariano', reason='Researcher installs requirements-baselines.lock before training')
    statistic,p = dm_from_losses([2,4,3,5,5,7],[1,2,2,2,3,4],2)
    assert statistic == pytest.approx(sqrt(80/3),rel=1e-10)
    assert 0 < p < 1


def test_installed_boosting_constructor_matches_cpu_poisson_contract():
    pytest.importorskip('sklearn',reason='Researcher installs pinned CPU baseline dependencies')
    from importlib.metadata import version
    from sklearn.ensemble import HistGradientBoostingRegressor
    assert version('scikit-learn') == '1.6.1'
    estimator = HistGradientBoostingRegressor(loss='poisson',random_state=11,**configurations(config())[0])
    assert estimator.get_params()['loss'] == 'poisson'
    assert estimator.get_params()['early_stopping'] is False
    # Constructor/API test only: no training is performed.


def test_dm_comparison_uses_origin_averaged_seed_losses(tmp_path):
    from evaluation.baselines import compare
    observations = []
    names = ['seasonal_naive','gradient_boosting_own','gradient_boosting_neighbours']
    for model_id,model in enumerate(names):
        for seed in (11,29,47):
            for outcome in ('1','6','12','total_12'):
                for i,origin in enumerate(pd.period_range('2018-11',periods=36,freq='M').astype(str)):
                    observations.append({'model':model,'seed':seed,'outcome':outcome,'origin':origin,
                                         'group':'all','mae':model_id+i+seed/100})
    seen = []
    def dm_stub(left,right,horizon):
        seen.append((left,right,horizon))
        return float(np.mean(left-right)),.2
    result = compare(pd.DataFrame(observations),tmp_path,dm=dm_stub)
    assert len(seen) == 12 and result.family_size.eq(12).all()
    assert len(seen[0][0]) == 36
    assert seen[0][0][0] == pytest.approx(2+(11+29+47)/300)
    assert seen[0][1][0] == pytest.approx(1+(11+29+47)/300)
    assert [s[2] for s in seen[:4]] == [1,6,12,12]


def test_validation_report_is_built_from_supplied_metrics_not_invented(panel,tmp_path,monkeypatch):
    from evaluation.baselines import compare
    from evaluation.result_report import write_report
    cfg = config(); builder = FeatureBuilder(panel)
    rows = validation_rows(cfg)
    truth = np.stack([builder.targets(o) for o in rows.origin])
    predictions = {name:{0:truth} for name in ('seasonal_naive','gradient_boosting_own','gradient_boosting_neighbours')}
    run = tmp_path/'run'; run.mkdir()
    origin,_ = evaluate(panel,builder,predictions,cfg,run)
    compare(origin,run,dm=lambda a,b,h:(0.,1.))
    pd.DataFrame({'condition':['gradient_boosting_own']*46+['gradient_boosting_neighbours']*46}).to_csv(run/'fit_records.csv',index=False)
    pd.DataFrame({'group':['neighbour_lags']*2,'mae_increase_systems':[0.,0.]}).to_csv(run/'neighbour_importance.csv',index=False)
    monkeypatch.chdir(tmp_path)
    Path('reports/experiments').mkdir(parents=True)
    target = write_report(run,cfg,{'run_id':'unit-test-only','protocol_sha256':'fixture','threads':8},
                          {'cpu_fit_count':92,'fitting_seconds_recorded':0.}, {'moran_i':None})
    text = target.read_text(encoding='utf-8')
    assert 'unit-test-only' in text and 'Outcome total_12: neighbour-model MAE is equal' in text
    assert 'No final-test forecast or error is evaluated' in text
