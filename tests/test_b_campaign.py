import copy
import json
import numpy as np
import pandas as pd
import pytest
import torch


def test_equal_weights_average_forecasts_not_losses():
    from evaluation.anchor_equal_weight import combinations
    value=combinations(np.array([0.]),np.array([2.]),np.array([10.]),np.array([6.]))
    assert {k:v.item() for k,v in value.items()}=={'half_own_B':5.,'half_neighbour_B':6.,'half_own_C':3.}
    assert all(v.dtype==np.float64 for v in value.values())
    with pytest.raises(ValueError):combinations([1],[2,3],[4],[5])


def test_campaign_budget_and_eligible_reuse(monkeypatch):
    from models import b_validation as campaign
    dates=pd.period_range('2018-11',periods=12,freq='3M').astype(str)
    monkeypatch.setattr(campaign,'validation_rows',lambda cfg:pd.DataFrame({'fit_origin':dates}))
    plan=campaign.plan({})
    assert [x['condition'] for x in plan]==list(campaign.ORDER)
    assert [x['fits'] for x in plan]==[36]*4
    assert [x['reused'] for x in plan]==[2,0,2,0]
    assert sum(x['new'] for x in plan)==140
    assert campaign.reused_fit('real',11,'2019-08') is not None
    assert campaign.reused_fit('real',29,'2019-08') is None
    assert campaign.reused_fit('without_base',11,'2019-08') is None


def test_ablation_channels_and_b_parameterisation():
    from types import SimpleNamespace
    from models.b_validation import make_model,channels
    torch.set_num_threads(1)
    panel=SimpleNamespace(edges=np.array([[0,1],[1,3]]),observed=np.array([True,True,True,False]))
    assert channels('without_base')==[0,2,3,4,5]
    real=make_model(panel,'real',11); ablation=make_model(panel,'without_base',11)
    assert sum(p.numel() for p in real.parameters())==15180
    assert sum(p.numel() for p in ablation.parameters())==14988
    x=torch.randn(1,4,4,6)
    assert ablation(x[:,:,:,channels('without_base')]).shape==(1,4,12)
    assert torch.count_nonzero(real(x)[:,3])==0
    control=copy.deepcopy(real); control.graph_enabled=False
    real.graph_enabled=False
    torch.testing.assert_close(real(x),control(x),rtol=0,atol=0)


def test_release_blocks_prediction_reads_before_ablation(tmp_path,monkeypatch):
    from models import b_validation as campaign
    from evaluation.b_gate_c import load_predictions
    monkeypatch.setattr(campaign,'ROOT',tmp_path)
    monkeypatch.setattr(np,'load',lambda *args,**kwargs:pytest.fail('Premature forecast access'))
    with pytest.raises(RuntimeError,match='withheld'):load_predictions(None)
    for condition in campaign.ORDER[:-1]:
        path=tmp_path/condition; path.mkdir()
        (path/'condition_complete.json').write_text(json.dumps({'condition':condition,'fits':36,'seeds':[11,29,47],
            'validation_origins':36,'last_target':'2022-10','test_forecasts_or_losses':0}))
    with pytest.raises(RuntimeError,match='without_base incomplete'):load_predictions(None)


def test_declared_twenty_test_family_and_global_holm():
    from evaluation.b_gate_c import dm_family
    from evaluation.gate_c_fixtures import synthetic_fixture
    from evaluation.gate_c_metrics import evaluate,compare
    family=dm_family()
    assert len(family)==len(set(family))==20
    assert {b for a,b,h in family}=={'gnn_no_graph','gnn_shuffled','gradient_boosting_own','gradient_boosting_neighbours','gnn_no_base'}
    ctx,pred=synthetic_fixture()
    results=compare(evaluate(pred,ctx)['origin'],True,dm=lambda *args:(-1.,.01))
    assert results.family_size.eq(20).all()
    np.testing.assert_allclose(results.p_holm,.2)


def test_synthetic_combined_report_and_figures(tmp_path,monkeypatch):
    from evaluation import b_gate_c as pipeline,gate_c_io
    from evaluation.gate_c_fixtures import synthetic_fixture
    from visuals import b_gate_c as figures
    ctx,pred=synthetic_fixture()
    monkeypatch.chdir(tmp_path); (tmp_path/'reports/experiments').mkdir(parents=True)
    # Palette is the sole fixture asset; no study predictions or GPU access.
    (tmp_path/'configs').mkdir()
    colours={'seasonal_naive':'#777777','gradient_boosting_own':'#E69F00','gradient_boosting_neighbours':'#56B4E9',
             'gnn_real':'#009E73','gnn_no_graph':'#0072B2','gnn_shuffled':'#D55E00'}
    import yaml
    (tmp_path/'configs/style.yaml').write_text(yaml.safe_dump({'models':colours}))
    monkeypatch.setattr(pipeline,'require_release',lambda:({},{}))
    monkeypatch.setattr(pipeline,'load_predictions',lambda c:({k:v for k,v in pred.items() if k.startswith('gnn_')},{}))
    monkeypatch.setattr(gate_c_io,'context_from_panel',lambda cfg:ctx)
    monkeypatch.setattr(gate_c_io,'load_baselines',lambda cfg,c:({k:v for k,v in pred.items() if not k.startswith('gnn_')},None,{}))
    monkeypatch.setattr(figures,'require_release',lambda:({},{}))
    monkeypatch.setattr(figures,'study_geometry',lambda cfg:figures.synthetic_geometry(ctx))
    pipeline.run()
    assert len(pd.read_csv('data/processed/t03_b_gate_c/dm_tests.csv'))==20
    text=(tmp_path/'reports/experiments/b_validation.md').read_text(encoding='utf-8')
    assert 'B validation' in text and '20 two-sided' in text
    assert (tmp_path/'data/explore/t03/b_validation/gnn_scaled_error_map.png').exists()
    assert len(list((tmp_path/'visuals/t03/b_validation').glob('*.png')))==4
