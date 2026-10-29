import pytest

from evaluation.frozen import frozen_protocol
from models.gnn_pilot import pilot_plan


def test_pilot_is_exactly_two_fixed_training_only_configurations():
    cfg,_ = frozen_protocol('protocol-v1.1')
    plan = pilot_plan(cfg)
    assert [item['width'] for item in plan] == [32,96]
    assert all(item['seed']==11 and item['fit_origin']=='2020-08' and item['epochs']==75 for item in plan)
    assert all(item['condition']=='real' and item['learning_rate']==.001 and item['weight_decay']==.0001 for item in plan)
    cfg['tuning']['timing_pilot']['epochs'] = 10
    with pytest.raises(ValueError,match='approved'):
        pilot_plan(cfg)
