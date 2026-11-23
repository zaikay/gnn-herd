"""EXPLORATORY robustness and area error offsets from locked test forecasts."""
from dataclasses import replace
import json
from pathlib import Path

import numpy as np
import pandas as pd

from evaluation.final_test import context
from evaluation.final_test_metrics import BANDS, fixed_combination, forecast_ensembles
from evaluation.gate_c_metrics import evaluate
from evaluation.test_exploratory import FINAL, NEIGH, OUT, OWN
from evaluation.test_exploratory_hybrids import PAIRS, PERIODS, period_scores
from features.sealed_panel import load_prefix
from models.final_test_runtime import PANEL, ROOT, authorize, calendar, sha, write_json

SCOPE = 'EXPLORATORY post-test'
METRICS = ['mae', 'mase', 'rmse']
GROUPS = ['all', 'low', 'medium', 'high']
CORE = ['combination', 'B2_without_base', 'B2_real', 'B2_no_graph', OWN, NEIGH]
PREFIX = 'exploratory_t04_'
REPORT = Path('reports/experiments/test_exploratory.md')
MARKER = '## EXPLORATORY complete outputs and provenance'
RESULTS = '### EXPLORATORY results'


def verified_calendar(spec):
    rows = calendar(spec['first_origin'], spec['last_origin'], spec['refit_interval_months'])
    full, first, second = [rows.origin.between(start, end) for _, start, end in PERIODS]
    if (full.sum(), first.sum(), second.sum()) != (24, 12, 12):
        raise ValueError('Unexpected period sizes')
    if not (full.all() and (first ^ second).all()):
        raise ValueError('Unexpected period boundaries')
    if spec['last_target'] != '2025-09' or rows.last_target.max() != '2025-09':
        raise ValueError('Expected final target September 2025')
    return rows


def robustness(scores):
    keys = ['period', 'group', 'outcome', 'metric']
    losses = scores.melt(id_vars=['model', *keys[:-1]], value_vars=METRICS,
                         var_name='metric', value_name='loss')
    wide = losses.pivot(index=keys, columns='model', values='loss')
    expected = pd.MultiIndex.from_product(
        [[p[0] for p in PERIODS], GROUPS, [str(h) for h in range(1, 13)] + ['total_12'], METRICS],
        names=keys)
    if set(wide.index) != set(expected) or not np.isfinite(wide.to_numpy()).all():
        raise ValueError('Incomplete robustness score grid')
    better = wide[[OWN, NEIGH]].min(axis=1).rename('better_boosting')
    cells = losses.join(better, on=keys)
    cells['not_lower'] = cells.loss >= cells.better_boosting
    cells['gain_percent'] = 100 * (cells.better_boosting - cells.loss) / cells.better_boosting.where(
        cells.better_boosting.ne(0))
    consistency = []
    for split in ([], ['period'], ['metric'], ['period', 'metric']):
        summary = cells.groupby(['model', *split]).agg(
            cells=('not_lower', 'size'), not_lower_cells=('not_lower', 'sum'),
            min_gain_percent=('gain_percent', 'min')).reset_index()
        consistency.append(summary.assign(
            period=summary.get('period', 'all_periods'), metric=summary.get('metric', 'all_metrics')))

    halves = cells.loc[cells.period.ne('full_test')].copy()
    worst = halves.groupby(['model', *keys[1:]], as_index=False).loss.max()
    worst = worst.rename(columns={'loss': 'worst_half_loss'})
    minima = worst.groupby(keys[1:]).worst_half_loss.transform('min')
    worst['lowest_worst_half'] = worst.worst_half_loss.eq(minima)
    wins = worst.groupby(['model', 'group', 'metric'], as_index=False).lowest_worst_half.sum()
    best = halves.groupby(keys).loss.transform('min')
    halves['ratio_to_best'] = halves.loss / best
    gaps = pd.concat([
        part.groupby(['model', 'metric'], as_index=False).ratio_to_best.max().assign(group=label)
        for label, part in [('all_areas', halves.loc[halves.group.eq('all')]), ('all_groups', halves)]
    ], ignore_index=True)
    return dict(robustness_cells=cells, worst_half_cells=worst, worst_half_wins=wins,
                boosting_consistency=pd.concat(consistency, ignore_index=True), best_model_gaps=gaps)


