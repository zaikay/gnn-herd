"""Write diagnostic tables and verify against existing Gate C scores, CPU only."""
import hashlib
import json
import re
from pathlib import Path
import numpy as np
import pandas as pd

ROOT=Path('data/explore/t03/graph_diagnostics')
REPORT=Path('reports/experiments/t03_graph_diagnostics.md')


def table(frame):
    def cell(value):
        if isinstance(value,(float,np.floating)):return f'{value:.6f}'
        return str(value)
    return '\n'.join(['| '+' | '.join(map(str,frame.columns))+' |',
                      '| '+' | '.join(['---']*len(frame.columns))+' |']+
                     ['| '+' | '.join(cell(v) for v in row)+' |' for row in frame.itertuples(index=False,name=None)])


def main():
    area=pd.read_csv(ROOT/'degree_area_ratios.csv.gz',dtype={'postcode':str,'outcome':str})
    scores=pd.read_csv('data/processed/t03_gate_c/scores.csv',dtype={'outcome':str})
    # Independent aggregate checks against the completed, previously verified evaluation.
    checked=0
    for model,column in [('gnn_real','real_mae'),('gnn_no_graph','no_graph_mae')]:
        aggregate=area.groupby('outcome')[column].mean()
        reference=scores.loc[scores.model.eq(model)&scores.group.eq('all')].set_index('outcome').mae
        np.testing.assert_allclose(aggregate.sort_index(),reference.sort_index(),rtol=1e-12,atol=1e-12)
        checked+=len(aggregate)
    signed=pd.read_csv(ROOT/'signed_error_maturity.csv',dtype={'outcome':str})
    joined=signed.merge(scores[['model','outcome','group','mean_signed_error']],on=['model','outcome','group'],suffixes=('_new','_old'),validate='one_to_one')
    assert len(joined)==208
    np.testing.assert_allclose(joined.mean_signed_error_new,joined.mean_signed_error_old,rtol=1e-11,atol=1e-11)
    before=json.loads(Path('logs/t03_graph_diagnostics_frozen_before.json').read_text())
    after={name:hashlib.sha256(Path(name).read_bytes()).hexdigest() for name in before}
    assert before==after, 'Protected file changed'
    Path('logs/t03_graph_diagnostics_frozen_after.json').write_text(json.dumps(after,indent=2))
    summary=json.loads((ROOT/'summary.json').read_text())
    isolates=pd.read_csv(ROOT/'isolates_mae.csv',dtype={'outcome':str})
    isolates['sort']=isolates.outcome.map({str(i):i for i in range(1,13)}|{'total_12':13})
    isolates=isolates.sort_values('sort').drop(columns='sort')
    bins=pd.read_csv(ROOT/'degree_binned.csv',dtype={'outcome':str})
    association=pd.read_csv(ROOT/'degree_association.csv',dtype={'outcome':str})
    pull=pd.read_csv(ROOT/'pull_summary.csv',dtype={'outcome':str})
    fits=pd.read_csv(ROOT/'selected_training_fit.csv')
    training=fits.groupby('condition',as_index=False).agg(width=('width','first'),learning_rate=('learning_rate','first'),
        fits=('seed','size'),mean_final_loss=('final_training_loss','mean'),min_final_loss=('final_training_loss','min'),
        max_final_loss=('final_training_loss','max'),mean_last10_decrease=('last10_loss_decrease','mean'))
    paired=fits.pivot(index=['fit_origin','seed'],columns='condition',values='final_training_loss')
    paired_summary=[]
    for condition in ['real','within_state_shuffled','real_without_installed_base']:
        difference=paired[condition]-paired.no_graph
        paired_summary.append({'condition':condition,'mean_loss_minus_no_graph':difference.mean(),
                               'fits_with_higher_loss':int((difference>0).sum()),'paired_fits':len(difference)})
    four_hours=summary['screening_reference_four_fit_hours']
    boost_hours=summary['boosting_reference_eight_fit_hours']
    budget=pd.DataFrame([
        {'candidate':'A: separate self/neighbour GRU','fits':4,'measured_old_reference_h':four_hours,
         'planning_lower_h':1.5*four_hours,'planning_upper_h':2.5*four_hours},
        {'candidate':'B: local GRU + late residual graph','fits':4,'measured_old_reference_h':four_hours,
         'planning_lower_h':.8*four_hours,'planning_upper_h':1.5*four_hours},
        {'candidate':'Two boosting conditions combined (CPU)','fits':8,'measured_old_reference_h':boost_hours,
         'planning_lower_h':boost_hours,'planning_upper_h':1.5*boost_hours}])
    budget.to_csv(ROOT/'proposed_screening_budget.csv',index=False)
    index=ROOT/'index.md'
    entry='- [proposed_screening_budget.csv](proposed_screening_budget.csv): `evaluation.graph_diagnostics_report`; unmeasured candidate planning ranges from saved fit times.\n'
    existing=index.read_text(encoding='utf-8')
    if '[proposed_screening_budget.csv]' not in existing:index.write_text(existing+'\n'+entry,encoding='utf-8')
    text=REPORT.read_text(encoding='utf-8').split('\n## Diagnostic results\n')[0]
    text+='''
## Diagnostic results

### 1. Actual operator and identity check

The code uses **S = D^(-1/2) (A_observed + I) D^(-1/2)**, with D the row degree including the self edge. A node with d observed neighbours gives itself weight 1/(d+1), and neighbour j weight 1/sqrt((d+1)(d_j+1)). The neighbour's degree matters: degree alone does not determine the neighbour weights. Unknown nodes cannot send or receive cross-node messages; they are masked before and after aggregation.

The actual code was called on a nine-node graph: one isolate, one isolated pair, and a five-leaf star. These are state weights before the learned gate projections:

'''
    op=pd.read_csv(ROOT/'operator_summary.csv')
    text+=table(op.loc[op.condition.eq('real')&op.node.isin(['isolate','pair_a','hub_5','leaf_1']),
                       ['node','degree','self_weight','neighbour_weights','neighbour_weight_sum','row_sum']])
    text+='''

Thus the pair node has self 0.5 and neighbour 0.5. The degree-five star hub has self 1/6 and **each** leaf weight 1/sqrt(12), not 1/6. Its row sum exceeds one. A degree-one leaf connected to that hub has self 0.5 and hub weight 1/sqrt(12). Symmetric normalisation does not preserve a constant signal on an irregular graph. This is an implemented design property, not evidence that identity was omitted.

The toy real and shuffled calls use the same supplied edges to check their common operator implementation; shuffling itself happens upstream. Independently, one saved seed-11, August-2020 selected checkpoint from each of the four conditions was loaded with `map_location='cpu'`. Each stored operator exactly matches its actual saved real/shuffled/no-graph edge construction and all diagonals are positive. All 15 observed isolate rows are identity. On the toy graph, copying identical learned weights into the three operator conditions gives **exactly equal isolated-node forecasts**. No training was performed. This checks the operator and local computation, not every possible implementation fault in the entire campaign.

The gate and candidate projections each act on graph-mixed concatenated input/hidden state. There is one shared projection for own and neighbour information within each gate/candidate, rather than separate learned self and neighbour projections. The GRU update retains its usual hidden-state path; there is no separate unaggregated current-input projection.

[Operator figure](../../data/explore/t03/graph_diagnostics/operator_weights.png), [all weights](../../data/explore/t03/graph_diagnostics/operator_toy_weights.csv), [checkpoint checks](../../data/explore/t03/graph_diagnostics/checkpoint_operator_checks.csv).

### 2. Observed isolates

There are 15 original observed isolates and 15 effective observed isolates: masking unknown nodes creates no additional observed isolates. MAE is systems per area/month, or systems per area/window for total_12.

'''+table(isolates)+'''

Isolates are worse under independently trained real graph: monthly mean-MAE ratios are about 1.10–1.17, and the total ratio is 1.23. That is a warning, not equality. It is smaller than the overall horizon-1 ratio (about 1.45), and median monthly isolate ratios are closer to one than ratios of means. Missing identity is ruled out by the actual-operator and same-weights checks. Different globally learned weights and selected widths (64 real, 96 no graph) can damage isolates even though their local operator is identity. Saved forecasts cannot separate those contributions. No claim that all implementation faults are ruled out follows.

[Isolate figure](../../data/explore/t03/graph_diagnostics/isolates_horizon.png); [all 15 individual areas, every horizon](../../data/explore/t03/graph_diagnostics/isolated_area_mae.csv).

### 3. Degree and per-area MAE ratios

Horizon-1 bins (all areas retained):

'''+table(bins.loc[bins.outcome.eq('1')])+'''

Spearman association between degree and area MAE ratio among connected areas:

'''+table(association.loc[association.outcome.isin(['1','6','12','total_12'])])+'''

**There is no consistent increasing degree gradient.** The highest-degree bin is worse, but intermediate bins are not monotone and connected-area rank correlations are near zero. This part of the proposed shared-mixing signature is absent. Degree is not the full mixing strength because neighbour degrees enter symmetric weights. No zero-denominator ratio needed an epsilon or exclusion.

[All-area scatter](../../data/explore/t03/graph_diagnostics/degree_ratios.png), [bin figure](../../data/explore/t03/graph_diagnostics/degree_bins.png), [all horizons/areas](../../data/explore/t03/graph_diagnostics/degree_area_ratios.csv.gz), [all bins](../../data/explore/t03/graph_diagnostics/degree_binned.csv).

### 4. Pull toward neighbours

Primary gap: neighbours' mean installations at origin minus own installations at that origin. Correlations are computed separately within each area across 36 origins, never by pooling areas. Selected horizons:

'''+table(pull.loc[pull.level_definition.eq('origin')&pull.outcome.isin(['1','6','12']),
                         ['model','outcome','defined_areas','undefined_areas','median_correlation','share_positive']])+'''

The real signed-error correlation itself is weakly positive; it is negative under no graph. More directly, the forecast/error change from no graph to real follows the origin-level neighbour gap: horizon-1 median r is 0.481, positive in 96.1% of connected areas. The common actual target cancels in this difference. This is strong descriptive evidence of a relative neighbour-directed forecast shift, not proof that every shift worsens error or that neighbour influence causes adoption.

Sensitivity medians, horizon 1:

'''+table(pull.loc[pull.outcome.eq('1'),['level_definition','model','median_correlation','share_positive']])+'''

On trailing-twelve-month and log-input scales the real signed-error correlation is negative or near zero. The real-minus-no-graph correlation stays positive, but weaker for the smoothed level. Thus the strongest supported claim is a **relative pull toward neighbours**, rather than a universally positive raw-error relationship. All 15 isolates have undefined gaps/correlations and are explicitly retained as undefined; the other 2,619 areas have defined correlations. No significance tests or independence assumptions are attached to these descriptive correlations.

[Pull figure and sensitivity curves](../../data/explore/t03/graph_diagnostics/neighbour_pull.png), [every area/horizon, primary definition](../../data/explore/t03/graph_diagnostics/pull_correlations_origin.csv.gz), [all summaries](../../data/explore/t03/graph_diagnostics/pull_summary.csv).

### 5. Saved training fit and selected configuration

Each row summarises the same 12 quarterly fit origins × three seeds. Weight decay is 0.0001 for every condition. Epoch count is 65. Logged online epoch loss omits the Poisson constant; lower/more negative is better. Magnitudes across different origins reflect different training samples and must not be interpreted as a single shared dataset score.

'''+table(training)+'''

Paired by fit origin and seed:

'''+table(pd.DataFrame(paired_summary))+'''

The graph weakness is visible in training as well as validation. Positive last-ten-epoch decreases show continued improvement under the fixed epoch budget. They do not establish how much longer training would help. Width selection, optimisation and graph mixing remain intertwined. These are the **saved online epoch losses**, not fresh full-training-set checkpoint evaluations. No checkpoint inference over the study training set or refit was run.

[Saved training curves at both tuning anchors](../../data/explore/t03/graph_diagnostics/training_curves.png), [every selected fit's final loss/configuration](../../data/explore/t03/graph_diagnostics/selected_training_fit.csv).

### 6. Signed errors by maturity

Forecast minus actual; positive means overprediction. Maturity is the same origin-dependent tercile used in Gate C. Values average origins and three seeds; the CSV also includes between-seed SD. Monthly units are systems/area/month; total_12 is systems/area/window.

'''+table(signed.loc[signed.group.ne('all')&signed.outcome.isin(['1','6','12','total_12'])].pivot(
            index=['outcome','group'],columns='model',values='mean_signed_error').reset_index())+'''

The real and shuffled models overpredict medium-maturity areas and underpredict high-maturity areas at horizon 1 much more than no graph. This is consistent with compressing local differences, but it does not uniquely identify the reason. Removing installed base does not restore the no-graph pattern.

[All monthly horizons, all four conditions, with seed SD](../../data/explore/t03/graph_diagnostics/maturity_signed_errors.png), [all horizons including totals, full table](../../data/explore/t03/graph_diagnostics/signed_error_maturity.csv), [per-seed values](../../data/explore/t03/graph_diagnostics/signed_error_by_seed.csv).

## Explanation supported, and what remains unresolved

**The evidence favours an architecture/optimisation problem involving forced shared mixing over a missing-identity implementation fault.** Code and checkpoint inspection confirm self information is present. The real-minus-no-graph forecast shift follows neighbour gaps, and graph training fit is worse. Symmetric normalisation changes constant-signal gain, while a shared projection prevents learning independent own-history and neighbour-history coefficients.

The full proposed signature is **not** satisfied: isolates are measurably worse, and damage does not grow monotonically with degree. Therefore this is a supported working explanation, not a demonstrated sole cause. Global training effects, selected width and incomplete optimisation at 65 epochs cannot be separated using these saved artifacts. A matched-width design with a protected self path is a useful next screen. No conclusion about individual behaviour follows. Gate C remains unaccepted.

## Proposed screens — NOT approved, implemented or run

### Recommended candidate A: independent own and neighbour GRU projections

For each gate/candidate, keep `[x_i, h_i]` as an explicit self branch. Form a **neighbour-only arithmetic mean**, excluding self and unknown sources, and give it a separate learned projection: `W_self z_i + W_neighbour mean(z_j) + b`. Empty neighbour sets contribute zero. This removes symmetric degree gain and lets neighbour weights go to zero without losing own history. The no-graph control uses the same architecture with the neighbour branch zeroed. It shares the self/aggregate separation idea of [GraphSAGE, Hamilton et al.](https://arxiv.org/abs/1706.02216); this temporal gate proposal is our adaptation, not a reproduction of that paper.

### Candidate B: local GRU with a late graph residual

Encode each area's history with an ordinary local GRU. Add a separately projected neighbour-minus-own hidden-state correction only at the forecast head, before softplus. Initialise that correction at zero; keep a direct local head. Use neighbour-only row means, zero correction for isolates, and a zeroed graph branch in the no-graph control. This protects the temporal encoder and allows the graph contribution to shrink to zero. The general residual idea is supported by [He et al.](https://arxiv.org/abs/1512.03385); the proposed forecasting adaptation has not been benchmarked here.

### Common cheap plan and laptop-hour estimates

For **each candidate**, use seed 11, the two frozen tuning anchors (August 2019 and August 2020), real graph and no graph: **four fits**. Freeze the v2 real-graph-selected configuration, width 64, learning rate 0.003, weight decay 0.0001, 65 epochs, six channels and all original masks/objective/data. Use width 64 in both paired conditions to hold capacity fixed; the original no-graph winner was width 96. This is a proposed matched comparison, not a claim that v2 selected the same width for both. No new width/rate/epoch search, shuffled campaign or test access is included.

Report anchor validation MAE, MASE, RMSE and signed errors, training curves, isolate checks and measured resources; inspect agreement across the two anchors. Recommend screening A first. B is a fallback if A still harms local fit or fails to reduce the neighbour-gap shift. These two-anchor, one-seed outcomes would be exploratory selection evidence, not a new confirmatory Gate C/DM verdict. Any expanded campaign needs a new approved protocol before running.

The reference is the **four existing matched width-64, rate-0.003 real/no-graph anchor fits**, not a generic GPU estimate. Planning multipliers are explicit assumptions: A 1.5–2.5× the measured old four-fit time (extra dense branch); B 0.8–1.5× (local recurrent encoder, late graph head). They are unmeasured for the candidates and are not guarantees. Same RTX 4070 laptop, 8 GB VRAM and 32 GB RAM; peak memory for new candidates is unknown until measured.

'''+table(budget)+'''

If both GNN candidates are retained, there are eight proposed GPU fits. No full 46-fit condition is proposed at this stage. Time excludes setup, inference and session breaks.

### Matching extra boosting search

Give **each** boosting condition two additional candidate configurations, each at the same two anchors and seed 11: **four CPU fits per condition, eight CPU fits total**. This matches the two proposed architecture choices per graph/no-graph condition. Proposed settings: learning rate 0.05 with 31 or 63 leaves; retain 300 iterations, L2=1, Poisson objective, no early stopping and the same masks/features. These are new choices relative to the frozen 0.03/0.1 rate grid. No parameters or configs are changed now.

CPU time is estimated from the saved fits for the same condition/anchor/leaf counts at the two neighbouring old rates, averaging their measured times. The table above uses a 1–1.5× planning range. Matching fit counts and candidate choices does not mean equal CPU/GPU hours or identical statistical complexity. [Per-fit reference estimates](../../data/explore/t03/graph_diagnostics/boosting_extra_budget.csv), [measured GPU timing reference](../../data/explore/t03/graph_diagnostics/screening_time_reference.csv), [budget CSV](../../data/explore/t03/graph_diagnostics/proposed_screening_budget.csv).

## Reproducibility and stopping state

Sources: `evaluation.graph_diagnostics` computes operator, forecast and curve tables; `visuals.graph_diagnostics` creates the seven private figures with plotted-value CSVs; `evaluation.graph_diagnostics_report` builds these tables and checks aggregates. [Complete output index](../../data/explore/t03/graph_diagnostics/index.md). No new model was fitted, no GPU API was used, and no sealed-test forecast/loss was read. Only CPU toy forward passes used model execution.

'''
    text+=f'Independent checks reproduce {checked} overall real/no-graph MAEs and {len(joined)} signed-error rows against the previous Gate C output. All {len(before)} protected model/feature/config/protocol file hashes match the pre-diagnostic snapshot. Four focused tests passed (`logs/t03_graph_diagnostics_tests.log`). The preceding full suite remains 98 passed; it was not rerun for this isolated diagnostic addition. Every output is below 5 MB. No exclusions or imputation were made.\n'
    REPORT.write_text(text,encoding='utf-8')
    links=re.findall(r'\]\(([^)]+)\)',text)
    for link in links:
        if not link.startswith('https://'):assert (REPORT.parent/link).exists(),link
    verification={'mae_rows_reproduced':checked,'signed_rows_reproduced':len(joined),
        'protected_files_unchanged':len(before),'new_tests_passed':4,'figures':7,
        'report_links_checked':len(links),'new_fits':0,'gpu_use':False,'test_forecasts_or_losses':0}
    Path('reports/experiments/t03_graph_diagnostics_verification.json').write_text(json.dumps(verification,indent=2)+'\n')
    print(json.dumps(verification,indent=2))


if __name__=='__main__':main()
