"""EXPLORATORY fixed-weight boosting-member swap on saved forecasts."""
from dataclasses import replace
import json
from pathlib import Path

import numpy as np
import pandas as pd

from evaluation.baselines import validation_rows
from evaluation.final_test import context
from evaluation.final_test_metrics import fixed_combination, forecast_ensembles
from evaluation.gate_c_io import read_prediction
from evaluation.gate_c_metrics import evaluate
from evaluation.graph_diagnostics_report import table
from evaluation.result_report import completed_run
from evaluation.test_exploratory import FINAL, NEIGH, OUT, OWN, scores
from evaluation.test_exploratory_hybrids import period_scores
from evaluation.test_exploratory_offsets import confirmatory_hashes, verified_calendar
from features.sealed_panel import load_prefix
from models.final_test_runtime import PANEL, ROOT, authorize, sha, write_json

ORIGINAL = 'combination'
SWAP = 'combination_own_lag'
REAL = 'B2_real'
METRICS = ['mae', 'mase', 'rmse']
SCOPE = 'EXPLORATORY post-test'
PREFIX = 'exploratory_t05_'
REPORT = Path('reports/experiments/test_exploratory.md')
MARKER = '## EXPLORATORY complete outputs and provenance'
RESULTS = '### EXPLORATORY 10.1 Results'
VALIDATION = Path('data/processed/t03_b2_ensemble_combination')


def score_saved(paths, ctx, spec, inputs, locked=None):
    runs = {}
    for model, seed_paths in paths.items():
        runs[model] = {}
        for seed, path in seed_paths.items():
            digest = sha(path)
            if locked is not None and locked[str(path)] != digest:
                raise ValueError(f'Locked forecast changed: {path}')
            inputs[str(path)] = digest
            runs[model][seed] = read_prediction(path, ctx)
    point = forecast_ensembles(runs, spec['seeds'])
    for name, member in [(ORIGINAL, NEIGH), (SWAP, OWN)]:
        point[name] = fixed_combination(point[member], point[REAL], ctx.groups, spec['weights'])
    return evaluate({m: {'ensemble': point[m]} for m in (ORIGINAL, SWAP, OWN, NEIGH, REAL)},
                    ctx, seeds=('ensemble',))['origin']


def contrasts(frame):
    keys = ['period', 'group', 'outcome', 'metric']
    wide = frame.melt(id_vars=['period', 'group', 'outcome', 'model'], value_vars=METRICS,
                      var_name='metric', value_name='loss').pivot(index=keys, columns='model', values='loss')
    parts = []
    for comparison, own, neighbour in [('hybrids', SWAP, ORIGINAL), ('boosting', OWN, NEIGH)]:
        part = wide[[own, neighbour]].rename(columns={own: 'own_loss', neighbour: 'neighbour_loss'}).copy()
        part['difference'] = part.own_loss - part.neighbour_loss
        part['comparison'] = comparison
        parts.append(part.reset_index())
    return pd.concat(parts, ignore_index=True)


def verify_scores(actual, reference):
    keys = ['model', 'outcome', 'group']
    expected = reference.set_index(keys).sort_index()
    current = actual.set_index(keys).loc[expected.index, METRICS]
    np.testing.assert_allclose(current, expected[METRICS], atol=1e-10, rtol=0)


def validation_scores(permit, inputs):
    root, _, manifest, _ = completed_run()
    spec = permit.spec
    for model in (OWN, NEIGH):
        selection = json.loads((root / f'{model}_selection.json').read_text())
        selected = selection['configurations'][selection['selected_config_id']]
        if selected != spec['boosting'][model]:
            raise ValueError(f'Saved validation boosting configuration conflicts with v7: {model}')
    paths = {m: {s: root / f'{m}_seed{s}.npz' for s in spec['seeds']} for m in (OWN, NEIGH)}
    missing = [p.name for p in paths[OWN].values() if not p.is_file()]
    if missing:
        return None, 'Missing own-lag seed forecasts: ' + ', '.join(missing)
    paths[REAL] = {s: Path('data/processed/t03_b2_validation/real') / f'predictions_seed{s}.npz'
                   for s in spec['seeds']}
    rows = validation_rows(permit.cfg)
    cutoff = rows.last_target.max()
    if (len(rows), rows.origin.min(), rows.origin.max(), cutoff) != (36, '2018-11', '2021-10', '2022-10'):
        raise ValueError('Unexpected validation calendar')
    if manifest['panel_sha256'] != permit.manifest['panel_sha256']:
        raise ValueError('Validation panel differs from locked panel')
    ctx = context(load_prefix(PANEL, cutoff), rows, permit.cfg)
    result = scores(score_saved(paths, ctx, spec, inputs)).assign(period='validation', origins=len(rows))
    check = VALIDATION / 'ensemble_scores.csv'
    expected = pd.read_csv(check, dtype={'outcome': str})
    names = {m + '_ensemble': m for m in (OWN, NEIGH, REAL)}
    verify_scores(result, expected.loc[expected.model.isin(names)].replace({'model': names}))
    inputs[str(check)] = sha(check)
    return result, None