def reproduction(scores):
    result = robustness(scores.loc[scores.model.isin(CORE)])
    summary = result['boosting_consistency'].query("period == 'all_periods' and metric == 'all_metrics'")
    summary = summary.set_index('model').loc[CORE[:4]]
    np.testing.assert_array_equal(summary.not_lower_cells, [25, 66, 136, 145])
    np.testing.assert_array_equal(summary.min_gain_percent.round(2), [-1.46, -11.45, -25.83, -28.32])
    wins = result['worst_half_wins'].query("group == 'all'").pivot(
        index='metric', columns='model', values='lowest_worst_half')
    np.testing.assert_array_equal(wins.loc[METRICS, CORE],
                                  [[1, 9, 2, 1, 0, 0], [0, 13, 0, 0, 0, 0], [10, 3, 0, 0, 0, 0]])
    return summary, wins


def decompose(boost, network, hybrid, weight, reference):
    boost_abs, network_abs, hybrid_abs, ref_abs = map(np.abs, (boost, network, hybrid, reference))
    adjustment = ref_abs - boost_abs
    weighting = (1 - weight) * (boost_abs - network_abs)
    cancelling = weight * boost_abs + (1 - weight) * network_abs - hybrid_abs
    gain = ref_abs - hybrid_abs
    np.testing.assert_allclose(weighting + adjustment + cancelling, gain, atol=1e-10, rtol=0)
    return weighting, adjustment, cancelling, gain


def offsets(point, ctx, weights):
    weight = fixed_combination(np.ones_like(ctx.truth), np.zeros_like(ctx.truth), ctx.groups, weights)
    errors = {name: pred - ctx.truth for name, pred in point.items()}
    boost = errors[NEIGH]
    rows = []
    for hybrid, member in PAIRS:
        network = errors[member]
        zero = (boost == 0) | (network == 0)
        opposite = (~zero) & (np.signbit(boost) != np.signbit(network))
        for reference in (NEIGH, OWN):
            weighting, adjustment, cancelling, gain = decompose(
                boost, network, errors[hybrid], weight, errors[reference])
            for period, start, end in PERIODS:
                period_mask = (ctx.origins >= start) & (ctx.origins <= end)
                for group_index, group in enumerate(GROUPS, start=-1):
                    mask = ctx.groups[period_mask] == group_index if group_index >= 0 else np.ones_like(
                        ctx.groups[period_mask], dtype=bool)
                    for first, last, band in (*BANDS, (0, 12, 'all')):
                        def cases(array):
                            return array[period_mask, :, first:last][mask]

                        def mae_average(array):
                            area_sums = np.sum(array[period_mask, :, first:last], axis=2, where=mask[:, :, None])
                            return np.mean(area_sums.sum(axis=1) / (mask.sum(axis=1) * (last - first)))

                        raw, shift, cancel, observed = map(mae_average, (weighting, adjustment, cancelling, gain))
                        np.testing.assert_allclose(raw + shift + cancel, observed, atol=1e-10, rtol=0)
                        both = np.stack([cases(boost).ravel(), cases(network).ravel()])
                        corr = np.corrcoef(both)[0, 1] if np.all(both.std(axis=1) > 0) else np.nan
                        rows.append(dict(
                            model=hybrid, network=member, reference=reference, period=period,
                            group=group, band=band, cases=both.shape[1], opposite_cases=cases(opposite).sum(),
                            zero_cases=cases(zero).sum(), opposite_share=cases(opposite).mean(),
                            zero_share=cases(zero).mean(), correlation=corr, member_weighting_gain=raw,
                            reference_adjustment=shift, weighting_gain=raw + shift, cancelling_gain=cancel,
                            mae_gain=observed, cancelling_share_of_gain=cancel / observed if observed > 0 else np.nan))
    return pd.DataFrame(rows)


def confirmatory_hashes(locked):
    hashes = {path: sha(path) for path in locked['artifact_sha256']}
    if len(hashes) != 22 or hashes != locked['artifact_sha256']:
        raise ValueError('Expected all 22 locked confirmatory artifacts unchanged')
    return hashes


