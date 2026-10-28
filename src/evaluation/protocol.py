"""Approved protocol calendar, training eligibility and scoring helpers; no plotting or model runs."""
from pathlib import Path

import numpy as np
import pandas as pd
import yaml


def config():
    return yaml.safe_load(Path('configs/experiments.yaml').read_text(encoding='utf-8'))



def origins(first, last):
    return pd.period_range(first, last, freq='M')



def splits(cfg):
    result = []
    for block in ('validation', 'test'):
        values = cfg['splits'][block]
        block_origins = origins(values['first_origin'], values['last_origin'])
        interval = cfg['tuning']['refit_interval_months']
        for position, origin in enumerate(block_origins):
            fit_origin = block_origins[(position // interval) * interval]
            result.append({'block': block, 'origin': str(origin),
                           'first_target': str(origin + 1), 'last_target': str(origin + 12),
                           'fit_origin': str(fit_origin),
                           'latest_training_sample_origin': str(fit_origin - 1),
                           'latest_sample_with_all_12_targets': str(fit_origin - 12)})
    return pd.DataFrame(result)



def fit_budget(cfg):
    dates = splits(cfg)
    validation = dates.loc[dates.block.eq('validation')]
    refits = validation.fit_origin.nunique()
    anchors = cfg['splits']['tuning_origins']
    if not set(anchors).issubset(set(validation.fit_origin)):
        raise ValueError('Tuning anchors must be scheduled refits')
    seed_overlap = len(set(cfg['tuning']['seeds']) & set(cfg['tuning']['tuning_seeds']))
    tuning = cfg['tuning']['configurations_per_tunable_condition'] * len(cfg['tuning']['tuning_seeds']) * len(anchors)
    evaluation = refits * len(cfg['tuning']['seeds'])
    reused = len(anchors) * seed_overlap
    return {'tuning_fits': tuning, 'evaluation_fits': evaluation, 'reused_fits': reused,
            'unique_fits': tuning + evaluation - reused, 'validation_refits': int(refits)}



def target_eligibility(sample_origins, fit_origin, first_target='2011-01', horizons=12):
    """Protocol calendar mask only; not a model panel or feature builder."""
    sample = pd.PeriodIndex(sample_origins, freq='M').asi8
    targets = sample[:, None] + np.arange(1, horizons + 1)[None, :]
    return (targets <= pd.Period(fit_origin, freq='M').ordinal) & (targets >= pd.Period(first_target, freq='M').ordinal)



def training_calendar(fit_origin, first_target='2011-01', horizons=12):
    sample_origins = pd.period_range(pd.Period(first_target, freq='M')-horizons,
                                    pd.Period(fit_origin, freq='M')-1, freq='M')
    return sample_origins, target_eligibility(sample_origins, fit_origin, first_target, horizons)



def maturity_groups(base, codes):
    order = np.lexsort((np.asarray(codes), np.asarray(base)))
    groups = np.empty(len(order), dtype=int)
    groups[order] = np.minimum(np.arange(len(order)) * 3 // len(order), 2)
    return groups



def seasonal_scales(values, months, origin, start='2011-01', lag=12):
    """Training diagnostic only, not forecast evaluation."""
    indices = np.flatnonzero((months >= start) & (months <= origin))
    indices = indices[indices >= lag]
    if not len(indices):
        raise ValueError('No training targets with historical reference')
    return np.mean(np.abs(values[:, indices] - values[:, indices-lag]), axis=1)
