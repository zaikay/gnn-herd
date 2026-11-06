"""Synthetic EXPLORATORY frozen-mixture and period scoring tests."""
import numpy as np
import pandas as pd
import pytest
from evaluation.final_test_metrics import fixed_combination
from evaluation.test_exploratory_hybrids import period_scores

def test_frozen_mix_uses_origin_group_band_and_correct_orientation():
    a=np.full((2,3,12),10.);b=np.full_like(a,2.);groups=np.array([[0,1,2],[2,0,1]])
    weights={g:dict(zip(('1-3','4-6','7-12'),vals)) for g,vals in [('low',(0.,.1,.2)),('medium',(.3,.4,.5)),('high',(.6,.7,1.))]}
    c=fixed_combination(a,b,groups,weights)
    assert c[0,0,0]==2 and c[0,2,11]==10 and c[1,0,0]==pytest.approx(6.8)
    assert c[1,1,4]==pytest.approx(2.8)

def test_period_pooling_and_incomplete_calendar():
    d=pd.DataFrame([dict(model='hybrid',group='all',outcome='1',origin=str(o),mae=i+1,mase=1,mse=(i+1)**2,mean_signed_error=-i) for i,o in enumerate(pd.period_range('2022-10','2024-09',freq='M'))])
    x=period_scores(d).set_index('period');assert x.loc['first_half','mae']==6.5 and x.loc['second_half','mae']==18.5
    assert x.loc['full_test','rmse']==pytest.approx(np.sqrt(np.mean(np.arange(1,25)**2)))
    with pytest.raises(ValueError):period_scores(d.iloc[1:])
