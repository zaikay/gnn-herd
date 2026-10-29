"""Validation-only metrics and comparisons; no model fitting."""
import json
from pathlib import Path

import numpy as np
import pandas as pd

from evaluation.dm import dm_from_losses
from evaluation.protocol import maturity_groups, seasonal_scales, splits

OUTCOMES = ('1', '6', '12', 'total_12')
MODELS = ('seasonal_naive', 'gradient_boosting_own', 'gradient_boosting_neighbours')


def validation_rows(cfg):
    return splits(cfg).loc[lambda f: f.block.eq('validation')].reset_index(drop=True)


def mase_scales(panel, refit, cfg):
    values = panel.targets[panel.observed]
    scales = seasonal_scales(values, panel.months, refit, cfg['metrics']['mase']['scale_targets_start'])
    fallback = float(scales[scales > 0].mean()) if (scales > 0).any() else 1.0
    return np.where(scales > 0, scales, fallback)


def seasonal_predictions(builder, origins):
    result = []
    for origin in origins:
        t = builder.panel.index(origin)
        # h=1 uses o-11; h=12 uses o. No validation target is used as an input.
        result.append(builder.values[builder.panel.observed, t-11:t+1])
    return np.stack(result).astype(np.float32)


def holm(values):
    p = np.asarray(values, dtype=float)
    output = np.full(len(p), np.nan)
    valid = np.flatnonzero(np.isfinite(p))
    order = valid[np.argsort(p[valid], kind='stable')]
    previous = 0.0
    for rank, index in enumerate(order):
        previous = max(previous, min(1.0, (len(p)-rank)*p[index]))
        output[index] = previous
    return output


def evaluate(panel, builder, predictions, cfg, output):
    output = Path(output)
    output.mkdir(parents=True, exist_ok=True)
    rows = validation_rows(cfg)
    origins = rows.origin.tolist()
    truth = np.stack([builder.targets(origin) for origin in origins])
    if any(str(pd.Period(o, freq='M')+12) > cfg['splits']['test']['first_origin'] for o in origins):
        raise ValueError('Validation targets crossed sealed test boundary')
    scales = np.stack([mase_scales(panel, date, cfg) for date in rows.fit_origin])
    groups = np.stack([maturity_groups(builder.base[panel.observed, panel.index(o)], panel.codes[panel.observed]) for o in origins])
    origin_records, area_records = [], []
    for model in MODELS:
        seed_losses = []
        for seed in cfg['tuning']['seeds']:
            prediction = predictions[model].get(seed, predictions[model].get(0))
            if prediction is None or prediction.shape != truth.shape:
                raise ValueError(f'Missing or misaligned predictions: {model}, seed {seed}')
            if not np.isfinite(prediction).all() or (prediction < 0).any():
                raise ValueError('Predictions must be finite nonnegative unrounded counts')
            errors = np.stack([np.abs(prediction[:, :, h-1]-truth[:, :, h-1]) for h in (1,6,12)] +
                              [np.abs(prediction.sum(axis=2)-truth.sum(axis=2))], axis=2)
            seed_losses.append(errors)
            for t, row in enumerate(rows.itertuples()):
                for k, outcome in enumerate(OUTCOMES):
                    scale = scales[t] * (12 if outcome == 'total_12' else 1)
                    for group_id, label in ((None,'all'), (0,'low'), (1,'medium'), (2,'high')):
                        use = np.ones(len(scale), dtype=bool) if group_id is None else groups[t] == group_id
                        if not use.any():
                            continue
                        origin_records.append({'model':model, 'seed':seed, 'origin':row.origin,
                            'fit_origin':row.fit_origin, 'outcome':outcome, 'group':label, 'areas':int(use.sum()),
                            'mae':float(errors[t, use, k].mean()), 'mase':float((errors[t, use, k]/scale[use]).mean())})
        mean_errors = np.mean(seed_losses, axis=(0,1))
        mean_scaled = np.mean(np.stack(seed_losses)/scales[None, :, :, None] /
                              np.array([1,1,1,12])[None,None,None,:], axis=(0,1))
        for i, code in enumerate(panel.codes[panel.observed]):
            for k, outcome in enumerate(OUTCOMES):
                area_records.append({'model':model, 'postcode':code, 'outcome':outcome,
                                     'mae':float(mean_errors[i,k]), 'mase':float(mean_scaled[i,k])})
    origin = pd.DataFrame(origin_records)
    per_seed = origin.groupby(['model','seed','outcome','group'], as_index=False)[['mae','mase']].mean()
    scores = per_seed.groupby(['model','outcome','group']).agg(
        mae=('mae','mean'), mase=('mase','mean'), mae_seed_sd=('mae','std'), mase_seed_sd=('mase','std')).reset_index()
    origin.to_csv(output/'origin_metrics.csv', index=False)
    per_seed.to_csv(output/'seed_metrics.csv', index=False)
    scores.to_csv(output/'scores.csv', index=False)
    pd.DataFrame(area_records).to_csv(output/'area_metrics.csv', index=False)
    return origin, scores


def compare(origin_metrics, output, dm=dm_from_losses):
    frame = origin_metrics.loc[origin_metrics.group.eq('all')].groupby(
        ['model','outcome','origin']).mae.mean()
    records = []
    pairs = [('gradient_boosting_neighbours','gradient_boosting_own'),
             ('gradient_boosting_own','seasonal_naive'), ('gradient_boosting_neighbours','seasonal_naive')]
    for a, b in pairs:
        for outcome in OUTCOMES:
            left, right = frame.loc[(a,outcome)], frame.loc[(b,outcome)]
            right = right.reindex(left.index)
            if right.isna().any():
                raise ValueError('Comparison origins differ')
            record = {'model_a':a, 'model_b':b, 'outcome':outcome, 'origins':len(left),
                      'h':12 if outcome == 'total_12' else int(outcome), 'statistic':np.nan, 'p_raw':np.nan}
            try:
                statistic, p = dm(left.to_numpy(), right.to_numpy(), record['h'])
                if not np.isfinite(statistic) or not np.isfinite(p):
                    raise ValueError('Nonfinite DM result')
                record.update(statistic=float(statistic), p_raw=float(p), status='defined')
            except (ArithmeticError, ValueError) as error:
                record['status'] = 'undefined: ' + str(error)
            records.append(record)
    result = pd.DataFrame(records)
    result['p_holm'] = holm(result.p_raw)
    result['family_size'] = len(result)
    result.to_csv(Path(output)/'dm_tests.csv', index=False)
    return result
