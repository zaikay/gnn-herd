# GNN validation — Task 3 Gate C review

## Gate C finding

**No: real graph is worse than shuffled on both MAE and MASE for every reported outcome.** This is validation development evidence for the frozen T-GCN implementation, not a claim that geography never matters or that individual behaviour was identified.

Real graph also has higher primary MAE than no-graph GNN at every reported outcome. All four MAE-loss comparisons have Holm-adjusted p < 0.05.
Real graph also has higher primary MAE than own-history boosting at every reported outcome. All four MAE-loss comparisons have Holm-adjusted p < 0.05.
Real graph also has higher primary MAE than neighbour-history boosting at every reported outcome. All four MAE-loss comparisons have Holm-adjusted p < 0.05.

Removing the explicit installed-base channel worsens MASE at every reported outcome. Primary-MAE differences are mixed and none of the four ablation comparisons has Holm-adjusted p < 0.05.

For real versus shuffled, only horizon 1 has a Holm-adjusted MAE-loss p-value below 0.05 (p = 0.0287011), in the direction of worse real-graph forecasts. Horizon 6 is p = 0.0531935; horizon 12 is p = 1; the total is p = 0.531569. These validation tests do not establish the other mean differences as statistically distinct.

The corrected family contains 20 comparisons. P-values are conditional on the frozen development protocol and fixed seeds; seed spread is reported separately. Review Gate C before any further experiments or hybrids. No tuning change, refit or sealed-test evaluation is proposed here.

| outcome | real_mae | shuffled_mae | real_minus_shuffled_mae_percent | real_mase | shuffled_mase | mae_direction | mase_direction | p_holm |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | 5.231934 | 5.155356 | 1.485402 | 1.525363 | 1.445430 | higher | higher | 0.0287011 |
| 6 | 5.637801 | 5.548519 | 1.609107 | 1.659314 | 1.612484 | higher | higher | 0.0531935 |
| 12 | 5.912238 | 5.808168 | 1.791801 | 1.718776 | 1.613370 | higher | higher | 1 |
| total_12 | 56.698450 | 55.655387 | 1.874145 | 1.272117 | 1.206977 | higher | higher | 0.531569 |

This report is validation development evidence only. The final test is sealed; no individual behaviour or causal mechanism is identified.

## Metrics and weighting

All models share identical observed areas, origin dates, per-origin maturity terciles and training-only seasonal MASE scales. Areas without CER records are not evaluated. Origin groups are recomputed from cumulative base through each origin, with postcode ties. Absolute/squared losses are averaged across areas within each origin, then origins and seeds. MAE is primary. RMSE is the root after pooling squared losses, not the mean of seed RMSE and not a prediction ensemble. Total error sums all twelve forecasts/actuals before subtraction, preserving saved float32 forecast totals and float64 loss accumulation. Monthly errors are systems/area/month; total errors are systems/area/twelve-month window. MASE is unitless, with total scale twelve times the monthly training scale.

Seed spread is sample SD (ddof=1), minimum and maximum of independently scored seed results. Seasonal naive is the same fixed prediction across all three seeds; its spread is zero. No model is refit.

### Maturity: all

