import copy
import numpy as np
import pandas as pd
import pytest
import torch
from models.screen_architectures import ScreenNetwork


@pytest.mark.parametrize('candidate',['A','B','C'])
def test_zero_neighbour_branch_exactly_reproduces_no_graph(candidate):
    torch.set_num_threads(1); torch.manual_seed(11)
    real=ScreenNetwork(candidate,np.array([[0,1],[1,2],[2,4]]),[True,True,True,True,False])
    # Nonzero late weights make the test informative beyond initialisation.
    if candidate!='A':torch.nn.init.normal_(real.neighbour_head.weight)
    control=copy.deepcopy(real); control.graph_enabled=False
    x=torch.randn(2,4,5,6); base=torch.rand(2,5,12)+.1
    real.graph_enabled=False
    torch.testing.assert_close(real(x,base),control(x,base),rtol=0,atol=0)
    real.graph_enabled=True
    if candidate=='A':
        real.neighbour_contribution=lambda values:torch.zeros_like(values)
    else:
        real.late_correction=lambda hidden:hidden.new_zeros((*hidden.shape[:2],12))
    torch.testing.assert_close(real(x,base),control(x,base),rtol=0,atol=0)
    assert sum(p.numel() for p in real.parameters())==sum(p.numel() for p in control.parameters())


@pytest.mark.parametrize('candidate',['A','B','C'])
def test_isolates_and_unknown_sources_have_zero_neighbour_contribution(candidate):
    model=ScreenNetwork(candidate,np.array([[0,1],[1,4]]),[True,True,True,True,False])
    values=torch.randn(2,5,64)
    assert torch.count_nonzero(model.neighbour_contribution(values)[:,2:])==0
    altered=values.clone(); altered[:,4]=999
    torch.testing.assert_close(model.mean(values),model.mean(altered),rtol=0,atol=0)
    if candidate!='A':
        torch.nn.init.normal_(model.neighbour_head.weight)
        assert torch.count_nonzero(model.late_correction(values)[:,2:4])==0


def test_c_zero_correction_returns_base_bit_exactly():
    model=ScreenNetwork('C',np.array([[0,1]]),[True,True,True])
    base=torch.tensor([[[1e-6]*12,[2.125]*12,[100.5]*12]])
    torch.testing.assert_close(model(torch.randn(1,24,3,6),base),base,rtol=0,atol=0)


def test_strict_base_calendar_and_training_start():
    from models.screen_cpu import base_schedule, base_fit_for
    assert base_schedule()[0]=='2011-02'
    assert base_fit_for('2011-03')=='2011-02'
    assert base_fit_for('2019-08')=='2019-05'
    assert base_fit_for('2020-08')=='2020-05'
    assert base_fit_for('2011-02') is None
    for origin in pd.period_range('2011-03','2020-08',freq='M').astype(str):
        assert pd.Period(base_fit_for(origin),freq='M')<pd.Period(origin,freq='M')


def test_selection_rule_and_cost_tie():
    from evaluation.screen_report import select_candidate
    rows=pd.DataFrame({'candidate':['A','B','C'],'mae':[4.,4.05,4.2],'cost_seconds':[200.,100.,10.]})
    assert select_candidate(rows)=='B'
    rows.loc[1,'mae']=4.09
    assert select_candidate(rows)=='A'


def test_selection_rejects_incomplete_or_nonfinite_candidates():
    from evaluation.screen_report import select_candidate
    with pytest.raises(ValueError):
        select_candidate(pd.DataFrame({'candidate':['A'],'mae':[1.],'cost_seconds':[2.]}))
    with pytest.raises(ValueError):
        select_candidate(pd.DataFrame({'candidate':['A','B','C'],'mae':[1.,np.nan,2.],'cost_seconds':[2.,3.,4.]}))


def test_reused_boosting_anchor_expands_to_three_origins_without_refit(tmp_path,monkeypatch):
    import joblib
    from models import screen_cpu as cpu
    monkeypatch.setattr(cpu,'ROOT',tmp_path)
    condition=cpu.CONDITIONS[0]
    jobs=[dict(condition=condition,origin='2019-08',seed=s,name=f'anchor_{s}') for s in (11,29,47)]
    monkeypatch.setattr(cpu,'full_jobs',lambda *args:jobs)
    dates=['2019-08','2019-09','2019-10']
    monkeypatch.setattr(cpu,'validation_rows',lambda cfg:pd.DataFrame({'origin':dates,'fit_origin':['2019-08']*3}))
    monkeypatch.setattr(cpu,'load_panel',lambda **kwargs:None)
    monkeypatch.setattr(cpu,'FeatureBuilder',lambda *args:None)
    monkeypatch.setattr(joblib,'load',lambda path:object())
    monkeypatch.setattr(cpu,'predict',lambda *args:np.ones((2,12),dtype=np.float32)*3)
    for job in jobs:
        path=cpu.folder(job); path.mkdir(parents=True)
        (path/'complete.json').write_text('{}')
        origins=dates[:1] if job['seed']==11 else dates
        np.savez_compressed(path/'forecasts.npz',origins=np.array(origins),codes=np.array(['0001','0002']),prediction=np.ones((len(origins),2,12),dtype=np.float32))
    decision={condition:{'improved':True,'winner':{'parameters':{}}}}
    cpu.assemble_full({},decision)
    with np.load(tmp_path/f'{condition}_updated_seed11.npz') as data:
        assert data['prediction'].shape==(3,2,12)
        np.testing.assert_array_equal(data['prediction'][1:],3)


