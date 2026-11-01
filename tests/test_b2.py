import numpy as np
import pandas as pd
import torch
from features.panel import Panel
from features.b2 import area_scale,B2Windows
from models.b2 import B2Network
from models.screen_architectures import ScreenNetwork
from features.gnn import GNNWindows
from evaluation.protocol import config


def panel():
    months=pd.period_range('2008-01','2012-12',freq='M').astype(str).to_numpy()
    values=np.stack([np.arange(len(months))%6,np.arange(len(months))%3,np.zeros(len(months)),np.full(len(months),np.nan)]).astype(np.float32)
    return Panel(np.array(['0001','0002','0003','0004']),months,values,np.array([True,True,True,False]),np.array([[0,1],[1,3]]))


def test_scale_cannot_use_post_fit_targets():
    p=panel(); expected=area_scale(p,'2011-12')
    p.targets[:,p.index('2012-01'):]=1e9
    np.testing.assert_array_equal(area_scale(p,'2011-12'),expected)
    np.testing.assert_allclose(expected[:3],1+p.targets[:3,p.index('2011-01'):p.index('2011-12')+1].mean(axis=1))
    assert expected[3]==1


def test_all_unit_scales_reproduce_b_features_and_outputs_exactly():
    torch.set_num_threads(1); p=panel().through('2011-12'); cfg=config(); ones=np.ones(4)
    original=GNNWindows(p,cfg); scaled=B2Windows(p,cfg,ones)
    np.testing.assert_array_equal(original.values,scaled.values)
    for graph in (True,False):
        b=ScreenNetwork('B',p.edges,p.observed,32,graph)
        b2=B2Network(p.edges,p.observed,32,ones,graph)
        b2.load_state_dict({**b2.state_dict(),**b.state_dict()})
        x=torch.from_numpy(original.at('2011-12')[None])
        torch.testing.assert_close(b2(x),b(x),rtol=0,atol=0)


def test_scale_changes_only_count_and_base_channels():
    p=panel().through('2011-12'); cfg=config(); scale=area_scale(p,'2011-12')
    original=GNNWindows(p,cfg); transformed=B2Windows(p,cfg,scale)
    np.testing.assert_array_equal(original.values[:,:,2:],transformed.values[:,:,2:])
    np.testing.assert_allclose(transformed.values[:,0,0],np.log1p(p.inputs[0]/scale[0]),rtol=1e-6)
    np.testing.assert_allclose(transformed.values[:,0,1],np.log1p(np.cumsum(p.inputs[0],dtype=float)/scale[0]),rtol=1e-6)
    assert not transformed.values[:,3].any()


def test_rates_rescale_in_raw_count_units():
    p=panel(); scale=np.array([2.,3.,1.,1.])
    model=B2Network(p.edges,p.observed,32,scale,False)
    with torch.no_grad():
        for parameter in model.parameters():parameter.zero_()
    actual=model(torch.zeros(1,4,4,6))
    expected=torch.tensor(np.log(2)*scale,dtype=torch.float32)[None,:,None].expand(1,4,12).clone()
    expected[:,3]=0
    torch.testing.assert_close(actual,expected)


def test_screen_selection_and_negative_loss_extension_rule():
    from models.b2_screen import select,still_falling,choose_epochs
    scores=np.array([[3.,2.,4.,5.,6.,7.],[1.,4.,5.,6.,7.,8.]])
    assert select(scores)==0
    losses=-10*np.log(np.arange(1,66))
    curve=pd.DataFrame({'epoch':range(1,66),'training_poisson_loss':losses})
    assert still_falling(curve)['trigger']
    shifted=curve.copy(); shifted.training_poisson_loss+=1000
    assert still_falling(shifted)['trigger']
    curve.loc[55:,'training_poisson_loss']=curve.training_poisson_loss.iloc[54]
    assert not still_falling(curve)['trigger']
    assert choose_epochs(4.,3.98)==100
    assert choose_epochs(4.,3.981)==65
    assert choose_epochs(4.,4.1)==65
    assert choose_epochs(0.,0.)==65


def test_continuation_preserves_original_65_epoch_snapshot():
    from models.b2_screen import continuation_snapshot
    original={'completed_epochs':65,'total_epochs':65,'model':{'weight':torch.tensor([2.])},'optimiser':{'state':1},'cpu_rng':'retained'}
    continued=continuation_snapshot(original)
    assert original['total_epochs']==65 and continued['total_epochs']==100
    assert continued['completed_epochs']==65 and continued['optimiser']==original['optimiser'] and continued['cpu_rng']=='retained'