| model | outcome | mae | mae_seed_sd | mase | mase_seed_sd | rmse | rmse_seed_sd |
| --- | --- | --- | --- | --- | --- | --- | --- |
| gnn_no_base | 1 | 5.197026 | 0.049374 | 1.747230 | 0.116174 | 12.466654 | 0.022475 |
| gnn_no_base | 12 | 5.940079 | 0.027536 | 1.989397 | 0.050271 | 13.644126 | 0.101310 |
| gnn_no_base | 6 | 5.702703 | 0.035731 | 1.946864 | 0.082687 | 13.201094 | 0.036311 |
| gnn_no_base | total_12 | 56.899188 | 0.342979 | 1.544244 | 0.059490 | 137.701196 | 0.877426 |
| gnn_no_graph | 1 | 3.600159 | 0.068844 | 1.024426 | 0.022423 | 9.783389 | 0.017906 |
| gnn_no_graph | 12 | 4.673923 | 0.064357 | 1.320074 | 0.063196 | 11.475043 | 0.135496 |
| gnn_no_graph | 6 | 4.215004 | 0.035652 | 1.195480 | 0.044313 | 10.773123 | 0.015656 |
| gnn_no_graph | total_12 | 35.083815 | 0.592595 | 0.694025 | 0.031760 | 103.223178 | 0.756184 |
| gnn_real | 1 | 5.231934 | 0.049218 | 1.525363 | 0.017580 | 12.949559 | 0.036148 |
| gnn_real | 12 | 5.912238 | 0.012392 | 1.718776 | 0.022996 | 14.012265 | 0.087779 |
| gnn_real | 6 | 5.637801 | 0.035341 | 1.659314 | 0.054734 | 13.581405 | 0.034262 |
| gnn_real | total_12 | 56.698450 | 0.298394 | 1.272117 | 0.014955 | 143.436860 | 0.784513 |
| gnn_shuffled | 1 | 5.155356 | 0.104891 | 1.445430 | 0.056053 | 12.450073 | 0.208149 |
| gnn_shuffled | 12 | 5.808168 | 0.133044 | 1.613370 | 0.036578 | 13.593981 | 0.223861 |
| gnn_shuffled | 6 | 5.548519 | 0.132756 | 1.612484 | 0.036883 | 13.030419 | 0.252542 |
| gnn_shuffled | total_12 | 55.655387 | 1.745033 | 1.206977 | 0.020596 | 136.369628 | 2.982031 |
| gradient_boosting_neighbours | 1 | 3.240554 | 0.007218 | 1.009142 | 0.000562 | 7.542176 | 0.059252 |
| gradient_boosting_neighbours | 12 | 4.436481 | 0.003678 | 1.198639 | 0.000931 | 10.305286 | 0.016457 |
| gradient_boosting_neighbours | 6 | 3.954436 | 0.005485 | 1.118497 | 0.000230 | 9.365410 | 0.046755 |
| gradient_boosting_neighbours | total_12 | 31.118270 | 0.026271 | 0.626576 | 0.000438 | 79.241504 | 0.289208 |
| gradient_boosting_own | 1 | 3.256133 | 0.007532 | 1.054212 | 0.000717 | 7.509802 | 0.075904 |
| gradient_boosting_own | 12 | 4.433081 | 0.002229 | 1.274145 | 0.000483 | 10.188115 | 0.007306 |
| gradient_boosting_own | 6 | 3.961972 | 0.006813 | 1.170082 | 0.000614 | 9.293712 | 0.033041 |
| gradient_boosting_own | total_12 | 30.866269 | 0.046997 | 0.680405 | 0.000553 | 77.106792 | 0.140563 |
| seasonal_naive | 1 | 4.366257 | 0.000000 | 1.100749 | 0.000000 | 9.696268 | 0.000000 |
| seasonal_naive | 12 | 4.699696 | 0.000000 | 1.190132 | 0.000000 | 10.575579 | 0.000000 |
| seasonal_naive | 6 | 4.584599 | 0.000000 | 1.145248 | 0.000000 | 10.296439 | 0.000000 |
| seasonal_naive | total_12 | 31.145143 | 0.000000 | 0.571081 | 0.000000 | 72.658397 | 0.000000 |

### Maturity: low

| model | outcome | mae | mae_seed_sd | mase | mase_seed_sd | rmse | rmse_seed_sd |
| --- | --- | --- | --- | --- | --- | --- | --- |
| gnn_no_base | 1 | 0.985364 | 0.086720 | 2.854817 | 0.322956 | 1.680256 | 0.055421 |
| gnn_no_base | 12 | 1.092205 | 0.043617 | 3.265320 | 0.163558 | 1.953930 | 0.012667 |
| gnn_no_base | 6 | 1.081745 | 0.059068 | 3.212125 | 0.232031 | 1.913977 | 0.033232 |
| gnn_no_base | total_12 | 9.264403 | 0.598424 | 2.541348 | 0.176093 | 17.302649 | 0.236290 |
| gnn_no_graph | 1 | 0.661993 | 0.009468 | 1.499209 | 0.080994 | 1.129382 | 0.003050 |
| gnn_no_graph | 12 | 0.737604 | 0.014192 | 1.954118 | 0.189248 | 1.414344 | 0.003302 |
| gnn_no_graph | 6 | 0.726492 | 0.022799 | 1.771061 | 0.149700 | 1.338541 | 0.010619 |
| gnn_no_graph | total_12 | 3.958103 | 0.086633 | 0.977730 | 0.117333 | 6.885771 | 0.108783 |
| gnn_real | 1 | 0.899635 | 0.013886 | 2.220334 | 0.004073 | 1.637139 | 0.018885 |
| gnn_real | 12 | 0.993904 | 0.009583 | 2.506647 | 0.052152 | 1.896409 | 0.038438 |
| gnn_real | 6 | 0.990821 | 0.054031 | 2.440721 | 0.166693 | 1.845400 | 0.020986 |
| gnn_real | total_12 | 8.074653 | 0.262661 | 1.795634 | 0.068147 | 16.454170 | 0.157661 |
| gnn_shuffled | 1 | 0.919999 | 0.034376 | 2.012748 | 0.194400 | 1.515999 | 0.043919 |
| gnn_shuffled | 12 | 1.023963 | 0.038097 | 2.244351 | 0.184338 | 1.771638 | 0.048589 |
| gnn_shuffled | 6 | 1.044095 | 0.059835 | 2.325384 | 0.161122 | 1.756161 | 0.072705 |
| gnn_shuffled | total_12 | 8.630874 | 0.446524 | 1.625589 | 0.137891 | 14.734633 | 0.884955 |
| gradient_boosting_neighbours | 1 | 0.669236 | 0.000327 | 1.522775 | 0.001178 | 1.123627 | 0.000132 |
| gradient_boosting_neighbours | 12 | 0.729146 | 0.000347 | 1.691817 | 0.002010 | 1.408581 | 0.000644 |
| gradient_boosting_neighbours | 6 | 0.705782 | 0.000147 | 1.608706 | 0.001501 | 1.317585 | 0.001404 |
| gradient_boosting_neighbours | total_12 | 3.889148 | 0.001581 | 0.851100 | 0.000930 | 6.869953 | 0.005201 |
| gradient_boosting_own | 1 | 0.693392 | 0.000192 | 1.647050 | 0.000428 | 1.136751 | 0.000344 |
| gradient_boosting_own | 12 | 0.774594 | 0.000204 | 1.911445 | 0.000514 | 1.431625 | 0.000436 |
| gradient_boosting_own | 6 | 0.736364 | 0.000518 | 1.755160 | 0.000022 | 1.342536 | 0.000681 |
| gradient_boosting_own | total_12 | 4.318011 | 0.002326 | 1.015836 | 0.000532 | 7.122706 | 0.002854 |
| seasonal_naive | 1 | 0.731745 | 0.000000 | 1.262172 | 0.000000 | 1.451888 | 0.000000 |
| seasonal_naive | 12 | 0.775753 | 0.000000 | 1.400665 | 0.000000 | 1.690996 | 0.000000 |
| seasonal_naive | 6 | 0.758099 | 0.000000 | 1.323052 | 0.000000 | 1.614816 | 0.000000 |
| seasonal_naive | total_12 | 3.815648 | 0.000000 | 0.655036 | 0.000000 | 7.139211 | 0.000000 |

