"""Gate C orchestration: baseline-only preflight now; guarded GNN release later."""
import argparse
import json
import os
from pathlib import Path

import numpy as np
import pandas as pd
from threadpoolctl import threadpool_limits

from evaluation.gate_c_metrics import evaluate, compare, spatial_diagnostics, REPORTED
from evaluation.gate_c_io import frozen_context, load_baselines, load_gnn_predictions, comparison_release, campaign_path
from evaluation.frozen import frozen_protocol
from evaluation.result_report import table
from evaluation.gate_c_findings import executive_summary


def write_tables(bundle,output):
    output=Path(output); output.mkdir(parents=True,exist_ok=True)
    entries=[]
    for key,name in (('origin','origin_metrics.csv.gz'),('seed','seed_metrics.csv'),
                     ('scores','scores.csv'),('areas','area_metrics.csv.gz'),
                     ('dm','dm_tests.csv'),('moran','error_moran.csv'),('difference','real_minus_shuffled.csv')):
        if key in bundle:
            bundle[key].to_csv(output/name,index=False)
            if (output/name).stat().st_size>=5_000_000:
                raise ValueError(f'Evaluation table exceeds 5 MB: {name}')
            entries.append(f'- [{name}]({name}): {key} table; `evaluation.gate_c.write_tables`.')
    (output/'index.md').write_text('# Evaluation tables\n\n'+'\n'.join(entries)+'\n',encoding='utf-8')


def verify_saved_baselines(cfg,ctx):
    """No GNN path lookup/load/metric/DM call occurs in this preflight."""
    predictions,root,provenance=load_baselines(cfg,ctx)
    bundle=evaluate(predictions,ctx,seeds=tuple(cfg['tuning']['seeds']))
    keys=['model','outcome','group']
    old=pd.read_csv(root/'scores.csv',dtype={'outcome':str}).set_index(keys).sort_index()
    actual=bundle['scores'].set_index(keys).reindex(old.index)
    for name in ('mae','mase','mae_seed_sd','mase_seed_sd'):
        np.testing.assert_allclose(actual[name],old[name],rtol=1e-11,atol=1e-10)
    rmse=pd.read_csv(root/'amendment_v1_1/rmse_summary.csv',dtype={'outcome':str}).set_index(keys)
    np.testing.assert_allclose(bundle['scores'].set_index(keys).reindex(rmse.index).rmse,rmse.rmse,rtol=1e-11,atol=1e-10)
    seed_keys=['model','seed','outcome','group']
    old_seed=pd.read_csv(root/'seed_metrics.csv',dtype={'outcome':str}).set_index(seed_keys)
    new_seed=bundle['seed'].set_index(seed_keys).reindex(old_seed.index)
    np.testing.assert_allclose(new_seed[['mae','mase']],old_seed[['mae','mase']],rtol=1e-11,atol=1e-10)
    bundle['moran'],bundle['difference']=spatial_diagnostics(bundle['areas'],ctx)
    prior=pd.read_csv('data/explore/t02/validation_error_moran.csv').moran_i.iloc[0]
    current=bundle['moran'].loc[lambda f:f.model.eq('gradient_boosting_own') & f.outcome.eq('12') & f.error_type.eq('absolute'),'moran_i'].iloc[0]
    np.testing.assert_allclose(current,prior,rtol=1e-10)
    info={'scope':'saved_baselines_only','baseline_run':provenance['baseline_run'],
        'reported_score_rows_matched':len(old),'rmse_rows_matched':len(rmse),
        'seed_score_rows_matched':len(old_seed),'prior_moran_reproduced':True,
        'gnn_prediction_files_opened':0,'gnn_comparisons_computed':0,'new_fits':0,'gpu_use':False,
        'metrics':'MAE/MASE means across seeds; RMSE root after pooled MSE; seed SD/min/max on seed scores'}
    return bundle,info


