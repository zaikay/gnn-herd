# B validation — Gate C review

**Gate C accepted by the researcher on 1 November 2026.** All four B conditions are complete. No final-test access, refitting, new architecture search or estimated blending weights. This report concerns B, not the historical T-GCN. Internal `gnn_*` aliases in CSVs denote B real/shuffled/no graph/without installed base.

## Researcher acceptance findings (1 November 2026)

- B real beats B no graph on MAE at every reported outcome; Holm p < 0.05 at horizons 1 and 6.
- B real and B shuffled cannot be distinguished (all Holm p = 1). The graph gain is consistent with pooling information within states, not adjacency specifically; no causal mechanism is identified.
- Both boosting baselines beat B real on MAE at every reported outcome, but B real has lower MASE than own-lag boosting at every outcome, most clearly in low-maturity areas.
- Removing installed base worsens MASE at every outcome, most in low-maturity areas; the MAE tests are not significant.

## Real versus shuffled

The real-versus-shuffled finding is mixed across outcomes or metrics; inspect the outcome table.

| outcome | real_mae | shuffled_mae | real_minus_shuffled_mae_percent | real_mase | shuffled_mase | mae_direction | mase_direction | p_holm |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | 3.653635 | 3.664823 | -0.305289 | 0.983482 | 0.995899 | lower | lower | 1.000000 |
| 6 | 4.217250 | 4.227714 | -0.247505 | 1.115489 | 1.109515 | lower | higher | 1.000000 |
| 12 | 4.642173 | 4.663974 | -0.467438 | 1.178855 | 1.183468 | lower | lower | 1.000000 |
| total_12 | 35.284584 | 35.568231 | -0.797471 | 0.630839 | 0.640506 | lower | lower | 1.000000 |

Validation p-values are descriptive after architecture selection. No individual behaviour is identified. A lower Moran I does not imply lower prediction error.

## Metrics and seed spread

MAE is primary; MASE is unitless, using shared origin/fit-specific training seasonal scales and the existing pooled zero-scale fallback. RMSE roots pooled squared losses, not averaged seed RMSEs. Losses average areas, origins and seeds equally; scores are individual-seed losses, not an ensemble. Monthly units are systems/area/month; total units are systems/area/twelve-month window, with MASE scale multiplied by twelve. Maturity groups depend on installed base at each origin. Seven unknown areas are masked; isolates retained. All twelve monthly horizons, total and seed SD/min/max are in [scores](../../data/processed/t03_b_gate_c/scores.csv) and [per-seed scores](../../data/processed/t03_b_gate_c/seed_metrics.csv).

### Maturity: all

