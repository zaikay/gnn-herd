"""CPU-only pilot verification and calendar-based resource projection."""
import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd

from evaluation.frozen import frozen_protocol
from evaluation.protocol import splits, training_calendar
from evaluation.result_report import table


def scheduled_fits(cfg):
    dates = splits(cfg)
    rows = []
    anchors = cfg['splits']['tuning_origins']
    for origin in anchors:
        for configuration in range(cfg['tuning']['configurations_per_tunable_condition']):
            rows.append({'block':'validation_tuning','fit_origin':origin,'seed':11})
    for origin in dates.loc[dates.block.eq('validation'),'fit_origin'].unique():
        for seed in cfg['tuning']['seeds']:
            if origin in anchors and seed==11:
                continue  # selected configuration's anchor fit is already counted
            rows.append({'block':'validation_selected','fit_origin':origin,'seed':seed})
    for origin in dates.loc[dates.block.eq('test'),'fit_origin'].unique():
        for seed in cfg['tuning']['seeds']:
            rows.append({'block':'future_test_calendar_only','fit_origin':origin,'seed':seed})
    result = pd.DataFrame(rows)
    result['batches_per_epoch'] = [int(np.ceil(len(training_calendar(o,cfg['splits']['training_first_target'])[0])/cfg['tuning']['full_graph_batch_origins'])) for o in result.fit_origin]
    return result


def project(fits, pilot_seconds, anchor_seconds, anchor_batches, conditions, epochs=75, margin=1.2):
    full = fits.batches_per_epoch.sum()/anchor_batches*anchor_seconds*conditions*epochs/75/3600
    return {'conditions':conditions,'epochs_proposed':epochs,'full_fit_hours':float(full),
            'pilot_hours_already_spent':pilot_seconds/3600,
            'total_hours_without_margin':float(full+pilot_seconds/3600),
            'planning_margin_factor':margin,'total_hours_with_margin':float(full*margin+pilot_seconds/3600)}


