import numpy as np
import pandas as pd
import pytest
from evaluation.combination_validation import equal_weight,compare_combinations,dm_family
from evaluation.gate_c_fixtures import synthetic_fixture
from evaluation.gate_c_metrics import evaluate


def test_seed_pairing_and_equal_count_average():
    a={s:np.array([float(s)]) for s in (11,29,47)}
    b={s:np.array([float(s+2)]) for s in (11,29,47)}
    combined=equal_weight(a,b)
    for seed in a:
        assert combined[seed][0]==seed+1 and combined[seed].dtype==np.float64
    with pytest.raises(ValueError):equal_weight({11:a[11]},b)


def fixture_results():
    ctx,pred=synthetic_fixture()
    values={'gradient_boosting_own':pred['gradient_boosting_own'],'gnn_real':pred['gnn_real']}
    values['half_own_B']=equal_weight(values['gradient_boosting_own'],values['gnn_real'])
    values['half_neighbour_B']=equal_weight(pred['gradient_boosting_neighbours'],values['gnn_real'])
    return evaluate(values,ctx)


def test_sixteen_test_family_and_whole_family_holm():
    assert len(set(dm_family()))==16
    assert {r for c,r,h in dm_family()}=={'gradient_boosting_own','gnn_real'}
    result=compare_combinations(fixture_results()['origin'],dm=lambda *args:(-1.,.01))
    assert result.family_size.eq(16).all()
    np.testing.assert_allclose(result.p_holm,.16)


def test_undefined_comparison_keeps_family_slot():
    calls=[]
    def toy_dm(*args):
        calls.append(1)
        if len(calls)==1:raise ValueError('constant difference')
        return -1.,.01
    result=compare_combinations(fixture_results()['origin'],dm=toy_dm)
    assert result.iloc[0].status.startswith('undefined') and np.isnan(result.iloc[0].p_holm)
    np.testing.assert_allclose(result.p_holm.iloc[1:],.16)


def test_total_error_sums_months_before_absolute_value():
    ctx,pred=synthetic_fixture(); a={s:ctx.truth.copy() for s in (11,29,47)}
    b={s:ctx.truth.copy() for s in (11,29,47)}
    for seed in a:
        a[seed][:,:,0]+=2; b[seed][:,:,1]+=2
    result=evaluate({'mixed':equal_weight(a,b)},ctx)['scores']
    total=result.loc[result.outcome.eq('total_12')&result.group.eq('all')].iloc[0]
    assert total.mae==2
    assert total.mae_seed_sd==0


def test_cost_projection_uses_calendar_and_supplied_records_only(monkeypatch):
    from evaluation.final_test_cost import project
    monkeypatch.setattr(np,'load',lambda *args,**kwargs:pytest.fail('Cost must not read target/panel arrays'))
    cfg={'splits':{'training_first_target':'2011-01','validation':{'first_origin':'2020-01','last_origin':'2020-12'},
                   'test':{'first_origin':'2022-10','last_origin':'2024-09'}},'tuning':{'refit_interval_months':3,'seeds':[11,29,47]}}
    records=[{'condition':'real','seed':s,'fit_origin':o,'fit_seconds':65*60,'seconds':60.,'rows':1000}
             for s in (11,29,47) for o in ('2020-01','2020-04','2020-07','2020-10')]
    calendar,detail,summary=project(cfg,pd.DataFrame(records),pd.DataFrame(records),3)
    assert len(calendar)==8 and calendar.fit_origin.iloc[0]=='2022-10' and calendar.fit_origin.iloc[-1]=='2024-07'
    assert len(detail)==48 and summary.fits.tolist()==[24,24]
    assert (summary.hours_low<=summary.hours_central).all() and (summary.hours_central<=summary.hours_high).all()
