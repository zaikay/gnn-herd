"""Write the validation report only from a completed, audited CPU run."""
import json
from pathlib import Path

import numpy as np
import pandas as pd

from evaluation.frozen import frozen_protocol


def table(frame):
    def value(item):
        if isinstance(item,(float,np.floating)):
            return 'undefined' if not np.isfinite(item) else f'{item:.6f}'
        return str(item).replace('|','/')
    rows = ['| '+' | '.join(frame.columns)+' |','| '+' | '.join(['---']*len(frame.columns))+' |']
    rows += ['| '+' | '.join(value(x) for x in row)+' |' for row in frame.itertuples(index=False,name=None)]
    return '\n'.join(rows)


def completed_run():
    # Completed v1 fits retain their original authority after a later approved
    # amendment. This reader cannot authorise new fitting under changed rules.
    cfg, signature = frozen_protocol(require_working=False)
    parent = Path('data/processed/t02_baselines')
    if not (parent/'latest_complete.txt').exists():
        raise RuntimeError('CPU baselines have not completed; do not generate result claims')
    run_id = (parent/'latest_complete.txt').read_text().strip()
    if len(run_id)!=16 or any(c not in '0123456789abcdef' for c in run_id):
        raise ValueError('Invalid completed-run pointer')
    root = parent/run_id
    manifest = json.loads((root/'run_manifest.json').read_text())
    completion = json.loads((root/'complete.json').read_text())
    if manifest['protocol_sha256'] != signature or manifest['device'] != 'CPU' or completion['final_test_accessed']:
        raise ValueError('Completed run has wrong protocol, device or split')
    if completion['cpu_fit_count'] != 92:
        raise ValueError('Incomplete fit budget')
    return root,cfg,manifest,completion