def forecasts(permit, locked, ctx):
    runs, inputs = {}, {}
    for model in (NEIGH, OWN, *(member for _, member in PAIRS), 'B2_shuffled'):
        paths = [ROOT / model / f'predictions_seed{seed}.npz' for seed in permit.spec['seeds']]
        if model == 'B2_shuffled' and not all(path.is_file() for path in paths):
            continue
        runs[model] = {}
        for seed, path in zip(permit.spec['seeds'], paths):
            digest = sha(path)
            if digest != locked['forecast_sha256'][str(path)]:
                raise ValueError(f'Saved forecast hash mismatch: {path}')
            inputs[str(path)] = digest
            with np.load(path, allow_pickle=False) as saved:
                np.testing.assert_array_equal(saved['origins'], ctx.origins)
                np.testing.assert_array_equal(saved['codes'], ctx.codes)
                runs[model][seed] = saved['prediction']
    point = forecast_ensembles(runs, permit.spec['seeds'])
    for hybrid, network in PAIRS:
        point[hybrid] = fixed_combination(point[NEIGH], point[network], ctx.groups, permit.spec['weights'])
    return point, inputs


def run():
    report = REPORT.read_text(encoding='utf-8')
    if '### EXPLORATORY predictions recorded before analysis' not in report or MARKER not in report:
        raise ValueError('Record the predictions in section 9 before running the analysis')
    permit = authorize()
    locked = json.loads((FINAL / 'complete.json').read_text())
    if locked['signature'] != permit.signature:
        raise ValueError('Final evaluation signature mismatch')
    before = confirmatory_hashes(locked)
    check_path = OUT / 'exploratory_hybrid_sensitivity_scores.csv'
    saved = pd.read_csv(check_path, dtype={'outcome': str}, float_precision='round_trip')
    summary, wins = reproduction(saved)
    print(SCOPE, 'six-model reproduction passed')
    rows = verified_calendar(permit.spec)
    cutoff = permit.spec['last_target']
    panel = load_prefix(PANEL, cutoff, replace(permit, max_month=cutoff))
    ctx = context(panel, rows, permit.cfg)
    point, inputs = forecasts(permit, locked, ctx)
    origin = evaluate({name: {'ensemble': pred} for name, pred in point.items()}, ctx, seeds=('ensemble',))['origin']
    scores = period_scores(origin)
    keys = ['model', 'period', 'group', 'outcome']
    expected = saved.set_index(keys).sort_index()
    np.testing.assert_allclose(scores.set_index(keys).loc[expected.index, METRICS], expected[METRICS],
                               atol=1e-10, rtol=0)
    outputs = robustness(scores)
    outputs['robustness_scores'] = scores
    errors = offsets(point, ctx, permit.spec['weights'])
    outputs['error_offsets'] = errors
    plotted = errors.query("reference == @NEIGH and group == 'all' and period != 'full_test' and band != 'all'")
    outputs['error_offsets_plot'] = plotted
    from visuals.test_exploratory_offsets import render
    files = {}
    for name, frame in outputs.items():
        file = OUT / (PREFIX + name + '.csv')
        frame.assign(scope=SCOPE)[['scope', *frame.columns]].to_csv(file, index=False)
        files[file.name] = sha(file)
    render(OUT, PREFIX)
    if any(path.stat().st_size >= 5_000_000 for path in OUT.glob(PREFIX + '*')):
        raise ValueError('Exploratory output exceeds the 5 MB limit')
    after = confirmatory_hashes(locked)
    if before != after:
        raise ValueError('Confirmatory hashes changed during this run')
    missing = [] if 'B2_shuffled' in point else ['B2_shuffled']
    provenance = dict(scope=SCOPE, csv_sha256=files, forecast_sha256=inputs,
                      section_8_scores_sha256=sha(check_path), last_target=cutoff,
                      protocol_signature=permit.signature, missing_models=missing,
                      source_sha256={path: sha(path) for path in (
                          'src/evaluation/test_exploratory_offsets.py',
                          'src/visuals/test_exploratory_offsets.py', 'configs/style.yaml')},
                      confirmatory_artifacts_unchanged=len(after), fits=0, gpu=False)
    write_json(OUT / (PREFIX + 'provenance.json'), provenance)
    write_report(report, outputs, summary, wins, provenance)
    print(json.dumps(provenance, indent=2))


