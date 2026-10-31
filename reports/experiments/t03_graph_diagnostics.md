# Graph-condition diagnostics — 31 October 2026

**Gate C is not accepted. CPU-only diagnosis from saved artifacts; no refit or GPU use.** Frozen protocol/config/model files will remain unchanged. Candidate architectures and screening budgets are proposals only.

## Expectations written before computing these diagnostics

1. **Implementation-fault warning.** If the 15 observed isolated areas are much worse under the real graph than under no graph, suspect an implementation fault. Their graph operator should be identity. Check the actual operator and a same-weights isolated-node toy before attributing an isolate difference to missing self information. Independently trained conditions and their different selected widths can also change isolated-area forecasts, so saved-condition errors alone are not a proof of faulty code.
2. **Shared mixing explanation.** If isolated-area errors are similar, deterioration grows with degree and signed errors follow the neighbour–own level gap, the evidence supports the graph layer mixing own and neighbour history before one shared gate projection. A positive within-area association means overprediction when neighbours are higher and underprediction when they are lower. Compare with no graph and with the real-minus-no-graph signed-error difference. This is a computational explanation, not identification of individual neighbour influence.
3. **Mixed evidence stays mixed.** Report contradictory/non-monotone degree patterns and undefined correlations; do not force the second explanation if its predicted pattern is absent. Symmetric normalisation also need not preserve a constant signal on an irregular graph. Separate that property from a missing-identity implementation fault.

## Definitions fixed for the checks

- Use only the frozen validation origins and saved three-seed forecasts. MAE averages individual seed losses, not losses of an ensemble. Isolate tables cover monthly horizons 1–12, with the twelve-month total separately available.
- Primary degree is the original rook neighbour count. Also record effective observed-neighbour degree after the seven unknown-area message sources are masked. Original observed isolates and any extra effective isolates are distinguished.
- Degree bins are fixed as 0, 1, 2, 3–4, 5–8, 9–16 and 17+. Show per-area real/no-graph MAE ratios, bin medians/IQR and ratios of mean MAE. Zero no-graph MAE produces an explicitly flagged undefined/infinite ratio; do not add an epsilon or silently drop it.
- Primary level is the observed monthly installation count at each forecast origin, inclusive. Gap = arithmetic mean of observed rook neighbours' levels minus own level. Sensitivities use the trailing twelve-month mean and the actual log1p-count input scale. None uses target-month counts.
- For each area and horizon, correlate the gap with signed forecast error across the 36 origins, after averaging forecasts/errors across the same three seeds. Also correlate gap with real-minus-no-graph signed error, which cancels the common target. Isolates/no observed neighbours and constant series have undefined correlations and are counted explicitly. These are descriptive correlations without significance tests.
- Final training loss is the final saved epoch's logged Poisson loss (constant omitted; lower/more negative is better), not a newly evaluated checkpoint loss. Compare matched fit origins/seeds and record independently selected configurations.

Computation and figures follow below. No candidate model will be implemented or run in this diagnostic task.

## Diagnostic results

### 1. Actual operator and identity check

The code uses **S = D^(-1/2) (A_observed + I) D^(-1/2)**, with D the row degree including the self edge. A node with d observed neighbours gives itself weight 1/(d+1), and neighbour j weight 1/sqrt((d+1)(d_j+1)). The neighbour's degree matters: degree alone does not determine the neighbour weights. Unknown nodes cannot send or receive cross-node messages; they are masked before and after aggregation.

The actual code was called on a nine-node graph: one isolate, one isolated pair, and a five-leaf star. These are state weights before the learned gate projections:

| node | degree | self_weight | neighbour_weights | neighbour_weight_sum | row_sum |
| --- | --- | --- | --- | --- | --- |
| isolate | 0 | 1.000000 | [] | 0.000000 | 1.000000 |
| pair_a | 1 | 0.500000 | [0.5] | 0.500000 | 1.000000 |
| hub_5 | 5 | 0.166667 | [0.28867512941360474, 0.28867512941360474, 0.28867512941360474, 0.28867512941360474, 0.28867512941360474] | 1.443376 | 1.610042 |
| leaf_1 | 1 | 0.500000 | [0.28867512941360474] | 0.288675 | 0.788675 |

Thus the pair node has self 0.5 and neighbour 0.5. The degree-five star hub has self 1/6 and **each** leaf weight 1/sqrt(12), not 1/6. Its row sum exceeds one. A degree-one leaf connected to that hub has self 0.5 and hub weight 1/sqrt(12). Symmetric normalisation does not preserve a constant signal on an irregular graph. This is an implemented design property, not evidence that identity was omitted.