### Maturity: medium

| model | outcome | mae | mae_seed_sd | mase | mase_seed_sd | rmse | rmse_seed_sd |
| --- | --- | --- | --- | --- | --- | --- | --- |
| gnn_no_base | 1 | 3.295425 | 0.033690 | 1.307129 | 0.017807 | 5.042787 | 0.022244 |
| gnn_no_base | 12 | 3.658783 | 0.047877 | 1.441401 | 0.017313 | 5.558596 | 0.073116 |
| gnn_no_base | 6 | 3.602472 | 0.041221 | 1.420158 | 0.018587 | 5.506568 | 0.029561 |
| gnn_no_base | total_12 | 33.601111 | 0.263781 | 1.103427 | 0.006610 | 54.253602 | 0.399085 |
| gnn_no_graph | 1 | 2.083308 | 0.031990 | 0.818021 | 0.012069 | 3.142623 | 0.013424 |
| gnn_no_graph | 12 | 2.514905 | 0.020451 | 0.970534 | 0.006458 | 3.866001 | 0.014382 |
| gnn_no_graph | 6 | 2.316963 | 0.030262 | 0.902128 | 0.009905 | 3.584814 | 0.028340 |
| gnn_no_graph | total_12 | 14.932067 | 0.572452 | 0.469119 | 0.017931 | 23.628005 | 0.540707 |
| gnn_real | 1 | 3.220915 | 0.077887 | 1.276514 | 0.029530 | 4.893958 | 0.116567 |
| gnn_real | 12 | 3.567270 | 0.060184 | 1.406552 | 0.023207 | 5.392614 | 0.083325 |
| gnn_real | 6 | 3.446827 | 0.034695 | 1.360228 | 0.015030 | 5.224786 | 0.056361 |
| gnn_real | total_12 | 31.982130 | 0.366713 | 1.051918 | 0.009175 | 51.096379 | 0.863779 |
| gnn_shuffled | 1 | 3.152763 | 0.078463 | 1.239392 | 0.028110 | 4.631086 | 0.133290 |
| gnn_shuffled | 12 | 3.484853 | 0.117574 | 1.363658 | 0.045682 | 5.213057 | 0.163253 |
| gnn_shuffled | 6 | 3.420755 | 0.134172 | 1.343481 | 0.055047 | 5.047402 | 0.167119 |
| gnn_shuffled | total_12 | 31.565231 | 1.573433 | 1.029604 | 0.052591 | 48.167050 | 2.386475 |
| gradient_boosting_neighbours | 1 | 2.035803 | 0.000278 | 0.800762 | 0.000048 | 3.081380 | 0.001150 |
| gradient_boosting_neighbours | 12 | 2.388459 | 0.001329 | 0.923334 | 0.000487 | 3.833280 | 0.008636 |
| gradient_boosting_neighbours | 6 | 2.247032 | 0.001581 | 0.874218 | 0.000548 | 3.518911 | 0.002318 |
| gradient_boosting_neighbours | total_12 | 14.222212 | 0.012784 | 0.445815 | 0.000337 | 23.255112 | 0.063675 |
| gradient_boosting_own | 1 | 2.059580 | 0.001986 | 0.810321 | 0.000721 | 3.108866 | 0.003394 |
| gradient_boosting_own | 12 | 2.415790 | 0.001287 | 0.936209 | 0.000443 | 3.828124 | 0.004621 |
| gradient_boosting_own | 6 | 2.276109 | 0.001004 | 0.886775 | 0.000157 | 3.549353 | 0.003058 |
| gradient_boosting_own | total_12 | 14.415432 | 0.014659 | 0.454350 | 0.000346 | 23.042983 | 0.021843 |
| seasonal_naive | 1 | 2.737155 | 0.000000 | 1.066349 | 0.000000 | 4.254853 | 0.000000 |
| seasonal_naive | 12 | 2.888984 | 0.000000 | 1.124344 | 0.000000 | 4.553803 | 0.000000 |
| seasonal_naive | 6 | 2.812010 | 0.000000 | 1.093415 | 0.000000 | 4.380692 | 0.000000 |
| seasonal_naive | total_12 | 15.142780 | 0.000000 | 0.471949 | 0.000000 | 24.671336 | 0.000000 |

