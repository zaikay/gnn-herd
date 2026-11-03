import io
import json
from pathlib import Path
from types import SimpleNamespace
import numpy as np
import pandas as pd
import pytest
from scipy.stats import t
from features.sealed_panel import target_prefix,load_prefix
from models.final_test_runtime import calendar,validate_spec
from models.final_test import execute_calendar
from evaluation.final_test_metrics import forecast_ensembles,fixed_combination,chains,hac_interval,target_periods
from evaluation.final_test import receipt


def spec():return json.loads(Path('configs/protocol_v7_test.json').read_text())


class FakeBoosting:
    fits=0
    def __init__(self,**kwargs):self.parameters=kwargs;self.n_iter_=kwargs['max_iter']
    def fit(self,x,y):type(self).fits+=1;return self


def test_atomic_CPU_checkpoint_resumes_without_fitting_again(tmp_path,monkeypatch):
    import sklearn.ensemble
    from models.final_test import cpu_model
    from models.final_test_runtime import Permit
    monkeypatch.setattr(sklearn.ensemble,'HistGradientBoostingRegressor',FakeBoosting)
    FakeBoosting.fits=0;s=spec();permit=Permit(s,{},'synthetic-approved',{})
    x=np.ones((6,3),dtype=np.float32);y=np.ones(6)
    parameters=s['boosting']['gradient_boosting_own']
    _,first=cpu_model(tmp_path,x,y,parameters,11,permit,'gradient_boosting_own')
    before=(tmp_path/'model.joblib').read_bytes()
    _,second=cpu_model(tmp_path,x,y,parameters,11,permit,'gradient_boosting_own')
    assert first==second and FakeBoosting.fits==1
    with pytest.raises(RuntimeError,match='identity changed'):
        cpu_model(tmp_path,x,y,{**parameters,'learning_rate':.1},11,permit,'gradient_boosting_own')
    assert (tmp_path/'model.joblib').read_bytes()==before


@pytest.mark.parametrize('fortran',[False,True])
def test_prefix_reader_never_reads_or_decodes_future_cells(fortran):
    values=np.arange(4*20,dtype=np.float32).reshape(4,20)
    values=np.asfortranarray(values) if fortran else np.ascontiguousarray(values)
    raw=io.BytesIO();np.save(raw,values);raw.seek(0)
    np.lib.format.read_magic(raw);np.lib.format.read_array_header_1_0(raw);header=raw.tell()
    class Guard(io.BytesIO):
        def read(self,n=-1):
            start=self.tell()
            if start>=header:
                if fortran:assert start+n<=header+4*7*4
                else:
                    row=(start-header)//(20*4);offset=(start-header)%(20*4)
                    assert row<4 and offset+n<=7*4
            return super().read(n)
    got=target_prefix(Guard(raw.getvalue()),7,4,20)
    np.testing.assert_array_equal(got,values[:,:7])


def test_unapproved_target_access_fails_before_any_file_open():
    with pytest.raises(RuntimeError,match='BEFORE opening'):load_prefix('does-not-exist.npz','2023-01')


def test_calendar_exact_budget_and_approved_orders():
    s=spec();validate_spec(s);rows=calendar(s['first_origin'],s['last_origin'])
    assert len(rows)==24 and rows.fit_origin.nunique()==8 and rows.last_target.max()=='2025-09'
    assert rows.fit_origin.unique().tolist()==['2022-10','2023-01','2023-04','2023-07','2023-10','2024-01','2024-04','2024-07']
    assert rows.groupby('fit_origin').size().eq(3).all()
    assert s['chains']['Accuracy']==['A7','A2','A1','A4','A3','A6','A5']
    bad=json.loads(json.dumps(s));bad['chains']['Behavioural'].append('B4')
    with pytest.raises(RuntimeError):validate_spec(bad)


def test_tag_failure_precedes_panel_or_GPU_access(monkeypatch):
    import models.final_test_runtime as runtime
    monkeypatch.setattr(runtime.subprocess,'run',lambda *a,**k:SimpleNamespace(returncode=128,stdout=b''))
    monkeypatch.setattr(runtime,'sha',lambda p:pytest.fail('Data accessed before tag'))
    with pytest.raises(RuntimeError,match='commit and tag'):runtime.authorize()


