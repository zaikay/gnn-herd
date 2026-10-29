import numpy as np
import pandas as pd
import pytest

from evaluation.amendment import pooled_rmse, error_arrays, row_moran, national_revision
from evaluation.protocol import config
from evaluation.frozen import frozen_protocol


def test_root_after_pooling_and_signed_total():
    assert pooled_rmse([0, 18]) == 3
    prediction = np.array([[[0, 4], [4, 0]]],dtype=np.float32)
    actual = np.array([[[1, 1], [1, 1]]],dtype=np.float64)
    errors,total = error_arrays(prediction,actual)
    np.testing.assert_array_equal(errors,[[[-1,3],[3,-1]]])
    np.testing.assert_array_equal(total,[[2,2]])
    assert pooled_rmse(errors**2) == pytest.approx(np.sqrt(5))
    # Averaging the two predictions before scoring would instead give RMSE 1.


def test_moran_hand_computed_and_undefined():
    assert row_moran([0,1,2],[[0,1],[1,2]]) == 0
    assert row_moran([0,2],[[0,1]]) == -1
    assert row_moran([1,1],[[0,1]]) is None
    assert row_moran([0,1],[]) is None


def test_national_revision_all_postcodes_exact_window():
    frame = pd.DataFrame([(p,f'2025-{m:02d}',10) for p in ('0800','9999') for m in range(1,10)],
                         columns=['postcode','month','count'])
    result = national_revision(frame,reference=150)
    assert result['current_count_systems'] == 180
    assert result['increase_systems'] == 30
    assert result['growth_percent'] == pytest.approx(20)
    with pytest.raises(ValueError):
        national_revision(pd.concat([frame,frame.iloc[:1]]))
    with pytest.raises(ValueError):
        national_revision(frame.loc[frame.month.ne('2025-09')])
    with pytest.raises(ValueError):
        national_revision(frame.iloc[1:])


def test_amendment_keeps_fitting_protocol_and_disables_optional():
    old,_ = frozen_protocol(require_working=False)
    new,_ = frozen_protocol('protocol-v1.1',require_working=False)
    for key in ('data','splits','horizons','objective','features','tuning','state_assignment'):
        assert new[key] == old[key]
    assert new['metrics']['primary'] == 'MAE'
    assert new['metrics']['secondary'] == ['MASE','RMSE']
    assert new['metrics']['dm']['comparisons'] == old['metrics']['dm']['comparisons']
    assert new['metrics']['dm']['task3']['family_size'] == 16
    assert new['metrics']['dm']['task3']['family_size_if_optional_approved'] == 20
    assert not new['gnn_design']['optional_condition']['enabled']
    assert new['gnn_design']['graph_conditions'] == old['gnn_design']['graph_conditions']
    with pytest.raises(RuntimeError,match='differs'):
        frozen_protocol()