### Maturity: high

| model | outcome | mae | mae_seed_sd | mase | mase_seed_sd | rmse | rmse_seed_sd |
| --- | --- | --- | --- | --- | --- | --- | --- |
| gnn_no_base | 1 | 11.310289 | 0.028785 | 1.079745 | 0.008019 | 20.928436 | 0.049461 |
| gnn_no_base | 12 | 13.069248 | 0.091756 | 1.261471 | 0.006565 | 22.886037 | 0.176766 |
| gnn_no_base | 6 | 12.423893 | 0.050702 | 1.208310 | 0.011567 | 22.109297 | 0.057442 |
| gnn_no_base | total_12 | 127.832050 | 0.652295 | 0.987957 | 0.005912 | 231.607476 | 1.497877 |
| gnn_no_graph | 1 | 8.055174 | 0.177069 | 0.756050 | 0.017514 | 16.613023 | 0.031617 |
| gnn_no_graph | 12 | 10.769260 | 0.191518 | 1.035569 | 0.012645 | 19.444370 | 0.242419 |
| gnn_no_graph | 6 | 9.601556 | 0.085715 | 0.913251 | 0.011458 | 18.263022 | 0.032475 |
| gnn_no_graph | total_12 | 86.361276 | 1.881916 | 0.635226 | 0.013773 | 177.085790 | 1.388177 |
| gnn_real | 1 | 11.575252 | 0.064971 | 1.079242 | 0.021081 | 21.827556 | 0.091379 |
| gnn_real | 12 | 13.175542 | 0.064632 | 1.243127 | 0.011217 | 23.587159 | 0.177640 |
| gnn_real | 6 | 12.475754 | 0.061056 | 1.176993 | 0.016858 | 22.861754 | 0.068856 |
| gnn_real | total_12 | 130.038567 | 0.687937 | 0.968798 | 0.015324 | 242.571265 | 1.565522 |
| gnn_shuffled | 1 | 11.393308 | 0.300509 | 1.084151 | 0.027974 | 21.006373 | 0.348399 |
| gnn_shuffled | 12 | 12.915687 | 0.333020 | 1.232100 | 0.033140 | 22.892669 | 0.365511 |
| gnn_shuffled | 6 | 12.180706 | 0.392203 | 1.168587 | 0.038146 | 21.927496 | 0.426976 |
| gnn_shuffled | total_12 | 126.770057 | 4.565982 | 0.965739 | 0.037610 | 230.765796 | 4.904146 |
| gradient_boosting_neighbours | 1 | 7.016623 | 0.021636 | 0.703889 | 0.000637 | 12.644992 | 0.105905 |
| gradient_boosting_neighbours | 12 | 10.191837 | 0.009680 | 0.980766 | 0.000925 | 17.375805 | 0.027367 |
| gradient_boosting_neighbours | 6 | 8.910495 | 0.017958 | 0.872568 | 0.001038 | 15.780177 | 0.083764 |
| gradient_boosting_neighbours | total_12 | 75.243451 | 0.068418 | 0.582812 | 0.000629 | 135.091271 | 0.503821 |
| gradient_boosting_own | 1 | 7.015428 | 0.020600 | 0.705266 | 0.001177 | 12.579115 | 0.135120 |
| gradient_boosting_own | 12 | 10.108860 | 0.006931 | 0.974782 | 0.000684 | 17.166507 | 0.013976 |
| gradient_boosting_own | 6 | 8.873443 | 0.020789 | 0.868310 | 0.001810 | 15.643494 | 0.058356 |
| gradient_boosting_own | total_12 | 73.865364 | 0.129433 | 0.571029 | 0.000915 | 131.356995 | 0.244071 |
| seasonal_naive | 1 | 9.629872 | 0.000000 | 0.973725 | 0.000000 | 16.181504 | 0.000000 |
| seasonal_naive | 12 | 10.434352 | 0.000000 | 1.045388 | 0.000000 | 17.661597 | 0.000000 |
| seasonal_naive | 6 | 10.183688 | 0.000000 | 1.019275 | 0.000000 | 17.211970 | 0.000000 |
| seasonal_naive | total_12 | 74.476999 | 0.000000 | 0.586257 | 0.000000 | 123.199370 | 0.000000 |