def main():
    cfg,signature = frozen_protocol('protocol-v1.1')
    root = Path('data/processed/t03_gnn/pilot')
    complete = json.loads((root/'pilot_complete.json').read_text())
    if not complete['weights_discarded'] or complete['validation_or_test_scoring']:
        raise ValueError('Pilot was not training-only with discarded weights')
    records = complete['fits']
    if sorted(r['hidden_size'] for r in records)!=[32,96] or len(records)!=2:
        raise ValueError('Wrong pilot configurations')
    curves = []
    hardware = json.loads(Path('data/processed/t03_gnn/machine.json').read_text())
    for record in records:
        folder = root/f"real_seed11_width{record['hidden_size']}_2020-08"
        manifest = json.loads((folder/'manifest.json').read_text())
        if (manifest['protocol_sha256']!=signature or manifest['hardware']!=hardware or
                record['epochs']!=75 or record['seed']!=11 or record['condition']!='real' or record['validation_or_test_scoring']):
            raise ValueError('Pilot differs from frozen settings/machine')
        for name,expected in manifest['sources'].items():
            if hashlib.sha256(Path(name).read_bytes()).hexdigest()!=expected:
                raise ValueError(f'Pilot source changed: {name}')
        if hashlib.sha256(Path('data/processed/t02_panel.npz').read_bytes()).hexdigest()!=manifest['panel']:
            raise ValueError('Pilot panel changed')
        curve = pd.read_csv(folder/'training_curve.csv')
        np.testing.assert_array_equal(curve.epoch,np.arange(1,76))
        if not np.isfinite(curve[['training_poisson_loss','epoch_seconds']].to_numpy()).all():
            raise ValueError('Nonfinite pilot measurements')
        np.testing.assert_allclose(curve.epoch_seconds.mean(),record['mean_epoch_seconds'])
        if (folder/'checkpoint.pt').exists():
            raise ValueError('Completed pilot weights were not discarded')
        curve['hidden_size'] = record['hidden_size']
        curves.append(curve)
    out = Path('data/explore/t03')
    pd.concat(curves,ignore_index=True).to_csv(out/'pilot_training_curves.csv',index=False)
    measurements = pd.DataFrame(records)
    measurements['fit_minutes'] = measurements.wall_seconds/60
    measurements['peak_allocated_gib'] = measurements.peak_gpu_memory_bytes/1024**3
    measurements['peak_reserved_gib'] = measurements.peak_reserved_gpu_memory_bytes/1024**3
    measurements.to_csv(out/'pilot_measurements.csv',index=False)
    fits = scheduled_fits(cfg)
    fits.to_csv(out/'pilot_projection_schedule.csv',index=False)
    anchor_batches = int(np.ceil(len(training_calendar('2020-08')[0])/cfg['tuning']['full_graph_batch_origins']))
    slow = max(records,key=lambda row:row['wall_seconds'])
    # Do not allow a late-epoch slowdown to disappear into a faster early mean.
    slow_curve = next(c for c in curves if c.hidden_size.iloc[0]==slow['hidden_size'])
    overhead = max(0,slow['wall_seconds']-slow_curve.epoch_seconds.sum())
    anchor_seconds = max(slow['wall_seconds'],slow_curve.epoch_seconds.tail(10).mean()*75+overhead)
    pilot_seconds = sum(r['wall_seconds'] for r in records)
    scenarios = pd.DataFrame([project(fits,pilot_seconds,anchor_seconds,anchor_batches,k,e)
                             for k,e in ((3,75),(4,75),(3,20),(4,20),(4,15))])
    scenarios.to_csv(out/'pilot_projection_scenarios.csv',index=False)
    three,four = scenarios.iloc[0],scenarios.iloc[1]
    summary = {'protocol':'protocol-v1.1','protocol_sha256':signature,'verification':'passed',
        'pilot_fits':2,'pilot_hours':pilot_seconds/3600,'anchor_batches_per_epoch':anchor_batches,
        'reference_fit_seconds':float(anchor_seconds),'validation_fits_per_condition':46,
        'future_test_fits_per_condition':24,'three_conditions':three.to_dict(),
        'optional_four_conditions':four.to_dict(),'full_runs_authorised':False,
        'verdict':'STOP: exceeds 24 GPU hours; protocol v2 approval required',
        'projection_note':'slower width applied to every fit and condition, scaled by training batches; 20% planning margin, not a confidence interval; no test targets loaded'}
    Path('reports/experiments/t03_pilot_verification.json').write_text(json.dumps(summary,indent=2),encoding='utf-8')
    lines = ['# Task 3 pilot report — 29 October 2026','',
        '**Decision required: approve a protocol v2 proposal before any full GNN run.** The current protocol exceeds its 24-GPU-hour limit. No further command is needed from the researcher now; do not repeat the pilot.','',
        '## Measurements and verification','',
        'Two real-graph fits, seed 11, August 2020 anchor, 75 epochs, learning rate 0.001, weight decay 0.0001, FP32 and batch two. Same Windows RTX 4070 Laptop GPU (8 GB), declared RAM 32 GB. Saved protocol/source/panel hashes and common machine inventory match; all 75 epochs are present and finite. Pilot weights are discarded. No validation/test forecast or loss was computed.','',
        table(measurements[['hidden_size','fit_minutes','mean_epoch_seconds','peak_allocated_gib','peak_reserved_gib','parameter_count']]),'',
        'Memory figures are PyTorch peak allocated/reserved device memory, not total GPU occupancy including the driver/display and other applications. Memory is comfortably below the device capacity for these pilot fits; the later-window activation batch shape stays fixed, but full-run peaks have not been measured. GPU time below means measured fit wall time projected to sequential GPU work; it is not hardware utilisation time.','',
        '[Measurements CSV](../../data/explore/t03/pilot_measurements.csv) · [Training loss curves](../../data/explore/t03/pilot_training_curves.png) / [CSV](../../data/explore/t03/pilot_training_curves.csv). Source: saved complete.json/training_curve.csv under data/processed/t03_gnn/pilot/, verified by `evaluation.pilot_report`; plots by `visuals.t03_pilot`. Negative Poisson loss is valid because the target-only factorial term is omitted. Curves are training diagnostics, not forecast accuracy or model-selection evidence.','',
        'The PowerShell transcript exists but contains no native Python test/epoch output in this session. Saved fit manifests/curves are the timing authority. A CPU-only test rerun after installation is recorded separately in logs/t03_pilot_review_tests.log; no GPU or fit was rerun.','',
        '## Projection under unchanged v1.1','',
        f"The slower pilot fit is the reference ({anchor_seconds/60:.3f} minutes, {anchor_batches} batches/epoch). For each scheduled fit, multiply that cost by ceil(training sample origins/2)/{anchor_batches}. The input window remains 24 months; the number of training origins grows. Use the slower width for all configurations and all graph conditions, even though narrower/no-graph conditions may be faster. Use the larger of full-fit time and the last-ten-epoch mean extrapolated to 75 epochs plus measured overhead. Add actual pilot time ({pilot_seconds/3600:.3f} hours) once.",'',
        'Per condition: 12 tuning fits + 36 selected quarterly fits − 2 reused selected/seed-11 anchor fits = 46 validation fits; eight future test refits × three seeds = 24 additional fits. Thus three conditions mean 138 validation + 72 future test fits (210); optional fourth means 184 + 96 (280). Future test dates are used only for resource arithmetic, never test targets.','',
        table(scenarios.iloc[:2][['conditions','epochs_proposed','full_fit_hours','pilot_hours_already_spent','total_hours_without_margin','total_hours_with_margin']]),'',
        'The final column adds a transparent 20% scheduling/thermal allowance to projected full-fit time, then actual pilot overhead. This is a planning margin, not a measured slowdown or statistical bound. Projection from one anchor/seed/graph cannot prove exact runtimes; graph conditions and laptop power/thermals can differ. Even without the margin, the conservative slower-width projection is well above 24 hours.','',
        '[Exact fit calendar and batch counts](../../data/explore/t03/pilot_projection_schedule.csv) · [Projection figure](../../visuals/t03/pilot_projection.png) / [Scenario CSV](../../data/explore/t03/pilot_projection_scenarios.csv) · [Verification JSON](t03_pilot_verification.json).','',
        '## Protocol v2 proposals — not approved or implemented','',
        '**Recommended A: retain the three core conditions, six configurations, quarterly refits, all three seeds, objective and dates; replace 75 fixed epochs with 20 fixed epochs under a new protocol v2.** This preserves the main comparisons and changes one compute limit. The cost projection scales epoch-dependent work linearly; checkpoints/setup overhead can make it optimistic, so this is a planning projection rather than a runtime guarantee. Training at 20 epochs may underfit relative to 75; the pilot does not establish forecast quality. This is a resource proposal, not a selection made using validation scores.','',
        '**Alternative B: if the optional installed-base ablation is essential, propose 15 fixed epochs for all four conditions under v2.** Its projected cost is shown below; it sacrifices more optimisation for every condition and needs explicit optional-condition approval. It is not recommended over A without a clear priority for that ablation.','',
        table(scenarios.iloc[2:][['conditions','epochs_proposed','total_hours_without_margin','total_hours_with_margin']]),'',
        'A 20-epoch fourth condition still exceeds 24 hours in this projection. Another option is to revise the resource ceiling while retaining 75 epochs, but that requires explicit protocol approval and acceptance of the larger budget. No epoch cap, configuration, seed, objective or frozen file has been changed.','',
        '## Approval requested','',
        'Approve proposal A (three core conditions, fixed 20 epochs, protocol v2), choose another explicit v2 budget, or retain v1.1 and explicitly revise the 24-hour resource rule. Until then all full runs and the optional fourth condition remain blocked by the timing gate. Task 3 step 5 is complete; steps 6–8 have not started.','']
    Path('reports/experiments/t03_pilot.md').write_text('\n'.join(lines),encoding='utf-8')
    print(json.dumps(summary,indent=2))


if __name__=='__main__':
    main()