| model | outcome | mae | mae_seed_sd | mase | mase_seed_sd | rmse | rmse_seed_sd |
| --- | --- | --- | --- | --- | --- | --- | --- |
| gnn_no_base | 1 | 3.678089 | 0.021035 | 1.038841 | 0.002876 | 10.016965 | 0.049877 |
| gnn_no_base | 12 | 4.693218 | 0.047964 | 1.293440 | 0.034264 | 11.570709 | 0.087046 |
| gnn_no_base | 6 | 4.308810 | 0.025609 | 1.195299 | 0.018370 | 11.074111 | 0.072760 |
| gnn_no_base | total_12 | 36.224723 | 0.446178 | 0.719394 | 0.015608 | 106.658899 | 1.221076 |
| gnn_no_graph | 1 | 3.716506 | 0.036542 | 1.045328 | 0.035438 | 10.403251 | 0.104072 |
| gnn_no_graph | 12 | 4.727678 | 0.029320 | 1.347889 | 0.072461 | 11.873266 | 0.092264 |
| gnn_no_graph | 6 | 4.282964 | 0.022657 | 1.194480 | 0.051147 | 11.287853 | 0.029244 |
| gnn_no_graph | total_12 | 36.137568 | 0.416749 | 0.701617 | 0.042034 | 110.846867 | 1.008178 |
| gnn_real | 1 | 3.653635 | 0.036387 | 0.983482 | 0.028933 | 10.107133 | 0.060918 |
| gnn_real | 12 | 4.642173 | 0.020120 | 1.178855 | 0.010867 | 11.600262 | 0.085140 |
| gnn_real | 6 | 4.217250 | 0.033493 | 1.115489 | 0.012543 | 10.997935 | 0.024151 |
| gnn_real | total_12 | 35.284584 | 0.331149 | 0.630839 | 0.015196 | 106.807272 | 1.010904 |
| gnn_shuffled | 1 | 3.664823 | 0.035537 | 0.995899 | 0.022665 | 10.105997 | 0.065416 |
| gnn_shuffled | 12 | 4.663974 | 0.050505 | 1.183468 | 0.012130 | 11.688582 | 0.043185 |
| gnn_shuffled | 6 | 4.227714 | 0.045673 | 1.109515 | 0.009401 | 11.023539 | 0.033220 |
| gnn_shuffled | total_12 | 35.568231 | 0.671081 | 0.640506 | 0.017430 | 107.352067 | 0.774167 |
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
| gnn_no_base | 1 | 0.690614 | 0.008524 | 1.499643 | 0.020841 | 1.154569 | 0.006200 |
| gnn_no_base | 12 | 0.830062 | 0.032433 | 1.818142 | 0.086777 | 1.503104 | 0.026914 |
| gnn_no_base | 6 | 0.759929 | 0.018781 | 1.713844 | 0.054841 | 1.369041 | 0.009405 |
| gnn_no_base | total_12 | 4.892390 | 0.195788 | 0.977282 | 0.042882 | 7.906189 | 0.205907 |
| gnn_no_graph | 1 | 0.681114 | 0.017829 | 1.545067 | 0.101660 | 1.138004 | 0.009032 |
| gnn_no_graph | 12 | 0.755277 | 0.029773 | 2.038280 | 0.237320 | 1.414517 | 0.008459 |
| gnn_no_graph | 6 | 0.736484 | 0.028470 | 1.771319 | 0.173418 | 1.341384 | 0.009421 |
| gnn_no_graph | total_12 | 4.112772 | 0.248127 | 0.999948 | 0.148817 | 6.982884 | 0.171157 |
| gnn_real | 1 | 0.669171 | 0.025617 | 1.358069 | 0.063920 | 1.140096 | 0.010106 |
| gnn_real | 12 | 0.749614 | 0.008600 | 1.544362 | 0.043638 | 1.421042 | 0.001874 |
| gnn_real | 6 | 0.734195 | 0.006476 | 1.532720 | 0.062691 | 1.347653 | 0.004045 |
| gnn_real | total_12 | 4.242877 | 0.149868 | 0.779824 | 0.045276 | 7.160394 | 0.099121 |
| gnn_shuffled | 1 | 0.673508 | 0.013978 | 1.387573 | 0.047318 | 1.148659 | 0.007163 |
| gnn_shuffled | 12 | 0.748086 | 0.004089 | 1.552913 | 0.043588 | 1.425653 | 0.003093 |
| gnn_shuffled | 6 | 0.722897 | 0.012362 | 1.509835 | 0.049401 | 1.352231 | 0.005007 |
| gnn_shuffled | total_12 | 4.339565 | 0.041953 | 0.796907 | 0.041176 | 7.322430 | 0.043238 |
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
| gnn_no_base | 1 | 2.155640 | 0.013711 | 0.849639 | 0.003824 | 3.209976 | 0.017102 |
| gnn_no_base | 12 | 2.691034 | 0.046323 | 1.050956 | 0.018896 | 4.038575 | 0.049169 |
| gnn_no_base | 6 | 2.412510 | 0.007213 | 0.942706 | 0.001797 | 3.680126 | 0.013666 |
| gnn_no_base | total_12 | 16.876629 | 0.246050 | 0.542707 | 0.006318 | 25.830564 | 0.429920 |
| gnn_no_graph | 1 | 2.095806 | 0.031795 | 0.824398 | 0.013644 | 3.138630 | 0.022595 |
| gnn_no_graph | 12 | 2.517470 | 0.038103 | 0.972223 | 0.013171 | 3.862357 | 0.048865 |
| gnn_no_graph | 6 | 2.303530 | 0.031599 | 0.897308 | 0.010644 | 3.551135 | 0.035773 |
| gnn_no_graph | total_12 | 14.835376 | 0.480321 | 0.467261 | 0.014723 | 23.288517 | 0.563162 |
| gnn_real | 1 | 2.112850 | 0.039535 | 0.832267 | 0.016810 | 3.163820 | 0.018568 |
| gnn_real | 12 | 2.517553 | 0.046594 | 0.974709 | 0.017264 | 3.873258 | 0.049086 |
| gnn_real | 6 | 2.328341 | 0.042958 | 0.907808 | 0.015241 | 3.588602 | 0.042182 |
| gnn_real | total_12 | 15.376453 | 0.653760 | 0.488495 | 0.021155 | 23.977755 | 0.698931 |
| gnn_shuffled | 1 | 2.131326 | 0.041597 | 0.838602 | 0.016930 | 3.182116 | 0.018185 |
| gnn_shuffled | 12 | 2.526009 | 0.047455 | 0.977886 | 0.016537 | 3.895475 | 0.061640 |
| gnn_shuffled | 6 | 2.333520 | 0.037051 | 0.909553 | 0.012501 | 3.598855 | 0.043260 |
| gnn_shuffled | total_12 | 15.661485 | 0.746502 | 0.497482 | 0.023665 | 24.304273 | 0.909191 |
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
| gnn_no_base | 1 | 8.188013 | 0.059539 | 0.767241 | 0.008881 | 17.011226 | 0.088112 |
| gnn_no_base | 12 | 10.558557 | 0.078903 | 1.011223 | 0.011363 | 19.572290 | 0.144248 |
| gnn_no_base | 6 | 9.753990 | 0.063571 | 0.929348 | 0.005589 | 18.774723 | 0.128281 |
| gnn_no_base | total_12 | 86.905150 | 1.079904 | 0.638194 | 0.008301 | 182.752937 | 2.118246 |
| gnn_no_graph | 1 | 8.372598 | 0.067021 | 0.766520 | 0.008991 | 17.706972 | 0.183039 |
| gnn_no_graph | 12 | 10.910287 | 0.106820 | 1.033163 | 0.011840 | 20.149557 | 0.170966 |
| gnn_no_graph | 6 | 9.808879 | 0.053320 | 0.914813 | 0.011135 | 19.179077 | 0.055934 |
| gnn_no_graph | total_12 | 89.464556 | 1.399762 | 0.637642 | 0.011524 | 190.446759 | 1.814487 |
| gnn_real | 1 | 8.178883 | 0.046084 | 0.760110 | 0.010531 | 17.180012 | 0.109340 |
| gnn_real | 12 | 10.659352 | 0.081031 | 1.017492 | 0.010687 | 19.664098 | 0.159954 |
| gnn_real | 6 | 9.589216 | 0.065062 | 0.905941 | 0.014747 | 18.659300 | 0.049324 |
| gnn_real | total_12 | 86.234423 | 1.092744 | 0.624199 | 0.012693 | 183.295325 | 1.852761 |
| gnn_shuffled | 1 | 8.189635 | 0.057838 | 0.761522 | 0.011598 | 17.174058 | 0.119087 |
| gnn_shuffled | 12 | 10.717827 | 0.127231 | 1.019604 | 0.019873 | 19.815691 | 0.084399 |
| gnn_shuffled | 6 | 9.626726 | 0.110780 | 0.909156 | 0.015841 | 18.702272 | 0.062428 |
| gnn_shuffled | total_12 | 86.703641 | 1.616846 | 0.627128 | 0.019729 | 184.198489 | 1.442658 |
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