def write_report(report, outputs, summary, wins, provenance):
    from evaluation.graph_diagnostics_report import table

    consistency = outputs['boosting_consistency'].query("period == 'all_periods' and metric == 'all_metrics'")
    counts = outputs['worst_half_wins'].query("group == 'all'").pivot(
        index='model', columns='metric', values='lowest_worst_half').add_prefix('wins_')
    ratios = outputs['best_model_gaps'].pivot(
        index='model', columns=['group', 'metric'], values='ratio_to_best')
    ratios.columns = [f'{group}_{metric}_ratio' for group, metric in ratios.columns]
    robust = consistency.set_index('model').drop(columns=['period', 'metric']).join(counts).join(ratios)
    errors = outputs['error_offsets'].query("group == 'all' and band == 'all'")
    main = errors.query("model == 'combination' and reference == @NEIGH").set_index('period')
    without_base = PAIRS[2][0]
    alt = errors.query("model == @without_base and reference == @NEIGH").set_index('period')
    p1a, p1b = main.loc[['first_half', 'second_half'], 'opposite_share']
    p2a, p2b = alt.loc['full_test', 'opposite_share'], main.loc['full_test', 'opposite_share']
    p3a, p3b = main.loc[['first_half', 'second_half'], 'cancelling_share_of_gain']

    def prediction(label, left, right, agrees):
        verdict = ('Agrees' if agrees else 'Disagrees') if np.isfinite([left, right]).all() else 'Undefined'
        return f'- {label}. {verdict}. {left:.2%} versus {right:.2%}.'

    section = RESULTS + '\n\n23 November 2026. EXPLORATORY. All 22 confirmatory artifact hashes matched before and after.\n\n'
    section += 'The six-model reproduction matched all supplied counts and rounded gains. The table shows cells at or above the better boosting score, minimum percentage gain, and all-area worst-half wins out of 13 outcomes per metric.\n\n'
    section += table(summary.reset_index()) + '\n\n' + table(wins.reset_index()) + '\n\n'
    if provenance['missing_models']:
        section += 'B2 shuffled is missing because its complete seed forecasts are unavailable.\n\n'
    section += 'The full roster uses 468 cells per model. Ties count as at or above boosting and share worst-half wins. The full test overlaps both halves. Ratios are maxima across half-period cells and use the lowest loss in the scored roster as denominator. The all-groups maxima include all areas and the three maturity terciles.\n\n'
    section += table(robust.reset_index()) + '\n\n'
    section += 'Opposite-sign and zero shares use all area–origin–horizon cases in each slice. Correlation is Pearson correlation over those cases. Gains use equal areas within each origin and equal origins and horizons within each slice. Units are systems per area per month. For own-lag boosting, the weighting entry includes the difference between own-lag and neighbour absolute errors, and the cancellation term uses the original hybrid members. The CSV shows both weighting components. The case and aggregate identities passed absolute tolerance 1e-10.\n\n'
    section += table(errors[['model', 'reference', 'period', 'opposite_share', 'zero_share', 'correlation',
                             'weighting_gain', 'cancelling_gain', 'mae_gain']]) + '\n\n'
    section += '\n'.join([prediction('P1', p1a, p1b, p1a > p1b), prediction('P2', p2a, p2b, p2a < p2b),
                           prediction('P3', p3a, p3b, p3a > p3b)]) + '\n\n'
    section += 'P1 and P3 compare first half to second half. P2 compares the without-base hybrid to the main hybrid across the full test. All three comparisons pool all areas and monthly horizons. The cancellation share divides cancellation gain by positive net MAE gain. A negative weighting component in the first half puts the cancellation share above 100%.\n\n'
    base = '../../data/explore/t03/test_exploratory/'
    figure = PREFIX + 'error_offsets_plot.png'
    section += f'![EXPLORATORY area-level error offsets]({base}{figure})\n\n'
    entries = [*provenance['csv_sha256'], figure, PREFIX + 'provenance.json']
    for name in entries:
        digest = provenance['csv_sha256'].get(name)
        suffix = f' (SHA256 `{digest}`)' if digest else ''
        section += f'- [EXPLORATORY {name}]({base}{name}){suffix}\n'
    section += '\nGenerator `evaluation.test_exploratory_offsets`. Log `logs/t04_analysis.log`.\n\n'
    if RESULTS in report:
        report = report[:report.index(RESULTS)] + report[report.index(MARKER):]
    REPORT.write_text(report.replace(MARKER, section + MARKER, 1), encoding='utf-8')
    index = OUT / 'index.md'
    lines = [line for line in index.read_text(encoding='utf-8').splitlines() if PREFIX not in line]
    lines.extend(f'- EXPLORATORY [{name}]({name}). Generated by `evaluation.test_exploratory_offsets`.'
                 for name in entries)
    index.write_text('\n'.join(lines) + '\n', encoding='utf-8')


if __name__ == '__main__':
    from threadpoolctl import threadpool_limits

    with threadpool_limits(limits=1):
        run()
