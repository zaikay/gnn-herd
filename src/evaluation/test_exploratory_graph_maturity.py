"""EXPLORATORY graph intervals and descriptive summaries from saved files."""
import json
from pathlib import Path

import numpy as np
import pandas as pd

from evaluation.final_test_metrics import hac_interval
from evaluation.gate_c_metrics import OUTCOMES
from evaluation.graph_diagnostics_report import table
from evaluation.test_exploratory import FINAL, OUT
from evaluation.test_exploratory_hybrids import PERIODS
from evaluation.test_exploratory_neighbour_swap import MARKER, REPORT
from evaluation.test_exploratory_offsets import confirmatory_hashes
from features.sealed_panel import load_prefix
from models.final_test_runtime import PANEL, authorize, sha, write_json

SCOPE = 'EXPLORATORY post-results'
PREFIX = 'exploratory_t06_'
HEADING = '## EXPLORATORY 11. Graph intervals by maturity, area size and shuffled edges'
GRAPH = Path('data/explore/t03')
REFERENCES = ('B2_no_graph', 'B2_shuffled')
CANDIDATE = 'B2_real'
GROUPS = ('low', 'medium', 'high')
BOUNDS = ['mean_MAE_difference', 'lower95', 'upper95']


def graph_intervals(origin, periods, groups, confidence):
    rows = []
    for period, start, end in periods:
        calendar = pd.period_range(start, end, freq='M').astype(str).tolist()
        for group in groups:
            part = origin.loc[origin.origin.between(start, end) & origin.group.eq(group)
                              & origin.model.isin((CANDIDATE, *REFERENCES))]
            wide = part.pivot(index=['outcome', 'origin'], columns='model', values='mae')
            for outcome in OUTCOMES:
                cell = wide.loc[outcome].sort_index()
                if cell.index.tolist() != calendar or not np.isfinite(cell.to_numpy()).all():
                    raise ValueError(f'Incomplete origin losses for {period}, {group}, {outcome}')
                h = 12 if outcome == 'total_12' else int(outcome)
                for reference in REFERENCES:
                    d = (cell[CANDIDATE] - cell[reference]).to_numpy()
                    mean, lo, hi = hac_interval(d, h, confidence) if h < len(d) else (d.mean(), np.nan, np.nan)
                    defined = np.isfinite([lo, hi]).all()
                    rows.append(dict(period=period, group=group, candidate=CANDIDATE, reference=reference,
                                     outcome=outcome, origins=len(d), DM_h=h, mean_MAE_difference=mean,
                                     lower95=lo, upper95=hi,
                                     excludes_zero=bool(lo > 0 or hi < 0) if defined else pd.NA))
    return pd.DataFrame(rows)


def reproduce(actual, saved):
    keys = ['candidate', 'reference', 'outcome', 'origins', 'DM_h']
    current = actual.set_index(keys).sort_index()
    expected = saved.set_index(keys).sort_index()
    pd.testing.assert_index_equal(current.index, expected.index)
    pd.testing.assert_frame_equal(current[BOUNDS].round(6), expected[BOUNDS].round(6), check_exact=True)


def area_sizes(panel, end):
    use = (panel.months >= '2011-01') & (panel.months <= end)
    months = pd.period_range('2011-01', end, freq='M').astype(str).tolist()
    if panel.months[use].tolist() != months:
        raise ValueError('Area size calendar incomplete')
    counts = panel.targets[panel.observed][:, use]
    valid_months = np.isfinite(counts).sum(axis=1)
    if not valid_months.all() or np.isinf(counts).any():
        raise ValueError('Invalid area size history')
    areas = pd.DataFrame(dict(postcode=panel.codes[panel.observed], observed_months=valid_months,
                              mean_monthly_count=np.nanmean(counts, axis=1, dtype=np.float64)))
    quantiles = np.percentile(areas.mean_monthly_count, [0, 10, 50, 90, 100])
    summary = pd.DataFrame(dict(statistic=['minimum', 'p10', 'median', 'p90', 'maximum'],
                                mean_monthly_count=quantiles))
    return areas, summary


