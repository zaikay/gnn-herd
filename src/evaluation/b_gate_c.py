"""B validation Gate C evaluation; withheld until all four conditions complete."""
import hashlib
import json
from pathlib import Path
import numpy as np
import pandas as pd
from threadpoolctl import threadpool_limits
from evaluation.gate_c_metrics import evaluate,compare,spatial_diagnostics,comparison_pairs,REPORTED

OUT=Path('data/processed/t03_b_gate_c')


def dm_family():
    return [(a,b,h) for a,b in comparison_pairs(True) for h in REPORTED]


def require_release():
    from models.b_validation import ROOT,ORDER,SEEDS,authority
    # Check before authority/model/prediction access; no partial comparison release.
    for condition in ORDER:
        path=ROOT/condition/'condition_complete.json'
        if not path.exists():raise RuntimeError(f'B comparison withheld: {condition} incomplete')
        marker=json.loads(path.read_text())
        if (marker['condition']!=condition or marker['fits']!=36 or marker['seeds']!=list(SEEDS)
                or marker['validation_origins']!=36 or marker['last_target']!='2022-10' or marker['test_forecasts_or_losses']):
            raise RuntimeError('Invalid B completion marker')
    cfg,info=authority()
    if json.loads((ROOT/'campaign_manifest.json').read_text())!=info:raise RuntimeError('B campaign provenance changed')
    return cfg,info


def load_predictions(ctx):
    from models.b_validation import ROOT,ORDER,SEEDS,ALIASES,fit_path
    cfg,info=require_release()
    from evaluation.gate_c_io import read_prediction
    result={}; hashes={}
    for condition in ORDER:
        root=ROOT/condition
        records=pd.read_csv(root/'fit_records.csv',dtype={'fit_origin':str})
        if len(records)!=36 or records.duplicated(['seed','fit_origin']).any():raise RuntimeError('Missing/duplicate B fits')
        expected={(s,o) for o in dict.fromkeys(ctx.fit_origins) for s in SEEDS}
        if set(zip(records.seed,records.fit_origin))!=expected:raise RuntimeError('B fit identities differ')
        for s,o in expected:
            path=fit_path(condition,s,o)
            marker=json.loads((path/'complete.json').read_text())
            if marker['epochs']!=65 or not (path/'checkpoint.pt').exists():raise RuntimeError('Missing completed B checkpoint')
        result[ALIASES[condition]]={}
        for seed in SEEDS:
            path=root/f'predictions_seed{seed}.npz'
            result[ALIASES[condition]][seed]=read_prediction(path,ctx)
            hashes[path.as_posix()]=hashlib.sha256(path.read_bytes()).hexdigest()
    return result,{'campaign':info,'prediction_sha256':hashes}


