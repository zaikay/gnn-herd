"""Read-only verification of completed validation artifacts; never refit models."""
import hashlib
from importlib.metadata import version
import json
from pathlib import Path
import re

import numpy as np
import pandas as pd

from evaluation.baselines import validation_rows, mase_scales, holm
from evaluation.dm import dm_from_losses
from evaluation.protocol import maturity_groups
from evaluation.result_report import completed_run
from features.panel import load_panel


def main():
    root,cfg,manifest,completion = completed_run()
    for name,expected in manifest['source_sha256'].items():
        if hashlib.sha256(Path(name).read_bytes()).hexdigest() != expected:
            raise ValueError(f'Run source changed: {name}')
    for name,expected in manifest['versions'].items():
        if version(name) != expected:
            raise ValueError(f'Run package changed: {name}')
    if hashlib.sha256(Path('data/processed/t02_panel.npz').read_bytes()).hexdigest() != manifest['panel_sha256']:
        raise ValueError('Panel hash differs from completed run')
    fits = pd.read_csv(root/'fit_records.csv')
    if fits.groupby('condition').size().to_dict() != {'gradient_boosting_own':46,'gradient_boosting_neighbours':46}:
        raise ValueError('Wrong fit count')
    if fits.duplicated(['condition','config_id','seed','fit_origin']).any() or not fits.device.eq('CPU').all():
        raise ValueError('Duplicate or non-CPU fit records')
    for row in fits.itertuples():
        path = root/f'{row.condition}_c{row.config_id}_seed{row.seed}_{row.fit_origin}.joblib'
        if not path.exists() or not path.with_suffix('.json').exists():
            raise ValueError('Missing checkpoint or metadata')
    rows = validation_rows(cfg)
    panel = load_panel(through=rows.last_target.max())
    observed = panel.observed
    truth = np.stack([panel.targets[observed,panel.index(o)+1:panel.index(o)+13].astype(np.float64) for o in rows.origin])
    scales = np.stack([mase_scales(panel,r,cfg) for r in rows.fit_origin])
    cumulative = np.cumsum(panel.inputs,axis=1,dtype=np.float64)
    groups = np.stack([maturity_groups(cumulative[observed,panel.index(o)],panel.codes[observed]) for o in rows.origin])
    origin = pd.read_csv(root/'origin_metrics.csv',dtype={'origin':str,'outcome':str})
    indexed = origin.set_index(['model','seed','origin','outcome','group'])
    if indexed.index.duplicated().any() or set(origin.origin) != set(rows.origin):
        raise ValueError('Wrong evaluation origin keys')
    checks = 0
    for model in ('seasonal_naive','gradient_boosting_own','gradient_boosting_neighbours'):
        if model != 'seasonal_naive':
            selection = json.loads((root/f'{model}_selection.json').read_text())
            if len(selection['anchor_scores_mae']) != 6 or selection['selected_config_id'] != int(np.argmin(selection['anchor_scores_mae'])):
                raise ValueError('Selection differs from frozen budget/tie break')
        for seed in cfg['tuning']['seeds']:
            path = root/'seasonal_naive.npz' if model == 'seasonal_naive' else root/f'{model}_seed{seed}.npz'
            with np.load(path,allow_pickle=False) as data:
                predictions = data['prediction']
                if model != 'seasonal_naive':
                    np.testing.assert_array_equal(data['codes'],panel.codes[observed])
                    np.testing.assert_array_equal(data['origins'],rows.origin.to_numpy(dtype='U7'))
            if predictions.shape != truth.shape or not np.isfinite(predictions).all() or (predictions<0).any():
                raise ValueError('Invalid stored predictions')
            if model == 'seasonal_naive':
                reference = np.stack([panel.inputs[observed,panel.index(o)-11:panel.index(o)+1] for o in rows.origin])
                np.testing.assert_array_equal(predictions,reference)
            for t,date in enumerate(rows.origin):
                for outcome,h in (('1',1),('6',6),('12',12),('total_12',None)):
                    error = np.abs(predictions[t].sum(axis=1)-truth[t].sum(axis=1)) if h is None else np.abs(predictions[t,:,h-1]-truth[t,:,h-1])
                    scaled = error/(scales[t]*(12 if h is None else 1))
                    for group_id,label in ((None,'all'),(0,'low'),(1,'medium'),(2,'high')):
                        use = np.ones(len(error),bool) if group_id is None else groups[t] == group_id
                        record = indexed.loc[(model,seed,date,outcome,label)]
                        np.testing.assert_allclose([record.mae,record.mase],[error[use].mean(),scaled[use].mean()],rtol=1e-10,atol=1e-10)
                        if int(record.areas) != int(use.sum()):
                            raise ValueError('Maturity-group membership count differs')
                        checks += 1
    seed_summary = origin.groupby(['model','seed','outcome','group'])[['mae','mase']].mean()
    expected = seed_summary.groupby(['model','outcome','group']).mean().sort_index()
    scores = pd.read_csv(root/'scores.csv',dtype={'outcome':str}).set_index(['model','outcome','group']).sort_index()
    np.testing.assert_allclose(scores[['mae','mase']],expected[['mae','mase']],rtol=1e-10,atol=1e-10)
    tests = pd.read_csv(root/'dm_tests.csv',dtype={'outcome':str})
    loss = origin.loc[origin.group.eq('all')].groupby(['model','outcome','origin']).mae.mean()
    recomputed = []
    for row in tests.itertuples():
        left = loss.loc[(row.model_a,row.outcome)]
        right = loss.loc[(row.model_b,row.outcome)].reindex(left.index)
        if row.status == 'defined':
            statistic,p = dm_from_losses(left.to_numpy(),right.to_numpy(),row.h)
            np.testing.assert_allclose([statistic,p],[row.statistic,row.p_raw],rtol=1e-8,atol=1e-10)
            recomputed.append(p)
        else:
            recomputed.append(np.nan)
    np.testing.assert_allclose(holm(recomputed),tests.p_holm,rtol=1e-8,atol=1e-10,equal_nan=True)
    import joblib
    for condition in ('gradient_boosting_own','gradient_boosting_neighbours'):
        selected = json.loads((root/f'{condition}_selection.json').read_text())['selected_config_id']
        model = joblib.load(root/f'{condition}_c{selected}_seed11_{cfg["splits"]["tuning_origins"][0]}.joblib')
        if model.n_iter_ != 300 or model.get_params()['loss'] != 'poisson' or model.get_params()['early_stopping']:
            raise ValueError('Fitted estimator contract differs')
    report = Path('reports/experiments/baselines_validation.md')
    links = re.findall(r'\]\(([^)]+)\)',report.read_text(encoding='utf-8'))
    broken = [link for link in links if not link.startswith(('http://','https://')) and not (report.parent/link).exists()]
    if broken:
        raise ValueError(f'Missing report artifact: {broken}')
    visual_files = [Path(name) for name in ('visuals/t02/baseline_error_horizon.png','visuals/t02/baseline_error_horizon.csv',
        'visuals/t02/baseline_error_maturity.png','visuals/t02/baseline_error_maturity.csv',
        'data/explore/t02/validation_error_map.png','data/explore/t02/validation_error_map.csv',
        'data/explore/t02/validation_errors_time.png','data/explore/t02/validation_errors_time.csv',
        'data/explore/t02/validation_error_moran.csv')]
    if any(not p.exists() or p.stat().st_size>=5_000_000 for p in visual_files):
        raise ValueError('Visual output missing or too large')
    comparison = scores.loc[(slice(None),slice(None),'all'),['mae','mase']].reset_index()
    answer = {'run_id':manifest['run_id'],'verification':'passed','cpu_fits':len(fits),
        'fit_hours_recorded':completion['fitting_seconds_recorded']/3600,
        'origin_metric_rows_checked':checks,'dm_comparisons_checked':len(tests),'source_and_package_checks':'passed',
        'last_validation_target':rows.last_target.max(),'test_forecasts_or_losses':0,
        'visual_files_checked':len(visual_files),'broken_report_links':broken,
        'overall_scores':comparison.to_dict('records')}
    Path('reports/experiments/t02_run_verification.json').write_text(json.dumps(answer,indent=2),encoding='utf-8')
    print(json.dumps(answer,indent=2))


if __name__ == '__main__':
    main()