The toy real and shuffled calls use the same supplied edges to check their common operator implementation; shuffling itself happens upstream. Independently, one saved seed-11, August-2020 selected checkpoint from each of the four conditions was loaded with `map_location='cpu'`. Each stored operator exactly matches its actual saved real/shuffled/no-graph edge construction and all diagonals are positive. All 15 observed isolate rows are identity. On the toy graph, copying identical learned weights into the three operator conditions gives **exactly equal isolated-node forecasts**. No training was performed. This checks the operator and local computation, not every possible implementation fault in the entire campaign.

The gate and candidate projections each act on graph-mixed concatenated input/hidden state. There is one shared projection for own and neighbour information within each gate/candidate, rather than separate learned self and neighbour projections. The GRU update retains its usual hidden-state path; there is no separate unaggregated current-input projection.

[Operator figure](../../data/explore/t03/graph_diagnostics/operator_weights.png), [all weights](../../data/explore/t03/graph_diagnostics/operator_toy_weights.csv), [checkpoint checks](../../data/explore/t03/graph_diagnostics/checkpoint_operator_checks.csv).

### 2. Observed isolates

There are 15 original observed isolates and 15 effective observed isolates: masking unknown nodes creates no additional observed isolates. MAE is systems per area/month, or systems per area/window for total_12.

| outcome | areas | real_mae | no_graph_mae | median_area_ratio | ratio_of_mean_mae |
| --- | --- | --- | --- | --- | --- |
| 1 | 15 | 2.167061 | 1.884346 | 1.069300 | 1.150033 |
| 2 | 15 | 2.225784 | 1.899414 | 1.039852 | 1.171827 |
| 3 | 15 | 2.241721 | 1.924620 | 1.039109 | 1.164761 |
| 4 | 15 | 2.260169 | 2.020141 | 1.027215 | 1.118817 |
| 5 | 15 | 2.320083 | 2.097019 | 1.046643 | 1.106372 |
| 6 | 15 | 2.357682 | 2.139645 | 1.022160 | 1.101903 |
| 7 | 15 | 2.421455 | 2.191777 | 1.037892 | 1.104790 |
| 8 | 15 | 2.510248 | 2.172517 | 1.025030 | 1.155456 |
| 9 | 15 | 2.574331 | 2.257693 | 1.025257 | 1.140248 |
| 10 | 15 | 2.666912 | 2.366516 | 1.055709 | 1.126936 |
| 11 | 15 | 2.730468 | 2.465450 | 1.048545 | 1.107493 |
| 12 | 15 | 2.800672 | 2.533403 | 1.089898 | 1.105498 |
| total_12 | 15 | 21.019542 | 17.054952 | 1.169243 | 1.232460 |

Isolates are worse under independently trained real graph: monthly mean-MAE ratios are about 1.10–1.17, and the total ratio is 1.23. That is a warning, not equality. It is smaller than the overall horizon-1 ratio (about 1.45), and median monthly isolate ratios are closer to one than ratios of means. Missing identity is ruled out by the actual-operator and same-weights checks. Different globally learned weights and selected widths (64 real, 96 no graph) can damage isolates even though their local operator is identity. Saved forecasts cannot separate those contributions. No claim that all implementation faults are ruled out follows.

[Isolate figure](../../data/explore/t03/graph_diagnostics/isolates_horizon.png); [all 15 individual areas, every horizon](../../data/explore/t03/graph_diagnostics/isolated_area_mae.csv).

### 3. Degree and per-area MAE ratios

Horizon-1 bins (all areas retained):

| outcome | degree_bin | areas | median_ratio | q25_ratio | q75_ratio | ratio_of_mean_mae | undefined_or_infinite_ratios |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | 0 | 15 | 1.069300 | 1.017434 | 1.086463 | 1.150033 | 0 |
| 1 | 1 | 61 | 1.169493 | 1.029100 | 1.385961 | 1.278554 | 0 |
| 1 | 2 | 205 | 1.144642 | 1.002782 | 1.404407 | 1.401831 | 0 |
| 1 | 3-4 | 792 | 1.149028 | 0.989164 | 1.527593 | 1.507087 | 0 |
| 1 | 5-8 | 1300 | 1.155428 | 0.990773 | 1.530181 | 1.425803 | 0 |
| 1 | 9-16 | 245 | 1.094695 | 0.982351 | 1.509297 | 1.484831 | 0 |
| 1 | 17+ | 16 | 1.485480 | 1.242537 | 2.085596 | 1.687573 | 0 |

Spearman association between degree and area MAE ratio among connected areas:

| outcome | spearman_degree_mae_ratio | areas |
| --- | --- | --- |
| 1 | 0.015029 | 2619 |
| 12 | -0.011733 | 2619 |
| 6 | 0.004658 | 2619 |
| total_12 | -0.036780 | 2619 |

**There is no consistent increasing degree gradient.** The highest-degree bin is worse, but intermediate bins are not monotone and connected-area rank correlations are near zero. This part of the proposed shared-mixing signature is absent. Degree is not the full mixing strength because neighbour degrees enter symmetric weights. No zero-denominator ratio needed an epsilon or exclusion.

