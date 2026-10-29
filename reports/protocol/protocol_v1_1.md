# Protocol v1.1 amendment — 29 October 2026

[Baseline report and RMSE](../experiments/baselines_validation.md) · [Exploration index](../../data/explore/t02/index.md) · [Albers paper map](../figures/cumulative_sep2025.png) / [POA values](../figures/cumulative_sep2025.csv) / [Inset bounds](../figures/cumulative_sep2025_insets.csv).

**Approved by the researcher at Gate B; pending commit and `protocol-v1.1` tag.** Applies before any GNN run. It supersedes only the items listed below; protocol-v1 remains the immutable authority for the completed baseline fitting run. No refitting or final-test forecast/error evaluation is authorised by this amendment. Task 3 has not started.

## Gate B accepted

Neighbour lags give no clear overall MAE gain, but lower MASE than own-history boosting for all reported horizons and the twelve-month total, with important differences in the low-maturity tercile. Its twelve-month-total MAE is about 3.89 versus 4.32 systems in that tercile. Both boosting models improve over seasonal naive at horizons 1 and 6 in the corrected DM comparisons; there is no such evidence at horizon 12 or for the twelve-month total, even where raw MAE is numerically lower. The spatial model relies chiefly on neighbours installed base and hardly on recent neighbour counts in the saved grouped-permutation diagnostic. Reliance is not added value and is not causal evidence.

## A. Add RMSE, retain the objective and primary metric

MAE remains primary. Secondary metrics are MASE and RMSE for every model, including seasonal naive and all approved GNN conditions. MAE is minimised by a conditional median; squared error is minimised by a conditional mean. Fitted Poisson models predict a mean, so RMSE adds a mean-aligned view without changing the frozen Poisson training objective, tuning selection by MAE, dates, seeds or budget. This does not guarantee calibration or improvements.

RMSE is the square root of equally weighted mean squared errors across evaluated areas within each origin/maturity group, then across origins and seeds. Take the square root after pooling squared losses, not before, and do not evaluate an ensemble of averaged predictions. For the twelve-month total, sum predicted and observed monthly counts first, then square their difference. Units are systems per area/month for monthly horizons and systems per area/twelve-month window for the total. Compute origin-specific maturity membership from history only, as before.

Existing baseline RMSE is computed solely from saved validation predictions. Original model files, forecasts, MAE/MASE files and v1 DM results are retained unchanged. New metric files are a labelled amendment overlay.

## B. Extend the Task 3 DM/Holm family

Compare real-graph GNN against (1) no-graph GNN, (2) within-state shuffled GNN, (3) own-history boosting and (4) neighbour-history boosting. Apply one Holm adjustment across the entire four-pair x four-outcome family: 16 tests for outcomes 1, 6, 12 and twelve-month total. Keep the v1 origin-level area/seed-averaged MAE loss, Bartlett estimator, HLN correction and two-sided testing. RMSE is an added secondary score; this amendment does not add an unrequested squared-loss DM family. Validation p-values remain descriptive; the final test is still sealed.

## C. Optional installed-base-channel condition

A fourth GNN condition may use the real graph with the explicit installed-base input channel removed. All other approved inputs, objective, masks, architecture settings and tuning rules stay the same. Compare it against the real-graph GNN. It is disabled now and runs only if the researcher explicitly approves it after the Task 3 pilot. If enabled, include its four outcome comparisons in the same Holm family, making 20 tests. Do not introduce a separate more favourable testing family. Its extra compute must be presented for approval; no such fit is run now.

## D. What remains unchanged

The April 2001 panel, ASGS Edition 3, matching ledger, unknown-area masks, isolate rule, target definition, target-availability mask, split dates, 24-month input window, horizons, Poisson loss, MAE tuning rule, configuration budget, quarterly refits, seeds and Task 3 timing/24-GPU-hour stop remain as v1. July–September 2025 remains in the sealed test calendar with the recorded battery-eligibility timing limitation. Exploratory 2025 source counts and the paper map are descriptive outputs explicitly requested at Gate B, not final-test model evaluation or a basis for additional tuning.

## Existing-baseline RMSE (no refit)

| model | outcome | group | rmse |
| --- | --- | --- | --- |
| gradient_boosting_neighbours | 1 | all | 7.542176 |
| gradient_boosting_neighbours | 1 | high | 12.644992 |
| gradient_boosting_neighbours | 1 | low | 1.123627 |
| gradient_boosting_neighbours | 1 | medium | 3.081380 |
| gradient_boosting_neighbours | 12 | all | 10.305286 |
| gradient_boosting_neighbours | 12 | high | 17.375805 |
| gradient_boosting_neighbours | 12 | low | 1.408581 |
| gradient_boosting_neighbours | 12 | medium | 3.833280 |
| gradient_boosting_neighbours | 6 | all | 9.365410 |
| gradient_boosting_neighbours | 6 | high | 15.780177 |
| gradient_boosting_neighbours | 6 | low | 1.317585 |
| gradient_boosting_neighbours | 6 | medium | 3.518911 |
| gradient_boosting_neighbours | total_12 | all | 79.241504 |
| gradient_boosting_neighbours | total_12 | high | 135.091271 |
| gradient_boosting_neighbours | total_12 | low | 6.869953 |
| gradient_boosting_neighbours | total_12 | medium | 23.255112 |
| gradient_boosting_own | 1 | all | 7.509802 |
| gradient_boosting_own | 1 | high | 12.579115 |
| gradient_boosting_own | 1 | low | 1.136751 |
| gradient_boosting_own | 1 | medium | 3.108866 |
| gradient_boosting_own | 12 | all | 10.188115 |
| gradient_boosting_own | 12 | high | 17.166507 |
| gradient_boosting_own | 12 | low | 1.431625 |
| gradient_boosting_own | 12 | medium | 3.828124 |
| gradient_boosting_own | 6 | all | 9.293712 |
| gradient_boosting_own | 6 | high | 15.643494 |
| gradient_boosting_own | 6 | low | 1.342536 |
| gradient_boosting_own | 6 | medium | 3.549353 |
| gradient_boosting_own | total_12 | all | 77.106792 |
| gradient_boosting_own | total_12 | high | 131.356995 |
| gradient_boosting_own | total_12 | low | 7.122706 |
| gradient_boosting_own | total_12 | medium | 23.042983 |
| seasonal_naive | 1 | all | 9.696268 |
| seasonal_naive | 1 | high | 16.181504 |
| seasonal_naive | 1 | low | 1.451888 |
| seasonal_naive | 1 | medium | 4.254853 |
| seasonal_naive | 12 | all | 10.575579 |
| seasonal_naive | 12 | high | 17.661597 |
| seasonal_naive | 12 | low | 1.690996 |
| seasonal_naive | 12 | medium | 4.553803 |
| seasonal_naive | 6 | all | 10.296439 |
| seasonal_naive | 6 | high | 17.211970 |
| seasonal_naive | 6 | low | 1.614816 |
| seasonal_naive | 6 | medium | 4.380692 |
| seasonal_naive | total_12 | all | 72.658397 |
| seasonal_naive | total_12 | high | 123.199370 |
| seasonal_naive | total_12 | low | 7.139211 |
| seasonal_naive | total_12 | medium | 24.671336 |

Generated by `python -m evaluation.amendment`; original run: be4f68799849cb4c. New RMSE, signed-error and spatial diagnostics link from reports/experiments/baselines_validation.md and data/explore/t02/index.md. Plotting outputs and generators remain local-only under the researcher policy. No model/GPU command was run.