def write_report(bundle,metadata,output=Path('reports/experiments/gnn_validation.md'),data_root=Path('data/processed/t03_gate_c'),figure_roots=None):
    output=Path(output)
    synthetic=metadata.get('source_kind')=='synthetic'
    if not synthetic and metadata.get('source_kind')!='released_gnn_validation':
        raise ValueError('Study report requires a released GNN evaluation; fixture reports must be marked synthetic')
    if not synthetic:
        comparison_release(campaign_path(metadata['protocol_sha256']),metadata['gnn']['release'].get('decision_file'))
    roots=figure_roots or {'visual':Path('visuals/t03'),'explore':Path('data/explore/t03'),'paper':Path('reports/figures')}
    def link(path):
        return os.path.relpath(Path(path).resolve(),output.parent.resolve()).replace(os.sep,'/')
    lines=['# '+('SYNTHETIC TEST FIXTURE — not study results' if synthetic else 'GNN validation — Task 3 Gate C review'),'']
    if not synthetic:
        summary,comparison=executive_summary(bundle['scores'],bundle['dm'])
        lines += summary
        comparison=comparison.copy()
        comparison['p_holm']=comparison.p_holm.map(lambda p:'undefined' if not np.isfinite(p) else f'{p:.6g}')
        lines += [table(comparison),'']
    lines += ['This report is '+('a synthetic pipeline test, not evidence about the study models.' if synthetic else 'validation development evidence only. The final test is sealed; no individual behaviour or causal mechanism is identified.'),'',
        '## Metrics and weighting','',
        'All models share identical observed areas, origin dates, per-origin maturity terciles and training-only seasonal MASE scales. Areas without CER records are not evaluated. Origin groups are recomputed from cumulative base through each origin, with postcode ties. Absolute/squared losses are averaged across areas within each origin, then origins and seeds. MAE is primary. RMSE is the root after pooling squared losses, not the mean of seed RMSE and not a prediction ensemble. Total error sums all twelve forecasts/actuals before subtraction, preserving saved float32 forecast totals and float64 loss accumulation. Monthly errors are systems/area/month; total errors are systems/area/twelve-month window. MASE is unitless, with total scale twelve times the monthly training scale.','',
        'Seed spread is sample SD (ddof=1), minimum and maximum of independently scored seed results. Seasonal naive is the same fixed prediction across all three seeds; its spread is zero. No model is refit.','']
    for group in ('all','low','medium','high'):
        selected=bundle['scores'].loc[lambda f:f.group.eq(group) & f.outcome.isin(REPORTED)]
        lines += [f'### Maturity: {group}','',table(selected[['model','outcome','mae','mae_seed_sd','mase','mase_seed_sd','rmse','rmse_seed_sd']]),'']
    lines += ['All twelve monthly horizons, total, min/max and per-seed scores are in the linked CSVs.','',
        '## Predeclared DM/Holm family','',
        'Real graph versus no graph, shuffled graph and each boosting baseline; also versus no-base if retained. The testing unit is the origin: area-averaged absolute losses, averaged over the same seeds before DM. dieboldmariano 1.1.0, Bartlett h−1 covariance weights, HLN correction, two-sided tests; horizon 12 for totals. One Holm adjustment covers the whole 16- or 20-test family. Undefined statistics/p-values stay undefined and reserve their family slots. Validation p-values are descriptive because validation was used for tuning. RMSE adds no squared-loss testing family.','',
        table(bundle['dm'].assign(p_raw=bundle['dm'].p_raw.map(lambda p:'undefined' if not np.isfinite(p) else f'{p:.6g}'),
                                 p_holm=bundle['dm'].p_holm.map(lambda p:'undefined' if not np.isfinite(p) else f'{p:.6g}'))),'','## Spatial diagnostics','',
        'Maps use horizon-12 per-area seasonal scaled absolute errors and real-minus-shuffled scaled error (negative favours real). The real-error colour scale is logarithmic; the difference map uses symmetric-log colour, linear within -1 to 1 MASE, to retain all extreme values without obscuring typical differences. No values are clipped or excluded. Moran I is row-standardised rook clustering of per-area absolute, scaled absolute and signed errors averaged over origins/seeds. Isolates have zero weight rows; seven unknown areas are not zero-error observations. Signed error is forecast minus actual. No dwelling normalisation or permutation significance is supplied; absolute errors can mix volume and predictability. These diagnostics are descriptive.','',table(bundle['moran']),'',
        '## Gate C: real graph versus shuffled','']
    scores=bundle['scores'].set_index(['model','outcome','group'])
    for outcome in REPORTED:
        real=scores.loc[('gnn_real',outcome,'all')]; shuffled=scores.loc[('gnn_shuffled',outcome,'all')]
        lines.append(f'- Outcome {outcome}: real MAE {real.mae:.6f}, shuffled {shuffled.mae:.6f}; real MASE {real.mase:.6f}, shuffled {shuffled.mase:.6f}. These are development comparisons, not a causal or final-test conclusion.')
    lines += ['', 'The researcher reviews Gate C and decides any hybrid work. No hybrid is selected by this pipeline.','',
        '## Figures and provenance','',
        *[f'- [{title}]({link(Path(roots[kind])/(stem+".png"))}) / [CSV]({link(Path(roots[kind])/(stem+".csv"))}).' for kind,stem,title in (
            ('visual','gnn_error_horizon','All-model monthly error'),('visual','gnn_error_total','Twelve-month total'),
            ('visual','gnn_error_maturity','Maturity errors'),('paper','t03_graph_comparison','Core graph comparison / Figure 3 candidate'),
            ('explore','gnn_scaled_error_map','Real scaled-error map'),('explore','gnn_real_minus_shuffled_map','Real-minus-shuffled map'),
            ('explore','gnn_error_moran','Scaled/signed Moran summary'))],
        f'- [Full scores]({link(Path(data_root)/"scores.csv")}), [seed spread]({link(Path(data_root)/"seed_metrics.csv")}), [origin losses]({link(Path(data_root)/"origin_metrics.csv.gz")}), [area errors]({link(Path(data_root)/"area_metrics.csv.gz")}).','',
        'Generated by `evaluation.gate_c` and `visuals.gate_c`. All result figures/values and plot source remain local-only. Saved baselines retain their original fit provenance; protocol v2 governs GNN fitting and the combined evaluation.','']
    output.parent.mkdir(parents=True,exist_ok=True)
    output.write_text('\n'.join(lines),encoding='utf-8')


