# Protocol v7 final test results

All scores use the fixed three-seed forecast ensembles. Individual seed scores are separate. No model/weight fit occurs during this evaluation. Combination weights are the approved six-decimal validation constants; the no-graph sensitivity uses those SAME weights.

## Fixed-sequence confirmatory chains

Accuracy: A7, A2, A1, A4, A3, A6, A5. Behavioural: B3, B1, B2. Each chain alpha 0.025, one-sided in the predicted lower-loss direction, stopped at first non-rejection. B4 was dropped before the test. A6 tests E[Lc - 1.01 Lo] < 0; it can reject non-inferiority even if the unshifted combination loss is slightly higher. No Holm correction. Untested later hypotheses have no computed p-value.

| chain | position | candidate_id | candidate | reference | metric | outcome | group | alpha | p_one_sided | status | dm_statistic | candidate_loss | reference_loss | gain_reference_minus_candidate | gain_percent | mean_test_differential | noninferiority_margin_slack | test |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Accuracy | 1 | A7 | combination | gradient_boosting_own | mase | 1 | all | 0.025000 | 9.0166245e-12 | rejected | -12.122788 | 0.879191 | 0.964533 | 0.085342 | 8.847995 | -0.085342 | nan | directional superiority |
| Accuracy | 2 | A2 | combination | gradient_boosting_neighbours | mae | 1 | all | 0.025000 | 4.2355346e-06 | rejected | -5.694749 | 2.771767 | 2.918196 | 0.146429 | 5.017785 | -0.146429 | nan | directional superiority |
| Accuracy | 3 | A1 | combination | gradient_boosting_own | mae | 1 | all | 0.025000 | 6.8265528e-06 | rejected | -5.498798 | 2.771767 | 2.931850 | 0.160083 | 5.460132 | -0.160083 | nan | directional superiority |
| Accuracy | 4 | A4 | combination | gradient_boosting_neighbours | mae | 1-3 | all | 0.025000 | 2.6178025e-06 | rejected | -5.893803 | 2.834059 | 2.981767 | 0.147708 | 4.953703 | -0.147708 | nan | directional superiority |
| Accuracy | 5 | A3 | combination | gradient_boosting_own | mae | 1-3 | all | 0.025000 | 1.6188056e-06 | rejected | -6.094334 | 2.834059 | 2.996710 | 0.162651 | 5.427661 | -0.162651 | nan | directional superiority |
| Accuracy | 6 | A6 | combination | gradient_boosting_own | mae | total_12 | all | 0.025000 | 0.021927687 | rejected | -2.132593 | 22.898340 | 26.411932 | 3.513592 | 13.303048 | -3.777711 | 3.777711 | NI 1 percent |
| Accuracy | 7 | A5 | combination | gradient_boosting_own | mae | 6 | all | 0.025000 | 0.00022524595 | rejected | -4.089368 | 3.108717 | 3.313590 | 0.204873 | 6.182819 | -0.204873 | nan | directional superiority |
| Behavioural | 1 | B3 | B2_real | B2_without_base | mae | 1-3 | all | 0.025000 | 0.43964595 | not_rejected_stop | -0.153565 | 2.862878 | 2.869149 | 0.006271 | 0.218574 | -0.006271 | nan | directional superiority |
| Behavioural | 2 | B1 | B2_real | B2_without_base | mae | 1 | all | 0.025000 | not tested / undefined | not_tested_after_stop | nan | nan | nan | nan | nan | nan | nan | nan |
| Behavioural | 3 | B2 | B2_real | B2_without_base | mae | total_12 | all | 0.025000 | not tested / undefined | not_tested_after_stop | nan | nan | nan | nan | nan | nan | nan | nan |

## Forecast-ensemble descriptive scores

MAE/RMSE: systems/area/month, or systems/area/twelve-month window for total. MASE: unitless training-only seasonal scales with accepted pooled fallback, twelve times monthly scale for total. These are one-forecast ensemble scores; no seed SD applies. All monthly horizons and dynamic maturity groups are in the accompanying CSVs.

### all maturity