def summaries(deltas):
    hybrid = deltas.query("comparison == 'hybrids' and group != 'all' and outcome != 'total_12'").copy()
    hybrid['horizon'] = hybrid.outcome.astype(int)
    rows = []
    for (period, metric), part in hybrid.groupby(['period', 'metric'], sort=False):
        curve = part.pivot(index='horizon', columns='group', values='difference').sort_index()
        mean = curve.mean()
        rows.append(dict(period=period, metric=metric, low_mean=mean.low, medium_mean=mean.medium,
                         high_mean=mean.high, low_largest_horizons=int(
                             ((curve.low > curve.medium) & (curve.low > curve.high)).sum()),
                         low_h1=curve.low.iloc[0], low_h12=curve.low.iloc[-1],
                         low_increasing_steps=int((curve.low.diff() > 0).sum()),
                         low_slope_per_month=np.polyfit(curve.index, curve.low, 1)[0],
                         medium_max_abs=curve.medium.abs().max(), high_max_abs=curve.high.abs().max()))
    return pd.DataFrame(rows)


def run():
    report = REPORT.read_text(encoding='utf-8')
    if '## EXPLORATORY 10.' not in report or '- P7.' not in report or MARKER not in report:
        raise ValueError('Record P4–P7 before running')
    permit = authorize()
    spec = permit.spec
    locked = json.loads((FINAL / 'complete.json').read_text())
    if locked['signature'] != permit.signature:
        raise ValueError('Final evaluation signature mismatch')
    before = confirmatory_hashes(locked)
    rows = verified_calendar(spec)
    cutoff = spec['last_target']
    ctx = context(load_prefix(PANEL, cutoff, replace(permit, max_month=cutoff)), rows, permit.cfg)
    paths = {m: {s: ROOT / m / f'predictions_seed{s}.npz' for s in spec['seeds']} for m in (OWN, NEIGH, REAL)}
    inputs = {}
    test = period_scores(score_saved(paths, ctx, spec, inputs, locked['forecast_sha256']))
    check = OUT / 'exploratory_hybrid_sensitivity_scores.csv'
    expected = pd.read_csv(check, dtype={'outcome': str})
    for period, current in test.groupby('period'):
        verify_scores(current, expected.loc[expected.period.eq(period) & expected.model.isin([OWN, NEIGH, REAL, ORIGINAL])])
    inputs[str(check)] = sha(check)
    validation, missing = validation_scores(permit, inputs)
    frame = test if validation is None else pd.concat([test, validation], ignore_index=True)
    frame = frame.loc[frame.model.ne(REAL), ['period', 'model', 'group', 'outcome', 'origins', *METRICS]]
    deltas = contrasts(frame)
    plotted = deltas.query("outcome != 'total_12'").copy()
    plotted['horizon'] = plotted.outcome.astype(int)
    outputs = dict(scores=frame, differences=deltas, prediction_checks=summaries(deltas), plotted=plotted)
    files = {}
    for label, data in outputs.items():
        path = OUT / f'{PREFIX}{label}.csv'
        data.insert(0, 'scope', SCOPE)
        data.to_csv(path, index=False)
        files[path.name] = sha(path)
    from visuals.test_exploratory_neighbour_swap import render
    render(OUT, PREFIX)
    provenance_name = PREFIX + 'provenance.json'
    entries = [*files, PREFIX + 'differences.png', provenance_name]
    record = dict(scope=SCOPE, csv_sha256=files, input_sha256=inputs, validation_missing=missing,
                  protocol_signature=permit.signature, last_test_target=cutoff, fits=0, gpu=False)
    if before != confirmatory_hashes(locked):
        raise ValueError('Confirmatory hashes changed')
    record['confirmatory_artifacts_unchanged'] = len(before)
    write_json(OUT / provenance_name, record)
    if any((OUT / name).stat().st_size >= 5_000_000 for name in entries):
        raise ValueError('Output exceeds 5 MB')
    write_report(report, outputs['prediction_checks'].drop(columns='scope'), entries, record)
    index = OUT / 'index.md'
    lines = [line for line in index.read_text(encoding='utf-8').splitlines() if PREFIX not in line]
    lines.extend(f'- EXPLORATORY [{name}]({name}). Generated by evaluation.test_exploratory_neighbour_swap.'
                 for name in entries)
    index.write_text('\n'.join(lines) + '\n', encoding='utf-8')
    print(table(outputs['prediction_checks']))
    print(json.dumps(record, indent=2))


