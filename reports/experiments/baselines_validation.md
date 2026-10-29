# Validation baselines — Task 2 Gate B accepted

**Gate B accepted by the researcher on 29 October 2026.** Protocol v1.1 adds RMSE from saved validation predictions; no refit or final-test forecast/error evaluation.

## Provenance and model conditions

Run `be4f68799849cb4c`; protocol-v1 SHA256 `adc8bb45620144fb1c9b2ab1cdc5da17be5f03cdaef8f72fc6232b1698fc27d0`. CPU only, 8 threads, 92 boosting fits. Software and code hashes: [run manifest](../../data/processed/t02_baselines/be4f68799849cb4c/run_manifest.json). Recorded fit time sums to 2.637 hours; this excludes prediction, data preparation, metrics and plotting time.

Models: fixed seasonal naive, own-history Poisson histogram gradient boosting, and the same boosting family with neighbour history. Both fitted conditions use six configurations, seed 11 at the two tuning anchors and the selected configuration with seeds 11/29/47 under quarterly expanding refits. Every observed eligible horizon target is used, with identical availability masks and 46 unique fits per condition. Unknown-area graph nodes are not loss/evaluation cases or message sources. No artificial links are added.

Validation origins are November 2018–October 2021, with targets ending October 2022. No validation target falls after the first sealed test origin. Data after that boundary are not loaded by the baseline runner. The final-test battery-scheme timing limitation and September 2025 target cutoff remain as frozen, without evaluating that block here.

## MAE and seasonal MASE

MAE is in systems per observed area (per forecast month or twelve-month total). MASE is unitless, with the approved pooled zero-scale fallback and training-only denominators frozen between quarterly refits. Total error is computed after summing all twelve predicted/actual counts; its MASE denominator is twelve times the monthly scale. Numbers below average losses across equal-area origins and the three seeds, not errors of a prediction ensemble. Per-seed metrics and seed spread are in the linked CSV.

### Maturity group: all

| model | outcome | mae | mase | mae_seed_sd | mase_seed_sd |
| --- | --- | --- | --- | --- | --- |
| gradient_boosting_neighbours | 1 | 3.240554 | 1.009142 | 0.007218 | 0.000562 |
| gradient_boosting_neighbours | 12 | 4.436481 | 1.198639 | 0.003678 | 0.000931 |
| gradient_boosting_neighbours | 6 | 3.954436 | 1.118497 | 0.005485 | 0.000230 |
| gradient_boosting_neighbours | total_12 | 31.118270 | 0.626576 | 0.026271 | 0.000438 |
| gradient_boosting_own | 1 | 3.256133 | 1.054212 | 0.007532 | 0.000717 |
| gradient_boosting_own | 12 | 4.433081 | 1.274145 | 0.002229 | 0.000483 |
| gradient_boosting_own | 6 | 3.961972 | 1.170082 | 0.006813 | 0.000614 |
| gradient_boosting_own | total_12 | 30.866269 | 0.680405 | 0.046997 | 0.000553 |
| seasonal_naive | 1 | 4.366257 | 1.100749 | 0.000000 | 0.000000 |
| seasonal_naive | 12 | 4.699696 | 1.190132 | 0.000000 | 0.000000 |
| seasonal_naive | 6 | 4.584599 | 1.145248 | 0.000000 | 0.000000 |
| seasonal_naive | total_12 | 31.145143 | 0.571081 | 0.000000 | 0.000000 |

### Maturity group: low