| model | outcome | mae | mase | rmse | mean_signed_error |
| --- | --- | --- | --- | --- | --- |
| B2_no_graph | 1 | 2.791144 | 0.872477 | 5.444606 | -0.440730 |
| B2_no_graph | 12 | 3.383159 | 1.032985 | 7.619901 | -0.626954 |
| B2_no_graph | 6 | 3.130530 | 0.938473 | 6.711321 | -0.719925 |
| B2_no_graph | total_12 | 23.242031 | 0.524514 | 57.563614 | -7.730987 |
| B2_real | 1 | 2.761449 | 0.869120 | 5.375454 | -0.385369 |
| B2_real | 12 | 3.334618 | 1.004167 | 7.521697 | -0.683736 |
| B2_real | 6 | 3.133856 | 0.943969 | 6.688695 | -0.817236 |
| B2_real | total_12 | 23.022026 | 0.519302 | 56.972452 | -8.510011 |
| B2_shuffled | 1 | 2.768395 | 0.876034 | 5.370751 | -0.330505 |
| B2_shuffled | 12 | 3.315532 | 1.024936 | 7.511986 | -0.802872 |
| B2_shuffled | 6 | 3.141542 | 0.952169 | 6.683417 | -0.713895 |
| B2_shuffled | total_12 | 22.982911 | 0.530852 | 56.657306 | -8.318300 |
| B2_without_base | 1 | 2.805178 | 0.868412 | 5.366716 | -0.097370 |
| B2_without_base | 12 | 3.461310 | 1.026493 | 7.235713 | 0.474014 |
| B2_without_base | 6 | 3.126439 | 0.939663 | 6.270133 | 0.216298 |
| B2_without_base | total_12 | 22.699198 | 0.519305 | 49.837879 | 3.138493 |
| combination | 1 | 2.771767 | 0.879191 | 5.257605 | 0.174154 |
| combination | 12 | 3.472684 | 1.017065 | 6.985684 | 1.052789 |
| combination | 6 | 3.108717 | 0.953332 | 6.188631 | 0.466790 |
| combination | total_12 | 22.898340 | 0.529339 | 49.690030 | 6.482794 |
| combination_no_graph_sensitivity | 1 | 2.786124 | 0.879863 | 5.293826 | 0.145629 |
| combination_no_graph_sensitivity | 12 | 3.486890 | 1.024320 | 7.012559 | 1.064360 |
| combination_no_graph_sensitivity | 6 | 3.118070 | 0.952191 | 6.207607 | 0.495324 |
| combination_no_graph_sensitivity | total_12 | 23.099269 | 0.531954 | 50.126665 | 6.662432 |
| gradient_boosting_neighbours | 1 | 2.918196 | 0.929990 | 5.458794 | 0.681211 |
| gradient_boosting_neighbours | 12 | 3.776452 | 1.052747 | 7.391263 | 1.770100 |
| gradient_boosting_neighbours | 6 | 3.293013 | 0.982957 | 6.410000 | 1.069511 |
| gradient_boosting_neighbours | total_12 | 26.178925 | 0.577017 | 54.006799 | 13.864600 |
| gradient_boosting_own | 1 | 2.931850 | 0.964533 | 5.465596 | 0.758465 |
| gradient_boosting_own | 12 | 3.795217 | 1.111335 | 7.395125 | 1.877749 |
| gradient_boosting_own | 6 | 3.313590 | 1.024666 | 6.427850 | 1.178144 |
| gradient_boosting_own | total_12 | 26.411932 | 0.619681 | 54.299503 | 15.079983 |

### low maturity

