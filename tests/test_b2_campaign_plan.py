import numpy as np
import pandas as pd
import pytest
from evaluation import b2_campaign_plan as plan


def test_graph_only_main_and_conditional_inclusion():
    result=plan.graph_screen_decision(4.,3.8,3.95)
    assert result['main']=='learned' and result['include_learned_and_identity']
    result=plan.graph_screen_decision(4.,4.1,3.95)
    assert result['main']=='real' and not result['include_learned_and_identity']
    assert plan.graph_screen_decision(4.,4.,4.2)['main']=='real'


def test_identity_safeguard_and_real_fallback():
    result=plan.graph_screen_decision(4.,3.97,3.96)
    assert not result['requires_researcher_review'] and result['main']=='real'
    assert not result['include_learned_and_identity']
    for learned in (3.8,4.1):
        result=plan.graph_screen_decision(4.,learned,3.92)
        assert result['requires_researcher_review'] and result['main'] is None
    assert plan.graph_screen_decision(0.,0.,0.)['main']=='real'


def test_families_are_unique_whole_20_or_28():
    core=plan.dm_family('real',False); extended=plan.dm_family('learned',True)
    assert len(core)==len(set(core))==20
    assert len(extended)==len(set(extended))==28
    assert {b for a,b,h in extended}=={'no_graph','shuffled','gradient_boosting_own','gradient_boosting_neighbours','without_base','real','identity'}
    with pytest.raises(ValueError):plan.dm_family('learned',False)


@pytest.mark.parametrize('machines',[1,2,3])
@pytest.mark.parametrize('include',[False,True])
def test_seed_blocks_and_reuse_are_disjoint(machines,include,monkeypatch):
    dates=pd.period_range('2018-11',periods=12,freq='3M').astype(str)
    monkeypatch.setattr(plan,'validation_rows',lambda cfg:pd.DataFrame({'fit_origin':dates}))
    jobs=plan.job_plan({},include,machines)
    assert len(jobs)==(216 if include else 144)
    assert jobs.new_fit.sum()==(208 if include else 140)
    assert jobs.reuse_screen.sum()==(8 if include else 4)
    assert jobs.groupby('seed').machine.nunique().eq(1).all()
    assert jobs.loc[jobs.seed.eq(11),'machine'].eq('A').all()
    assert not jobs.duplicated(['condition','seed','fit_origin']).any()