| model | outcome | mae | mase | mae_seed_sd | mase_seed_sd |
| --- | --- | --- | --- | --- | --- |
| gradient_boosting_neighbours | 1 | 0.669236 | 1.522775 | 0.000327 | 0.001178 |
| gradient_boosting_neighbours | 12 | 0.729146 | 1.691817 | 0.000347 | 0.002010 |
| gradient_boosting_neighbours | 6 | 0.705782 | 1.608706 | 0.000147 | 0.001501 |
| gradient_boosting_neighbours | total_12 | 3.889148 | 0.851100 | 0.001581 | 0.000930 |
| gradient_boosting_own | 1 | 0.693392 | 1.647050 | 0.000192 | 0.000428 |
| gradient_boosting_own | 12 | 0.774594 | 1.911445 | 0.000204 | 0.000514 |
| gradient_boosting_own | 6 | 0.736364 | 1.755160 | 0.000518 | 0.000022 |
| gradient_boosting_own | total_12 | 4.318011 | 1.015836 | 0.002326 | 0.000532 |
| seasonal_naive | 1 | 0.731745 | 1.262172 | 0.000000 | 0.000000 |
| seasonal_naive | 12 | 0.775753 | 1.400665 | 0.000000 | 0.000000 |
| seasonal_naive | 6 | 0.758099 | 1.323052 | 0.000000 | 0.000000 |
| seasonal_naive | total_12 | 3.815648 | 0.655036 | 0.000000 | 0.000000 |

### Maturity group: medium

| model | outcome | mae | mase | mae_seed_sd | mase_seed_sd |
| --- | --- | --- | --- | --- | --- |
| gradient_boosting_neighbours | 1 | 2.035803 | 0.800762 | 0.000278 | 0.000048 |
| gradient_boosting_neighbours | 12 | 2.388459 | 0.923334 | 0.001329 | 0.000487 |
| gradient_boosting_neighbours | 6 | 2.247032 | 0.874218 | 0.001581 | 0.000548 |
| gradient_boosting_neighbours | total_12 | 14.222212 | 0.445815 | 0.012784 | 0.000337 |
| gradient_boosting_own | 1 | 2.059580 | 0.810321 | 0.001986 | 0.000721 |
| gradient_boosting_own | 12 | 2.415790 | 0.936209 | 0.001287 | 0.000443 |
| gradient_boosting_own | 6 | 2.276109 | 0.886775 | 0.001004 | 0.000157 |
| gradient_boosting_own | total_12 | 14.415432 | 0.454350 | 0.014659 | 0.000346 |
| seasonal_naive | 1 | 2.737155 | 1.066349 | 0.000000 | 0.000000 |
| seasonal_naive | 12 | 2.888984 | 1.124344 | 0.000000 | 0.000000 |
| seasonal_naive | 6 | 2.812010 | 1.093415 | 0.000000 | 0.000000 |
| seasonal_naive | total_12 | 15.142780 | 0.471949 | 0.000000 | 0.000000 |

### Maturity group: high

| model | outcome | mae | mase | mae_seed_sd | mase_seed_sd |
| --- | --- | --- | --- | --- | --- |
| gradient_boosting_neighbours | 1 | 7.016623 | 0.703889 | 0.021636 | 0.000637 |
| gradient_boosting_neighbours | 12 | 10.191837 | 0.980766 | 0.009680 | 0.000925 |
| gradient_boosting_neighbours | 6 | 8.910495 | 0.872568 | 0.017958 | 0.001038 |
| gradient_boosting_neighbours | total_12 | 75.243451 | 0.582812 | 0.068418 | 0.000629 |
| gradient_boosting_own | 1 | 7.015428 | 0.705266 | 0.020600 | 0.001177 |
| gradient_boosting_own | 12 | 10.108860 | 0.974782 | 0.006931 | 0.000684 |
| gradient_boosting_own | 6 | 8.873443 | 0.868310 | 0.020789 | 0.001810 |
| gradient_boosting_own | total_12 | 73.865364 | 0.571029 | 0.129433 | 0.000915 |
| seasonal_naive | 1 | 9.629872 | 0.973725 | 0.000000 | 0.000000 |
| seasonal_naive | 12 | 10.434352 | 1.045388 | 0.000000 | 0.000000 |
| seasonal_naive | 6 | 10.183688 | 1.019275 | 0.000000 | 0.000000 |
| seasonal_naive | total_12 | 74.476999 | 0.586257 | 0.000000 | 0.000000 |

[Full score CSV](../../data/processed/t02_baselines/be4f68799849cb4c/scores.csv) · [Seed metrics](../../data/processed/t02_baselines/be4f68799849cb4c/seed_metrics.csv) · [Origin losses and group sizes](../../data/processed/t02_baselines/be4f68799849cb4c/origin_metrics.csv)

