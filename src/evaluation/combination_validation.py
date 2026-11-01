"""Exploratory validation-only equal-weight combinations; no fits/test evaluation."""
import json
from pathlib import Path
import numpy as np
import pandas as pd
from threadpoolctl import threadpool_limits
from evaluation.baselines import holm
from evaluation.dm import dm_from_losses
from evaluation.gate_c_metrics import REPORTED,evaluate

COMBINATIONS=('half_own_B','half_neighbour_B')
REFERENCES=('gradient_boosting_own','gnn_real')
OUT=Path('data/processed/t03_combination_validation')


def equal_weight(left,right):
    if set(left)!=set(right) or set(left)!={11,29,47}:raise ValueError('Identical three-seed forecasts required')
    result={}
    for seed in left:
        a=np.asarray(left[seed],dtype=np.float64); b=np.asarray(right[seed],dtype=np.float64)
        if a.shape!=b.shape or not np.isfinite(a).all() or not np.isfinite(b).all() or (a<0).any() or (b<0).any():
            raise ValueError('Aligned finite nonnegative forecasts required')
        result[seed]=.5*a+.5*b
    return result


def dm_family():return [(c,r,h) for c in COMBINATIONS for r in REFERENCES for h in REPORTED]


def compare_combinations(origin,dm=dm_from_losses):
    records=[]
    for combination,reference,outcome in dm_family():
        series=[]
        for model in (combination,reference):
            part=origin.loc[origin.model.eq(model)&origin.group.eq('all')&origin.outcome.eq(outcome)]
            if part.duplicated(['origin','seed']).any() or any(set(g.seed)!={11,29,47} for _,g in part.groupby('origin')):
                raise ValueError('Incomplete/duplicate combination DM losses')
            losses=part.groupby('origin').mae.mean().sort_index()
            if losses.empty or not np.isfinite(losses).all() or losses.lt(0).any():raise ValueError('Invalid loss series')
            series.append(losses)
        if not series[0].index.equals(series[1].index):raise ValueError('DM calendars differ')
        h=12 if outcome=='total_12' else int(outcome)
        row={'model_a':combination,'model_b':reference,'outcome':outcome,'h':h,'origins':len(series[0]),
             'statistic':np.nan,'p_raw':np.nan,'status':'defined'}
        try:
            statistic,p=dm(series[0].to_numpy(),series[1].to_numpy(),h)
            if not np.isfinite([statistic,p]).all() or not 0<=p<=1:raise ValueError('Nonfinite/invalid DM result')
            row.update(statistic=float(statistic),p_raw=float(p))
        except (ValueError,ArithmeticError) as error:row['status']='undefined: '+str(error)
        records.append(row)
    result=pd.DataFrame(records); result['family_size']=16; result['p_holm']=holm(result.p_raw)
    return result


