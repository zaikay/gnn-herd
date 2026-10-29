import json
from pathlib import Path

import numpy as np
import pytest

from evaluation.frozen import frozen_protocol
from evaluation.gnn_progress import journal_summary, write_progress
from models.gnn_validation import configurations, fit_name, selected_jobs, select_configuration, plan


def cfg():
    return frozen_protocol('protocol-v2')[0]


def test_validation_schedule_reuses_two_anchor_fits_and_keeps_exact_budget():
    config = cfg()
    assert len(configurations(config))==6
    tuning = {fit_name(i,11,anchor) for i in range(6) for anchor in config['splits']['tuning_origins']}
    selected = {fit_name(i,seed,origin) for i,seed,origin in selected_jobs(config,2)}
    assert len(tuning)==12 and len(selected)==36
    assert len(tuning & selected)==2 and len(tuning | selected)==46
    session_plan = plan(config,'real')
    assert session_plan['epochs_per_fit']==65
    assert session_plan['validation_origins']==36
    assert session_plan['last_validation_target']=='2022-10'
    assert not session_plan['switch_to_next_condition']
    assert session_plan['test_forecasts_or_losses']==0


def test_selection_averages_both_anchors_and_breaks_ties_by_index():
    assert select_configuration([[0,1,20,20,20,20],[4,3,20,20,20,20]],6)==0
    with pytest.raises(ValueError):
        select_configuration([[0]*6],6)
    with pytest.raises(ValueError):
        select_configuration([[np.nan]*6,[0]*6],6)


def test_progress_sums_attempts_not_duplicate_epoch_observations(tmp_path):
    config = cfg(); signature = 'test-signature'
    folder = tmp_path/'real'/fit_name(0,11,'2019-08'); folder.mkdir(parents=True)
    (folder/'manifest.json').write_text(json.dumps({'protocol_sha256':signature,'condition':'real','fit_origin':'2019-08'}))
    (folder/'complete.json').write_text(json.dumps({'epochs':65,'wall_seconds':50}))
    (folder/'checkpoint.pt').write_bytes(b'test-only-presence-marker')
    events = [{'session_id':'a','event':'epoch_end','attempt_seconds':10,'checkpoint_epoch':5},
              {'session_id':'a','event':'attempt_end','attempt_seconds':12,'checkpoint_epoch':5},
              {'session_id':'b','event':'attempt_end','attempt_seconds':38,'checkpoint_epoch':65}]
    (folder/'sessions.jsonl').write_text('\n'.join(json.dumps(row) for row in events)+'\n')
    assert journal_summary(folder/'sessions.jsonl')==(50,65,False)
    result = write_progress(config,signature,base=tmp_path,pilot_records=[{'wall_seconds':1000}],write=False)
    real = result['conditions'][0]
    assert real['completed_fits']==1
    assert real['measured_hours']==pytest.approx(50/3600)
    assert real['projection_source'].startswith('condition-specific')
    assert result['conditions'][1]['completed_fits']==0
    assert 'pilot fallback' in result['conditions'][1]['projection_source']


def test_progress_marks_open_or_truncated_attempt_time_as_lower_bound(tmp_path):
    path = tmp_path/'sessions.jsonl'
    path.write_text(json.dumps({'session_id':'a','event':'epoch_end','attempt_seconds':4,'checkpoint_epoch':0})+'\n{')
    assert journal_summary(path)==(4,0,True)