All twelve monthly horizons, total, min/max and per-seed scores are in the linked CSVs.

## Predeclared DM/Holm family

Real graph versus no graph, shuffled graph and each boosting baseline; also versus no-base if retained. The testing unit is the origin: area-averaged absolute losses, averaged over the same seeds before DM. dieboldmariano 1.1.0, Bartlett h−1 covariance weights, HLN correction, two-sided tests; horizon 12 for totals. One Holm adjustment covers the whole 16- or 20-test family. Undefined statistics/p-values stay undefined and reserve their family slots. Validation p-values are descriptive because validation was used for tuning. RMSE adds no squared-loss testing family.

| model_a | model_b | outcome | h | origins | statistic | p_raw | status | family_size | p_holm |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| gnn_real | gnn_no_graph | 1 | 1 | 36 | 31.009295 | 4.80172e-27 | defined | 20 | 9.60344e-26 |
| gnn_real | gnn_no_graph | 6 | 6 | 36 | 10.551813 | 2.04098e-12 | defined | 20 | 3.46967e-11 |
| gnn_real | gnn_no_graph | 12 | 12 | 36 | 6.030170 | 7.04614e-07 | defined | 20 | 7.75076e-06 |
| gnn_real | gnn_no_graph | total_12 | 12 | 36 | 8.864338 | 1.80035e-10 | defined | 20 | 2.88056e-09 |
| gnn_real | gnn_shuffled | 1 | 1 | 36 | 3.122502 | 0.00358764 | defined | 20 | 0.0287011 |
| gnn_real | gnn_shuffled | 6 | 6 | 36 | 2.833093 | 0.00759907 | defined | 20 | 0.0531935 |
| gnn_real | gnn_shuffled | 12 | 12 | 36 | 0.750743 | 0.457825 | defined | 20 | 1 |
| gnn_real | gnn_shuffled | total_12 | 12 | 36 | 1.751643 | 0.0885948 | defined | 20 | 0.531569 |
| gnn_real | gradient_boosting_own | 1 | 1 | 36 | 23.170554 | 8.09438e-23 | defined | 20 | 1.45699e-21 |
| gnn_real | gradient_boosting_own | 6 | 6 | 36 | 8.460431 | 5.55419e-10 | defined | 20 | 8.33128e-09 |
| gnn_real | gradient_boosting_own | 12 | 12 | 36 | 5.614143 | 2.49149e-06 | defined | 20 | 2.49149e-05 |
| gnn_real | gradient_boosting_own | total_12 | 12 | 36 | 7.276227 | 1.68721e-08 | defined | 20 | 2.19337e-07 |
| gnn_real | gradient_boosting_neighbours | 1 | 1 | 36 | 25.340093 | 4.19015e-24 | defined | 20 | 7.96129e-23 |
| gnn_real | gradient_boosting_neighbours | 6 | 6 | 36 | 8.150521 | 1.33634e-09 | defined | 20 | 1.87088e-08 |
| gnn_real | gradient_boosting_neighbours | 12 | 12 | 36 | 5.540588 | 3.1154e-06 | defined | 20 | 2.80386e-05 |
| gnn_real | gradient_boosting_neighbours | total_12 | 12 | 36 | 7.069365 | 3.10958e-08 | defined | 20 | 3.7315e-07 |
| gnn_real | gnn_no_base | 1 | 1 | 36 | 1.155055 | 0.255893 | defined | 20 | 1 |
| gnn_real | gnn_no_base | 6 | 6 | 36 | -0.782330 | 0.439282 | defined | 20 | 1 |
| gnn_real | gnn_no_base | 12 | 12 | 36 | -0.255220 | 0.800047 | defined | 20 | 1 |
| gnn_real | gnn_no_base | total_12 | 12 | 36 | -0.171780 | 0.8646 | defined | 20 | 1 |

## Spatial diagnostics

Maps use horizon-12 per-area seasonal scaled absolute errors and real-minus-shuffled scaled error (negative favours real). The real-error colour scale is logarithmic; the difference map uses symmetric-log colour, linear within -1 to 1 MASE, to retain all extreme values without obscuring typical differences. No values are clipped or excluded. Moran I is row-standardised rook clustering of per-area absolute, scaled absolute and signed errors averaged over origins/seeds. Isolates have zero weight rows; seven unknown areas are not zero-error observations. Signed error is forecast minus actual. No dwelling normalisation or permutation significance is supplied; absolute errors can mix volume and predictability. These diagnostics are descriptive.