def main():
    from evaluation.b_gate_c import require_release,load_predictions
    from evaluation.gate_c_io import context_from_panel,load_baselines
    from evaluation.gate_c import write_tables
    from evaluation.graph_diagnostics_report import table
    from evaluation.final_test_cost import saved_cost_projection
    cfg,_=require_release()
    with threadpool_limits(limits=1):
        ctx=context_from_panel(cfg)
        b,b_provenance=load_predictions(ctx); baseline,_,base_provenance=load_baselines(cfg,ctx)
        values={'gradient_boosting_own':baseline['gradient_boosting_own'],
                'gradient_boosting_neighbours':baseline['gradient_boosting_neighbours'],'gnn_real':b['gnn_real']}
        values['half_own_B']=equal_weight(values['gradient_boosting_own'],values['gnn_real'])
        values['half_neighbour_B']=equal_weight(values['gradient_boosting_neighbours'],values['gnn_real'])
        bundle=evaluate(values,ctx); bundle['dm']=compare_combinations(bundle['origin'])
        write_tables(bundle,OUT)
        calendar,cost_detail,cost=saved_cost_projection(cfg,len(ctx.codes))
        calendar.to_csv(OUT/'final_test_refit_calendar.csv',index=False)
        cost_detail.to_csv(OUT/'final_test_cost_details.csv',index=False); cost.to_csv(OUT/'final_test_cost_summary.csv',index=False)
        metadata={'scope':'validation only; test calendar arithmetic/fit records only','weights':[.5,.5],
                  'combination_storage':'float64 arithmetic, no fitted weights or cross-seed ensemble',
                  'B':b_provenance,'baselines':base_provenance,'descriptive_dm_family':dm_family(),
                  'test_forecasts_or_losses':0,'new_fits':0,'gpu_use':False}
        (OUT/'manifest.json').write_text(json.dumps(metadata,indent=2)+'\n',encoding='utf-8')
    from visuals.combination_validation import render
    render(bundle['scores'],cost)
    text='''# Equal-weight combination validation — 1 November 2026

**Descriptive and exploratory; CPU only, no fits. Gate C accepted by the researcher on 1 November 2026.** Final-test targets/forecasts/losses remain untouched. All results below use the 36 frozen validation origins, November 2018–October 2021, twelve horizons, 2,634 observed areas and seeds 11/29/47.

## Accepted Gate C findings

- B real beats B no graph on MAE at every reported outcome, with Holm p below 0.05 at horizons 1 and 6.
- B real and B shuffled cannot be distinguished (all Holm p = 1). The gain is consistent with pooling information within states, rather than adjacency specifically; this does not identify a causal mechanism.
- Both boosting baselines beat B real on MAE at every reported outcome. B real has lower MASE than own-lag boosting at every outcome, most clearly in low-maturity areas.
- Removing installed base worsens MASE at every outcome, most in low-maturity areas; the MAE tests are not significant.

## Fixed combinations and scoring

`half_own_B` is 0.5 × own-lag boosting + 0.5 × B real. `half_neighbour_B` is 0.5 × neighbour-lag boosting + 0.5 × B real. Each seed is paired with the same seed; no weight is estimated and forecasts are not averaged across seeds before scoring. Arithmetic is float64 on saved forecasts, including summation of combination totals. Existing float32 baseline/B total conventions are retained for those references. Tiny rounding differences are possible, without an economic change to the weights.

Absolute/squared errors average areas within each origin/group, then origins and seeds. RMSE roots pooled squared errors. MASE uses shared training-only seasonal scales, including the existing pooled fallback for zero scales; total scale is twelve times monthly scale. Maturity is recomputed at each origin; unknown areas remain masked and isolates retained. Seed spread is sample SD/min/max of individually scored seeds. Monthly units: systems/area/month; total: systems/area/twelve-month window; MASE unitless.

'''
    against_b=bundle['dm'].loc[bundle['dm'].model_b.eq('gnn_real')]
    against_own=bundle['dm'].loc[bundle['dm'].model_b.eq('gradient_boosting_own')]
    text+=f"## Descriptive result summary\n\nBoth combinations have lower MAE than B real at all four tested outcomes. {int(against_b.p_holm.lt(.05).sum())}/8 comparisons against B real have Holm p < 0.05; {int(against_own.p_holm.lt(.05).sum())}/8 against own-lag boosting do. Differences against own-lag boosting vary by horizon; the combinations do not establish an improvement over that baseline. These are validation-development comparisons, not final-test confirmation.\n\n"
    for group in ('all','low','medium','high'):
        part=bundle['scores'].loc[bundle['scores'].group.eq(group)]
        text+=f'### Maturity: {group}\n\n'+table(part[['model','outcome','mae','mae_seed_sd','mase','mase_seed_sd','rmse','rmse_seed_sd']])+'\n\n'
    text+='''All monthly horizons 1–12, totals and seed min/max are in [scores](../../data/processed/t03_combination_validation/scores.csv), [per-seed metrics](../../data/processed/t03_combination_validation/seed_metrics.csv) and [origin losses](../../data/processed/t03_combination_validation/origin_metrics.csv.gz). [Horizon/total figure](../../data/explore/t03/combination_validation/errors.png); [maturity figure](../../data/explore/t03/combination_validation/maturity.png).

## Separate descriptive DM/Holm family

Exactly 16 two-sided MAE-loss tests: each of the two combinations against frozen own-lag boosting and against B real, at horizons 1, 6, 12 and the twelve-month total. No test against neighbour boosting was added. This family is separate from the accepted B 20-test family. Average area losses per origin and then average over the same three seeds before DM; HLN/Bartlett h−1 covariance convention, total h=12. One Holm adjustment across all 16; undefined tests reserve slots. No RMSE/MASE testing family. Inspection of already-used validation data makes all p-values descriptive.

'''
    dm=bundle['dm'].copy()
    for c in ('p_raw','p_holm'):dm[c]=dm[c].map(lambda x:'undefined' if not np.isfinite(x) else f'{x:.6g}')
    text+=table(dm)+'\n\n## Final-test cost estimate — not execution authorisation\n\n'
    totals=cost.groupby('device')[['hours_low','hours_central','hours_high']].sum()
    text+='Resource totals:\n\n'+table(totals.reset_index())+'\n\nPer condition:\n\n'
    text+=table(cost)+'\n\n'
    text+='''Calendar arithmetic only: eight quarterly test refits, October 2022–July 2024, serving 24 test origins through September 2024. Each condition requires 8 × 3 = 24 fits: 48 CPU fits for both boosting baselines, 96 GPU fits for the four B conditions, 144 fits overall. No validation checkpoint can substitute for a later expanding-window test refit. No retuning/search, C model or additional blending fit is included. Equal-weight combinations add only arithmetic after forecasts, not fitted models.

Projected times use the last four observed validation refit dates for each condition/seed. B uses measured seconds per epoch/origin batch × 65 epochs and future calendar batch counts. Boosting uses historical selected-configuration seconds per eligible training row × future calendar row counts. Central is the median per-seed rate; low/high use its empirical 25th/75th percentiles, not confidence intervals or guaranteed bounds. CPU historical times include serialization; B times exclude inference. Training-set growth may be nonlinear for boosting. Power/load/thermal variation, inference, setup, final scoring and session breaks are not forecast here. CPU hours and GPU hours are separate resources; serial wall time would approximately sum them, without parallelism.

[Refit calendar](../../data/processed/t03_combination_validation/final_test_refit_calendar.csv), [per-fit scenarios](../../data/processed/t03_combination_validation/final_test_cost_details.csv), [cost summary](../../data/processed/t03_combination_validation/final_test_cost_summary.csv), [cost figure](../../visuals/t03/combination_validation/final_test_cost.png). No panel, feature or target array is read by the cost module: it uses protocol dates and saved fit records only. No test runner or test command is implemented or executed.

## Reproducibility and stop

Sources: `evaluation.combination_validation`, `evaluation.final_test_cost`, `visuals.combination_validation`. [Provenance](../../data/processed/t03_combination_validation/manifest.json), [exploration index](../../data/explore/t03/combination_validation/index.md). No frozen fit/config/protocol source was changed. Stop for researcher review; Gate C acceptance does not itself authorise touching the final test.
'''
    Path('reports/experiments/combination_validation.md').write_text(text,encoding='utf-8')
    print(bundle['scores'].loc[bundle['scores'].group.eq('all')&bundle['scores'].outcome.isin(REPORTED),['model','outcome','mae','mase','rmse']].to_string(index=False))
    print(cost.to_string(index=False))


if __name__=='__main__':main()
