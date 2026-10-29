import hashlib
import json
from pathlib import Path

import pandas as pd
import pytest

from evaluation.epoch_selection import select_epoch
from evaluation.frozen import frozen_protocol
from evaluation.protocol import config


def test_v2_keeps_data_dates_objective_grids_and_seed_budget():
    old,_ = frozen_protocol('protocol-v1.1',require_working=False)
    cfg = config()
    assert cfg['protocol']=='protocol-v2'
    for key in ('data','splits','horizons','metrics','objective','features','state_assignment'):
        assert cfg[key]==old[key]
    for key in ('seeds','tuning_seeds','gradient_boosting_grid','gnn_grid','refit_interval_months','configurations_per_tunable_condition'):
        assert cfg['tuning'][key]==old['tuning'][key]
    assert cfg['tuning']['max_gnn_epochs']==65
    assert cfg['tuning']['sessions']['gpu_hour_limit'] is None
    assert cfg['tuning']['timing_pilot']['projected_three_gnn_conditions_limit_gpu_hours'] is None
    assert cfg['tuning']['checkpoints']['interval_epochs']==5
    assert cfg['tuning']['checkpoints']['retain_completed_fit_checkpoint']
    assert cfg['gnn_design']['run_order']==['real','within_state_shuffled','no_graph','real_without_installed_base']
    assert cfg['gnn_design']['optional_condition']['enabled']


def test_epoch_choice_reproduces_original_training_only_pilot_hashes():
    evidence = json.loads(Path('reports/protocol/protocol_v2_epoch_selection.json').read_text())
    epochs = []
    for item in evidence['pilot_widths']:
        source = Path(item['source'])
        if not source.exists():
            pytest.skip('Private pilot CSVs are not distributed with the repository')
        assert hashlib.sha256(source.read_bytes()).hexdigest()==item['sha256']
        epoch,_ = select_epoch(pd.read_csv(source))
        assert epoch==item['first_epoch_98_percent']
        epochs.append(epoch)
    assert epochs==[63,60]
    assert evidence['fixed_epochs']==65
    assert not evidence['uses_validation_or_test_scores']