def test_positive_tag_gate_checks_all_sources_and_rejects_code_drift(monkeypatch):
    import models.final_test_runtime as runtime
    inventory=json.loads(runtime.INVENTORY.read_text())
    monkeypatch.setattr(runtime.platform,'system',lambda:'Windows')
    monkeypatch.setattr(runtime.platform,'node',lambda:inventory['hardware']['computer'])
    monkeypatch.setattr(runtime.platform,'platform',lambda:inventory['hardware']['os'])
    monkeypatch.setattr(runtime.platform,'python_version',lambda:inventory['python'])
    def tagged(args,**kwargs):
        path=args[2].split(':',1)[1]
        return SimpleNamespace(returncode=0,stdout=Path(path).read_bytes())
    monkeypatch.setattr(runtime.subprocess,'run',tagged)
    permit=runtime.authorize()
    assert permit.max_month=='2024-09' and permit.spec['seed_split'] is False
    original=tagged
    def altered(args,**kwargs):
        result=original(args,**kwargs)
        if args[2].endswith('src/models/final_test.py'):result.stdout+=b'\nchanged'
        return result
    monkeypatch.setattr(runtime.subprocess,'run',altered)
    with pytest.raises(RuntimeError,match='Working file differs'):runtime.authorize()


@pytest.mark.parametrize('arguments',[['--boosting'],['--condition','real'],['--plan']])
def test_every_fit_CLI_mode_requires_tag_before_work(arguments,monkeypatch):
    import models.final_test as module
    monkeypatch.setattr('sys.argv',['final_test',*arguments])
    monkeypatch.setattr(module,'authorize',lambda:(_ for _ in ()).throw(RuntimeError('tag gate')))
    monkeypatch.setattr(module,'run_one',lambda *a:pytest.fail('Work before tag'))
    with pytest.raises(RuntimeError,match='tag gate'):module.main()


def test_evaluation_CLI_requires_tag_before_work(monkeypatch):
    import evaluation.final_test as module
    monkeypatch.setattr('sys.argv',['final_test','--run'])
    monkeypatch.setattr(module,'authorize',lambda:(_ for _ in ()).throw(RuntimeError('tag gate')))
    monkeypatch.setattr(module,'run',lambda *a:pytest.fail('Evaluation before tag'))
    with pytest.raises(RuntimeError,match='tag gate'):module.main()


def test_scheduler_on_validation_dates_has_no_duplicate_fit_identities():
    rows=calendar('2018-11','2019-10');seen=[]
    def fake(origin,seed,dates):
        seen.append((origin,seed));return np.ones((3,3,12))*seed,{'fit_seconds':1}
    values,records=execute_calendar(rows,[11,29,47],fake)
    assert len(seen)==len(set(seen))==12 and len(records)==12
    assert all(a.shape==(12,3,12) for a in values.values())


def tiny_context():
    from evaluation.gate_c_metrics import Context
    origins=pd.period_range('2018-11',periods=36,freq='M').astype(str).to_numpy()
    truth=np.ones((36,3,12))*5
    return Context(origins,np.array(['0001','0002','0003']),truth,np.ones((36,3)),np.tile([0,1,2],(36,1)),np.array([[0,1]]),origins)


def test_each_chain_stops_at_first_non_rejection_and_never_tests_later_ids():
    s=spec();ctx=tiny_context();point={name:np.full(ctx.truth.shape,i+1.) for i,name in enumerate(('combination','gradient_boosting_own','gradient_boosting_neighbours','B2_real','B2_without_base'))}
    calls=[]
    def fake(a,b,h,ni):
        calls.append((h,ni));p=.5 if len(calls) in (2,4) else .001
        return {'candidate_loss':1.,'reference_loss':2.,'gain_reference_minus_candidate':1.,'gain_percent':50.,'mean_test_differential':-1.,'dm_statistic':-2.,'noninferiority_margin_slack':np.nan,'p_lower_loss':p,'status':'defined'}
    result=chains(point,ctx,s,fake)
    assert len(calls)==4
    assert result.loc[result.chain.eq('Accuracy'),'status'].tolist()==['rejected','not_rejected_stop']+['not_tested_after_stop']*5
    assert result.loc[result.chain.eq('Behavioural'),'status'].tolist()==['rejected','not_rejected_stop','not_tested_after_stop']
    assert result.loc[result.status.eq('not_tested_after_stop'),'p_one_sided'].isna().all()