[All-area scatter](../../data/explore/t03/graph_diagnostics/degree_ratios.png), [bin figure](../../data/explore/t03/graph_diagnostics/degree_bins.png), [all horizons/areas](../../data/explore/t03/graph_diagnostics/degree_area_ratios.csv.gz), [all bins](../../data/explore/t03/graph_diagnostics/degree_binned.csv).

### 4. Pull toward neighbours

Primary gap: neighbours' mean installations at origin minus own installations at that origin. Correlations are computed separately within each area across 36 origins, never by pooling areas. Selected horizons:

| model | outcome | defined_areas | undefined_areas | median_correlation | share_positive |
| --- | --- | --- | --- | --- | --- |
| gnn_real | 1 | 2619 | 15 | 0.049932 | 0.604811 |
| gnn_real | 6 | 2619 | 15 | 0.020571 | 0.539519 |
| gnn_real | 12 | 2619 | 15 | 0.020264 | 0.536846 |
| gnn_no_graph | 1 | 2619 | 15 | -0.116770 | 0.265750 |
| gnn_no_graph | 6 | 2619 | 15 | -0.084914 | 0.334861 |
| gnn_no_graph | 12 | 2619 | 15 | -0.090688 | 0.316533 |
| real_minus_no_graph | 1 | 2619 | 15 | 0.481060 | 0.961054 |
| real_minus_no_graph | 6 | 2619 | 15 | 0.384078 | 0.925162 |
| real_minus_no_graph | 12 | 2619 | 15 | 0.400903 | 0.939290 |

The real signed-error correlation itself is weakly positive; it is negative under no graph. More directly, the forecast/error change from no graph to real follows the origin-level neighbour gap: horizon-1 median r is 0.481, positive in 96.1% of connected areas. The common actual target cancels in this difference. This is strong descriptive evidence of a relative neighbour-directed forecast shift, not proof that every shift worsens error or that neighbour influence causes adoption.

Sensitivity medians, horizon 1:

| level_definition | model | median_correlation | share_positive |
| --- | --- | --- | --- |
| origin | gnn_real | 0.049932 | 0.604811 |
| origin | gnn_no_graph | -0.116770 | 0.265750 |
| origin | real_minus_no_graph | 0.481060 | 0.961054 |
| trailing12 | gnn_real | -0.068925 | 0.391371 |
| trailing12 | gnn_no_graph | -0.135414 | 0.253150 |
| trailing12 | real_minus_no_graph | 0.231174 | 0.706758 |
| log_input | gnn_real | -0.001102 | 0.496754 |
| log_input | gnn_no_graph | -0.138660 | 0.210386 |
| log_input | real_minus_no_graph | 0.405220 | 0.940435 |

On trailing-twelve-month and log-input scales the real signed-error correlation is negative or near zero. The real-minus-no-graph correlation stays positive, but weaker for the smoothed level. Thus the strongest supported claim is a **relative pull toward neighbours**, rather than a universally positive raw-error relationship. All 15 isolates have undefined gaps/correlations and are explicitly retained as undefined; the other 2,619 areas have defined correlations. No significance tests or independence assumptions are attached to these descriptive correlations.

[Pull figure and sensitivity curves](../../data/explore/t03/graph_diagnostics/neighbour_pull.png), [every area/horizon, primary definition](../../data/explore/t03/graph_diagnostics/pull_correlations_origin.csv.gz), [all summaries](../../data/explore/t03/graph_diagnostics/pull_summary.csv).

### 5. Saved training fit and selected configuration

Each row summarises the same 12 quarterly fit origins × three seeds. Weight decay is 0.0001 for every condition. Epoch count is 65. Logged online epoch loss omits the Poisson constant; lower/more negative is better. Magnitudes across different origins reflect different training samples and must not be interpreted as a single shared dataset score.

| condition | width | learning_rate | fits | mean_final_loss | min_final_loss | max_final_loss | mean_last10_decrease |
| --- | --- | --- | --- | --- | --- | --- | --- |
| no_graph | 96 | 0.003000 | 36 | -13.491528 | -15.268396 | -12.189461 | 0.067319 |
| real | 64 | 0.003000 | 36 | -12.863071 | -14.612210 | -11.587229 | 0.127595 |
| real_without_installed_base | 96 | 0.003000 | 36 | -12.976871 | -14.717361 | -11.717297 | 0.135902 |
| within_state_shuffled | 64 | 0.003000 | 36 | -13.080411 | -14.875974 | -11.695181 | 0.097893 |

Paired by fit origin and seed:

