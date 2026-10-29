import numpy as np
import pytest

from evaluation.frozen import frozen_protocol
from evaluation.pilot_report import scheduled_fits, project


def test_projection_counts_reuse_and_future_calendar_without_targets():
    cfg,_ = frozen_protocol('protocol-v1.1',require_working=False)
    fits = scheduled_fits(cfg)
    assert fits.groupby('block').size().to_dict() == {
        'validation_tuning':12,'validation_selected':34,'future_test_calendar_only':24}
    assert fits.loc[fits.fit_origin.eq('2020-08'),'batches_per_epoch'].eq(64).all()
    assert fits.loc[fits.block.eq('future_test_calendar_only'),'batches_per_epoch'].min()>64


def test_projection_margin_and_epoch_changes_never_rescale_spent_pilot():
    cfg,_ = frozen_protocol('protocol-v1.1',require_working=False)
    fits = scheduled_fits(cfg)
    full = project(fits,3600,1000,64,3)
    reduced = project(fits,3600,1000,64,3,epochs=20)
    assert full['total_hours_with_margin'] == pytest.approx(full['full_fit_hours']*1.2+1)
    assert reduced['full_fit_hours']/full['full_fit_hours'] == pytest.approx(20/75)
    assert full['pilot_hours_already_spent']==reduced['pilot_hours_already_spent']==1
    assert np.isfinite(reduced['total_hours_with_margin'])
