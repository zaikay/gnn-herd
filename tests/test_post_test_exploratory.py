"""Synthetic checks for EXPLORATORY post-test statistics."""
import numpy as np
import pandas as pd
import pytest
from evaluation.test_exploratory import scores,gains,compare

def fixture():
    records=[]
    for model,offset in [('a',0),('b',1)]:
        for i in range(24):
            loss=2+offset+i/20+(.15 if i%2 else -.1)
            records.append(dict(model=model,origin=f'{2020+i//12}-{i%12+1:02}',outcome='1',group='all',mae=loss,mase=loss/2,mse=loss**2,mean_signed_error=-loss))
    return pd.DataFrame(records)

def test_pooled_rmse_and_ties_flagged():
    d=fixture();s=scores(d);a=d.loc[d.model.eq('a')]
    assert s.loc[s.model.eq('a'),'rmse'].iloc[0]==pytest.approx(np.sqrt(a.mse.mean()))
    result=gains(s,('a',),('a',));assert result.not_lower.all();assert result.gain_percent.eq(0).all()

def test_dm_direction_and_interval_match_differential():
    d=fixture();d.loc[d.model.eq('b'),'mae']+=np.sin(np.arange(24))*.2
    x=compare(d,[('a','b')],outcomes=('1',)).iloc[0]
    assert x.gain_percent>0 and x.mean_MAE_difference<0 and x.p_lower_loss<x.p_two_sided
    assert x.lower95<x.mean_MAE_difference<x.upper95

def test_alignment_rejects_missing_or_duplicate_origins():
    d=fixture()
    with pytest.raises(ValueError):compare(d.iloc[:-1],[('a','b')],outcomes=('1',))
    with pytest.raises(ValueError):compare(pd.concat([d,d.iloc[:1]]),[('a','b')],outcomes=('1',))