| model | outcome | mae | mase | rmse | mean_signed_error |
| --- | --- | --- | --- | --- | --- |
| B2_no_graph | 1 | 0.621233 | 1.232070 | 0.981044 | 0.072970 |
| B2_no_graph | 12 | 0.666466 | 1.542690 | 1.003014 | 0.215597 |
| B2_no_graph | 6 | 0.647161 | 1.335848 | 1.028353 | 0.120907 |
| B2_no_graph | total_12 | 3.550141 | 0.747012 | 5.280646 | 1.651283 |
| B2_real | 1 | 0.622858 | 1.237418 | 0.980527 | 0.091518 |
| B2_real | 12 | 0.657781 | 1.479702 | 0.997380 | 0.205075 |
| B2_real | 6 | 0.649189 | 1.353036 | 1.029776 | 0.131399 |
| B2_real | total_12 | 3.571882 | 0.740662 | 5.301899 | 1.725413 |
| B2_shuffled | 1 | 0.627244 | 1.252710 | 0.981569 | 0.095182 |
| B2_shuffled | 12 | 0.659899 | 1.549499 | 0.995241 | 0.199203 |
| B2_shuffled | 6 | 0.654014 | 1.376752 | 1.029022 | 0.138145 |
| B2_shuffled | total_12 | 3.632039 | 0.776304 | 5.305846 | 1.799043 |
| B2_without_base | 1 | 0.614809 | 1.215380 | 0.982173 | 0.054273 |
| B2_without_base | 12 | 0.648583 | 1.499303 | 0.995216 | 0.162542 |
| B2_without_base | 6 | 0.642414 | 1.337731 | 1.034785 | 0.093145 |
| B2_without_base | total_12 | 3.484265 | 0.742008 | 5.310194 | 1.315649 |
| combination | 1 | 0.624405 | 1.247105 | 0.979922 | 0.096322 |
| combination | 12 | 0.661129 | 1.407414 | 0.993466 | 0.222369 |
| combination | 6 | 0.654142 | 1.357854 | 1.030495 | 0.146213 |
| combination | total_12 | 3.614860 | 0.726901 | 5.266797 | 1.894033 |
| combination_no_graph_sensitivity | 1 | 0.622911 | 1.242259 | 0.980474 | 0.079644 |
| combination_no_graph_sensitivity | 12 | 0.663400 | 1.421609 | 0.995252 | 0.224682 |
| combination_no_graph_sensitivity | 6 | 0.653336 | 1.349206 | 1.030468 | 0.140826 |
| combination_no_graph_sensitivity | total_12 | 3.599716 | 0.726493 | 5.262516 | 1.831353 |
| gradient_boosting_neighbours | 1 | 0.645175 | 1.340499 | 0.987817 | 0.139167 |
| gradient_boosting_neighbours | 12 | 0.664147 | 1.389267 | 0.998785 | 0.227242 |
| gradient_boosting_neighbours | 6 | 0.663135 | 1.367089 | 1.043833 | 0.161851 |
| gradient_boosting_neighbours | total_12 | 3.747494 | 0.749616 | 5.473036 | 2.075775 |
| gradient_boosting_own | 1 | 0.659652 | 1.445237 | 0.995212 | 0.157719 |
| gradient_boosting_own | 12 | 0.692823 | 1.563526 | 1.019559 | 0.271047 |
| gradient_boosting_own | 6 | 0.682424 | 1.490809 | 1.066520 | 0.187808 |
| gradient_boosting_own | total_12 | 4.006210 | 0.883580 | 5.790516 | 2.442949 |

### medium maturity