Maturity terciles are recomputed using cumulative base through each origin with postcode tie breaks. Group results are not fixed-cohort effects. Denominators and masks are shared across all models.

## Corrected Diebold–Mariano comparisons

Inputs are area-averaged absolute losses at each monthly origin, averaged across the fixed seeds. The testing unit is an origin, not an area or seed. dieboldmariano 1.1.0 uses Bartlett covariance weighting through horizon−1, HLN correction, two-sided tests and Holm adjustment across the twelve comparisons below. Undefined statistics/p-values remain undefined. Overlapping horizons and the limited number of origins constrain inference. Validation was used for tuning, so p-values are descriptive development evidence, not final-test confirmation.

| model_a | model_b | outcome | statistic | p_raw | p_holm | status |
| --- | --- | --- | --- | --- | --- | --- |
| gradient_boosting_neighbours | gradient_boosting_own | 1 | -0.836247 | 0.408689 | 1.000000 | defined |
| gradient_boosting_neighbours | gradient_boosting_own | 6 | -0.206782 | 0.837378 | 1.000000 | defined |
| gradient_boosting_neighbours | gradient_boosting_own | 12 | 0.099608 | 0.921224 | 1.000000 | defined |
| gradient_boosting_neighbours | gradient_boosting_own | total_12 | 0.736216 | 0.466505 | 1.000000 | defined |
| gradient_boosting_own | seasonal_naive | 1 | -11.543106 | 0.000000 | 0.000000 | defined |
| gradient_boosting_own | seasonal_naive | 6 | -4.294369 | 0.000132 | 0.001322 | defined |
| gradient_boosting_own | seasonal_naive | 12 | -1.617773 | 0.114690 | 0.917520 | defined |
| gradient_boosting_own | seasonal_naive | total_12 | -0.057289 | 0.954641 | 1.000000 | defined |
| gradient_boosting_neighbours | seasonal_naive | 1 | -12.615616 | 0.000000 | 0.000000 | defined |
| gradient_boosting_neighbours | seasonal_naive | 6 | -4.273160 | 0.000141 | 0.001322 | defined |
| gradient_boosting_neighbours | seasonal_naive | 12 | -1.607077 | 0.117023 | 0.917520 | defined |
| gradient_boosting_neighbours | seasonal_naive | total_12 | -0.005168 | 0.995906 | 1.000000 | defined |

## Neighbour-feature sensitivity

Grouped permutation sensitivity is computed on the selected spatial model, seed 11, at the two tuning anchors, with three fixed shuffles per group. Shuffle area identities jointly across all twelve horizons for each selected feature group; no model is refit and no new configuration is tried. Changes in MAE may be negative. Predictors are correlated and these perturbed inputs need not be typical geographic combinations; this is descriptive predictive sensitivity, not causal or unique behavioural importance.

| group | mean | std |
| --- | --- | --- |
| neighbour_base | 0.212422 | 0.035904 |
| neighbour_flag | 0.000000 | 0.000000 |
| neighbour_lags | 0.006500 | 0.012950 |

## Gate B: do neighbour lags help on validation?

- Outcome 1: neighbour-model MAE is lower (3.240554 versus own-history 3.256133 systems); reduction in MAE = 0.015579 systems.
- Outcome 6: neighbour-model MAE is lower (3.954436 versus own-history 3.961972 systems); reduction in MAE = 0.007536 systems.
- Outcome 12: neighbour-model MAE is higher (4.436481 versus own-history 4.433081 systems); reduction in MAE = -0.003399 systems.
- Outcome total_12: neighbour-model MAE is higher (31.118270 versus own-history 30.866269 systems); reduction in MAE = -0.252001 systems.

This per-outcome development result is a warning sign only. The core GNN experiment proceeds regardless after the accepted Gate B decision, a separate Task 3 instruction and its timing gate. No hybrid decision or final-test conclusion is made here.

## Visuals and spatial error exploration

