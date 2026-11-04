"""EXPLORATORY synthetic checks for exact halves and pooled RMSE."""
import numpy as np
import pandas as pd
import pytest
from evaluation.test_exploratory_halves import half_scores,MODELS,REPORTED

def fixture():
    return pd.DataFrame([dict(model=m,outcome=h,group='all',origin=str(o),mae=i+1,mase=1,mse=(i+1)**2,mean_signed_error=-(i+1)) for m in MODELS for h in REPORTED for i,o in enumerate(pd.period_range('2022-10','2024-09',freq='M'))])

def test_exact_half_boundaries_and_root_after_pooling():
    d=half_scores(fixture());assert len(d)==64 and d.origins.eq(12).all()
    a=d.loc[d.first_origin.eq('2022-10')].iloc[0];b=d.loc[d.first_origin.eq('2023-10')].iloc[0]
    assert a.mae==6.5 and b.mae==18.5
    assert a.rmse==pytest.approx(np.sqrt(np.mean(np.arange(1,13)**2)))
    assert b.mean_signed_error==-18.5

def test_incomplete_or_duplicate_cells_rejected():
    d=fixture()
    with pytest.raises(ValueError):half_scores(d.iloc[1:])
    with pytest.raises(ValueError):half_scores(pd.concat([d,d.iloc[:1]]))