## Predeclared DM/Holm family

Exactly 20 two-sided MAE-loss tests: B real against no graph, shuffled, both frozen boosting baselines and the included ablation; horizons 1, 6, 12 and total. Origin-level area losses are averaged over the fixed three seeds before DM. HLN/Bartlett h−1 correction; total h=12. One Holm adjustment over all 20 tests, retaining undefined-test slots. No RMSE/MASE test family.

| model_a | model_b | outcome | h | origins | statistic | p_raw | status | family_size | p_holm |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| gnn_real | gnn_no_graph | 1 | 1 | 36 | -8.690249 | 2.91844e-10 | defined | 20 | 5.54504e-09 |
| gnn_real | gnn_no_graph | 6 | 6 | 36 | -4.244650 | 0.000152967 | defined | 20 | 0.00260044 |
| gnn_real | gnn_no_graph | 12 | 12 | 36 | -2.761653 | 0.00909828 | defined | 20 | 0.145573 |
| gnn_real | gnn_no_graph | total_12 | 12 | 36 | -2.400645 | 0.021817 | defined | 20 | 0.28362 |
| gnn_real | gnn_shuffled | 1 | 1 | 36 | -1.567948 | 0.125891 | defined | 20 | 1 |
| gnn_real | gnn_shuffled | 6 | 6 | 36 | -0.631749 | 0.531656 | defined | 20 | 1 |
| gnn_real | gnn_shuffled | 12 | 12 | 36 | -1.065620 | 0.293892 | defined | 20 | 1 |
| gnn_real | gnn_shuffled | total_12 | 12 | 36 | -0.764974 | 0.449415 | defined | 20 | 1 |
| gnn_real | gradient_boosting_own | 1 | 1 | 36 | 8.084076 | 1.61553e-09 | defined | 20 | 2.90796e-08 |
| gnn_real | gradient_boosting_own | 6 | 6 | 36 | 2.574451 | 0.0144291 | defined | 20 | 0.216436 |
| gnn_real | gradient_boosting_own | 12 | 12 | 36 | 1.416757 | 0.165394 | defined | 20 | 1 |
| gnn_real | gradient_boosting_own | total_12 | 12 | 36 | 2.439967 | 0.0198945 | defined | 20 | 0.278524 |
| gnn_real | gradient_boosting_neighbours | 1 | 1 | 36 | 8.921330 | 1.53829e-10 | defined | 20 | 3.07658e-09 |
| gnn_real | gradient_boosting_neighbours | 6 | 6 | 36 | 2.229422 | 0.0323011 | defined | 20 | 0.387614 |
| gnn_real | gradient_boosting_neighbours | 12 | 12 | 36 | 1.340601 | 0.188687 | defined | 20 | 1 |
| gnn_real | gradient_boosting_neighbours | total_12 | 12 | 36 | 2.127679 | 0.0404833 | defined | 20 | 0.445317 |
| gnn_real | gnn_no_base | 1 | 1 | 36 | -0.971079 | 0.338172 | defined | 20 | 1 |
| gnn_real | gnn_no_base | 6 | 6 | 36 | -1.175783 | 0.247618 | defined | 20 | 1 |
| gnn_real | gnn_no_base | 12 | 12 | 36 | -0.534330 | 0.596491 | defined | 20 | 1 |
| gnn_real | gnn_no_base | total_12 | 12 | 36 | -0.679208 | 0.501473 | defined | 20 | 1 |