def main():
    parser=argparse.ArgumentParser(__doc__)
    sub=parser.add_subparsers(dest='command',required=True)
    sub.add_parser('baseline-check',help='Saved baseline predictions only; no GNN forecast access')
    live=sub.add_parser('evaluate',help='Withheld until fourth completes or researcher formally drops it')
    live.add_argument('--drop-decision',type=Path)
    args=parser.parse_args()
    with threadpool_limits(limits=1):
        if args.command=='baseline-check':
            cfg,signature,ctx=frozen_context()
            bundle,info=verify_saved_baselines(cfg,ctx)
            write_tables(bundle,'data/explore/t03/gate_c_preflight/baselines')
            Path('reports/experiments/t03_gate_c_baseline_check.json').write_text(json.dumps(info,indent=2),encoding='utf-8')
            print(json.dumps(info,indent=2))
            return
        cfg,signature=frozen_protocol('protocol-v2')
        # Guard first, before context/baseline/GNN loading or result computation.
        comparison_release(campaign_path(signature),args.drop_decision)
        from evaluation.gate_c_io import context_from_panel
        ctx=context_from_panel(cfg)
        baseline,_,base_provenance=load_baselines(cfg,ctx)
        gnn,gnn_provenance=load_gnn_predictions(cfg,ctx,signature,args.drop_decision)
        bundle=evaluate({**baseline,**gnn},ctx,seeds=tuple(cfg['tuning']['seeds']))
        bundle['dm']=compare(bundle['origin'],gnn_provenance['include_optional'])
        bundle['moran'],bundle['difference']=spatial_diagnostics(bundle['areas'],ctx)
        output=Path('data/processed/t03_gate_c'); write_tables(bundle,output)
        metadata={'source_kind':'released_gnn_validation','protocol_sha256':signature,
                  'baseline':base_provenance,'gnn':gnn_provenance,'test_forecasts_or_losses':0}
        (output/'manifest.json').write_text(json.dumps(metadata,indent=2),encoding='utf-8')
        from visuals.gate_c import render, study_geometry
        render(bundle,ctx,source_kind='released_gnn_validation',geometry=study_geometry(cfg),release=metadata)
        write_report(bundle,metadata,data_root=output)
        print('Released Gate C validation outputs written; no test evaluation or refit.')


if __name__=='__main__':
    main()