def test_complete_synthetic_report(tmp_path,monkeypatch):
    import json
    from types import SimpleNamespace
    from models import screen_cpu as cpu, architecture_screen as runner
    from evaluation import gate_c_io,baselines
    from evaluation.gate_c_metrics import Context
    from features import panel as panel_module,gnn
    from evaluation.screen_report import report
    from evaluation import screen_baseline_comparison
    monkeypatch.chdir(tmp_path)
    root=tmp_path/'campaign'; root.mkdir(); (tmp_path/'reports/experiments').mkdir(parents=True)
    monkeypatch.setattr(cpu,'ROOT',root); monkeypatch.setattr(runner,'ROOT',root)
    monkeypatch.setattr(runner,'fingerprint',lambda:({},{}))
    (root/'gpu_manifest.json').write_text('{}')
    codes=np.array(['0001','0002','0003','0004'])
    origins=np.array(cpu.ANCHORS); observed=np.ones(4,dtype=bool)
    truth=np.ones((2,4,12))*2
    ctx=Context(origins,codes,truth,np.ones((2,4)),np.array([[0,1,2,2]]*2),np.array([[0,1]]),origins)
    monkeypatch.setattr(gate_c_io,'context_from_panel',lambda cfg:ctx)
    panel=SimpleNamespace(codes=codes,observed=observed,edges=np.array([[0,1]]),targets=np.ones((4,2)),index=lambda a:list(origins).index(a))
    monkeypatch.setattr(panel_module,'load_panel',lambda **kwargs:panel)
    monkeypatch.setattr(runner,'load_base',lambda p:(origins,np.ones((2,4,12),dtype=np.float32)*2))
    monkeypatch.setattr(cpu,'base_jobs',lambda:[])
    monkeypatch.setattr(screen_baseline_comparison,'load_anchor_baselines',lambda context:(
        {'gradient_boosting_own_frozen':truth.astype(np.float32),
         'gradient_boosting_neighbours_frozen':truth.astype(np.float32)+.2,
         'gradient_boosting_own_improved':truth.astype(np.float32)+.1},
        {'seed':11,'synthetic':True}))
    class Windows:
        def __init__(self,*args):pass
        def training(self,a):return np.array(['2011-03','2011-04']),None,None
    monkeypatch.setattr(gnn,'GNNWindows',Windows)
    monkeypatch.setattr(baselines,'validation_rows',lambda cfg:pd.DataFrame({'fit_origin':origins}))
    for candidate,anchor,condition in runner.jobs():
        path=runner.output(candidate,anchor,condition); path.mkdir(parents=True)
        bias={'A':.5,'B':.8,'C':1.}[candidate]+(.1 if condition=='real' else 0)
        np.savez_compressed(path/'prediction.npz',prediction=np.full((4,12),2+bias,dtype=np.float32),codes=codes,origin=anchor)
        (path/'complete.json').write_text(json.dumps({'candidate':candidate,'anchor':anchor,'condition':condition,
            'epochs':65,'fit_seconds':10.,'training_loss':-1. if condition=='real' else -2.,
            'training_samples':2,'parameter_count':10,'peak_gpu_memory_bytes':1024}))
        pd.DataFrame({'epoch':[1,65],'training_poisson_loss':[-.5,-1.]}).to_csv(path/'training_curve.csv',index=False)
    report()
    text=(tmp_path/'reports/experiments/t03_architecture_screen.md').read_text(encoding='utf-8')
    assert 'No candidate real graph beats its own no graph at both anchors' in text
    assert json.loads((root/'selection.json').read_text())['selected']=='A'
    all_metrics=pd.read_csv(tmp_path/'data/explore/t03/architecture_screen/origin.csv',dtype={'outcome':str})
    assert set(all_metrics.outcome)==set(map(str,range(1,13)))|{'total_12'}
    np.testing.assert_allclose(all_metrics.rmse,np.sqrt(all_metrics.mse))
    comparisons=pd.read_csv(tmp_path/'data/explore/t03/architecture_screen/anchor_band_comparisons.csv')
    assert set(comparisons.reference)=={'gradient_boosting_own_frozen','gradient_boosting_neighbours_frozen','gradient_boosting_own_improved','C_base'}
    assert set(comparisons.loc[comparisons.reference.eq('C_base'),'candidate'])=={'C'}
    assert 'Descriptive comparisons with anchor-matched boosting' in text
    assert 'Maturity terciles, pooled across both anchors' in text
    assert len(list((tmp_path/'data/explore/t03/architecture_screen').glob('*.png')))==5