| model | outcome | mae | mase | rmse | mean_signed_error |
| --- | --- | --- | --- | --- | --- |
| B2_no_graph | 1 | 1.982505 | 0.768857 | 2.813807 | -0.153000 |
| B2_no_graph | 12 | 2.104874 | 0.811829 | 3.112765 | -0.052113 |
| B2_no_graph | 6 | 2.043823 | 0.788878 | 2.980186 | -0.208224 |
| B2_no_graph | total_12 | 12.306583 | 0.386659 | 18.905557 | -1.869096 |
| B2_real | 1 | 1.964686 | 0.762852 | 2.786739 | -0.122529 |
| B2_real | 12 | 2.075393 | 0.800524 | 3.093418 | -0.174929 |
| B2_real | 6 | 2.040902 | 0.787328 | 2.989471 | -0.304451 |
| B2_real | total_12 | 12.206550 | 0.383259 | 18.902808 | -2.790030 |
| B2_shuffled | 1 | 1.976252 | 0.766853 | 2.801221 | -0.118465 |
| B2_shuffled | 12 | 2.062821 | 0.794796 | 3.104386 | -0.261847 |
| B2_shuffled | 6 | 2.038597 | 0.786476 | 2.982976 | -0.271683 |
| B2_shuffled | total_12 | 12.168748 | 0.381644 | 18.912919 | -2.861269 |
| B2_without_base | 1 | 1.986411 | 0.769877 | 2.821667 | -0.129053 |
| B2_without_base | 12 | 2.101841 | 0.808108 | 3.082964 | 0.053571 |
| B2_without_base | 6 | 2.041057 | 0.787873 | 2.959509 | -0.091725 |
| B2_without_base | total_12 | 12.108792 | 0.380980 | 18.264430 | -0.390057 |
| combination | 1 | 2.020329 | 0.783036 | 2.794883 | 0.302667 |
| combination | 12 | 2.277842 | 0.872685 | 3.160875 | 0.850246 |
| combination | 6 | 2.119287 | 0.817043 | 2.947324 | 0.484720 |
| combination | total_12 | 13.733854 | 0.429551 | 19.068610 | 6.567636 |
| combination_no_graph_sensitivity | 1 | 2.026168 | 0.784902 | 2.803874 | 0.293148 |
| combination_no_graph_sensitivity | 12 | 2.288433 | 0.876639 | 3.170760 | 0.870889 |
| combination_no_graph_sensitivity | 6 | 2.127336 | 0.819933 | 2.953500 | 0.505430 |
| combination_no_graph_sensitivity | total_12 | 13.853388 | 0.433076 | 19.198620 | 6.729704 |
| gradient_boosting_neighbours | 1 | 2.078017 | 0.803190 | 2.845315 | 0.495866 |
| gradient_boosting_neighbours | 12 | 2.372510 | 0.905141 | 3.259450 | 1.057373 |
| gradient_boosting_neighbours | 6 | 2.192715 | 0.842243 | 3.012539 | 0.701146 |
| gradient_boosting_neighbours | total_12 | 15.026089 | 0.466517 | 20.559624 | 8.983835 |
| gradient_boosting_own | 1 | 2.070957 | 0.800890 | 2.841257 | 0.445504 |
| gradient_boosting_own | 12 | 2.368466 | 0.904790 | 3.260317 | 1.046999 |
| gradient_boosting_own | 6 | 2.182981 | 0.839424 | 3.003274 | 0.669842 |
| gradient_boosting_own | total_12 | 14.739629 | 0.458254 | 20.319004 | 8.628932 |

### high maturity

| model | outcome | mae | mase | rmse | mean_signed_error |
| --- | --- | --- | --- | --- | --- |
| B2_no_graph | 1 | 5.769694 | 0.616505 | 8.947136 | -1.242161 |
| B2_no_graph | 12 | 7.378136 | 0.744437 | 12.786451 | -2.044346 |
| B2_no_graph | 6 | 6.700607 | 0.690695 | 11.188675 | -2.072456 |
| B2_no_graph | total_12 | 53.869368 | 0.439872 | 97.751745 | -22.975149 |
| B2_real | 1 | 5.696802 | 0.607091 | 8.829448 | -1.125095 |
| B2_real | 12 | 7.270680 | 0.732273 | 12.616012 | -2.081355 |
| B2_real | 6 | 6.711476 | 0.691543 | 11.145337 | -2.278655 |
| B2_real | total_12 | 53.287646 | 0.433985 | 96.706538 | -24.465415 |
| B2_shuffled | 1 | 5.701688 | 0.608540 | 8.816154 | -0.968231 |
| B2_shuffled | 12 | 7.223876 | 0.730512 | 12.596114 | -2.345972 |
| B2_shuffled | 6 | 6.732015 | 0.693279 | 11.137646 | -2.008148 |
| B2_shuffled | total_12 | 53.147947 | 0.434608 | 96.147286 | -23.892674 |
| B2_without_base | 1 | 5.814314 | 0.619979 | 8.802185 | -0.217330 |
| B2_without_base | 12 | 7.633505 | 0.772067 | 12.106672 | 1.205929 |
| B2_without_base | 6 | 6.695845 | 0.693385 | 10.397799 | 0.647475 |
| B2_without_base | total_12 | 52.504538 | 0.434926 | 84.200089 | 8.489886 |
| combination | 1 | 5.670566 | 0.607431 | 8.611365 | 0.123473 |
| combination | 12 | 7.479082 | 0.771095 | 11.637062 | 2.085753 |
| combination | 6 | 6.552722 | 0.685098 | 10.254211 | 0.769436 |
| combination | total_12 | 51.346306 | 0.431564 | 83.761245 | 10.986713 |
| combination_no_graph_sensitivity | 1 | 5.709294 | 0.612429 | 8.674719 | 0.064095 |
| combination_no_graph_sensitivity | 12 | 7.508837 | 0.774713 | 11.682625 | 2.097509 |
| combination_no_graph_sensitivity | 6 | 6.573538 | 0.687435 | 10.286794 | 0.839716 |
| combination_no_graph_sensitivity | total_12 | 51.844703 | 0.436295 | 84.508973 | 11.426238 |
| gradient_boosting_neighbours | 1 | 6.031395 | 0.646283 | 8.962348 | 1.408601 |
| gradient_boosting_neighbours | 12 | 8.292699 | 0.863834 | 12.339803 | 4.025685 |
| gradient_boosting_neighbours | 6 | 7.023188 | 0.739538 | 10.634816 | 2.345536 |
| gradient_boosting_neighbours | total_12 | 59.763192 | 0.514918 | 91.090892 | 30.534188 |
| gradient_boosting_own | 1 | 6.064940 | 0.647471 | 8.975245 | 1.672171 |
| gradient_boosting_own | 12 | 8.324362 | 0.865689 | 12.344815 | 4.315200 |
| gradient_boosting_own | 6 | 7.075365 | 0.743764 | 10.667457 | 2.676783 |
| gradient_boosting_own | total_12 | 60.489958 | 0.517208 | 91.645600 | 34.168066 |

