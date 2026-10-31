import numpy as np
import pandas as pd

from evaluation.gate_c_findings import findings
from evaluation.gate_c_metrics import REPORTED


def data(real_errors):
    rows=[]; tests=[]
    for h,real in zip(REPORTED,real_errors):
        for model,mae in (('gnn_real',real),('gnn_shuffled',2.),('gnn_no_graph',1.)):
            rows.append({'model':model,'outcome':h,'group':'all','mae':mae,'mase':mae/2})
        tests.append({'model_a':'gnn_real','model_b':'gnn_shuffled','outcome':h,'p_holm':.03})
    return pd.DataFrame(rows),pd.DataFrame(tests)


def test_negative_gate_c_does_not_reverse_the_comparison_direction():
    scores,dm=data([3.,3.,3.,3.])
    answer,frame=findings(scores,dm)
    assert answer.startswith('No:')
    assert frame.mae_direction.eq('higher').all() and frame.mase_direction.eq('higher').all()
    np.testing.assert_allclose(frame.real_minus_shuffled_mae_percent,50)


def test_mixed_outcomes_are_not_called_uniformly_negative_or_positive():
    scores,dm=data([1.,3.,1.,3.])
    answer,_=findings(scores,dm)
    assert 'mixed' in answer
