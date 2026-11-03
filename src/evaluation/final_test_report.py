"""Final v7 tables/report; a separate labelled root is mandatory for preflight."""
from pathlib import Path
import numpy as np
from evaluation.graph_diagnostics_report import table


def write_outputs(bundle,ctx,spec,root,scope):
    if scope not in ('final_test','synthetic_validation_preflight'):raise ValueError('Explicit report scope required')
    root=Path(root);root.mkdir(parents=True,exist_ok=True)
    if scope!='final_test' and root==Path('data/processed/t03_final_test/evaluation'):raise ValueError('Preflight cannot write final results')
    paths=[]
    for kind in ('individual','ensemble'):
        for name,frame in bundle[kind].items():
            path=root/(kind+'_'+name+('.csv.gz' if name in ('origin','areas') else '.csv'))
            frame.to_csv(path,index=False);paths.append(path)
    for name in ('chains','intervals','target_periods','target_coverage','target_period_cells'):
        path=root/(name+'.csv');bundle[name].to_csv(path,index=False);paths.append(path)
    from visuals.final_test import render
    figure_root=Path('data/explore/t03/protocol_v7_final_test') if scope=='final_test' else root/'figures'
    paths+=render(bundle,figure_root,scope)
    report=Path('reports/experiments/protocol_v7_final_test_results.md') if scope=='final_test' else root/'preflight_report.md'
    title='Protocol v7 final test results' if scope=='final_test' else 'SYNTHETIC / VALIDATION-DATE PREFLIGHT: not final-test results'
    text='# '+title+'\n\n'
    text+='All scores use the fixed three-seed forecast ensembles. Individual seed scores are separate. No model/weight fit occurs during this evaluation. Combination weights are the approved six-decimal validation constants; the no-graph sensitivity uses those SAME weights.\n\n'
    text+='## Fixed-sequence confirmatory chains\n\nAccuracy: A7, A2, A1, A4, A3, A6, A5. Behavioural: B3, B1, B2. Each chain alpha 0.025, one-sided in the predicted lower-loss direction, stopped at first non-rejection. B4 was dropped before the test. A6 tests E[Lc - 1.01 Lo] < 0; it can reject non-inferiority even if the unshifted combination loss is slightly higher. No Holm correction. Untested later hypotheses have no computed p-value.\n\n'
    shown=bundle['chains'].copy()
    shown['p_one_sided']=shown.p_one_sided.map(lambda p:'not tested / undefined' if not np.isfinite(p) else f'{p:.8g}')
    text+=table(shown)+'\n\n## Forecast-ensemble descriptive scores\n\n'
    text+='MAE/RMSE: systems/area/month, or systems/area/twelve-month window for total. MASE: unitless training-only seasonal scales with accepted pooled fallback, twelve times monthly scale for total. These are one-forecast ensemble scores; no seed SD applies. All monthly horizons and dynamic maturity groups are in the accompanying CSVs.\n\n'
    for group in ('all','low','medium','high'):
        selected=bundle['ensemble']['scores'].loc[lambda f:f.group.eq(group)&f.outcome.isin(['1','6','12','total_12'])]
        text+='### '+group+' maturity\n\n'+table(selected[['model','outcome','mae','mase','rmse','mean_signed_error']])+'\n\n'
    text+='## Individual seed scores and spread\n\nEvery individual seed is in individual_seed.csv; individual_scores.csv holds the mean/SD/min/max of individual losses, which are not the primary ensemble scores.\n\n'
    text+='## Descriptive real-minus-control 95% intervals\n\nMean origin MAE differences with Bartlett HAC h-1 and the approved HLN-inverted Student t interval; h=12 for total, otherwise forecast horizon. Pointwise, descriptive, no additional confirmatory family. Negative favours real; undefined intervals are reported as missing.\n\n'+table(bundle['intervals'])+'\n\n'
    text+='## Target months after battery eligibility\n\nJuly-September 2025 target months are separately described and remain IN all primary scores. Grouping uses target month, not forecast origin. These are monthly losses, not partial twelve-month totals. Available origin/horizon cell counts are reported; no additional p-values.\n\n'+table(bundle['target_periods'])+'\n\n'
    text+='## Interpretation limits\n\nOnly 24 overlapping forecast origins and three fixed seeds. Revised CER data and certificate reporting lag remain limitations. Aggregate prediction differences cannot identify individual behaviour. A non-rejection is not proof of equivalence. No test result may change weights, epochs, configurations, chain order or selected primary model. No further computation or model change is initiated by this report.\n\n'
    text+='Numeric tables and figure CSVs are retained beside this report/output root. Protocol authority: reports/protocol/protocol_v7_final_test.md and configs/protocol_v7_test.json at protocol-v7-test.\n'
    report.write_text(text,encoding='utf-8');paths.append(report)
    for path in paths:
        if path.stat().st_size>=5_000_000:raise ValueError('Result/figure file exceeds 5 MB')
    return paths,report