## Individual seed scores and spread

Every individual seed is in individual_seed.csv; individual_scores.csv holds the mean/SD/min/max of individual losses, which are not the primary ensemble scores.

## Descriptive real-minus-control 95% intervals

Mean origin MAE differences with Bartlett HAC h-1 and the approved HLN-inverted Student t interval; h=12 for total, otherwise forecast horizon. Pointwise, descriptive, no additional confirmatory family. Negative favours real; undefined intervals are reported as missing.

| candidate | reference | outcome | origins | DM_h | mean_MAE_difference | lower95 | upper95 | interpretation |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| B2_real | B2_no_graph | 1 | 24 | 1 | -0.029695 | -0.075298 | 0.015907 | negative favours real; pointwise descriptive |
| B2_real | B2_no_graph | 2 | 24 | 2 | -0.034338 | -0.070073 | 0.001396 | negative favours real; pointwise descriptive |
| B2_real | B2_no_graph | 3 | 24 | 3 | -0.026576 | -0.057754 | 0.004603 | negative favours real; pointwise descriptive |
| B2_real | B2_no_graph | 4 | 24 | 4 | -0.000854 | -0.040078 | 0.038369 | negative favours real; pointwise descriptive |
| B2_real | B2_no_graph | 5 | 24 | 5 | 0.012009 | -0.021165 | 0.045184 | negative favours real; pointwise descriptive |
| B2_real | B2_no_graph | 6 | 24 | 6 | 0.003326 | -0.048112 | 0.054763 | negative favours real; pointwise descriptive |
| B2_real | B2_no_graph | 7 | 24 | 7 | 0.010972 | -0.037482 | 0.059425 | negative favours real; pointwise descriptive |
| B2_real | B2_no_graph | 8 | 24 | 8 | 0.015037 | -0.029014 | 0.059087 | negative favours real; pointwise descriptive |
| B2_real | B2_no_graph | 9 | 24 | 9 | 0.007523 | -0.050592 | 0.065639 | negative favours real; pointwise descriptive |
| B2_real | B2_no_graph | 10 | 24 | 10 | -0.050577 | -0.078487 | -0.022668 | negative favours real; pointwise descriptive |
| B2_real | B2_no_graph | 11 | 24 | 11 | -0.040448 | -0.104840 | 0.023945 | negative favours real; pointwise descriptive |
| B2_real | B2_no_graph | 12 | 24 | 12 | -0.048541 | -0.155958 | 0.058876 | negative favours real; pointwise descriptive |
| B2_real | B2_no_graph | total_12 | 24 | 12 | -0.220004 | -0.664934 | 0.224925 | negative favours real; pointwise descriptive |
| B2_real | B2_shuffled | 1 | 24 | 1 | -0.006946 | -0.042880 | 0.028987 | negative favours real; pointwise descriptive |
| B2_real | B2_shuffled | 2 | 24 | 2 | -0.015603 | -0.063736 | 0.032530 | negative favours real; pointwise descriptive |
| B2_real | B2_shuffled | 3 | 24 | 3 | -0.025827 | -0.087406 | 0.035753 | negative favours real; pointwise descriptive |
| B2_real | B2_shuffled | 4 | 24 | 4 | -0.027504 | -0.086362 | 0.031354 | negative favours real; pointwise descriptive |
| B2_real | B2_shuffled | 5 | 24 | 5 | -0.005303 | -0.052005 | 0.041398 | negative favours real; pointwise descriptive |
| B2_real | B2_shuffled | 6 | 24 | 6 | -0.007686 | -0.070591 | 0.055219 | negative favours real; pointwise descriptive |
| B2_real | B2_shuffled | 7 | 24 | 7 | -0.016096 | -0.065926 | 0.033733 | negative favours real; pointwise descriptive |
| B2_real | B2_shuffled | 8 | 24 | 8 | 0.047704 | 0.018793 | 0.076615 | negative favours real; pointwise descriptive |
| B2_real | B2_shuffled | 9 | 24 | 9 | 0.036591 | -0.014402 | 0.087585 | negative favours real; pointwise descriptive |
| B2_real | B2_shuffled | 10 | 24 | 10 | -0.008697 | -0.076084 | 0.058691 | negative favours real; pointwise descriptive |
| B2_real | B2_shuffled | 11 | 24 | 11 | -0.031816 | -0.154533 | 0.090901 | negative favours real; pointwise descriptive |
| B2_real | B2_shuffled | 12 | 24 | 12 | 0.019086 | -0.071644 | 0.109816 | negative favours real; pointwise descriptive |
| B2_real | B2_shuffled | total_12 | 24 | 12 | 0.039115 | -0.370993 | 0.449223 | negative favours real; pointwise descriptive |