- [Error by reported horizon](../../visuals/t02/baseline_error_horizon.png) / [CSV](../../visuals/t02/baseline_error_horizon.csv).
- [Error by maturity group](../../visuals/t02/baseline_error_maturity.png) / [CSV](../../visuals/t02/baseline_error_maturity.csv).
- [Own-history validation error map](../../data/explore/t02/validation_error_map.png) / [CSV](../../data/explore/t02/validation_error_map.csv).
- [Errors over validation origins](../../data/explore/t02/validation_errors_time.png) / [CSV](../../data/explore/t02/validation_errors_time.csv).
- [Global Moran I of own-history validation errors](../../data/explore/t02/validation_error_moran.csv).

The map and Moran statistic use per-area horizon-12 MAE averaged over origins and seeds. Missing-record areas have no evaluated error; they are not zero-error cases. No population/dwelling scaling or permutation significance test is supplied; error size can mix installation volume with predictability. Spatial clustering is descriptive and does not identify behavioural transmission.

## Reproduction

Run only after the dependency/test checks and the researcher CPU fitting command in internal/STATUS.md. Checkpoints and data are local-only; the original v1 tag is retained and the approved changes are recorded separately in v1.1.

```powershell
python -m models.baselines --threads 8 2>&1 | Tee-Object logs/t02_baselines_cpu.log
python -m visuals.baselines_validation 2>&1 | Tee-Object logs/t02_baseline_report.log
```

The model command is researcher-run training and can exceed the agent time limit. Completed fits are fingerprinted and reused; completed runs are not repeated. The visual script creates CSV/PNG pairs, updates exploration and visual indexes, and writes this report. All figures, plotting source and data remain local-only under the researcher policy.

## Approved Gate B interpretation and v1.1 RMSE

Neighbour features give no clear overall MAE gain, but lower MASE at every reported horizon and the twelve-month total. In the low-maturity tercile, total MAE is 3.89 versus 4.32 systems. Both boosting models beat seasonal naive in corrected DM comparisons at horizons 1 and 6, without such evidence at 12 or for the total. Reliance on neighbours installed base, with little sensitivity to their recent counts, is not evidence of added value.

MAE stays primary. RMSE is secondary alongside MASE: squared error targets the conditional mean predicted by fitted Poisson models, while absolute error targets a median. Pool squared losses across equally weighted areas, origins and seeds before taking the root; do not score averaged predictions. Total errors use sums of the same twelve saved monthly forecasts. Monthly units are systems/area/month; total units are systems/area/twelve-month window.

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

[RMSE CSV](../../data/processed/t02_baselines/be4f68799849cb4c/amendment_v1_1/rmse_summary.csv) · [Amendment](../protocol/protocol_v1_1.md). Generated by `python -m evaluation.amendment`, with zero new fits. Original v1 scores and forecasts are unchanged.

## Additional descriptive exploration

- [Mean signed error by horizon and maturity](../../data/explore/t02/mean_signed_error.png) / [CSV](../../data/explore/t02/mean_signed_error.csv); forecast minus actual, so negative means underprediction.
- [Absolute, scaled absolute and signed error Moran I](../../data/explore/t02/error_moran_comparison.png) / [CSV](../../data/explore/t02/error_moran_comparison.csv); horizon 12, same observed-area graph and row-standardised weights, no permutation inference. Training-error scaling is not dwelling normalisation.
- [January–September 2025 national snapshot comparison](../../data/explore/t02/pv_2025_snapshot_comparison.csv); all CER postcodes, including unmatched. This is revision growth for the same installation months across snapshots, not year-on-year deployment growth.
- [September 2025 cumulative paper map with capital insets](../figures/cumulative_sep2025.png) / [POA values](../figures/cumulative_sep2025.csv) / [Inset bounds](../figures/cumulative_sep2025_insets.csv); EPSG:9473 Australian Albers. Unknown targets and isolates remain marked.

National January–September 2025 certificate-backed PV installations: **191,869 systems** in the 30 September 2026 snapshot, compared with **174,204** supplied by the researcher for 30 September 2025: **+17,665 systems (10.1404%)**. Source: `evaluation.amendment`, national SGU Solar records; reference is researcher-supplied and its archive was not downloaded.