def write_report(report, summary, entries, record):
    section = RESULTS + '\n\n24 November 2026. EXPLORATORY. The three seed forecasts were averaged before mixing. Both hybrids use B2 real and the same nine frozen, origin-dependent maturity and horizon-band weights. Scores average areas within each origin, then origins. RMSE roots pooled MSE. Differences are own-lag minus neighbour-lag loss, so a positive value favours the neighbour-lag specification. The full test and its origin halves overlap.\n\n'
    section += 'The two boosting models also differ in tree size (max_leaf_nodes 15 for own lag and 31 for neighbour lags in configs/protocol_v7_test.json). The difference measures neighbour lags plus tree size, not neighbour lags alone. The weights were estimated on the validation period, so validation results are not out of sample.\n\n'
    if record['validation_missing']:
        section += record['validation_missing'] + '. P7 could not be evaluated.\n\n'
    section += 'The prediction table uses hybrid differences over monthly horizons. Means give each horizon equal weight. Low-largest horizons count strict wins over both other terciles out of 12. The low-maturity slope and increasing steps describe the horizon profile. Medium and high maximum absolute differences give the scale without choosing a cutoff for “small”. MAE and RMSE are systems per area per month here, and systems per area per 12-month window for totals in the CSV. MASE is unitless.\n\n'
    section += table(summary) + '\n\n'
    section += prediction_text(summary, record['validation_missing']) + '\n\n'
    section += 'The saved test scores for the original hybrid and its comparable baselines reproduced within 1e-10. All 22 confirmatory artifact hashes matched before and after.\n\n'
    base = '../../data/explore/t03/test_exploratory/'
    section += f'![EXPLORATORY own-lag minus neighbour-lag loss]({base}{PREFIX}differences.png)\n\n'
    for name in entries:
        digest = record['csv_sha256'].get(name)
        suffix = f' (SHA256 `{digest}`)' if digest else ''
        section += f'- [EXPLORATORY {name}]({base}{name}){suffix}\n'
    section += '\nGenerator `evaluation.test_exploratory_neighbour_swap`. Log `logs/t05_analysis.log`.\n\n'
    if RESULTS in report:
        report = report[:report.index(RESULTS)] + report[report.index(MARKER):]
    REPORT.write_text(report.replace(MARKER, section + MARKER, 1), encoding='utf-8')


def prediction_text(summary, missing):
    test = summary.query("period == 'full_test'").set_index('metric').loc[METRICS]
    largest = test.index[(test.low_mean > test.medium_mean) & (test.low_mean > test.high_mean)].tolist()
    growing = test.index[(test.low_slope_per_month > 0) & (test.low_h12 > test.low_h1)].tolist()
    metrics = lambda names: ', '.join(name.upper() for name in names) or 'none'
    relative = test.index[(test.medium_max_abs < test.low_mean.abs()) &
                          (test.high_max_abs < test.low_mean.abs())].tolist()
    text = f'- P4. On the full test, low maturity has the largest mean signed difference for {metrics(largest)}.\n'
    text += f'- P5. A positive slope and a higher value at horizon 12 than at horizon 1 occur for {metrics(growing)}. The step counts show whether the increases are monotonic.\n'
    text += f'- P6. Both medium and high maximum absolute differences are below the absolute low-maturity mean for {metrics(relative)}. Smallness has no absolute threshold here.\n'
    if not missing:
        val = summary.query("period == 'validation'").set_index('metric').loc[METRICS]
        val_largest = val.index[(val.low_mean > val.medium_mean) & (val.low_mean > val.high_mean)].tolist()
        val_growing = val.index[(val.low_slope_per_month > 0) & (val.low_h12 > val.low_h1)].tolist()
        val_relative = val.index[(val.medium_max_abs < val.low_mean.abs()) &
                                 (val.high_max_abs < val.low_mean.abs())].tolist()
        same = (largest, growing, relative) == (val_largest, val_growing, val_relative)
        text += f'- P7. The metric-level pattern {"repeats" if same else "differs"} in validation. The largest low-maturity mean occurs for {metrics(val_largest)}, growth for {metrics(val_growing)}, and the relative magnitude check holds for {metrics(val_relative)}.'
    return text.rstrip()


if __name__ == '__main__':
    from threadpoolctl import threadpool_limits

    with threadpool_limits(limits=1):
        run()
