import json
from pathlib import Path

import numpy as np
import pytest

from evaluation.gate_c_io import comparison_release,load_gnn_predictions,read_prediction
from evaluation.gate_c_fixtures import synthetic_fixture


def test_no_gnn_array_is_opened_before_fourth_condition_release(tmp_path,monkeypatch):
    ctx,_=synthetic_fixture()
    def forbidden(*args,**kwargs):raise AssertionError('GNN forecast accessed before release')
    monkeypatch.setattr(np,'load',forbidden)
    with pytest.raises(RuntimeError,match='withheld'):
        load_gnn_predictions({},ctx,'test',campaign=tmp_path)


def test_completed_fourth_opens_twenty_test_case(tmp_path):
    root=tmp_path/'real_without_installed_base'; root.mkdir()
    (root/'condition_complete.json').write_text(json.dumps({'condition':'real_without_installed_base','unique_fits':46,'seeds':[11,29,47],'test_forecasts_or_losses':0}))
    included,proof=comparison_release(tmp_path)
    assert included and proof['basis']=='fourth condition complete'


def test_formal_drop_is_required_for_sixteen_test_case(tmp_path):
    path=tmp_path/'drop.json'
    path.write_text(json.dumps({'condition':'real_without_installed_base','decision':'drop','approved_by':'researcher','date':'2026-10-31','reason':'time budget'}))
    included,proof=comparison_release(tmp_path,path)
    assert not included and proof['reason']=='time budget'
    path.write_text(json.dumps({'decision':'drop','approved_by':'agent'}))
    with pytest.raises(RuntimeError,match='researcher'):comparison_release(tmp_path,path)


def test_invalid_completion_marker_cannot_release_comparisons(tmp_path):
    root=tmp_path/'real_without_installed_base'; root.mkdir()
    (root/'condition_complete.json').write_text('{}')
    with pytest.raises(RuntimeError,match='invalid'):comparison_release(tmp_path)


def test_prediction_identifiers_cannot_be_reordered_or_partially_missing(tmp_path):
    ctx,predictions=synthetic_fixture()
    values=predictions['seasonal_naive'][11]
    path=tmp_path/'prediction.npz'
    np.savez(path,prediction=values,codes=ctx.codes[::-1],origins=ctx.origins)
    with pytest.raises(AssertionError):read_prediction(path,ctx)
    np.savez(path,prediction=values,codes=ctx.codes)
    with pytest.raises(ValueError,match='Partially'):read_prediction(path,ctx,allow_legacy=True)
    np.savez(path,prediction=values,codes=ctx.codes,origins=ctx.origins)
    np.testing.assert_array_equal(read_prediction(path,ctx),values)