| model | outcome | error_type | moran_i | observed_areas | weights |
| --- | --- | --- | --- | --- | --- |
| gnn_no_base | 1 | absolute | 0.285289 | 2634 | row-standardised rook; observed isolates zero rows |
| gnn_no_base | 1 | training_scaled_absolute | 0.035808 | 2634 | row-standardised rook; observed isolates zero rows |
| gnn_no_base | 1 | signed | -0.018675 | 2634 | row-standardised rook; observed isolates zero rows |
| gnn_no_base | 12 | absolute | 0.336815 | 2634 | row-standardised rook; observed isolates zero rows |
| gnn_no_base | 12 | training_scaled_absolute | 0.034081 | 2634 | row-standardised rook; observed isolates zero rows |
| gnn_no_base | 12 | signed | -0.005192 | 2634 | row-standardised rook; observed isolates zero rows |
| gnn_no_base | 6 | absolute | 0.321428 | 2634 | row-standardised rook; observed isolates zero rows |
| gnn_no_base | 6 | training_scaled_absolute | 0.043036 | 2634 | row-standardised rook; observed isolates zero rows |
| gnn_no_base | 6 | signed | -0.017616 | 2634 | row-standardised rook; observed isolates zero rows |
| gnn_no_base | total_12 | absolute | 0.283642 | 2634 | row-standardised rook; observed isolates zero rows |
| gnn_no_base | total_12 | training_scaled_absolute | 0.036206 | 2634 | row-standardised rook; observed isolates zero rows |
| gnn_no_base | total_12 | signed | -0.014095 | 2634 | row-standardised rook; observed isolates zero rows |
| gnn_no_graph | 1 | absolute | 0.224638 | 2634 | row-standardised rook; observed isolates zero rows |
| gnn_no_graph | 1 | training_scaled_absolute | 0.158941 | 2634 | row-standardised rook; observed isolates zero rows |
| gnn_no_graph | 1 | signed | 0.083289 | 2634 | row-standardised rook; observed isolates zero rows |
| gnn_no_graph | 12 | absolute | 0.301840 | 2634 | row-standardised rook; observed isolates zero rows |
| gnn_no_graph | 12 | training_scaled_absolute | 0.145062 | 2634 | row-standardised rook; observed isolates zero rows |
| gnn_no_graph | 12 | signed | 0.097307 | 2634 | row-standardised rook; observed isolates zero rows |
| gnn_no_graph | 6 | absolute | 0.271796 | 2634 | row-standardised rook; observed isolates zero rows |
| gnn_no_graph | 6 | training_scaled_absolute | 0.144036 | 2634 | row-standardised rook; observed isolates zero rows |
| gnn_no_graph | 6 | signed | 0.091001 | 2634 | row-standardised rook; observed isolates zero rows |
| gnn_no_graph | total_12 | absolute | 0.220975 | 2634 | row-standardised rook; observed isolates zero rows |
| gnn_no_graph | total_12 | training_scaled_absolute | 0.128538 | 2634 | row-standardised rook; observed isolates zero rows |
| gnn_no_graph | total_12 | signed | 0.092403 | 2634 | row-standardised rook; observed isolates zero rows |
| gnn_real | 1 | absolute | 0.271922 | 2634 | row-standardised rook; observed isolates zero rows |
| gnn_real | 1 | training_scaled_absolute | 0.020239 | 2634 | row-standardised rook; observed isolates zero rows |
| gnn_real | 1 | signed | -0.004535 | 2634 | row-standardised rook; observed isolates zero rows |
| gnn_real | 12 | absolute | 0.317136 | 2634 | row-standardised rook; observed isolates zero rows |
| gnn_real | 12 | training_scaled_absolute | 0.018600 | 2634 | row-standardised rook; observed isolates zero rows |
| gnn_real | 12 | signed | 0.011574 | 2634 | row-standardised rook; observed isolates zero rows |
| gnn_real | 6 | absolute | 0.293442 | 2634 | row-standardised rook; observed isolates zero rows |
| gnn_real | 6 | training_scaled_absolute | 0.023006 | 2634 | row-standardised rook; observed isolates zero rows |
| gnn_real | 6 | signed | 0.001923 | 2634 | row-standardised rook; observed isolates zero rows |
| gnn_real | total_12 | absolute | 0.264841 | 2634 | row-standardised rook; observed isolates zero rows |
| gnn_real | total_12 | training_scaled_absolute | 0.018894 | 2634 | row-standardised rook; observed isolates zero rows |
| gnn_real | total_12 | signed | 0.004136 | 2634 | row-standardised rook; observed isolates zero rows |
| gnn_shuffled | 1 | absolute | 0.248601 | 2634 | row-standardised rook; observed isolates zero rows |
| gnn_shuffled | 1 | training_scaled_absolute | 0.078372 | 2634 | row-standardised rook; observed isolates zero rows |
| gnn_shuffled | 1 | signed | 0.165889 | 2634 | row-standardised rook; observed isolates zero rows |
| gnn_shuffled | 12 | absolute | 0.283622 | 2634 | row-standardised rook; observed isolates zero rows |
| gnn_shuffled | 12 | training_scaled_absolute | 0.093235 | 2634 | row-standardised rook; observed isolates zero rows |
| gnn_shuffled | 12 | signed | 0.187456 | 2634 | row-standardised rook; observed isolates zero rows |
| gnn_shuffled | 6 | absolute | 0.263807 | 2634 | row-standardised rook; observed isolates zero rows |
| gnn_shuffled | 6 | training_scaled_absolute | 0.090401 | 2634 | row-standardised rook; observed isolates zero rows |
| gnn_shuffled | 6 | signed | 0.171227 | 2634 | row-standardised rook; observed isolates zero rows |
| gnn_shuffled | total_12 | absolute | 0.238231 | 2634 | row-standardised rook; observed isolates zero rows |
| gnn_shuffled | total_12 | training_scaled_absolute | 0.056094 | 2634 | row-standardised rook; observed isolates zero rows |
| gnn_shuffled | total_12 | signed | 0.175681 | 2634 | row-standardised rook; observed isolates zero rows |
| gradient_boosting_neighbours | 1 | absolute | 0.317242 | 2634 | row-standardised rook; observed isolates zero rows |
| gradient_boosting_neighbours | 1 | training_scaled_absolute | 0.181714 | 2634 | row-standardised rook; observed isolates zero rows |
| gradient_boosting_neighbours | 1 | signed | 0.268973 | 2634 | row-standardised rook; observed isolates zero rows |
| gradient_boosting_neighbours | 12 | absolute | 0.367270 | 2634 | row-standardised rook; observed isolates zero rows |
| gradient_boosting_neighbours | 12 | training_scaled_absolute | 0.191991 | 2634 | row-standardised rook; observed isolates zero rows |
| gradient_boosting_neighbours | 12 | signed | 0.290822 | 2634 | row-standardised rook; observed isolates zero rows |
| gradient_boosting_neighbours | 6 | absolute | 0.340027 | 2634 | row-standardised rook; observed isolates zero rows |
| gradient_boosting_neighbours | 6 | training_scaled_absolute | 0.185089 | 2634 | row-standardised rook; observed isolates zero rows |
| gradient_boosting_neighbours | 6 | signed | 0.255072 | 2634 | row-standardised rook; observed isolates zero rows |
| gradient_boosting_neighbours | total_12 | absolute | 0.352689 | 2634 | row-standardised rook; observed isolates zero rows |
| gradient_boosting_neighbours | total_12 | training_scaled_absolute | 0.174478 | 2634 | row-standardised rook; observed isolates zero rows |
| gradient_boosting_neighbours | total_12 | signed | 0.271672 | 2634 | row-standardised rook; observed isolates zero rows |
| gradient_boosting_own | 1 | absolute | 0.319476 | 2634 | row-standardised rook; observed isolates zero rows |
| gradient_boosting_own | 1 | training_scaled_absolute | 0.177680 | 2634 | row-standardised rook; observed isolates zero rows |
| gradient_boosting_own | 1 | signed | 0.211058 | 2634 | row-standardised rook; observed isolates zero rows |
| gradient_boosting_own | 12 | absolute | 0.364110 | 2634 | row-standardised rook; observed isolates zero rows |
| gradient_boosting_own | 12 | training_scaled_absolute | 0.177592 | 2634 | row-standardised rook; observed isolates zero rows |
| gradient_boosting_own | 12 | signed | 0.217109 | 2634 | row-standardised rook; observed isolates zero rows |
| gradient_boosting_own | 6 | absolute | 0.330198 | 2634 | row-standardised rook; observed isolates zero rows |
| gradient_boosting_own | 6 | training_scaled_absolute | 0.175981 | 2634 | row-standardised rook; observed isolates zero rows |
| gradient_boosting_own | 6 | signed | 0.190382 | 2634 | row-standardised rook; observed isolates zero rows |
| gradient_boosting_own | total_12 | absolute | 0.328055 | 2634 | row-standardised rook; observed isolates zero rows |
| gradient_boosting_own | total_12 | training_scaled_absolute | 0.156351 | 2634 | row-standardised rook; observed isolates zero rows |
| gradient_boosting_own | total_12 | signed | 0.207299 | 2634 | row-standardised rook; observed isolates zero rows |
| seasonal_naive | 1 | absolute | 0.350681 | 2634 | row-standardised rook; observed isolates zero rows |
| seasonal_naive | 1 | training_scaled_absolute | 0.200075 | 2634 | row-standardised rook; observed isolates zero rows |
| seasonal_naive | 1 | signed | 0.398574 | 2634 | row-standardised rook; observed isolates zero rows |
| seasonal_naive | 12 | absolute | 0.365201 | 2634 | row-standardised rook; observed isolates zero rows |
| seasonal_naive | 12 | training_scaled_absolute | 0.165995 | 2634 | row-standardised rook; observed isolates zero rows |
| seasonal_naive | 12 | signed | 0.328597 | 2634 | row-standardised rook; observed isolates zero rows |
| seasonal_naive | 6 | absolute | 0.360262 | 2634 | row-standardised rook; observed isolates zero rows |
| seasonal_naive | 6 | training_scaled_absolute | 0.200830 | 2634 | row-standardised rook; observed isolates zero rows |
| seasonal_naive | 6 | signed | 0.369429 | 2634 | row-standardised rook; observed isolates zero rows |
| seasonal_naive | total_12 | absolute | 0.376778 | 2634 | row-standardised rook; observed isolates zero rows |
| seasonal_naive | total_12 | training_scaled_absolute | 0.223087 | 2634 | row-standardised rook; observed isolates zero rows |
| seasonal_naive | total_12 | signed | 0.386290 | 2634 | row-standardised rook; observed isolates zero rows |