def shuffled_summary(diagnostics, summary, seeds):
    if diagnostics.duplicated(['state_code', 'seed']).any() or set(diagnostics.seed) != set(seeds):
        raise ValueError('Unexpected shuffle state–seed grid')
    states = diagnostics.state_code.nunique()
    if not diagnostics.groupby('seed').size().eq(states).all():
        raise ValueError('Missing state–seed shuffle diagnostics')
    if not diagnostics.target_reached.eq(diagnostics.accepted_swaps.ge(diagnostics.target_swaps)).all():
        raise ValueError('Shuffle target flags disagree with swap counts')
    fixed = summary['cross_state_edges_fixed']
    if fixed != 190:
        raise ValueError(f'Expected 190 fixed cross-state edges, got {fixed}')
    return pd.DataFrame([dict(states_and_territories=states, seeds=len(seeds),
                              min_original_edge_share=diagnostics.original_edge_share.min(),
                              max_original_edge_share=diagnostics.original_edge_share.max(),
                              all_swap_targets_reached=bool(diagnostics.target_reached.all()),
                              cross_state_edges_fixed=fixed)])


def run():
    permit = authorize()
    locked = json.loads((FINAL / 'complete.json').read_text())
    if permit.signature != locked['signature']:
        raise ValueError('Final evaluation signature mismatch')
    before = confirmatory_hashes(locked)
    report = REPORT.read_text(encoding='utf-8')
    if MARKER not in report:
        raise ValueError('Report insertion marker missing')
    test_path = FINAL / 'ensemble_origin.csv.gz'
    frozen_path = GRAPH / 'protocol_v7_final_test/real_control_intervals.csv'
    graph_csv = GRAPH / 'graph_swap_diagnostics.csv'
    graph_json = GRAPH / 'graph_conditions_summary.json'
    validation_path = Path('data/processed/t03_b2_ensemble_combination/ensemble_origin.csv.gz')
    test = pd.read_csv(test_path, dtype={'outcome': str})
    confidence = permit.spec['interval_confidence']
    reproduce(graph_intervals(test, PERIODS[:1], ('all',), confidence),
              pd.read_csv(frozen_path, dtype={'outcome': str}))
    print(SCOPE, '26 frozen full-test interval rows matched to six decimals')
    end = permit.spec['last_origin']
    areas, size = area_sizes(load_prefix(PANEL, end, permit), end)
    np.testing.assert_equal(len(areas), 2634)
    np.testing.assert_array_equal(size.mean_monthly_count.round(2), [.01, .25, 3.25, 22.54, 132.15])
    print(SCOPE, '2,634 area means and all five summary values matched')
    intervals = graph_intervals(test, PERIODS, GROUPS, confidence)
    inputs = [test_path, frozen_path, PANEL, graph_csv, graph_json]
    validation_note = 'Validation is included using the saved ensemble origin losses for 36 origins.'
    aliases = {m + '_ensemble': m for m in (CANDIDATE, *REFERENCES)}
    if validation_path.is_file():
        validation = pd.read_csv(validation_path, dtype={'outcome': str})
        if set(aliases).issubset(validation.model) and set(GROUPS).issubset(validation.group):
            validation = validation.replace({'model': aliases})
            intervals = pd.concat([intervals, graph_intervals(
                validation, [('validation', '2018-11', '2021-10')], GROUPS, confidence)], ignore_index=True)
            inputs.append(validation_path)
        else:
            validation_note = 'The saved validation loss table lacks the required ensembles or maturity groups.'
    else:
        validation_note = 'The saved validation ensemble origin loss table is unavailable.'
    shuffled = shuffled_summary(pd.read_csv(graph_csv), json.loads(graph_json.read_text()), permit.spec['seeds'])
    outputs = dict(graph_intervals=intervals, area_means=areas, area_size_summary=size, shuffled_summary=shuffled)
    hashes = {}
    for label, frame in outputs.items():
        path = OUT / f'{PREFIX}{label}.csv'
        frame.insert(0, 'scope', SCOPE)
        frame.to_csv(path, index=False)
        hashes[path.name] = sha(path)
    if confirmatory_hashes(locked) != before:
        raise ValueError('Confirmatory artifacts changed')
    provenance = dict(scope=SCOPE, csv_sha256=hashes, input_sha256={p.as_posix(): sha(p) for p in inputs},
                      protocol_signature=permit.signature, confirmatory_artifacts_unchanged=len(before),
                      frozen_interval_rows_reproduced=26, area_percentiles_reproduced=True,
                      validation_included=validation_path in inputs, fits=0, gpu=False)
    name = PREFIX + 'provenance.json'
    write_json(OUT / name, provenance)
    write_report(report, intervals, size, shuffled, validation_note, hashes, name)
    index = OUT / 'index.md'
    lines = [line for line in index.read_text(encoding='utf-8').splitlines() if PREFIX not in line]
    lines.extend(f'- EXPLORATORY [{entry}]({entry}). Generated by evaluation.test_exploratory_graph_maturity.'
                 for entry in [*hashes, name])
    index.write_text('\n'.join(lines) + '\n', encoding='utf-8')
    print(json.dumps(provenance, indent=2))


