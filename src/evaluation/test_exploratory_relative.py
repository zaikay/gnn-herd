"""Append the EXPLORATORY relative view using the saved Task 5 differences."""
import json

import numpy as np
import pandas as pd

from evaluation.graph_diagnostics_report import table
from evaluation.test_exploratory_neighbour_swap import MARKER, OUT, PREFIX, REPORT
from models.final_test_runtime import sha, write_json

HEADING = '### EXPLORATORY 10.2 Relative differences added after reviewing the results'
SOURCE = PREFIX + 'differences.csv'
OUTPUT = PREFIX + 'relative_differences.csv'
PROVENANCE = PREFIX + 'provenance.json'


def add_percentages(frame):
    denominator = frame.own_loss.where(frame.own_loss.ne(0))
    return frame.assign(difference_percent=100 * frame.difference / denominator)


def mae_tables(frame):
    mae = frame.loc[frame.metric.eq('mae')]
    hybrids = mae.loc[mae.comparison.eq('hybrids')]
    rows = []
    for period in ['full_test', 'first_half', 'second_half', 'validation']:
        if period not in set(hybrids.period):
            continue
        for group in ['low', 'medium', 'high']:
            part = hybrids.loc[hybrids.period.eq(period) & hybrids.group.eq(group)].set_index('outcome')
            pct = part.difference_percent
            monthly = [str(h) for h in range(1, 13)]
            rows.append(dict(period=period, maturity=group, h1_percent=pct.loc['1'],
                             h12_percent=pct.loc['12'], total_percent=pct.loc['total_12'],
                             monthly_mean_percent=pct.loc[monthly].mean(),
                             positive_horizons=f"{part.loc[monthly, 'difference'].gt(0).sum()}/12"))
    hybrid = pd.DataFrame(rows)
    boost = mae.query("comparison == 'boosting' and group == 'low' and outcome == 'total_12'")
    boost = boost.set_index('period').loc[hybrid.period.drop_duplicates(), ['difference_percent']].reset_index()
    return hybrid, boost.rename(columns={'difference_percent': 'boosting_low_total_percent'})


def verify(hybrid, boost):
    expected = {
        ('full_test', 'low'): ([.19, 3.09, 3.55], '12/12'),
        ('validation', 'low'): ([.30, 4.38, 5.04], '12/12'),
        ('full_test', 'medium'): ([-.21, -.18, -1.69], '0/12'),
        ('full_test', 'high'): ([.15, .09, .16], '10/12'),
    }
    index = hybrid.set_index(['period', 'maturity'])
    for key, (percentages, positive) in expected.items():
        row = index.loc[key]
        actual = row[['h1_percent', 'h12_percent', 'total_percent']].astype(float).round(2).tolist()
        if actual != percentages or row.positive_horizons != positive:
            raise ValueError(f'{key}: expected {percentages}, {positive}; got {actual}, {row.positive_horizons}')
    np.testing.assert_equal(round(boost.set_index('period').loc['full_test', 'boosting_low_total_percent'], 2), 6.46)


def report_table(frame):
    formatted = frame.copy()
    for col in formatted.filter(regex='_percent$'):
        formatted[col] = formatted[col].map(lambda value: f'{value:.2f}' if np.isfinite(value) else 'undefined')
    return table(formatted)


def run():
    source_path = OUT / SOURCE
    record_path = OUT / PROVENANCE
    record = json.loads(record_path.read_text(encoding='utf-8'))
    source_hash = sha(source_path)
    if source_hash != record['csv_sha256'][SOURCE]:
        raise ValueError('Saved Task 5 differences do not match provenance')
    report = REPORT.read_text(encoding='utf-8')
    if '## EXPLORATORY 10.' not in report or MARKER not in report:
        raise ValueError('Section 10 or report insertion marker missing')
    frame = add_percentages(pd.read_csv(source_path, dtype={'outcome': str}, float_precision='round_trip'))
    hybrid, boost = mae_tables(frame)
    verify(hybrid, boost)
    print('EXPLORATORY reproduction matched all supplied percentages and positive counts')
    output = OUT / OUTPUT
    frame.to_csv(output, index=False)
    digest = sha(output)
    record['csv_sha256'][OUTPUT] = digest
    record['relative_view'] = dict(scope='EXPLORATORY, added after reviewing results',
                                   source_csv=SOURCE, source_sha256=source_hash,
                                   formula='100 * difference / own_loss',
                                   zero_denominator='undefined (blank CSV field)',
                                   reproduction_matched=True)
    write_json(record_path, record)
    section = HEADING + '\n\nThis percentage view was added after the absolute results were seen. It expresses the saved own-minus-neighbour difference as a percentage of own-lag loss. A zero own-lag loss gives an undefined percentage. The monthly mean gives each defined horizon percentage equal weight. The positive count uses the sign of the saved difference. All supplied reproduction values matched to two decimals, and all supplied counts matched.\n\n'
    section += '**Hybrid MAE differences (%) by maturity**\n\n' + report_table(hybrid) + '\n\n'
    section += '**Boosting alone, low-maturity 12-month total MAE difference (%)**\n\n'
    section += report_table(boost) + '\n\n'
    section += (f'[EXPLORATORY relative differences CSV](../../data/explore/t03/test_exploratory/{OUTPUT}) '
                f'(SHA256 `{digest}`). Generator `evaluation.test_exploratory_relative`. '
                'Log `logs/t05b_analysis.log`.\n\n')
    if HEADING in report:
        report = report[:report.index(HEADING)] + report[report.index(MARKER):]
    REPORT.write_text(report.replace(MARKER, section + MARKER, 1), encoding='utf-8')
    index = OUT / 'index.md'
    lines = [line for line in index.read_text(encoding='utf-8').splitlines() if OUTPUT not in line]
    lines.append(f'- EXPLORATORY [{OUTPUT}]({OUTPUT}). Generated by evaluation.test_exploratory_relative.')
    index.write_text('\n'.join(lines) + '\n', encoding='utf-8')
    print(report_table(hybrid))
    print(report_table(boost))
    print(f'{OUTPUT} SHA256 {digest}')


if __name__ == '__main__':
    run()