## Gate C: real graph versus shuffled

- Outcome 1: real MAE 5.231934, shuffled 5.155356; real MASE 1.525363, shuffled 1.445430. These are development comparisons, not a causal or final-test conclusion.
- Outcome 6: real MAE 5.637801, shuffled 5.548519; real MASE 1.659314, shuffled 1.612484. These are development comparisons, not a causal or final-test conclusion.
- Outcome 12: real MAE 5.912238, shuffled 5.808168; real MASE 1.718776, shuffled 1.613370. These are development comparisons, not a causal or final-test conclusion.
- Outcome total_12: real MAE 56.698450, shuffled 55.655387; real MASE 1.272117, shuffled 1.206977. These are development comparisons, not a causal or final-test conclusion.

The researcher reviews Gate C and decides any hybrid work. No hybrid is selected by this pipeline.

## Figures and provenance

- [All-model monthly error](../../visuals/t03/gnn_error_horizon.png) / [CSV](../../visuals/t03/gnn_error_horizon.csv).
- [Twelve-month total](../../visuals/t03/gnn_error_total.png) / [CSV](../../visuals/t03/gnn_error_total.csv).
- [Maturity errors](../../visuals/t03/gnn_error_maturity.png) / [CSV](../../visuals/t03/gnn_error_maturity.csv).
- [Core graph comparison / Figure 3 candidate](../figures/t03_graph_comparison.png) / [CSV](../figures/t03_graph_comparison.csv).
- [Real scaled-error map](../../data/explore/t03/gnn_scaled_error_map.png) / [CSV](../../data/explore/t03/gnn_scaled_error_map.csv).
- [Real-minus-shuffled map](../../data/explore/t03/gnn_real_minus_shuffled_map.png) / [CSV](../../data/explore/t03/gnn_real_minus_shuffled_map.csv).
- [Scaled/signed Moran summary](../../data/explore/t03/gnn_error_moran.png) / [CSV](../../data/explore/t03/gnn_error_moran.csv).
- [Full scores](../../data/processed/t03_gate_c/scores.csv), [seed spread](../../data/processed/t03_gate_c/seed_metrics.csv), [origin losses](../../data/processed/t03_gate_c/origin_metrics.csv.gz), [area errors](../../data/processed/t03_gate_c/area_metrics.csv.gz).