| condition | mean_loss_minus_no_graph | fits_with_higher_loss | paired_fits |
| --- | --- | --- | --- |
| real | 0.628456 | 36 | 36 |
| within_state_shuffled | 0.411116 | 36 | 36 |
| real_without_installed_base | 0.514657 | 36 | 36 |

The graph weakness is visible in training as well as validation. Positive last-ten-epoch decreases show continued improvement under the fixed epoch budget. They do not establish how much longer training would help. Width selection, optimisation and graph mixing remain intertwined. These are the **saved online epoch losses**, not fresh full-training-set checkpoint evaluations. No checkpoint inference over the study training set or refit was run.

[Saved training curves at both tuning anchors](../../data/explore/t03/graph_diagnostics/training_curves.png), [every selected fit's final loss/configuration](../../data/explore/t03/graph_diagnostics/selected_training_fit.csv).

### 6. Signed errors by maturity

Forecast minus actual; positive means overprediction. Maturity is the same origin-dependent tercile used in Gate C. Values average origins and three seeds; the CSV also includes between-seed SD. Monthly units are systems/area/month; total_12 is systems/area/window.

| outcome | group | gnn_no_base | gnn_no_graph | gnn_real | gnn_shuffled |
| --- | --- | --- | --- | --- | --- |
| 1 | high | -2.904201 | -1.167268 | -4.051747 | -4.144293 |
| 1 | low | 0.446551 | 0.048646 | 0.317032 | 0.377760 |
| 1 | medium | 1.756453 | 0.057864 | 1.585633 | 1.362024 |
| 12 | high | -3.241905 | -1.187280 | -4.606488 | -5.263391 |
| 12 | low | 0.540062 | 0.103205 | 0.404251 | 0.477160 |
| 12 | medium | 1.932702 | 0.349285 | 1.761867 | 1.384786 |
| 6 | high | -2.526429 | -1.247404 | -4.159089 | -4.264018 |
| 6 | low | 0.546444 | 0.132632 | 0.422300 | 0.529535 |
| 6 | medium | 2.026205 | 0.217937 | 1.757833 | 1.581490 |
| total_12 | high | -34.247707 | -14.818387 | -52.074602 | -55.169908 |
| total_12 | low | 6.137542 | 1.301897 | 4.579236 | 5.642248 |
| total_12 | medium | 23.093965 | 2.424806 | 20.319812 | 17.433590 |

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

| candidate | fits | measured_old_reference_h | planning_lower_h | planning_upper_h |
| --- | --- | --- | --- | --- |
| A: separate self/neighbour GRU | 4 | 0.770580 | 1.155871 | 1.926451 |
| B: local GRU + late residual graph | 4 | 0.770580 | 0.616464 | 1.155871 |
| Two boosting conditions combined (CPU) | 8 | 0.253296 | 0.253296 | 0.379944 |

If both GNN candidates are retained, there are eight proposed GPU fits. No full 46-fit condition is proposed at this stage. Time excludes setup, inference and session breaks.

### Matching extra boosting search

Give **each** boosting condition two additional candidate configurations, each at the same two anchors and seed 11: **four CPU fits per condition, eight CPU fits total**. This matches the two proposed architecture choices per graph/no-graph condition. Proposed settings: learning rate 0.05 with 31 or 63 leaves; retain 300 iterations, L2=1, Poisson objective, no early stopping and the same masks/features. These are new choices relative to the frozen 0.03/0.1 rate grid. No parameters or configs are changed now.

CPU time is estimated from the saved fits for the same condition/anchor/leaf counts at the two neighbouring old rates, averaging their measured times. The table above uses a 1–1.5× planning range. Matching fit counts and candidate choices does not mean equal CPU/GPU hours or identical statistical complexity. [Per-fit reference estimates](../../data/explore/t03/graph_diagnostics/boosting_extra_budget.csv), [measured GPU timing reference](../../data/explore/t03/graph_diagnostics/screening_time_reference.csv), [budget CSV](../../data/explore/t03/graph_diagnostics/proposed_screening_budget.csv).

## Reproducibility and stopping state

Sources: `evaluation.graph_diagnostics` computes operator, forecast and curve tables; `visuals.graph_diagnostics` creates the seven private figures with plotted-value CSVs; `evaluation.graph_diagnostics_report` builds these tables and checks aggregates. [Complete output index](../../data/explore/t03/graph_diagnostics/index.md). No new model was fitted, no GPU API was used, and no sealed-test forecast/loss was read. Only CPU toy forward passes used model execution.

Independent checks reproduce 26 overall real/no-graph MAEs and 208 signed-error rows against the previous Gate C output. All 22 protected model/feature/config/protocol file hashes match the pre-diagnostic snapshot. Four focused tests passed (`logs/t03_graph_diagnostics_tests.log`). The preceding full suite remains 98 passed; it was not rerun for this isolated diagnostic addition. Every output is below 5 MB. No exclusions or imputation were made.