def test_undefined_and_threshold_equality_stop_their_chain():
    s=spec();ctx=tiny_context();point={name:np.full(ctx.truth.shape,7.) for name in ('combination','gradient_boosting_own','gradient_boosting_neighbours','B2_real','B2_without_base')}
    calls=[]
    def undefined(*args):calls.append(1);raise ValueError('Undefined baseline/variance')
    result=chains(point,ctx,s,undefined)
    assert len(calls)==2 and result.status.eq('undefined_stop').sum()==2
    assert result.status.eq('not_tested_after_stop').sum()==8
    def equal(*args):
        return {'candidate_loss':1.,'reference_loss':2.,'gain_reference_minus_candidate':1.,'gain_percent':50.,'mean_test_differential':-1.,'dm_statistic':-2.,'noninferiority_margin_slack':np.nan,'p_lower_loss':.025,'status':'defined'}
    result=chains(point,ctx,s,equal)
    assert result.status.eq('rejected').sum()==0 and result.status.eq('not_rejected_stop').sum()==2


def test_forecast_ensemble_and_fixed_weights_have_no_test_target_argument():
    s=spec();ctx=tiny_context()
    values=forecast_ensembles({'a':{11:np.ones_like(ctx.truth),29:np.ones_like(ctx.truth)*2,47:np.ones_like(ctx.truth)*6}},[11,29,47])
    assert np.allclose(values['a'],3)
    result=fixed_combination(np.ones_like(ctx.truth)*10,np.ones_like(ctx.truth)*2,ctx.groups,s['weights'])
    assert result[0,0,0]==pytest.approx(2+8*.100818)
    assert result[0,2,11]==pytest.approx(2+8*.682345)


def test_interval_matches_approved_HLN_inversion():
    mean,lo,hi=hac_interval([1.,2,1,3,2,3],2)
    half=t.ppf(.975,5)*np.sqrt(1/12)/np.sqrt(5/9)
    assert mean==2 and lo==pytest.approx(2-half) and hi==pytest.approx(2+half)


def test_battery_grouping_uses_target_month_and_retains_coverage():
    ctx=tiny_context();point={'toy':ctx.truth+1}
    summary,coverage,cells=target_periods(point,ctx,'2019-07','2019-09')
    marked=coverage.loc[coverage.period.eq('synthetic_marked_months')]
    assert set(marked.target_month)=={'2019-07','2019-08','2019-09'}
    assert len(coverage)==36*12 and len(cells)==36*12*4
    assert summary.mae.eq(1).all()


def test_evaluation_receipt_rejects_changed_forecasts_on_resume(tmp_path):
    receipt(tmp_path,'approved',{'a':'hash1'})
    receipt(tmp_path,'approved',{'a':'hash1'})
    with pytest.raises(RuntimeError,match='inputs changed'):receipt(tmp_path,'approved',{'a':'hash2'})


def test_evaluation_does_not_open_targets_before_all_models_complete(monkeypatch,tmp_path):
    import evaluation.final_test as module
    import features.sealed_panel as loader
    from models.final_test_runtime import Permit
    monkeypatch.setattr(module,'ROOT',tmp_path)
    monkeypatch.setattr(module,'bind',lambda p:None)
    monkeypatch.setattr(module,'require_complete',lambda p:(_ for _ in ()).throw(RuntimeError('incomplete')))
    monkeypatch.setattr(loader,'load_prefix',lambda *a,**k:pytest.fail('Targets opened before release'))
    with pytest.raises(RuntimeError,match='incomplete'):module.run(Permit(spec(),{},'signature',{}))
