"""Build the model panel while preserving unknown targets and all graph nodes."""
from dataclasses import dataclass
import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd

from audit.cer import validate_panel
from evaluation.frozen import frozen_protocol

PANEL = Path('data/processed/t02_panel.npz')


@dataclass
class Panel:
    codes: np.ndarray
    months: np.ndarray
    targets: np.ndarray
    observed: np.ndarray
    edges: np.ndarray

    def index(self, month):
        matches = np.flatnonzero(self.months == str(month))
        if len(matches) != 1:
            raise ValueError(f'Month outside available panel: {month}')
        return int(matches[0])

    @property
    def inputs(self):
        return np.where(self.observed[:, None], self.targets, 0).astype(np.float32)

    def through(self, month):
        stop = self.index(month) + 1
        return Panel(self.codes, self.months[:stop], self.targets[:, :stop], self.observed, self.edges)


def assemble(cer, nodes, edges, start, end):
    validate_panel(cer.sort_values(['postcode', 'month']))
    if not nodes.postcode.map(lambda code: isinstance(code,str) and len(code)==4 and code.isdigit()).all():
        raise ValueError('Graph postcodes must be four-character strings')
    codes = np.array(sorted(nodes.postcode), dtype='U4')
    if len(set(codes)) != len(codes):
        raise ValueError('Duplicate graph nodes')
    months = pd.period_range(start, end, freq='M').astype(str).to_numpy(dtype='U7')
    wide = cer.pivot(index='postcode', columns='month', values='count')
    observed = np.isin(codes, wide.index)
    target = wide.reindex(index=codes, columns=months).to_numpy(dtype=np.float32)
    if not np.isfinite(target[observed]).all() or (target[observed] < 0).any():
        raise ValueError('Unexpected gaps or bad values in observed-area history; review before changes')
    if np.isfinite(target[~observed]).any():
        raise ValueError('Unexpected target in a record-free area')
    lookup = {code: i for i, code in enumerate(codes)}
    indexed = []
    seen = set()
    for a, b in edges[['source', 'target']].itertuples(index=False, name=None):
        if a not in lookup or b not in lookup or a == b:
            raise ValueError('Invalid graph endpoint')
        pair = tuple(sorted((a,b)))
        if pair in seen:
            raise ValueError('Duplicate graph edge')
        seen.add(pair)
        indexed.append((lookup[a], lookup[b]))
    return Panel(codes, months, target, observed, np.array(indexed, dtype=np.int32).reshape(-1, 2))


def load_panel(path=PANEL, through=None):
    with np.load(path, allow_pickle=False) as data:
        result = Panel(*(data[key] for key in ('codes', 'months', 'targets', 'observed', 'edges')))
    return result.through(through) if through else result


def main():
    cfg, protocol_hash = frozen_protocol()
    cer = pd.read_csv('data/interim/cer_panel.csv', dtype={'postcode': str, 'month': str})
    nodes = pd.read_csv('reports/audit/graph_nodes.csv', dtype={'postcode': str})
    edges = pd.read_csv('data/processed/rook_edges.csv', dtype=str)
    history = pd.read_csv('reports/audit/historical_totals.csv', dtype={'postcode': str}).set_index('postcode')
    for code in cfg['data']['historical_zero_deductions']['postcodes']:
        if history.loc[code, 'reported_total'] != 0 or (cer.loc[cer.postcode.eq(code), 'count'] < 0).any():
            raise ValueError('Authorised zero-total deduction is not supported by input')
        if code in set(nodes.postcode):
            raise ValueError('Historical deduction code unexpectedly matched; review panel eligibility')
    panel = assemble(cer, nodes, edges, cfg['data']['start'], cfg['data']['last_month'])
    expected_missing = {'2331','3920','6182','6470','6712','6762','7139'}
    if set(panel.codes[~panel.observed]) != expected_missing:
        raise ValueError('Observation mask changed since approved protocol')
    join = pd.read_csv('reports/audit/postcode_poa_join.csv', dtype={'postcode': str})
    unmatched = join.loc[~join.matched]
    if set(unmatched.postcode) != set(cer.postcode) - set(panel.codes):
        raise ValueError('Unmatched-code ledger differs from panel membership')
    entries = [{'source_file': 'data/interim/cer_panel.csv', 'postcode': row.postcode, 'month': '',
                'scope': 'model panel only', 'reason': 'Unmatched CER postcode retained with totals in postcode_poa_join.csv; outside spatial model panel',
                'approved_by': 'researcher Gate A, 2026-10-28'} for row in unmatched.itertuples()]
    entries += [{'source_file': 'ABS graph node / no CER records', 'postcode': code, 'month': '',
                 'scope': 'model loss, evaluation and outgoing messages only',
                 'reason': 'Graph node retained; targets unknown; zero input placeholder with observation flag zero',
                 'approved_by': 'researcher P1, protocol-v1, 2026-10-28'} for code in panel.codes[~panel.observed]]
    ledger = Path('reports/audit/exclusions.csv')
    old = pd.read_csv(ledger, dtype=str, keep_default_na=False)
    pd.concat([old, pd.DataFrame(entries)], ignore_index=True).fillna('').drop_duplicates().to_csv(ledger, index=False)
    pd.DataFrame([{'postcode': code, 'first_month': '2001-04', 'last_month': '2010-12',
                   'deduced_value': 0, 'basis': 'Zero CER historical total plus nonnegative monthly counts; deduction, not imputation',
                   'outside_model_panel': True} for code in history.index if code in cfg['data']['historical_zero_deductions']['postcodes']]
                 ).to_csv('reports/audit/t02_panel_deductions.csv', index=False)
    PANEL.parent.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(PANEL, codes=panel.codes, months=panel.months, targets=panel.targets,
                        observed=panel.observed, edges=panel.edges)
    manifest = {'protocol_sha256': protocol_hash, 'panel_sha256': hashlib.sha256(PANEL.read_bytes()).hexdigest(),
        'nodes': len(panel.codes), 'observed_nodes': int(panel.observed.sum()), 'months': len(panel.months),
        'edges': len(panel.edges), 'unmatched_codes': len(unmatched), 'missing_codes': panel.codes[~panel.observed].tolist(),
        'target_storage': 'NaN for unknown targets; zero inputs provided separately; no target imputation',
        'input_sha256': {p: hashlib.sha256(Path(p).read_bytes()).hexdigest() for p in
                         ('data/interim/cer_panel.csv','data/processed/rook_edges.csv','reports/audit/postcode_poa_join.csv')},
        'test_evaluation': 'sealed; model runners load targets only through last validation target'}
    Path('data/processed/t02_panel_manifest.json').write_text(json.dumps(manifest, indent=2), encoding='utf-8')
    print(json.dumps(manifest, indent=2))


if __name__ == '__main__':
    main()