def write_report(report, intervals, size, shuffled, validation_note, hashes, provenance):
    section = HEADING + '\n\n24 November 2026. These EXPLORATORY analyses were requested after the results were seen.\n\n'
    section += '### EXPLORATORY 11.1 Graph intervals by maturity\n\n'
    section += ('B2 real minus each graph control uses saved origin-level ensemble MAE, with origins weighted equally. '
                'Negative differences favour B2 real. The frozen method uses Bartlett HAC variance and inverts the '
                'HLN-corrected Student t statistic at 95%, with h equal to the monthly horizon and 12 for the total. '
                'The 26 all-area full-test mean and interval rows matched protocol v7 to six decimals. '
                + validation_note + '\n\n'
                'These are pointwise descriptive intervals. Each half has 12 origins. At horizon 12 and the 12-month total, '
                'h equals n and the HLN factor is zero. The mean is reported and the bounds and zero-exclusion flag are undefined. '
                'A zero-exclusion flag requires both bounds to be strictly on the same side of zero. '
                'MAE differences are systems per area per month, or systems per area per 12-month window for the total.\n\n')
    selected = intervals.loc[intervals.period.eq('full_test') & intervals.outcome.eq('total_12')]
    section += 'Full-test 12-month totals by maturity. The CSV covers all 13 outcomes and all available periods.\n\n'
    section += table(selected[['reference', 'group', *BOUNDS, 'excludes_zero']]) + '\n\n'
    section += '### EXPLORATORY 11.2 Area size\n\n'
    section += ('Each of the 2,634 observed Postal Areas contributes one mean over January 2011 through September 2024, '
                'excluding masked months. The units are systems per area per month. All five values matched the supplied check.\n\n')
    section += table(size.drop(columns='scope').assign(
        mean_monthly_count=size.mean_monthly_count.map(lambda x: f'{x:.2f}'))) + '\n\n'
    section += '### EXPLORATORY 11.3 Shuffled graph\n\n'
    row = shuffled.iloc[0]
    section += (f'The diagnostics cover {row.states_and_territories} state and territory codes and {row.seeds} seeds. '
                f'The retained share of original within-state edges ranged from {row.min_original_edge_share:.2%} '
                f'to {row.max_original_edge_share:.2%} across state–seed pairs. Every swap target was reached, '
                f'and {row.cross_state_edges_fixed} cross-state edges were kept fixed.\n\n')
    section += 'All 22 confirmatory artifact hashes matched before and after.\n\n'
    base = '../../data/explore/t03/test_exploratory/'
    for name, digest in hashes.items():
        section += f'- [EXPLORATORY {name}]({base}{name}) (SHA256 `{digest}`)\n'
    section += (f'- [EXPLORATORY provenance]({base}{provenance})\n\n'
                'Generator `evaluation.test_exploratory_graph_maturity`. Log `logs/t06_analysis.log`.\n\n')
    if HEADING in report:
        report = report[:report.index(HEADING)] + report[report.index(MARKER):]
    REPORT.write_text(report.replace(MARKER, section + MARKER, 1), encoding='utf-8')


if __name__ == '__main__':
    run()