def write_report(root, cfg, manifest, completion, spatial_diagnostic=None):
    root = Path(root)
    scores = pd.read_csv(root/'scores.csv',dtype={'outcome':str})
    tests = pd.read_csv(root/'dm_tests.csv',dtype={'outcome':str})
    fits = pd.read_csv(root/'fit_records.csv')
    importance = pd.read_csv(root/'neighbour_importance.csv')
    expected = {'gradient_boosting_own':46,'gradient_boosting_neighbours':46}
    if fits.groupby('condition').size().to_dict() != expected:
        raise ValueError('Reported fit budget differs from protocol-v1')
    lines = ['# Validation baselines — Task 2 Gate B review', '',
        '**Status: completed validation run; Gate B awaits researcher review.** No final-test forecast or error is evaluated. These are retrospective forecasts using the revised CER snapshot; no individual behaviour or causal mechanism is identified.', '',
        '## Provenance and model conditions', '',
        f"Run `{manifest['run_id']}`; protocol-v1 SHA256 `{manifest['protocol_sha256']}`. CPU only, {manifest['threads']} threads, {completion['cpu_fit_count']} boosting fits. Software and code hashes: [run manifest](../../{root.as_posix()}/run_manifest.json). Recorded fit time sums to {completion['fitting_seconds_recorded']/3600:.3f} hours; this excludes prediction, data preparation, metrics and plotting time.", '',
        'Models: fixed seasonal naive, own-history Poisson histogram gradient boosting, and the same boosting family with neighbour history. Both fitted conditions use six configurations, seed 11 at the two tuning anchors and the selected configuration with seeds 11/29/47 under quarterly expanding refits. Every observed eligible horizon target is used, with identical availability masks and 46 unique fits per condition. Unknown-area graph nodes are not loss/evaluation cases or message sources. No artificial links are added.', '',
        'Validation origins are November 2018–October 2021, with targets ending October 2022. No validation target falls after the first sealed test origin. Data after that boundary are not loaded by the baseline runner. The final-test battery-scheme timing limitation and September 2025 target cutoff remain as frozen, without evaluating that block here.', '',
        '## MAE and seasonal MASE', '',
        'MAE is in systems per observed area (per forecast month or twelve-month total). MASE is unitless, with the approved pooled zero-scale fallback and training-only denominators frozen between quarterly refits. Total error is computed after summing all twelve predicted/actual counts; its MASE denominator is twelve times the monthly scale. Numbers below average losses across equal-area origins and the three seeds, not errors of a prediction ensemble. Per-seed metrics and seed spread are in the linked CSV.', '']
    for group in ('all','low','medium','high'):
        frame = scores.loc[scores.group.eq(group),['model','outcome','mae','mase','mae_seed_sd','mase_seed_sd']]
        lines += [f'### Maturity group: {group}', '',table(frame),'']
    lines += [f'[Full score CSV](../../{root.as_posix()}/scores.csv) · [Seed metrics](../../{root.as_posix()}/seed_metrics.csv) · [Origin losses and group sizes](../../{root.as_posix()}/origin_metrics.csv)', '',
        'Maturity terciles are recomputed using cumulative base through each origin with postcode tie breaks. Group results are not fixed-cohort effects. Denominators and masks are shared across all models.', '',
        '## Corrected Diebold–Mariano comparisons', '',
        'Inputs are area-averaged absolute losses at each monthly origin, averaged across the fixed seeds. The testing unit is an origin, not an area or seed. dieboldmariano 1.1.0 uses Bartlett covariance weighting through horizon−1, HLN correction, two-sided tests and Holm adjustment across the twelve comparisons below. Undefined statistics/p-values remain undefined. Overlapping horizons and the limited number of origins constrain inference. Validation was used for tuning, so p-values are descriptive development evidence, not final-test confirmation.', '',
        table(tests[['model_a','model_b','outcome','statistic','p_raw','p_holm','status']]), '',
        '## Neighbour-feature sensitivity', '',
        'Grouped permutation sensitivity is computed on the selected spatial model, seed 11, at the two tuning anchors, with three fixed shuffles per group. Shuffle area identities jointly across all twelve horizons for each selected feature group; no model is refit and no new configuration is tried. Changes in MAE may be negative. Predictors are correlated and these perturbed inputs need not be typical geographic combinations; this is descriptive predictive sensitivity, not causal or unique behavioural importance.', '',
        table(importance.groupby('group').mae_increase_systems.agg(['mean','std']).reset_index()), '',
        '## Gate B: do neighbour lags help on validation?', '']
    for outcome in ('1','6','12','total_12'):
        own = float(scores.loc[scores.model.eq('gradient_boosting_own') & scores.group.eq('all') & scores.outcome.eq(outcome),'mae'].iloc[0])
        neighbour = float(scores.loc[scores.model.eq('gradient_boosting_neighbours') & scores.group.eq('all') & scores.outcome.eq(outcome),'mae'].iloc[0])
        answer = 'lower' if neighbour < own else 'higher' if neighbour > own else 'equal'
        lines.append(f'- Outcome {outcome}: neighbour-model MAE is {answer} ({neighbour:.6f} versus own-history {own:.6f} systems); reduction in MAE = {own-neighbour:.6f} systems.')
    lines += ['', 'This per-outcome development result is a warning sign only. The core GNN experiment proceeds regardless after researcher Gate B review and the separate Task 3 timing gate. No hybrid decision or final-test conclusion is made here.', '',
        '## Visuals and spatial error exploration', '',
        '- [Error by reported horizon](../../visuals/t02/baseline_error_horizon.png) / [CSV](../../visuals/t02/baseline_error_horizon.csv).',
        '- [Error by maturity group](../../visuals/t02/baseline_error_maturity.png) / [CSV](../../visuals/t02/baseline_error_maturity.csv).',
        '- [Own-history validation error map](../../data/explore/t02/validation_error_map.png) / [CSV](../../data/explore/t02/validation_error_map.csv).',
        '- [Errors over validation origins](../../data/explore/t02/validation_errors_time.png) / [CSV](../../data/explore/t02/validation_errors_time.csv).',
        '- [Global Moran I of own-history validation errors](../../data/explore/t02/validation_error_moran.csv).', '',
        'The map and Moran statistic use per-area horizon-12 MAE averaged over origins and seeds. Missing-record areas have no evaluated error; they are not zero-error cases. No population/dwelling scaling or permutation significance test is supplied; error size can mix installation volume with predictability. Spatial clustering is descriptive and does not identify behavioural transmission.', '']
    if spatial_diagnostic is not None:
        value = spatial_diagnostic['moran_i']
        label = 'undefined (constant error or no usable links)' if value is None else f'{value:.6f}'
        lines += [f'Own-history horizon-12 error Moran I: {label}; see the plotted-values CSV.','']
    lines += ['## Reproduction', '', 'Run only after the dependency/test checks and the researcher CPU fitting command in internal/STATUS.md. Checkpoints and data are local-only; the frozen protocol is not edited.', '',
        '```powershell','python -m models.baselines --threads 8 2>&1 | Tee-Object logs/t02_baselines_cpu.log',
        'python -m visuals.baselines_validation 2>&1 | Tee-Object logs/t02_baseline_report.log','```', '',
        'The model command is researcher-run training and can exceed the agent time limit. Completed fits are fingerprinted and reused; completed runs are not repeated. The visual script creates CSV/PNG pairs, updates exploration and visual indexes, and writes this report. All figures, plotting source and data remain local-only under the researcher policy.', '']
    overlay = root/'amendment_v1_1'
    if (overlay/'summary.json').exists():
        lines[0] = '# Validation baselines — Task 2 Gate B accepted'
        lines = [line.replace('after researcher Gate B review and the separate Task 3 timing gate',
                              'after the accepted Gate B decision, a separate Task 3 instruction and its timing gate')
                 .replace('the frozen protocol is not edited',
                          'the original v1 tag is retained and the approved changes are recorded separately in v1.1')
                 for line in lines]
        lines[2] = '**Gate B accepted by the researcher on 29 October 2026.** Protocol v1.1 adds RMSE from saved validation predictions; no refit or final-test forecast/error evaluation.'
        lines += ['## Approved Gate B interpretation and v1.1 RMSE', '',
            'Neighbour features give no clear overall MAE gain, but lower MASE at every reported horizon and the twelve-month total. In the low-maturity tercile, total MAE is 3.89 versus 4.32 systems. Both boosting models beat seasonal naive in corrected DM comparisons at horizons 1 and 6, without such evidence at 12 or for the total. Reliance on neighbours installed base, with little sensitivity to their recent counts, is not evidence of added value.', '',
            'MAE stays primary. RMSE is secondary alongside MASE: squared error targets the conditional mean predicted by fitted Poisson models, while absolute error targets a median. Pool squared losses across equally weighted areas, origins and seeds before taking the root; do not score averaged predictions. Total errors use sums of the same twelve saved monthly forecasts. Monthly units are systems/area/month; total units are systems/area/twelve-month window.', '',
            table(pd.read_csv(overlay/'rmse_summary.csv',dtype={'outcome':str})[['model','outcome','group','rmse']]), '',
            f'[RMSE CSV](../../{overlay.as_posix()}/rmse_summary.csv) · [Amendment](../protocol/protocol_v1_1.md). Generated by `python -m evaluation.amendment`, with zero new fits. Original v1 scores and forecasts are unchanged.', '',
            '## Additional descriptive exploration', '',
            '- [Mean signed error by horizon and maturity](../../data/explore/t02/mean_signed_error.png) / [CSV](../../data/explore/t02/mean_signed_error.csv); forecast minus actual, so negative means underprediction.',
            '- [Absolute, scaled absolute and signed error Moran I](../../data/explore/t02/error_moran_comparison.png) / [CSV](../../data/explore/t02/error_moran_comparison.csv); horizon 12, same observed-area graph and row-standardised weights, no permutation inference. Training-error scaling is not dwelling normalisation.',
            '- [January–September 2025 national snapshot comparison](../../data/explore/t02/pv_2025_snapshot_comparison.csv); all CER postcodes, including unmatched. This is revision growth for the same installation months across snapshots, not year-on-year deployment growth.',
            '- [September 2025 cumulative paper map with capital insets](../figures/cumulative_sep2025.png) / [POA values](../figures/cumulative_sep2025.csv) / [Inset bounds](../figures/cumulative_sep2025_insets.csv); EPSG:9473 Australian Albers. Unknown targets and isolates remain marked.', '']
        revision = json.loads((overlay/'summary.json').read_text())['snapshot_comparison']
        lines += [f"National January–September 2025 certificate-backed PV installations: **{revision['current_count_systems']:,} systems** in the 30 September 2026 snapshot, compared with **{revision['reference_count_systems']:,}** supplied by the researcher for 30 September 2025: **+{revision['increase_systems']:,} systems ({revision['growth_percent']:.4f}%)**. Source: `evaluation.amendment`, national SGU Solar records; reference is researcher-supplied and its archive was not downloaded.", '']
    target = Path('reports/experiments/baselines_validation.md')
    target.write_text('\n'.join(lines),encoding='utf-8')
    return target