def test_epoch_choice_survives_repeated_primary_command(tmp_path,monkeypatch):
    from models import b2_screen as screen
    monkeypatch.setattr(screen,'ROOT',tmp_path)
    monkeypatch.setattr(screen,'selected_real_mae',lambda config,epochs:4. if epochs==65 else 3.98)
    assert screen.write_epoch_decision(0,True)['pending_100']
    for anchor in screen.ANCHORS:
        for condition in ('real','no_graph'):
            path=screen.path_for(0,anchor,condition,100); path.mkdir(parents=True)
            (path/'complete.json').write_text('{}')
    result=screen.write_epoch_decision(0,True)
    assert result['selected_epochs']==100 and not result['pending_100']
    assert result==screen.write_epoch_decision(0,True)
    assert set(result['applies_to'])=={'real','no_graph','learned_graph','identity_control'}


def test_missing_continuation_evidence_requires_fresh_fallback(tmp_path,monkeypatch):
    from models import b2_screen as screen
    monkeypatch.setattr(screen,'CONTINUATION_EVIDENCE',tmp_path/'absent.json')
    assert not screen.continuation_allowed()


def test_robustness_zero_denominators_are_explicit():
    from evaluation.mase_robustness import robust_metrics
    result=robust_metrics([2,9,0],[2,0,0],[1,3,0])
    assert result['fallback_areas']==2 and result['zero_mean_areas']==1
    assert result['mase_without_fallback']==result['median_scaled_error_without_fallback']==1
    assert result['mean_level_scaled_error']==2.5
    empty=robust_metrics([0],[0],[0])
    assert np.isnan(empty['mase_without_fallback']) and np.isnan(empty['mean_level_scaled_error'])


def test_synthetic_b2_report_before_any_study_run(tmp_path,monkeypatch):
    import json
    from models import b2_screen,architecture_screen
    from evaluation import frozen,gate_c_io
    from evaluation.gate_c_metrics import Context
    from evaluation.b2_screen_report import report
    monkeypatch.chdir(tmp_path); (tmp_path/'reports/experiments').mkdir(parents=True)
    root=tmp_path/'b2'; root.mkdir(); monkeypatch.setattr(b2_screen,'ROOT',root)
    cfg={'tuning':{'gnn_grid':{'hidden_size':[32,64,96],'learning_rate':[.001,.003]}}}
    monkeypatch.setattr(frozen,'frozen_protocol',lambda *args,**kwargs:(cfg,'synthetic'))
    origins=np.array(['2019-08','2020-08']); codes=np.array(['0001','0002','0003'])
    ctx=Context(origins,codes,np.ones((2,3,12))*2,np.ones((2,3)),np.array([[0,1,2]]*2),np.array([[0,1]]),origins)
    monkeypatch.setattr(gate_c_io,'context_from_panel',lambda cfg:ctx)
    chosen=2
    (root/'selection.json').write_text(json.dumps({'config_id':chosen,'configuration':b2_screen.grid(cfg)[chosen]}))
    (root/'extension_decision.json').write_text(json.dumps({'trigger':False,'anchors':{a:{'trigger':False} for a in origins}}))
    for i in range(6):
        for anchor in origins:
            for condition in (('real','no_graph') if i==chosen else ('real',)):
                path=b2_screen.path_for(i,anchor,condition); path.mkdir(parents=True)
                (path/'complete.json').write_text(json.dumps({'config_id':i,'anchor':anchor,'condition':condition,'epochs':65,'fit_seconds':1.}))
                pd.DataFrame({'epoch':range(1,66),'training_poisson_loss':-np.arange(1,66)}).to_csv(path/'training_curve.csv',index=False)
                np.savez_compressed(path/'prediction.npz',prediction=np.ones((3,12),dtype=np.float32)*2.5,codes=codes,origin=anchor,scale=np.ones(3))
    def old_output(candidate,anchor,condition):return tmp_path/'old'/f'{anchor}_{condition}'
    monkeypatch.setattr(architecture_screen,'output',old_output)
    for anchor in origins:
        for condition in ('real','no_graph'):
            path=old_output('B',anchor,condition); path.mkdir(parents=True)
            np.savez_compressed(path/'prediction.npz',prediction=np.ones((3,12),dtype=np.float32)*3,codes=codes,origin=anchor)
    report()
    text=(tmp_path/'reports/experiments/b2_screen.md').read_text(encoding='utf-8')
    assert 'Selected configuration **2**' in text and 'No later 100-epoch result changes that selection' in text
    assert (tmp_path/'data/explore/t03/b2_screen/grid_training_curves.png').exists()
