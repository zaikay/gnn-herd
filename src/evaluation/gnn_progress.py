"""CPU-only condition progress and measured-time-based remaining-work estimates."""
import argparse
from datetime import datetime, timezone
import json
from pathlib import Path

import numpy as np
import pandas as pd

from evaluation.frozen import frozen_protocol
from evaluation.pilot_report import scheduled_fits
from evaluation.protocol import training_calendar


def journal_summary(path):
    attempts = {}; checkpoint_epoch = 0; closed = set()
    if path.exists():
        lines = path.read_text(encoding='utf-8').splitlines()
        for i,line in enumerate(lines):
            try:
                row = json.loads(line)
            except json.JSONDecodeError:
                if i==len(lines)-1:
                    break
                raise
            key = row['session_id']
            attempts[key] = max(attempts.get(key,0),row.get('attempt_seconds',0))
            checkpoint_epoch = max(checkpoint_epoch,row.get('checkpoint_epoch',0))
            if row['event']=='attempt_end':
                closed.add(key)
    return sum(attempts.values()),checkpoint_epoch,bool(set(attempts)-closed)


def write_progress(cfg,signature,base=None,pilot_records=None,write=True):
    if base is None:
        base = Path('data/processed/t03_gnn/validation')/signature[:16]
    base = Path(base)
    schedule = scheduled_fits(cfg)
    validation = schedule.loc[schedule.block.ne('future_test_calendar_only')]
    total_batches = float(validation.batches_per_epoch.sum())
    if pilot_records is None:
        pilot_records = json.loads(Path('data/processed/t03_gnn/pilot/pilot_complete.json').read_text())['fits']
    pilot_rate = max(r['wall_seconds'] for r in pilot_records)/(64*75)
    epochs = cfg['tuning']['max_gnn_epochs']
    records = []; detailed = []
    for condition in cfg['gnn_design']['run_order']:
        done = 0; seconds = 0.; partial = 0; saved_batch_epochs = 0.; rates = []; lower_bound = False
        root = base/condition
        for manifest_path in sorted(root.glob('c*_seed*/manifest.json')):
            folder = manifest_path.parent
            manifest = json.loads(manifest_path.read_text())
            if manifest['protocol_sha256']!=signature or manifest['condition']!=condition:
                raise ValueError('Progress encountered a fit from a different protocol/condition')
            batches = int(np.ceil(len(training_calendar(manifest['fit_origin'])[0])/cfg['tuning']['full_graph_batch_origins']))
            observed_seconds,checkpoint_epoch,open_attempt = journal_summary(folder/'sessions.jsonl')
            complete_path = folder/'complete.json'
            if complete_path.exists():
                if not (folder/'checkpoint.pt').exists():
                    raise ValueError('Completed fit checkpoint is missing; do not count or refit silently')
                complete = json.loads(complete_path.read_text())
                if complete['epochs']!=epochs:
                    raise ValueError('Completed fit has wrong fixed epoch cap')
                observed_seconds = max(observed_seconds,complete['wall_seconds'])
                done += 1; checkpoint_epoch = epochs
                rates.append(complete['wall_seconds']/(batches*epochs))
            elif (folder/'checkpoint.pt').exists():
                partial += 1
            elif observed_seconds:
                partial += 1
            seconds += observed_seconds
            saved_batch_epochs += batches*checkpoint_epoch
            lower_bound |= open_attempt
            detailed.append({'condition':condition,'fit_directory':folder.name,
                             'complete':complete_path.exists(),'saved_epochs':checkpoint_epoch,
                             'measured_seconds':observed_seconds,'timing_lower_bound':open_attempt})
        # Before completed condition-specific fits exist, clearly label the
        # conservative width-96 pilot fallback. No test target is read.
        rate = float(np.mean(rates)) if rates else pilot_rate
        remaining = max(0.,total_batches*epochs-saved_batch_epochs)*rate/3600
        records.append({'condition':condition,'completed_fits':done,'planned_validation_fits':46,
            'partial_fits':partial,'measured_hours':seconds/3600,'timing_lower_bound':lower_bound,
            'projected_remaining_validation_hours':remaining,
            'projection_source':'condition-specific completed-fit mean per batch/epoch' if rates else 'slower-width pilot fallback; no completed condition fits yet',
            'condition_complete':(root/'condition_complete.json').exists()})
    result = {'protocol':'protocol-v2','protocol_sha256':signature,'updated_at':datetime.now(timezone.utc).isoformat(),
        'conditions':records,'measured_full_fit_hours_total':sum(r['measured_hours'] for r in records),
        'pilot_hours_separate':sum(r['wall_seconds'] for r in pilot_records)/3600,
        'projection_scope':'validation only, no test targets; checkpointed partial epochs deducted; replay time included in measured hours; inference time excluded',
        'test_forecasts_or_losses':0}
    if write:
        output = Path('reports/experiments/t03_session_progress.json')
        temporary = output.with_suffix('.tmp')
        temporary.write_text(json.dumps(result,indent=2),encoding='utf-8'); temporary.replace(output)
        pd.DataFrame(records).to_csv('data/explore/t03/session_progress.csv',index=False)
        pd.DataFrame(detailed,columns=['condition','fit_directory','complete','saved_epochs','measured_seconds','timing_lower_bound']).to_csv('data/explore/t03/session_fit_records.csv',index=False)
        index = Path('data/explore/t03/index.md')
        marker = '\n## Validation sessions\n'
        previous = index.read_text(encoding='utf-8').split(marker)[0]
        index.write_text(previous+marker+'\n- [session_progress.csv](session_progress.csv): completed/partial fits, measured hours and remaining validation fit-time estimates by condition; `evaluation.gnn_progress`.\n- [session_fit_records.csv](session_fit_records.csv): individual fit/checkpoint and replay-time observations; same generator.\n',encoding='utf-8')
    print(json.dumps(result,indent=2))
    return result


def main():
    argparse.ArgumentParser(__doc__).parse_args()
    cfg,signature = frozen_protocol('protocol-v2')
    write_progress(cfg,signature)


if __name__=='__main__':
    main()