## Target months after battery eligibility

July-September 2025 target months are separately described and remain IN all primary scores. Grouping uses target month, not forecast origin. These are monthly losses, not partial twelve-month totals. Available origin/horizon cell counts are reported; no additional p-values.

| model | period | group | mae | mase | rmse | mean_signed_error | origin_horizon_cells | unique_target_months | unique_origins |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| B2_no_graph | other_test_targets | all | 3.139564 | 0.952565 | 6.744900 | -0.686509 | 282 | 32 | 24 |
| B2_no_graph | other_test_targets | high | 6.720418 | 0.692753 | 11.251370 | -2.016429 | 282 | 32 | 24 |
| B2_no_graph | other_test_targets | low | 0.648559 | 1.373667 | 1.016728 | 0.134091 | 282 | 32 | 24 |
| B2_no_graph | other_test_targets | medium | 2.049714 | 0.791276 | 2.975559 | -0.177188 | 282 | 32 | 24 |
| B2_no_graph | post_eligibility_JulSep2025 | all | 3.180707 | 0.950910 | 6.669671 | 1.341962 | 6 | 3 | 3 |
| B2_no_graph | post_eligibility_JulSep2025 | high | 6.884018 | 0.709696 | 11.161470 | 2.871582 | 6 | 3 | 3 |
| B2_no_graph | post_eligibility_JulSep2025 | low | 0.624517 | 1.356921 | 0.810304 | 0.302830 | 6 | 3 | 3 |
| B2_no_graph | post_eligibility_JulSep2025 | medium | 2.033585 | 0.786114 | 2.866794 | 0.851473 | 6 | 3 | 3 |
| B2_real | other_test_targets | all | 3.127271 | 0.945546 | 6.713060 | -0.746534 | 282 | 32 | 24 |
| B2_real | other_test_targets | high | 6.694494 | 0.689549 | 11.194168 | -2.128523 | 282 | 32 | 24 |
| B2_real | other_test_targets | low | 0.647905 | 1.359876 | 1.016690 | 0.140826 | 282 | 32 | 24 |
| B2_real | other_test_targets | medium | 2.039414 | 0.787214 | 2.975307 | -0.251905 | 282 | 32 | 24 |
| B2_real | post_eligibility_JulSep2025 | all | 3.029799 | 0.922344 | 6.473598 | 1.047045 | 6 | 3 | 3 |
| B2_real | post_eligibility_JulSep2025 | high | 6.516538 | 0.673761 | 10.829211 | 2.178909 | 6 | 3 | 3 |
| B2_real | post_eligibility_JulSep2025 | low | 0.608603 | 1.332113 | 0.796069 | 0.282829 | 6 | 3 | 3 |
| B2_real | post_eligibility_JulSep2025 | medium | 1.964254 | 0.761159 | 2.795868 | 0.679397 | 6 | 3 | 3 |
| B2_shuffled | other_test_targets | all | 3.130447 | 0.959045 | 6.719453 | -0.731613 | 282 | 32 | 24 |
| B2_shuffled | other_test_targets | high | 6.698626 | 0.690665 | 11.204866 | -2.085279 | 282 | 32 | 24 |
| B2_shuffled | other_test_targets | low | 0.653703 | 1.399681 | 1.017197 | 0.147289 | 282 | 32 | 24 |
| B2_shuffled | other_test_targets | medium | 2.039010 | 0.786789 | 2.978159 | -0.256851 | 282 | 32 | 24 |
| B2_shuffled | post_eligibility_JulSep2025 | all | 3.048936 | 0.955993 | 6.387916 | 1.112631 | 6 | 3 | 3 |
| B2_shuffled | post_eligibility_JulSep2025 | high | 6.587576 | 0.682291 | 10.676685 | 2.437406 | 6 | 3 | 3 |
| B2_shuffled | post_eligibility_JulSep2025 | low | 0.612833 | 1.433932 | 0.790896 | 0.273580 | 6 | 3 | 3 |
| B2_shuffled | post_eligibility_JulSep2025 | medium | 1.946400 | 0.751756 | 2.792726 | 0.626909 | 6 | 3 | 3 |
| B2_without_base | other_test_targets | all | 3.139672 | 0.948554 | 6.315343 | 0.224835 | 282 | 32 | 24 |
| B2_without_base | other_test_targets | high | 6.731788 | 0.697279 | 10.482912 | 0.617572 | 282 | 32 | 24 |
| B2_without_base | other_test_targets | low | 0.641357 | 1.358887 | 1.018428 | 0.106973 | 282 | 32 | 24 |
| B2_without_base | other_test_targets | medium | 2.045871 | 0.789496 | 2.953307 | -0.050041 | 282 | 32 | 24 |
| B2_without_base | post_eligibility_JulSep2025 | all | 3.489418 | 0.966603 | 7.039413 | 1.986735 | 6 | 3 | 3 |
| B2_without_base | post_eligibility_JulSep2025 | high | 7.838940 | 0.793524 | 11.824836 | 4.933653 | 6 | 3 | 3 |
| B2_without_base | post_eligibility_JulSep2025 | low | 0.593357 | 1.326869 | 0.782066 | 0.234868 | 6 | 3 | 3 |
| B2_without_base | post_eligibility_JulSep2025 | medium | 2.035957 | 0.779415 | 2.867339 | 0.791682 | 6 | 3 | 3 |
| combination | other_test_targets | all | 3.123917 | 0.953825 | 6.212935 | 0.496936 | 282 | 32 | 24 |
| combination | other_test_targets | high | 6.579556 | 0.688552 | 10.294258 | 0.811371 | 282 | 32 | 24 |
| combination | other_test_targets | low | 0.652308 | 1.348676 | 1.016349 | 0.154801 | 282 | 32 | 24 |
| combination | other_test_targets | medium | 2.139888 | 0.824246 | 2.965966 | 0.524637 | 282 | 32 | 24 |
| combination | post_eligibility_JulSep2025 | all | 3.712257 | 1.009961 | 7.076899 | 2.575179 | 6 | 3 | 3 |
| combination | post_eligibility_JulSep2025 | high | 8.115999 | 0.841326 | 11.801941 | 5.812427 | 6 | 3 | 3 |
| combination | post_eligibility_JulSep2025 | low | 0.616565 | 1.274566 | 0.814631 | 0.300503 | 6 | 3 | 3 |
| combination | post_eligibility_JulSep2025 | medium | 2.404208 | 0.913990 | 3.209058 | 1.612606 | 6 | 3 | 3 |
| combination_no_graph_sensitivity | other_test_targets | all | 3.136193 | 0.956527 | 6.238650 | 0.510428 | 282 | 32 | 24 |
| combination_no_graph_sensitivity | other_test_targets | high | 6.609278 | 0.691806 | 10.338809 | 0.844096 | 282 | 32 | 24 |
| combination_no_graph_sensitivity | other_test_targets | low | 0.652166 | 1.350981 | 1.016538 | 0.149373 | 282 | 32 | 24 |
| combination_no_graph_sensitivity | other_test_targets | medium | 2.147134 | 0.826794 | 2.972865 | 0.537815 | 282 | 32 | 24 |
| combination_no_graph_sensitivity | post_eligibility_JulSep2025 | all | 3.776842 | 1.019633 | 7.179917 | 2.659629 | 6 | 3 | 3 |
| combination_no_graph_sensitivity | post_eligibility_JulSep2025 | high | 8.286976 | 0.858189 | 11.981163 | 6.032459 | 6 | 3 | 3 |
| combination_no_graph_sensitivity | post_eligibility_JulSep2025 | low | 0.619888 | 1.279840 | 0.817695 | 0.304900 | 6 | 3 | 3 |
| combination_no_graph_sensitivity | post_eligibility_JulSep2025 | medium | 2.423662 | 0.920869 | 3.230593 | 1.641529 | 6 | 3 | 3 |
| gradient_boosting_neighbours | other_test_targets | all | 3.319978 | 0.988163 | 6.453030 | 1.111806 | 282 | 32 | 24 |
| gradient_boosting_neighbours | other_test_targets | high | 7.088256 | 0.746639 | 10.708640 | 2.438996 | 282 | 32 | 24 |
| gradient_boosting_neighbours | other_test_targets | low | 0.660606 | 1.369132 | 1.024162 | 0.170162 | 282 | 32 | 24 |
| gradient_boosting_neighbours | other_test_targets | medium | 2.211071 | 0.848717 | 3.033301 | 0.726259 | 282 | 32 | 24 |
| gradient_boosting_neighbours | post_eligibility_JulSep2025 | all | 4.141658 | 1.059675 | 7.876787 | 3.203530 | 6 | 3 | 3 |
| gradient_boosting_neighbours | post_eligibility_JulSep2025 | high | 9.279508 | 0.963964 | 13.199324 | 7.503955 | 6 | 3 | 3 |
| gradient_boosting_neighbours | post_eligibility_JulSep2025 | low | 0.619818 | 1.259229 | 0.826084 | 0.305483 | 6 | 3 | 3 |
| gradient_boosting_neighbours | post_eligibility_JulSep2025 | medium | 2.525647 | 0.955830 | 3.350639 | 1.801153 | 6 | 3 | 3 |
| gradient_boosting_own | other_test_targets | all | 3.340021 | 1.033389 | 6.466182 | 1.213823 | 282 | 32 | 24 |
| gradient_boosting_own | other_test_targets | high | 7.135596 | 0.750026 | 10.732046 | 2.744403 | 282 | 32 | 24 |
| gradient_boosting_own | other_test_targets | low | 0.681793 | 1.503777 | 1.043626 | 0.200683 | 282 | 32 | 24 |
| gradient_boosting_own | other_test_targets | medium | 2.202673 | 0.846364 | 3.027966 | 0.696384 | 282 | 32 | 24 |
| gradient_boosting_own | post_eligibility_JulSep2025 | all | 4.206359 | 1.107855 | 8.004428 | 3.270245 | 6 | 3 | 3 |
| gradient_boosting_own | post_eligibility_JulSep2025 | high | 9.445892 | 0.975133 | 13.423587 | 7.685330 | 6 | 3 | 3 |
| gradient_boosting_own | post_eligibility_JulSep2025 | low | 0.645033 | 1.391648 | 0.849837 | 0.339700 | 6 | 3 | 3 |
| gradient_boosting_own | post_eligibility_JulSep2025 | medium | 2.528153 | 0.956785 | 3.361206 | 1.785703 | 6 | 3 | 3 |

## Interpretation limits

Only 24 overlapping forecast origins and three fixed seeds. Revised CER data and certificate reporting lag remain limitations. Aggregate prediction differences cannot identify individual behaviour. A non-rejection is not proof of equivalence. No test result may change weights, epochs, configurations, chain order or selected primary model. No further computation or model change is initiated by this report.

Numeric tables and figure CSVs are retained beside this report/output root. Protocol authority: reports/protocol/protocol_v7_final_test.md and configs/protocol_v7_test.json at protocol-v7-test.