Generated by `evaluation.gate_c` and `visuals.gate_c`. All result figures/values and plot source remain local-only. Saved baselines retain their original fit provenance; protocol v2 governs GNN fitting and the combined evaluation.

## Completion and verification

All four GNN conditions completed 46 unique fits at 65 epochs with retained checkpoints: **184 GNN fits**. All fit manifests confirm the same laptop/software inventory and frozen protocol. Three saved forecast arrays per condition cover all 36 validation origins, 2,634 observed areas and twelve horizons. Existing baseline fits are reused unchanged.

| Condition | Unique fits | Recorded fit wall hours |
| --- | ---: | ---: |
| real | 46 | 9.015958 |
| within_state_shuffled | 46 | 11.925686 |
| no_graph | 46 | 10.960404 |
| real_without_installed_base | 46 | 9.345205 |

Total recorded full-fit wall time: **41.247252 hours**; original pilot **0.475043 hours** is separate. Inference, between-session breaks and GPU utilisation are not included in this fit-time sum.

CPU verification recomputed all **39,312 origin/group loss rows** from saved forecasts, checked 364 score rows and 1092 per-seed rows, reproduced all 20 DM statistics/raw p-values and the single Holm adjustment, and checked 18 figure/CSV files plus both maps. No model/checkpoint was loaded for inference or retrained; no GPU operation or sealed-test scoring.

[Verification JSON](t03_gate_c_verification.json) · [Session progress](t03_session_progress.json) · [Full test log](../../logs/t03_gate_c_full_tests_final.log).

Each condition was tuned independently under the same grid/budget; selected widths can differ. This is a comparison of the frozen tuned procedures, not a matched-selected-width experiment. Low Moran I alone is not predictive improvement: accuracy and clustering describe different properties. Training/validation tuning, overlapping horizons, 36 origins, revised snapshot data and fixed-seed averaging limit inference.

**Gate C awaits researcher review.** No hybrid, extra fit, protocol change or final-test access is initiated by this report.

Final full suite after the report-summary additions: **98 passed**, one upstream GeoPandas/Shapely deprecation warning. No skipped tests. Log: `logs/t03_gate_c_full_tests_final.log`. The graph-comparison figure and difference-map layout were inspected once; the difference colour transform retains all outliers without clipping.
