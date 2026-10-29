import numpy as np
import pandas as pd
import pytest

from evaluation.protocol import config, splits, maturity_groups, seasonal_scales, fit_budget, training_calendar


def test_approved_splits_respect_cutoff_and_masked_training_bounds():
    cfg = config()
    result = splits(cfg)
    val = result.loc[result.block.eq('validation')]
    test = result.loc[result.block.eq('test')]
    assert len(val) == 36 and len(test) == 24
    assert val.last_target.max() <= test.origin.min()
    assert test.last_target.max() <= cfg['data']['evaluation_cutoff']
    for row in result.itertuples():
        assert pd.Period(row.latest_training_sample_origin, freq='M') + 1 == pd.Period(row.fit_origin, freq='M')
        assert pd.Period(row.latest_sample_with_all_12_targets, freq='M') + 12 == pd.Period(row.fit_origin, freq='M')
        assert pd.Period(row.fit_origin, freq='M') <= pd.Period(row.origin, freq='M')
        assert pd.Period(row.origin, freq='M') + 1 == pd.Period(row.first_target, freq='M')
    alt = cfg['splits']['alternative_horizon_24']
    assert not alt['enabled']
    assert pd.Period(alt['validation_last_origin'], freq='M') + 24 <= pd.Period(alt['test_first_origin'], freq='M')
    assert pd.Period(alt['test_last_origin'], freq='M') + 24 <= pd.Period(cfg['data']['evaluation_cutoff'], freq='M')



def test_training_scale_is_invariant_to_future_changes():
    months = pd.period_range('2001-04', '2012-12', freq='M').astype(str).to_numpy()
    values = np.vstack([np.zeros(len(months)), np.arange(len(months))])
    before = seasonal_scales(values, months, '2011-06')
    values[:, months > '2011-06'] = 999999
    after = seasonal_scales(values, months, '2011-06')
    np.testing.assert_array_equal(before, after)
    assert before[0] == 0 and before[1] == 12



def test_maturity_ties_keep_codes_and_equal_group_counts():
    codes = ['3000', '2000', '0800', '5000', '6000', '7000']
    result = maturity_groups(np.zeros(6), codes)
    assert result.tolist() == [1, 0, 0, 1, 2, 2]
    assert np.bincount(result).tolist() == [2, 2, 2]



def test_equal_configuration_budgets_and_no_automatic_early_stopping():
    from evaluation.frozen import frozen_protocol
    cfg,_ = frozen_protocol('protocol-v1.1',require_working=False)
    tune = cfg['tuning']
    gb, gnn = tune['gradient_boosting_grid'], tune['gnn_grid']
    assert len(gb['learning_rate']) * len(gb['max_leaf_nodes']) * len(gb['l2_regularization']) == 6
    assert len(gnn['hidden_size']) * len(gnn['learning_rate']) * len(gnn['weight_decay']) == 6
    assert tune['configurations_per_tunable_condition'] == 6
    assert not gb['early_stopping'] and not tune['early_stopping']
    assert not cfg['gnn_design']['implemented']
    assert cfg['status'] == 'approved_pending_commit_and_tag'



def test_recommended_budget_counts_reused_anchor_fits():
    from evaluation.frozen import frozen_protocol
    cfg,_ = frozen_protocol('protocol-v1.1',require_working=False)
    assert fit_budget(cfg) == {'tuning_fits': 12, 'evaluation_fits': 36, 'reused_fits': 2,
                               'unique_fits': 46, 'validation_refits': 12}
    assert splits(cfg).loc[lambda f: f.block.eq('test'), 'fit_origin'].nunique() == 8
    assert cfg['tuning']['timing_pilot']['full_workload_requires_measured_budget_approval']
    pilot = cfg['tuning']['timing_pilot']
    assert pilot['hidden_widths'] == [32, 96]
    assert pilot['origin'] in cfg['splits']['tuning_origins']
    assert pilot['epochs'] == cfg['tuning']['max_gnn_epochs'] == 75
    assert pilot['minimum_fits'] == 2 and pilot['maximum_fits'] == 4
    assert pilot['projected_three_gnn_conditions_limit_gpu_hours'] == 24



def test_training_mask_uses_each_observed_target_for_every_horizon():
    sample, mask = training_calendar('2011-03', '2011-01', horizons=3)
    assert sample.astype(str).tolist() == ['2010-10', '2010-11', '2010-12', '2011-01', '2011-02']
    np.testing.assert_array_equal(mask, [[False, False, True], [False, True, True],
                                       [True, True, True], [True, True, False], [True, False, False]])
    assert mask.sum(axis=0).tolist() == [3, 3, 3]
    for i, origin in enumerate(sample):
        for h in range(1, 4):
            if mask[i, h-1]:
                assert pd.Period('2011-01', freq='M') <= origin+h <= pd.Period('2011-03', freq='M')