def run():
    from evaluation.gate_c_io import context_from_panel,load_baselines
    from evaluation.gate_c import write_tables
    from evaluation.gate_c_findings import findings
    from evaluation.graph_diagnostics_report import table
    cfg,info=require_release()
    with threadpool_limits(limits=1):
        ctx=context_from_panel(cfg)
        b,provenance=load_predictions(ctx)
        baseline,_,base_provenance=load_baselines(cfg,ctx)
        bundle=evaluate({**baseline,**b},ctx)
        bundle['dm']=compare(bundle['origin'],True)
        assert len(bundle['dm'])==len(dm_family())==20
        bundle['moran'],bundle['difference']=spatial_diagnostics(bundle['areas'],ctx)
        write_tables(bundle,OUT)
        metadata={'architecture':'B','campaign':provenance,'baselines':base_provenance,
                  'dm_family':dm_family(),'new_fits':0,'gpu_use':False,'test_forecasts_or_losses':0}
        (OUT/'manifest.json').write_text(json.dumps(metadata,indent=2)+'\n',encoding='utf-8')
        from visuals.b_gate_c import render,study_geometry
        roots={'visual':Path('visuals/t03/b_validation'),'explore':Path('data/explore/t03/b_validation'),'paper':Path('reports/figures/b_validation')}
        render(bundle,ctx,'released_gnn_validation',geometry=study_geometry(cfg),release={'B':True},roots=roots)
    answer,comparison=findings(bundle['scores'],bundle['dm'])
    text=f'''# B validation — Gate C review

**Gate C remains open for researcher review.** All four B conditions are complete. No final-test access, refitting, new architecture search or estimated blending weights. This report concerns B, not the historical T-GCN. Internal `gnn_*` aliases in CSVs denote B real/shuffled/no graph/without installed base.

## Real versus shuffled

{answer}

{table(comparison)}

Validation p-values are descriptive after architecture selection. No individual behaviour is identified. A lower Moran I does not imply lower prediction error.

## Metrics and seed spread

MAE is primary; MASE is unitless, using shared origin/fit-specific training seasonal scales and the existing pooled zero-scale fallback. RMSE roots pooled squared losses, not averaged seed RMSEs. Losses average areas, origins and seeds equally; scores are individual-seed losses, not an ensemble. Monthly units are systems/area/month; total units are systems/area/twelve-month window, with MASE scale multiplied by twelve. Maturity groups depend on installed base at each origin. Seven unknown areas are masked; isolates retained. All twelve monthly horizons, total and seed SD/min/max are in [scores](../../data/processed/t03_b_gate_c/scores.csv) and [per-seed scores](../../data/processed/t03_b_gate_c/seed_metrics.csv).

'''
    for group in ('all','low','medium','high'):
        part=bundle['scores'].loc[bundle['scores'].group.eq(group)&bundle['scores'].outcome.isin(REPORTED)]
        text+=f'### Maturity: {group}\n\n'+table(part[['model','outcome','mae','mae_seed_sd','mase','mase_seed_sd','rmse','rmse_seed_sd']])+'\n\n'
    dm=bundle['dm'].copy()
    for column in ('p_raw','p_holm'):dm[column]=dm[column].map(lambda x:'undefined' if not np.isfinite(x) else f'{x:.6g}')
    text+='## Predeclared DM/Holm family\n\nExactly 20 two-sided MAE-loss tests: B real against no graph, shuffled, both frozen boosting baselines and the included ablation; horizons 1, 6, 12 and total. Origin-level area losses are averaged over the fixed three seeds before DM. HLN/Bartlett h−1 correction; total h=12. One Holm adjustment over all 20 tests, retaining undefined-test slots. No RMSE/MASE test family.\n\n'+table(dm)+'\n\n'
    text+='''## Spatial diagnostics and figures

[Error horizons](../../visuals/t03/b_validation/gnn_error_horizon.png), [totals](../../visuals/t03/b_validation/gnn_error_total.png), [maturity](../../visuals/t03/b_validation/gnn_error_maturity.png), [real/control comparisons](../../visuals/t03/b_validation/gnn_graph_comparison.png), [scaled errors](../../data/explore/t03/b_validation/gnn_scaled_error_map.png), [real minus shuffled](../../data/explore/t03/b_validation/gnn_real_minus_shuffled_map.png), [Moran I](../../data/explore/t03/b_validation/gnn_error_moran.png). Every figure has a plotted CSV. Maps retain extremes using log/symmetric-log scales; unknown areas are missing, not zero error. Row-standardised rook Moran I includes observed isolates with zero rows; no permutation significance or dwelling normalisation. [Numeric tables/index](../../data/processed/t03_b_gate_c/index.md).

## Limitations and stop

Retrospective revised CER data, 36 overlapping validation origins and three fixed seeds. The B architecture was selected on two of these origins; its gate evidence is development evidence. The late battery-scheme test-month limitation remains for the sealed test, which has not been evaluated. Screen anchor fits are reused only where exact model/data/training identity holds. No further fitting follows this report. Researcher Gate C decision required.

Generators: `models.b_validation`, `evaluation.b_gate_c`, `visuals.b_gate_c`; protocol-v4-b-validation. Frozen baseline selections unchanged; exploratory equal-weight anchor combinations are outside this family.
'''
    Path('reports/experiments/b_validation.md').write_text(text,encoding='utf-8')
    print(json.dumps({'event':'B_gate_c_report_complete','dm_family_size':20,'report':'reports/experiments/b_validation.md','test_forecasts_or_losses':0}))


if __name__=='__main__':run()
