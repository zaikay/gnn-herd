"""Researcher-only pilot entry point: two fixed fits, training losses only."""
import argparse
import json
from pathlib import Path

import pandas as pd

from evaluation.frozen import frozen_protocol
from features.panel import load_panel


def pilot_plan(cfg):
    pilot = cfg['tuning']['timing_pilot']
    if (pilot['hidden_widths']!=[32,96] or pilot['seed']!=11 or pilot['origin']!='2020-08'
            or pilot['epochs']!=75 or pilot['graph']!='real'):
        raise ValueError('Pilot settings differ from approved P5')
    return [dict(width=width,seed=pilot['seed'],fit_origin=pilot['origin'],
                 epochs=pilot['epochs'],learning_rate=pilot['learning_rate'],
                 weight_decay=pilot['weight_decay'],condition=pilot['graph']) for width in pilot['hidden_widths']]


def preflight_artifacts(signature):
    base = Path('data/explore/t03')
    states = json.loads((base/'state_assignment_summary.json').read_text())
    graphs = json.loads((base/'graph_conditions_summary.json').read_text())
    if states['protocol_sha256']!=signature or graphs['protocol_sha256']!=signature:
        raise ValueError('Graph/state artifacts use a different protocol')
    if states['coverage_failures'] or graphs['states_requiring_review']:
        raise ValueError('Unresolved state coverage or graph mixing; do not start pilot')


def main():
    parser = argparse.ArgumentParser(__doc__)
    parser.add_argument('--plan-only',action='store_true',help='CPU metadata only, no torch import or GPU access')
    args = parser.parse_args()
    cfg,signature = frozen_protocol('protocol-v1.1')
    preflight_artifacts(signature)
    plan = pilot_plan(cfg)
    if args.plan_only:
        print(json.dumps({'pilot':plan,'device':'Windows RTX 4070 Laptop 8 GB, 32 GB RAM',
                          'all_conditions_same_machine':True,'validation_or_test_scoring':False},indent=2))
        return
    # The training panel cannot expose even the tuning-anchor future targets.
    panel = load_panel(through=cfg['tuning']['timing_pilot']['origin'])
    from models.gnn_fit import fit
    output = Path('data/processed/t03_gnn/pilot')
    records = []
    for item in plan:
        destination = output/f"real_seed{item['seed']}_width{item['width']}_{item['fit_origin']}"
        records.append(fit(panel,cfg,signature,'real',item['seed'],item['width'],
                           item['learning_rate'],item['weight_decay'],destination,purpose='pilot'))
        pd.DataFrame(records).to_csv(output/'fit_records.csv',index=False)
    (output/'pilot_complete.json').write_text(json.dumps({'fits':records,
        'validation_or_test_scoring':False,'weights_discarded':True,
        'next':'STOP: researcher pilot review required before any full GNN workload'},indent=2),encoding='utf-8')
    print('Pilot complete. STOP for pilot report and researcher approval. No full runs were started.')


if __name__=='__main__':
    main()