## Spatial diagnostics and figures

[Error horizons](../../visuals/t03/b_validation/gnn_error_horizon.png), [totals](../../visuals/t03/b_validation/gnn_error_total.png), [maturity](../../visuals/t03/b_validation/gnn_error_maturity.png), [real/control comparisons](../../visuals/t03/b_validation/gnn_graph_comparison.png), [scaled errors](../../data/explore/t03/b_validation/gnn_scaled_error_map.png), [real minus shuffled](../../data/explore/t03/b_validation/gnn_real_minus_shuffled_map.png), [Moran I](../../data/explore/t03/b_validation/gnn_error_moran.png). Every figure has a plotted CSV. Maps retain extremes using log/symmetric-log scales; unknown areas are missing, not zero error. Row-standardised rook Moran I includes observed isolates with zero rows; no permutation significance or dwelling normalisation. [Numeric tables/index](../../data/processed/t03_b_gate_c/index.md).

## Limitations and stop

Retrospective revised CER data, 36 overlapping validation origins and three fixed seeds. The B architecture was selected on two of these origins; its gate evidence is development evidence. The late battery-scheme test-month limitation remains for the sealed test, which has not been evaluated. Screen anchor fits are reused only where exact model/data/training identity holds. No further fitting follows this report. Gate C accepted on 1 November 2026; no final-test run is authorised by this report.

Generators: `models.b_validation`, `evaluation.b_gate_c`, `visuals.b_gate_c`; protocol-v4-b-validation. Frozen baseline selections unchanged; exploratory equal-weight anchor combinations are outside this family.
