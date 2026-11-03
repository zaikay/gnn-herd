# B2 seed ensembles and learned combinations

3 November 2026. **Descriptive and exploratory, validation only.** B2 review accepted by the researcher. No model fits, GPU operations or final-test access. Validation origins November 2018 to October 2021; targets through October 2022 only.

## Accepted B2 findings

- B2 real has the lowest MAE at horizon 1 (not significant) but trails both boosting baselines from horizon 6, with growing overprediction at longer horizons.
- With per-area scaling, the graph adds no forecast value: no graph matches or beats real except at horizon 1, and real does not beat shuffled. The learned graph was excluded at the screen. The full-validation real/shuffled point scores differ, but no predeclared adjusted comparison is significant.
- Removing installed base worsens MAE and MASE at every reported outcome (minimum Holm p 0.056), consistent with the original B.

## Definitions and comparisons

Each B2 seed ensemble averages the three saved forecasts per origin/area/horizon **before** scoring. It is one forecast, not an average of three scores. Individual tables retain each seed's score and mean/SD/min/max. Ensemble tables have no seed SD: they contain one forecast. MAE/RMSE units are systems per area/month or per twelve-month window; MASE uses the unchanged training-only seasonal scales/fallback and twelve times the monthly denominator for total. Maturity groups remain origin-dependent. Float64 is used for means and new combinations; existing individual float32 total-sum conventions are preserved.

Learned combinations follow [the existing rules](../protocol/learned_weight_rules.md) unchanged: w times neighbour boosting plus (1-w) times B2, convex raw-MAE weights per maturity tercile and bands 1-3/4-6/7-12. One shared weight pools seeds 11/29/47; never optimise separately per seed. For the B2-ensemble variant, each boosting seed is paired with the SAME B2 mean forecast. For the individual variant, the matching B2 seed is used. Each variant therefore has three boosting-seed-paired combination forecasts. Their average is additionally scored as a single forecast ensemble. This preserves the pooled-seed objective; no weight is reoptimised against a mean forecast instead.

Only earlier origins and targets observed by the current origin enter expanding weights, including partially observed bands. Historical maturity remains attached to the historical origin. Three eligible prior origins are required; otherwise w=0.5. Warm-up origins remain scored. Exact weighted-median optimisation uses [0,1], choosing the minimiser nearest 0.5 on flat optima. Earlier learned-B combination forecasts are reused unchanged; they are not re-estimated. Both individual-seed and seed-mean boosting/earlier-combination references are shown, so the comparison basis is explicit. This adds no DM family and establishes no final-test protocol.

## Descriptive summary

The combination using B2 ensemble inputs, averaged across its three boosting-seed pairs, has MAE 3.143633, 3.917040, 4.470569, 30.789967 at horizons 1, 6, 12 and total. It improves on the B2 real ensemble at all four outcomes. Against both boosting forecast ensembles, it is lower at horizons 1 and 6 and total, but higher at horizon 12. The total advantage over own-lag boosting is small. The matched-individual-B2 combination forecast average is shown separately; no variant is selected or proposed for the final test here.

The added bias diagnostic qualifies the accepted review shorthand about growing overprediction. Across all 36 origins, B2 real ensemble signed error is +0.019646, +0.451603, -0.162291 systems/area/month at horizons 1, 6 and 12. Overprediction is time-dependent, not a uniform monotonic horizon effect: earlier underprediction offsets large overpredictions at later forecast origins. The origin-year table and full heatmaps below retain both signs. No causal explanation is inferred.

## Ensemble scores beside individual-seed scores

Full monthly/total/maturity scores and every individual seed are linked below. The following tables use horizons 1, 6, 12 and total for readability.

### Each seed alongside its forecast ensemble

[Every horizon/total and maturity group: 832 rows](../../data/explore/t03/b2_ensemble_combination/ensemble_vs_seeds.csv). The following comparison uses all areas and the four reported outcomes. Members 11, 29 and 47 are individual forecasts; member ensemble is their arithmetic forecast average, scored once.

| condition | forecast_type | member | outcome | group | mae | mase | rmse |
| --- | --- | --- | --- | --- | --- | --- | --- |
| B2_no_graph | forecast_ensemble | ensemble | 1 | all | 3.184224 | 0.977202 | 7.077407 |
| B2_no_graph | individual_seed | 11 | 1 | all | 3.224229 | 0.989770 | 7.212089 |
| B2_no_graph | individual_seed | 29 | 1 | all | 3.245495 | 0.978478 | 7.215175 |
| B2_no_graph | individual_seed | 47 | 1 | all | 3.224432 | 0.979103 | 7.162663 |
| B2_no_graph | forecast_ensemble | ensemble | 12 | all | 4.650685 | 1.258783 | 10.878351 |
| B2_no_graph | individual_seed | 11 | 12 | all | 4.696083 | 1.277882 | 11.090278 |
| B2_no_graph | individual_seed | 29 | 12 | all | 4.747518 | 1.279876 | 10.985358 |
| B2_no_graph | individual_seed | 47 | 12 | all | 4.624761 | 1.233321 | 10.884652 |
| B2_no_graph | forecast_ensemble | ensemble | 6 | all | 3.932429 | 1.105758 | 9.076483 |
| B2_no_graph | individual_seed | 11 | 6 | all | 4.062541 | 1.134985 | 9.326851 |
| B2_no_graph | individual_seed | 29 | 6 | all | 3.905275 | 1.106654 | 8.941673 |
| B2_no_graph | individual_seed | 47 | 6 | all | 3.948123 | 1.090893 | 9.286687 |
| B2_no_graph | forecast_ensemble | ensemble | total_12 | all | 31.147586 | 0.634708 | 76.993000 |
| B2_no_graph | individual_seed | 11 | total_12 | all | 32.351578 | 0.659029 | 79.684317 |
| B2_no_graph | individual_seed | 29 | total_12 | all | 31.105973 | 0.639494 | 76.113917 |
| B2_no_graph | individual_seed | 47 | total_12 | all | 31.004921 | 0.621485 | 77.503552 |
| B2_real | forecast_ensemble | ensemble | 1 | all | 3.178828 | 0.978393 | 7.116547 |
| B2_real | individual_seed | 11 | 1 | all | 3.212237 | 0.994209 | 7.246624 |
| B2_real | individual_seed | 29 | 1 | all | 3.219742 | 0.972793 | 7.202223 |
| B2_real | individual_seed | 47 | 1 | all | 3.225911 | 0.982963 | 7.215014 |
| B2_real | forecast_ensemble | ensemble | 12 | all | 4.694560 | 1.264677 | 11.062596 |
| B2_real | individual_seed | 11 | 12 | all | 4.746764 | 1.305558 | 11.172069 |
| B2_real | individual_seed | 29 | 12 | all | 4.779300 | 1.248932 | 11.203354 |
| B2_real | individual_seed | 47 | 12 | all | 4.673094 | 1.255762 | 11.099358 |
| B2_real | forecast_ensemble | ensemble | 6 | all | 4.074617 | 1.135143 | 9.381202 |
| B2_real | individual_seed | 11 | 6 | all | 4.120913 | 1.165533 | 9.445609 |
| B2_real | individual_seed | 29 | 6 | all | 4.177035 | 1.131603 | 9.550926 |
| B2_real | individual_seed | 47 | 6 | all | 4.071901 | 1.127130 | 9.583913 |
| B2_real | forecast_ensemble | ensemble | total_12 | all | 32.472620 | 0.653960 | 81.254647 |
| B2_real | individual_seed | 11 | total_12 | all | 33.185072 | 0.686621 | 82.395681 |
| B2_real | individual_seed | 29 | total_12 | all | 33.082264 | 0.649307 | 81.768786 |
| B2_real | individual_seed | 47 | total_12 | all | 32.008317 | 0.641991 | 81.759103 |
| B2_shuffled | forecast_ensemble | ensemble | 1 | all | 3.184378 | 0.995734 | 7.091169 |
| B2_shuffled | individual_seed | 11 | 1 | all | 3.255858 | 1.016355 | 7.272452 |
| B2_shuffled | individual_seed | 29 | 1 | all | 3.256469 | 0.994080 | 7.328486 |
| B2_shuffled | individual_seed | 47 | 1 | all | 3.230075 | 1.000263 | 7.129568 |
| B2_shuffled | forecast_ensemble | ensemble | 12 | all | 4.751824 | 1.342499 | 10.923438 |
| B2_shuffled | individual_seed | 11 | 12 | all | 4.847632 | 1.397058 | 11.189225 |
| B2_shuffled | individual_seed | 29 | 12 | all | 4.810307 | 1.334040 | 11.071549 |
| B2_shuffled | individual_seed | 47 | 12 | all | 4.839581 | 1.334659 | 11.112566 |
| B2_shuffled | forecast_ensemble | ensemble | 6 | all | 4.064546 | 1.176691 | 9.276221 |
| B2_shuffled | individual_seed | 11 | 6 | all | 4.179457 | 1.216986 | 9.597066 |
| B2_shuffled | individual_seed | 29 | 6 | all | 4.090027 | 1.176416 | 9.335895 |
| B2_shuffled | individual_seed | 47 | 6 | all | 4.141418 | 1.169359 | 9.410313 |
| B2_shuffled | forecast_ensemble | ensemble | total_12 | all | 32.414196 | 0.698930 | 79.618743 |
| B2_shuffled | individual_seed | 11 | total_12 | all | 33.653306 | 0.744908 | 82.255391 |
| B2_shuffled | individual_seed | 29 | total_12 | all | 32.912595 | 0.697228 | 80.963318 |
| B2_shuffled | individual_seed | 47 | total_12 | all | 33.528974 | 0.700842 | 81.446322 |
| B2_without_base | forecast_ensemble | ensemble | 1 | all | 3.304231 | 0.986202 | 7.550407 |
| B2_without_base | individual_seed | 11 | 1 | all | 3.388170 | 0.993454 | 7.798673 |
| B2_without_base | individual_seed | 29 | 1 | all | 3.438298 | 1.003487 | 7.828685 |
| B2_without_base | individual_seed | 47 | 1 | all | 3.294870 | 0.986970 | 7.580976 |
| B2_without_base | forecast_ensemble | ensemble | 12 | all | 4.868148 | 1.266170 | 11.742083 |
| B2_without_base | individual_seed | 11 | 12 | all | 4.810714 | 1.258617 | 11.687874 |
| B2_without_base | individual_seed | 29 | 12 | all | 5.112553 | 1.299883 | 12.220345 |
| B2_without_base | individual_seed | 47 | 12 | all | 4.897148 | 1.270481 | 11.806977 |
| B2_without_base | forecast_ensemble | ensemble | 6 | all | 4.351575 | 1.136197 | 10.533362 |
| B2_without_base | individual_seed | 11 | 6 | all | 4.453120 | 1.143444 | 10.806173 |
| B2_without_base | individual_seed | 29 | 6 | all | 4.470945 | 1.161068 | 10.692643 |
| B2_without_base | individual_seed | 47 | 6 | all | 4.343366 | 1.131608 | 10.630405 |
| B2_without_base | forecast_ensemble | ensemble | total_12 | all | 35.801208 | 0.660649 | 94.021864 |
| B2_without_base | individual_seed | 11 | total_12 | all | 36.100512 | 0.661220 | 96.086569 |
| B2_without_base | individual_seed | 29 | total_12 | all | 37.036731 | 0.683443 | 94.928037 |
| B2_without_base | individual_seed | 47 | total_12 | all | 35.999616 | 0.663166 | 94.485052 |

### all maturity: single forecast ensembles

| model | outcome | mae | mase | rmse | mean_signed_error |
| --- | --- | --- | --- | --- | --- |
| B2_no_graph_ensemble | 1 | 3.184224 | 0.977202 | 7.077407 | -0.029651 |
| B2_no_graph_ensemble | 12 | 4.650685 | 1.258783 | 10.878351 | -0.227465 |
| B2_no_graph_ensemble | 6 | 3.932429 | 1.105758 | 9.076483 | 0.050731 |
| B2_no_graph_ensemble | total_12 | 31.147586 | 0.634708 | 76.993000 | 0.499009 |
| B2_real_ensemble | 1 | 3.178828 | 0.978393 | 7.116547 | 0.019646 |
| B2_real_ensemble | 12 | 4.694560 | 1.264677 | 11.062596 | -0.162291 |
| B2_real_ensemble | 6 | 4.074617 | 1.135143 | 9.381202 | 0.451603 |
| B2_real_ensemble | total_12 | 32.472620 | 0.653960 | 81.254647 | 3.152688 |
| B2_shuffled_ensemble | 1 | 3.184378 | 0.995734 | 7.091169 | 0.015706 |
| B2_shuffled_ensemble | 12 | 4.751824 | 1.342499 | 10.923438 | 0.290604 |
| B2_shuffled_ensemble | 6 | 4.064546 | 1.176691 | 9.276221 | 0.511197 |
| B2_shuffled_ensemble | total_12 | 32.414196 | 0.698930 | 79.618743 | 5.078502 |
| B2_without_base_ensemble | 1 | 3.304231 | 0.986202 | 7.550407 | -0.069248 |
| B2_without_base_ensemble | 12 | 4.868148 | 1.266170 | 11.742083 | -0.752330 |
| B2_without_base_ensemble | 6 | 4.351575 | 1.136197 | 10.533362 | -0.089557 |
| B2_without_base_ensemble | total_12 | 35.801208 | 0.660649 | 94.021864 | -1.815434 |
| earlier_learned_B_ensemble | 1 | 3.219142 | 1.001079 | 7.506202 | -0.031755 |
| earlier_learned_B_ensemble | 12 | 4.443289 | 1.190950 | 10.396948 | -0.041610 |
| earlier_learned_B_ensemble | 6 | 3.955739 | 1.116171 | 9.379862 | 0.058388 |
| earlier_learned_B_ensemble | total_12 | 31.213834 | 0.620155 | 80.090487 | 0.029980 |
| gradient_boosting_neighbours_ensemble | 1 | 3.231582 | 1.008528 | 7.494483 | 0.001605 |
| gradient_boosting_neighbours_ensemble | 12 | 4.431376 | 1.198251 | 10.272937 | -0.102867 |
| gradient_boosting_neighbours_ensemble | 6 | 3.948055 | 1.118047 | 9.330545 | 0.085334 |
| gradient_boosting_neighbours_ensemble | total_12 | 31.041908 | 0.626090 | 78.784131 | 0.097786 |
| gradient_boosting_own_ensemble | 1 | 3.249231 | 1.053722 | 7.478334 | 0.013117 |
| gradient_boosting_own_ensemble | 12 | 4.428632 | 1.273807 | 10.167379 | -0.123931 |
| gradient_boosting_own_ensemble | 6 | 3.957506 | 1.169741 | 9.272501 | 0.087182 |
| gradient_boosting_own_ensemble | total_12 | 30.811300 | 0.680041 | 76.807527 | -0.088395 |
| learned_B2_ensemble_forecast_ensemble | 1 | 3.143633 | 0.972983 | 7.090864 | 0.008738 |
| learned_B2_ensemble_forecast_ensemble | 12 | 4.470569 | 1.213990 | 10.367119 | -0.130160 |
| learned_B2_ensemble_forecast_ensemble | 6 | 3.917040 | 1.115114 | 9.088502 | 0.262471 |
| learned_B2_ensemble_forecast_ensemble | total_12 | 30.789967 | 0.623096 | 77.060915 | 1.449314 |
| learned_B2_individual_forecast_ensemble | 1 | 3.145068 | 0.973294 | 7.107799 | 0.008791 |
| learned_B2_individual_forecast_ensemble | 12 | 4.468522 | 1.212954 | 10.357296 | -0.134390 |
| learned_B2_individual_forecast_ensemble | 6 | 3.911124 | 1.114081 | 9.086500 | 0.241868 |
| learned_B2_individual_forecast_ensemble | total_12 | 30.751871 | 0.622205 | 77.006515 | 1.320930 |

### all maturity: individual seed means and spread

| model | outcome | mae | mae_seed_sd | mase | mase_seed_sd | rmse | rmse_seed_sd |
| --- | --- | --- | --- | --- | --- | --- | --- |
| B2_no_graph | 1 | 3.231385 | 0.012220 | 0.982450 | 0.006346 | 7.196683 | 0.029468 |
| B2_no_graph | 12 | 4.689454 | 0.061646 | 1.263693 | 0.026322 | 10.987084 | 0.102820 |
| B2_no_graph | 6 | 3.971980 | 0.081302 | 1.110844 | 0.022343 | 9.186697 | 0.211743 |
| B2_no_graph | total_12 | 31.487491 | 0.750026 | 0.640003 | 0.018777 | 77.781145 | 1.799749 |
| B2_real | 1 | 3.219297 | 0.006848 | 0.983321 | 0.010713 | 7.221311 | 0.022855 |
| B2_real | 12 | 4.733052 | 0.054415 | 1.270084 | 0.030911 | 11.158345 | 0.053356 |
| B2_real | 6 | 4.123283 | 0.052607 | 1.141422 | 0.021000 | 9.526999 | 0.072235 |
| B2_real | total_12 | 32.758551 | 0.651752 | 0.659306 | 0.023936 | 81.975064 | 0.364765 |
| B2_shuffled | 1 | 3.247467 | 0.015066 | 1.003566 | 0.011499 | 7.243986 | 0.102570 |
| B2_shuffled | 12 | 4.832507 | 0.019642 | 1.355252 | 0.036206 | 11.124553 | 0.059731 |
| B2_shuffled | 6 | 4.136967 | 0.044881 | 1.187587 | 0.025704 | 9.448397 | 0.134551 |
| B2_shuffled | total_12 | 33.364958 | 0.396660 | 0.714326 | 0.026546 | 81.556752 | 0.652858 |
| B2_without_base | 1 | 3.373779 | 0.072789 | 0.994637 | 0.008322 | 7.736899 | 0.135186 |
| B2_without_base | 12 | 4.940139 | 0.155444 | 1.276327 | 0.021245 | 11.907252 | 0.279459 |
| B2_without_base | 6 | 4.422477 | 0.069090 | 1.145373 | 0.014824 | 10.709987 | 0.089123 |
| B2_without_base | total_12 | 36.378953 | 0.571882 | 0.669276 | 0.012307 | 95.168948 | 0.826971 |
| earlier_learned_B | 1 | 3.228369 | 0.004703 | 1.001813 | 0.003841 | 7.547487 | 0.060603 |
| earlier_learned_B | 12 | 4.449180 | 0.015193 | 1.191753 | 0.004104 | 10.428069 | 0.045434 |
| earlier_learned_B | 6 | 3.962544 | 0.006145 | 1.116781 | 0.003293 | 9.412885 | 0.041976 |
| earlier_learned_B | total_12 | 31.298642 | 0.117872 | 0.621076 | 0.002351 | 80.519375 | 0.409973 |
| gradient_boosting_neighbours | 1 | 3.240554 | 0.007218 | 1.009142 | 0.000562 | 7.542176 | 0.059252 |
| gradient_boosting_neighbours | 12 | 4.436481 | 0.003678 | 1.198639 | 0.000931 | 10.305286 | 0.016457 |
| gradient_boosting_neighbours | 6 | 3.954436 | 0.005485 | 1.118497 | 0.000230 | 9.365410 | 0.046755 |
| gradient_boosting_neighbours | total_12 | 31.118270 | 0.026271 | 0.626576 | 0.000438 | 79.241504 | 0.289208 |
| gradient_boosting_own | 1 | 3.256133 | 0.007532 | 1.054212 | 0.000717 | 7.509802 | 0.075904 |
| gradient_boosting_own | 12 | 4.433081 | 0.002229 | 1.274145 | 0.000483 | 10.188115 | 0.007306 |
| gradient_boosting_own | 6 | 3.961972 | 0.006813 | 1.170082 | 0.000614 | 9.293712 | 0.033041 |
| gradient_boosting_own | total_12 | 30.866269 | 0.046997 | 0.680405 | 0.000553 | 77.106792 | 0.140563 |
| learned_B2_ensemble | 1 | 3.145794 | 0.003286 | 0.973150 | 0.000154 | 7.100814 | 0.024648 |
| learned_B2_ensemble | 12 | 4.472400 | 0.001677 | 1.214152 | 0.000481 | 10.377301 | 0.011270 |
| learned_B2_ensemble | 6 | 3.918923 | 0.002200 | 1.115245 | 0.000189 | 9.097749 | 0.020240 |
| learned_B2_ensemble | total_12 | 30.809576 | 0.006011 | 0.623238 | 0.000192 | 77.187822 | 0.119978 |
| learned_B2_individual | 1 | 3.159238 | 0.007863 | 0.974904 | 0.010503 | 7.147830 | 0.027910 |
| learned_B2_individual | 12 | 4.476255 | 0.028000 | 1.213817 | 0.009032 | 10.385062 | 0.045764 |
| learned_B2_individual | 6 | 3.924774 | 0.010885 | 1.115623 | 0.013462 | 9.127936 | 0.063847 |
| learned_B2_individual | total_12 | 30.825903 | 0.187902 | 0.623379 | 0.009798 | 77.292004 | 0.178101 |

### low maturity: single forecast ensembles

| model | outcome | mae | mase | rmse | mean_signed_error |
| --- | --- | --- | --- | --- | --- |
| B2_no_graph_ensemble | 1 | 0.649801 | 1.415860 | 1.132213 | 0.003163 |
| B2_no_graph_ensemble | 12 | 0.713408 | 1.766919 | 1.424224 | 0.030722 |
| B2_no_graph_ensemble | 6 | 0.686485 | 1.554192 | 1.350027 | 0.003829 |
| B2_no_graph_ensemble | total_12 | 3.688524 | 0.826297 | 7.333479 | 0.105569 |
| B2_real_ensemble | 1 | 0.657236 | 1.427495 | 1.129385 | 0.048230 |
| B2_real_ensemble | 12 | 0.736079 | 1.786612 | 1.426912 | 0.105606 |
| B2_real_ensemble | 6 | 0.709248 | 1.600284 | 1.352480 | 0.089082 |
| B2_real_ensemble | total_12 | 3.973946 | 0.865602 | 7.405496 | 1.053745 |
| B2_shuffled_ensemble | 1 | 0.668647 | 1.472716 | 1.134199 | 0.070938 |
| B2_shuffled_ensemble | 12 | 0.791526 | 1.990837 | 1.445853 | 0.220219 |
| B2_shuffled_ensemble | 6 | 0.742340 | 1.723311 | 1.359110 | 0.161805 |
| B2_shuffled_ensemble | total_12 | 4.427662 | 0.998702 | 7.616575 | 1.984469 |
| B2_without_base_ensemble | 1 | 0.651162 | 1.408145 | 1.130617 | 0.016863 |
| B2_without_base_ensemble | 12 | 0.719965 | 1.757301 | 1.424360 | 0.037452 |
| B2_without_base_ensemble | 6 | 0.690425 | 1.529468 | 1.352995 | 0.016372 |
| B2_without_base_ensemble | total_12 | 3.773980 | 0.813537 | 7.395124 | 0.251930 |
| earlier_learned_B_ensemble | 1 | 0.668154 | 1.502908 | 1.121982 | 0.077712 |
| earlier_learned_B_ensemble | 12 | 0.730842 | 1.668306 | 1.399373 | 0.111503 |
| earlier_learned_B_ensemble | 6 | 0.706635 | 1.602462 | 1.316616 | 0.084638 |
| earlier_learned_B_ensemble | total_12 | 3.879639 | 0.834271 | 6.796039 | 1.076920 |
| gradient_boosting_neighbours_ensemble | 1 | 0.669201 | 1.522714 | 1.123555 | 0.077541 |
| gradient_boosting_neighbours_ensemble | 12 | 0.729101 | 1.691769 | 1.408497 | 0.098600 |
| gradient_boosting_neighbours_ensemble | 6 | 0.705755 | 1.608674 | 1.317485 | 0.080270 |
| gradient_boosting_neighbours_ensemble | total_12 | 3.888301 | 0.850992 | 6.868632 | 0.986435 |
| gradient_boosting_own_ensemble | 1 | 0.693366 | 1.647016 | 1.136680 | 0.118588 |
| gradient_boosting_own_ensemble | 12 | 0.774554 | 1.911391 | 1.431536 | 0.179125 |
| gradient_boosting_own_ensemble | 6 | 0.736334 | 1.755122 | 1.342396 | 0.132569 |
| gradient_boosting_own_ensemble | total_12 | 4.317597 | 1.015792 | 7.121790 | 1.683357 |
| learned_B2_ensemble_forecast_ensemble | 1 | 0.657551 | 1.432527 | 1.128831 | 0.049506 |
| learned_B2_ensemble_forecast_ensemble | 12 | 0.727564 | 1.718481 | 1.411434 | 0.096809 |
| learned_B2_ensemble_forecast_ensemble | 6 | 0.705994 | 1.600324 | 1.339338 | 0.087665 |
| learned_B2_ensemble_forecast_ensemble | total_12 | 3.844528 | 0.835944 | 7.014509 | 0.968947 |
| learned_B2_individual_forecast_ensemble | 1 | 0.657597 | 1.433704 | 1.128588 | 0.049863 |
| learned_B2_individual_forecast_ensemble | 12 | 0.727412 | 1.716282 | 1.411530 | 0.096286 |
| learned_B2_individual_forecast_ensemble | 6 | 0.705529 | 1.599617 | 1.336956 | 0.087023 |
| learned_B2_individual_forecast_ensemble | total_12 | 3.840628 | 0.835137 | 7.001772 | 0.964259 |

### low maturity: individual seed means and spread

| model | outcome | mae | mae_seed_sd | mase | mase_seed_sd | rmse | rmse_seed_sd |
| --- | --- | --- | --- | --- | --- | --- | --- |
| B2_no_graph | 1 | 0.650463 | 0.004998 | 1.416558 | 0.020269 | 1.133542 | 0.001073 |
| B2_no_graph | 12 | 0.714366 | 0.005598 | 1.767882 | 0.058422 | 1.425626 | 0.000988 |
| B2_no_graph | 6 | 0.687406 | 0.009379 | 1.555475 | 0.049168 | 1.351404 | 0.002321 |
| B2_no_graph | total_12 | 3.705035 | 0.075675 | 0.831195 | 0.039963 | 7.351154 | 0.042052 |
| B2_real | 1 | 0.658197 | 0.006057 | 1.428549 | 0.034362 | 1.131224 | 0.002017 |
| B2_real | 12 | 0.737438 | 0.008894 | 1.788132 | 0.092099 | 1.429120 | 0.002505 |
| B2_real | 6 | 0.710434 | 0.008983 | 1.601615 | 0.062658 | 1.354398 | 0.002166 |
| B2_real | total_12 | 3.999011 | 0.117950 | 0.871596 | 0.060513 | 7.434697 | 0.064243 |
| B2_shuffled | 1 | 0.670266 | 0.006833 | 1.474525 | 0.031922 | 1.137016 | 0.001926 |
| B2_shuffled | 12 | 0.796182 | 0.007559 | 1.996415 | 0.099243 | 1.453039 | 0.006800 |
| B2_shuffled | 6 | 0.745810 | 0.008477 | 1.727734 | 0.063458 | 1.364524 | 0.002937 |
| B2_shuffled | total_12 | 4.503043 | 0.102684 | 1.010621 | 0.068231 | 7.721826 | 0.067128 |
| B2_without_base | 1 | 0.652571 | 0.002189 | 1.409650 | 0.005721 | 1.133261 | 0.002820 |
| B2_without_base | 12 | 0.721952 | 0.002825 | 1.759403 | 0.010315 | 1.427261 | 0.001681 |
| B2_without_base | 6 | 0.692456 | 0.007340 | 1.531654 | 0.021757 | 1.356073 | 0.002905 |
| B2_without_base | total_12 | 3.810161 | 0.053997 | 0.819841 | 0.015391 | 7.433818 | 0.032244 |
| earlier_learned_B | 1 | 0.668274 | 0.003614 | 1.503041 | 0.010396 | 1.122277 | 0.001485 |
| earlier_learned_B | 12 | 0.731216 | 0.002463 | 1.668720 | 0.013757 | 1.399999 | 0.000912 |
| earlier_learned_B | 6 | 0.706810 | 0.002265 | 1.602651 | 0.009603 | 1.316964 | 0.001522 |
| earlier_learned_B | total_12 | 3.885073 | 0.020584 | 0.834994 | 0.008287 | 6.803530 | 0.017044 |
| gradient_boosting_neighbours | 1 | 0.669236 | 0.000327 | 1.522775 | 0.001178 | 1.123627 | 0.000132 |
| gradient_boosting_neighbours | 12 | 0.729146 | 0.000347 | 1.691817 | 0.002010 | 1.408581 | 0.000644 |
| gradient_boosting_neighbours | 6 | 0.705782 | 0.000147 | 1.608706 | 0.001501 | 1.317585 | 0.001404 |
| gradient_boosting_neighbours | total_12 | 3.889148 | 0.001581 | 0.851100 | 0.000930 | 6.869953 | 0.005201 |
| gradient_boosting_own | 1 | 0.693392 | 0.000192 | 1.647050 | 0.000428 | 1.136751 | 0.000344 |
| gradient_boosting_own | 12 | 0.774594 | 0.000204 | 1.911445 | 0.000514 | 1.431625 | 0.000436 |
| gradient_boosting_own | 6 | 0.736364 | 0.000518 | 1.755160 | 0.000022 | 1.342536 | 0.000681 |
| gradient_boosting_own | total_12 | 4.318011 | 0.002326 | 1.015836 | 0.000532 | 7.122706 | 0.002854 |
| learned_B2_ensemble | 1 | 0.657552 | 0.000038 | 1.432528 | 0.000168 | 1.128832 | 0.000022 |
| learned_B2_ensemble | 12 | 0.727589 | 0.000154 | 1.718512 | 0.001057 | 1.411470 | 0.000330 |
| learned_B2_ensemble | 6 | 0.705998 | 0.000071 | 1.600329 | 0.000392 | 1.339350 | 0.000337 |
| learned_B2_ensemble | total_12 | 3.844732 | 0.000484 | 0.835966 | 0.000480 | 7.014762 | 0.001666 |
| learned_B2_individual | 1 | 0.658460 | 0.005415 | 1.434669 | 0.033143 | 1.130230 | 0.001812 |
| learned_B2_individual | 12 | 0.727590 | 0.002453 | 1.716478 | 0.027914 | 1.411854 | 0.001223 |
| learned_B2_individual | 6 | 0.706108 | 0.005707 | 1.600247 | 0.041128 | 1.337879 | 0.001758 |
| learned_B2_individual | total_12 | 3.848858 | 0.052346 | 0.836696 | 0.027306 | 7.011319 | 0.033292 |

### medium maturity: single forecast ensembles

| model | outcome | mae | mase | rmse | mean_signed_error |
| --- | --- | --- | --- | --- | --- |
| B2_no_graph_ensemble | 1 | 2.067216 | 0.812231 | 3.186454 | -0.201813 |
| B2_no_graph_ensemble | 12 | 2.511728 | 0.965212 | 4.252570 | -0.392223 |
| B2_no_graph_ensemble | 6 | 2.286659 | 0.887599 | 3.733264 | -0.290045 |
| B2_no_graph_ensemble | total_12 | 15.456788 | 0.485350 | 27.673929 | -3.415063 |
| B2_real_ensemble | 1 | 2.052289 | 0.808025 | 3.156683 | -0.083896 |
| B2_real_ensemble | 12 | 2.480060 | 0.956561 | 4.171583 | -0.274493 |
| B2_real_ensemble | 6 | 2.307633 | 0.896954 | 3.708030 | -0.007253 |
| B2_real_ensemble | total_12 | 15.158970 | 0.476908 | 27.015887 | -0.822300 |
| B2_shuffled_ensemble | 1 | 2.072134 | 0.814831 | 3.174793 | -0.052775 |
| B2_shuffled_ensemble | 12 | 2.551689 | 0.983835 | 4.192583 | -0.010977 |
| B2_shuffled_ensemble | 6 | 2.332591 | 0.906687 | 3.710436 | 0.094817 |
| B2_shuffled_ensemble | total_12 | 15.517487 | 0.488828 | 27.094524 | 0.796311 |
| B2_without_base_ensemble | 1 | 2.075270 | 0.815793 | 3.225798 | -0.172985 |
| B2_without_base_ensemble | 12 | 2.464566 | 0.947444 | 4.251368 | -0.673365 |
| B2_without_base_ensemble | 6 | 2.332408 | 0.902284 | 3.874284 | -0.339796 |
| B2_without_base_ensemble | total_12 | 15.427569 | 0.482074 | 28.802146 | -4.421177 |
| earlier_learned_B_ensemble | 1 | 2.036226 | 0.801176 | 3.077228 | -0.038519 |
| earlier_learned_B_ensemble | 12 | 2.405782 | 0.930013 | 3.791732 | 0.056514 |
| earlier_learned_B_ensemble | 6 | 2.248715 | 0.875090 | 3.510622 | 0.012600 |
| earlier_learned_B_ensemble | total_12 | 14.198415 | 0.445283 | 22.884522 | 0.122907 |
| gradient_boosting_neighbours_ensemble | 1 | 2.035292 | 0.800581 | 3.080223 | -0.068015 |
| gradient_boosting_neighbours_ensemble | 12 | 2.387957 | 0.923159 | 3.832336 | -0.104094 |
| gradient_boosting_neighbours_ensemble | 6 | 2.246561 | 0.874056 | 3.517774 | -0.015933 |
| gradient_boosting_neighbours_ensemble | total_12 | 14.214772 | 0.445592 | 23.242917 | -0.700693 |
| gradient_boosting_own_ensemble | 1 | 2.059064 | 0.810146 | 3.108052 | -0.009323 |
| gradient_boosting_own_ensemble | 12 | 2.415461 | 0.936090 | 3.827275 | -0.023460 |
| gradient_boosting_own_ensemble | 6 | 2.275755 | 0.886652 | 3.548372 | 0.043149 |
| gradient_boosting_own_ensemble | total_12 | 14.410430 | 0.454196 | 23.034148 | 0.044113 |
| learned_B2_ensemble_forecast_ensemble | 1 | 2.025892 | 0.797507 | 3.078055 | -0.071495 |
| learned_B2_ensemble_forecast_ensemble | 12 | 2.403753 | 0.928550 | 3.917363 | -0.185067 |
| learned_B2_ensemble_forecast_ensemble | 6 | 2.249434 | 0.875449 | 3.549532 | -0.019518 |
| learned_B2_ensemble_forecast_ensemble | total_12 | 14.311407 | 0.449135 | 24.036955 | -0.898600 |
| learned_B2_individual_forecast_ensemble | 1 | 2.026213 | 0.797581 | 3.077130 | -0.070488 |
| learned_B2_individual_forecast_ensemble | 12 | 2.403432 | 0.928451 | 3.914748 | -0.183231 |
| learned_B2_individual_forecast_ensemble | 6 | 2.247868 | 0.874841 | 3.545508 | -0.021797 |
| learned_B2_individual_forecast_ensemble | total_12 | 14.295503 | 0.448617 | 23.976316 | -0.897774 |

### medium maturity: individual seed means and spread

| model | outcome | mae | mae_seed_sd | mase | mase_seed_sd | rmse | rmse_seed_sd |
| --- | --- | --- | --- | --- | --- | --- | --- |
| B2_no_graph | 1 | 2.077793 | 0.004412 | 0.816044 | 0.001368 | 3.201715 | 0.008352 |
| B2_no_graph | 12 | 2.524427 | 0.026672 | 0.969922 | 0.009854 | 4.267993 | 0.015839 |
| B2_no_graph | 6 | 2.299250 | 0.016933 | 0.892071 | 0.006206 | 3.751136 | 0.049860 |
| B2_no_graph | total_12 | 15.592253 | 0.085730 | 0.489598 | 0.002747 | 27.840461 | 0.381285 |
| B2_real | 1 | 2.063215 | 0.004046 | 0.812033 | 0.001204 | 3.171866 | 0.011136 |
| B2_real | 12 | 2.494310 | 0.022779 | 0.961805 | 0.008592 | 4.188533 | 0.027079 |
| B2_real | 6 | 2.322658 | 0.023646 | 0.902408 | 0.009385 | 3.730103 | 0.014122 |
| B2_real | total_12 | 15.292654 | 0.335830 | 0.481163 | 0.011011 | 27.177228 | 0.205989 |
| B2_shuffled | 1 | 2.090352 | 0.006301 | 0.821388 | 0.002604 | 3.199599 | 0.012138 |
| B2_shuffled | 12 | 2.586301 | 0.008853 | 0.996636 | 0.002463 | 4.234332 | 0.054782 |
| B2_shuffled | 6 | 2.360765 | 0.018976 | 0.917011 | 0.006215 | 3.748018 | 0.049675 |
| B2_shuffled | total_12 | 15.981564 | 0.278952 | 0.503617 | 0.007865 | 27.613641 | 0.663628 |
| B2_without_base | 1 | 2.094539 | 0.022071 | 0.822635 | 0.008003 | 3.252745 | 0.018388 |
| B2_without_base | 12 | 2.492057 | 0.048471 | 0.957135 | 0.017074 | 4.281960 | 0.029920 |
| B2_without_base | 6 | 2.355474 | 0.025845 | 0.910635 | 0.009225 | 3.904490 | 0.010754 |
| B2_without_base | total_12 | 15.670989 | 0.301979 | 0.489573 | 0.008785 | 29.064942 | 0.132631 |
| earlier_learned_B | 1 | 2.037257 | 0.003428 | 0.801586 | 0.001575 | 3.078882 | 0.001555 |
| earlier_learned_B | 12 | 2.408184 | 0.011607 | 0.930987 | 0.004340 | 3.794974 | 0.006450 |
| earlier_learned_B | 6 | 2.249682 | 0.002080 | 0.875453 | 0.000658 | 3.512059 | 0.001543 |
| earlier_learned_B | total_12 | 14.220635 | 0.102089 | 0.446059 | 0.003198 | 22.915648 | 0.074084 |
| gradient_boosting_neighbours | 1 | 2.035803 | 0.000278 | 0.800762 | 0.000048 | 3.081380 | 0.001150 |
| gradient_boosting_neighbours | 12 | 2.388459 | 0.001329 | 0.923334 | 0.000487 | 3.833280 | 0.008636 |
| gradient_boosting_neighbours | 6 | 2.247032 | 0.001581 | 0.874218 | 0.000548 | 3.518911 | 0.002318 |
| gradient_boosting_neighbours | total_12 | 14.222212 | 0.012784 | 0.445815 | 0.000337 | 23.255112 | 0.063675 |
| gradient_boosting_own | 1 | 2.059580 | 0.001986 | 0.810321 | 0.000721 | 3.108866 | 0.003394 |
| gradient_boosting_own | 12 | 2.415790 | 0.001287 | 0.936209 | 0.000443 | 3.828124 | 0.004621 |
| gradient_boosting_own | 6 | 2.276109 | 0.001004 | 0.886775 | 0.000157 | 3.549353 | 0.003058 |
| gradient_boosting_own | total_12 | 14.415432 | 0.014659 | 0.454350 | 0.000346 | 23.042983 | 0.021843 |
| learned_B2_ensemble | 1 | 2.026188 | 0.000225 | 0.797614 | 0.000055 | 3.078592 | 0.001051 |
| learned_B2_ensemble | 12 | 2.404121 | 0.001060 | 0.928675 | 0.000401 | 3.918006 | 0.007899 |
| learned_B2_ensemble | 6 | 2.249636 | 0.001268 | 0.875521 | 0.000395 | 3.550009 | 0.001921 |
| learned_B2_ensemble | total_12 | 14.315303 | 0.010901 | 0.449253 | 0.000303 | 24.043435 | 0.055283 |
| learned_B2_individual | 1 | 2.027617 | 0.001062 | 0.798090 | 0.000257 | 3.079269 | 0.004368 |
| learned_B2_individual | 12 | 2.404789 | 0.004374 | 0.928940 | 0.001618 | 3.916515 | 0.006598 |
| learned_B2_individual | 6 | 2.250011 | 0.008478 | 0.875609 | 0.003292 | 3.548635 | 0.002056 |
| learned_B2_individual | total_12 | 14.311653 | 0.076809 | 0.449131 | 0.002514 | 23.996970 | 0.055045 |

### high maturity: single forecast ensembles

| model | outcome | mae | mase | rmse | mean_signed_error |
| --- | --- | --- | --- | --- | --- |
| B2_no_graph_ensemble | 1 | 6.835654 | 0.703515 | 11.782771 | 0.109698 |
| B2_no_graph_ensemble | 12 | 10.726919 | 1.044218 | 18.300349 | -0.320894 |
| B2_no_graph_ensemble | 6 | 8.824143 | 0.875482 | 15.211437 | 0.438408 |
| B2_no_graph_ensemble | total_12 | 74.297446 | 0.592477 | 130.246458 | 4.806523 |
| B2_real_ensemble | 1 | 6.826960 | 0.699657 | 11.861516 | 0.094605 |
| B2_real_ensemble | 12 | 10.867541 | 1.050860 | 18.646848 | -0.317988 |
| B2_real_ensemble | 6 | 9.206969 | 0.908189 | 15.762047 | 1.272979 |
| B2_real_ensemble | total_12 | 78.284943 | 0.619369 | 137.921186 | 9.226619 |
| B2_shuffled_ensemble | 1 | 6.812353 | 0.699656 | 11.810517 | 0.028954 |
| B2_shuffled_ensemble | 12 | 10.912255 | 1.052826 | 18.392831 | 0.662571 |
| B2_shuffled_ensemble | 6 | 9.118707 | 0.900074 | 15.573385 | 1.276969 |
| B2_shuffled_ensemble | total_12 | 77.297439 | 0.609259 | 135.001138 | 12.454725 |
| B2_without_base_ensemble | 1 | 7.186261 | 0.734667 | 12.623070 | -0.051622 |
| B2_without_base_ensemble | 12 | 11.419912 | 1.093765 | 19.837505 | -1.621077 |
| B2_without_base_ensemble | 6 | 10.031893 | 0.976839 | 17.776797 | 0.054751 |
| B2_without_base_ensemble | total_12 | 88.202075 | 0.686337 | 160.112715 | -1.277054 |
| earlier_learned_B_ensemble | 1 | 6.953047 | 0.699153 | 12.581773 | -0.134459 |
| earlier_learned_B_ensemble | 12 | 10.193242 | 0.974531 | 17.548621 | -0.292846 |
| earlier_learned_B_ensemble | 6 | 8.911866 | 0.870960 | 15.807830 | 0.077925 |
| earlier_learned_B_ensemble | total_12 | 75.563448 | 0.580911 | 136.651275 | -1.109886 |
| gradient_boosting_neighbours_ensemble | 1 | 6.990253 | 0.702288 | 12.559924 | -0.004712 |
| gradient_boosting_neighbours_ensemble | 12 | 10.177069 | 0.979824 | 17.318459 | -0.303108 |
| gradient_boosting_neighbours_ensemble | 6 | 8.891849 | 0.871411 | 15.718356 | 0.191664 |
| gradient_boosting_neighbours_ensemble | total_12 | 75.022650 | 0.581687 | 134.288520 | 0.007616 |
| gradient_boosting_own_ensemble | 1 | 6.995263 | 0.704004 | 12.522955 | -0.069915 |
| gradient_boosting_own_ensemble | 12 | 10.095880 | 0.973940 | 17.129782 | -0.527459 |
| gradient_boosting_own_ensemble | 6 | 8.860429 | 0.867449 | 15.605923 | 0.085829 |
| gradient_boosting_own_ensemble | total_12 | 73.705874 | 0.570135 | 130.831559 | -1.992656 |
| learned_B2_ensemble_forecast_ensemble | 1 | 6.747454 | 0.688915 | 11.836063 | 0.048204 |
| learned_B2_ensemble_forecast_ensemble | 12 | 10.280390 | 0.994938 | 17.466929 | -0.302223 |
| learned_B2_ensemble_forecast_ensemble | 6 | 8.795691 | 0.869568 | 15.277749 | 0.719265 |
| learned_B2_ensemble_forecast_ensemble | total_12 | 74.213968 | 0.584210 | 131.103682 | 4.277595 |
| learned_B2_individual_forecast_ensemble | 1 | 6.751396 | 0.688598 | 11.866760 | 0.046997 |
| learned_B2_individual_forecast_ensemble | 12 | 10.274722 | 0.994129 | 17.450016 | -0.316224 |
| learned_B2_individual_forecast_ensemble | 6 | 8.779976 | 0.867785 | 15.275318 | 0.660377 |
| learned_B2_individual_forecast_ensemble | total_12 | 74.119483 | 0.582861 | 131.019545 | 3.896303 |

### high maturity: individual seed means and spread

| model | outcome | mae | mae_seed_sd | mase | mase_seed_sd | rmse | rmse_seed_sd |
| --- | --- | --- | --- | --- | --- | --- | --- |
| B2_no_graph | 1 | 6.965900 | 0.037788 | 0.714749 | 0.001867 | 11.993366 | 0.050937 |
| B2_no_graph | 12 | 10.829569 | 0.154093 | 1.053275 | 0.014696 | 18.490534 | 0.179942 |
| B2_no_graph | 6 | 8.929282 | 0.219599 | 0.884987 | 0.020447 | 15.404185 | 0.369178 |
| B2_no_graph | total_12 | 75.165184 | 2.092271 | 0.599215 | 0.015863 | 131.607707 | 3.156229 |
| B2_real | 1 | 6.936477 | 0.021272 | 0.709383 | 0.001867 | 12.045812 | 0.041625 |
| B2_real | 12 | 10.967409 | 0.143100 | 1.060316 | 0.012651 | 18.813288 | 0.092521 |
| B2_real | 6 | 9.336757 | 0.140848 | 0.920243 | 0.014223 | 16.016961 | 0.130005 |
| B2_real | total_12 | 78.983988 | 1.582782 | 0.625160 | 0.014134 | 139.161263 | 0.603697 |
| B2_shuffled | 1 | 6.981784 | 0.053354 | 0.714785 | 0.003865 | 12.078732 | 0.182734 |
| B2_shuffled | 12 | 11.115037 | 0.053186 | 1.072705 | 0.009884 | 18.741029 | 0.093786 |
| B2_shuffled | 6 | 9.304326 | 0.109752 | 0.918016 | 0.012794 | 15.871579 | 0.229330 |
| B2_shuffled | total_12 | 79.610268 | 0.866970 | 0.628741 | 0.011607 | 138.319817 | 1.025975 |
| B2_without_base | 1 | 7.374228 | 0.198240 | 0.751626 | 0.017790 | 12.950451 | 0.237579 |
| B2_without_base | 12 | 11.606407 | 0.416034 | 1.112443 | 0.039667 | 20.124008 | 0.489515 |
| B2_without_base | 6 | 10.219501 | 0.176304 | 0.993831 | 0.016097 | 18.083902 | 0.159962 |
| B2_without_base | total_12 | 89.655709 | 1.368471 | 0.698415 | 0.013295 | 162.084402 | 1.474739 |
| earlier_learned_B | 1 | 6.979578 | 0.015607 | 0.700811 | 0.000296 | 12.655223 | 0.108328 |
| earlier_learned_B | 12 | 10.208139 | 0.056928 | 0.975552 | 0.004680 | 17.603183 | 0.081544 |
| earlier_learned_B | 6 | 8.931139 | 0.019577 | 0.872240 | 0.000802 | 15.866262 | 0.075030 |
| earlier_learned_B | total_12 | 75.790219 | 0.443731 | 0.582176 | 0.002513 | 137.399761 | 0.732314 |
| gradient_boosting_neighbours | 1 | 7.016623 | 0.021636 | 0.703889 | 0.000637 | 12.644992 | 0.105905 |
| gradient_boosting_neighbours | 12 | 10.191837 | 0.009680 | 0.980766 | 0.000925 | 17.375805 | 0.027367 |
| gradient_boosting_neighbours | 6 | 8.910495 | 0.017958 | 0.872568 | 0.001038 | 15.780177 | 0.083764 |
| gradient_boosting_neighbours | total_12 | 75.243451 | 0.068418 | 0.582812 | 0.000629 | 135.091271 | 0.503821 |
| gradient_boosting_own | 1 | 7.015428 | 0.020600 | 0.705266 | 0.001177 | 12.579115 | 0.135120 |
| gradient_boosting_own | 12 | 10.108860 | 0.006931 | 0.974782 | 0.000684 | 17.166507 | 0.013976 |
| gradient_boosting_own | 6 | 8.873443 | 0.020789 | 0.868310 | 0.001810 | 15.643494 | 0.058356 |
| gradient_boosting_own | total_12 | 73.865364 | 0.129433 | 0.571029 | 0.000915 | 131.356995 | 0.244071 |
| learned_B2_ensemble | 1 | 6.753642 | 0.009874 | 0.689308 | 0.000410 | 11.853805 | 0.044056 |
| learned_B2_ensemble | 12 | 10.285489 | 0.004006 | 0.995268 | 0.000419 | 17.484911 | 0.018393 |
| learned_B2_ensemble | 6 | 8.801134 | 0.007489 | 0.869885 | 0.000543 | 15.294140 | 0.036574 |
| learned_B2_ensemble | total_12 | 74.268692 | 0.007497 | 0.584496 | 0.000373 | 131.326257 | 0.212218 |
| learned_B2_individual | 1 | 6.791635 | 0.027629 | 0.691952 | 0.001425 | 11.937970 | 0.049807 |
| learned_B2_individual | 12 | 10.296385 | 0.081140 | 0.996035 | 0.007100 | 17.499031 | 0.080029 |
| learned_B2_individual | 6 | 8.818203 | 0.029007 | 0.871013 | 0.004184 | 15.348449 | 0.113515 |
| learned_B2_individual | total_12 | 74.317199 | 0.473315 | 0.584311 | 0.005052 | 131.518625 | 0.323992 |

## Weights over time and all 36 validation origins

The expanding [weight paths](../../data/explore/t03/b2_ensemble_combination/weights_over_time.png) / [plotted CSV](../../data/explore/t03/b2_ensemble_combination/weights_over_time.csv) show both variants by maturity and horizon band, with availability and warm-up ledger. Weight w is the share assigned to neighbour boosting; 1-w is assigned to B2. Dashed full-validation reference lines are descriptive only.

The following weights use **all 36 validation origins and their full twelve-month targets**, through October 2022 at the latest. They are in-sample descriptive estimates, not a leakage-free validation forecast, not the weights used for any reported expanding score, and not an approved final-test specification. No score is supplied for applying these weights retrospectively. [Full-validation figure](../../data/explore/t03/b2_ensemble_combination/all36_weights.png) / [CSV](../../data/explore/t03/b2_ensemble_combination/all36_weights.csv).

| variant | maturity | band | neighbour_weight | graph_weight | validation_origins | seed_pooled_cells | latest_target_used |
| --- | --- | --- | --- | --- | --- | --- | --- |
| B2_ensemble | low | 1-3 | 0.100818 | 0.899182 | 36 | 284472 | 2022-01 |
| B2_ensemble | low | 4-6 | 0.486487 | 0.513513 | 36 | 284472 | 2022-04 |
| B2_ensemble | low | 7-12 | 0.780161 | 0.219839 | 36 | 568944 | 2022-10 |
| B2_ensemble | medium | 1-3 | 0.687581 | 0.312419 | 36 | 284472 | 2022-01 |
| B2_ensemble | medium | 4-6 | 0.784779 | 0.215221 | 36 | 284472 | 2022-04 |
| B2_ensemble | medium | 7-12 | 0.831918 | 0.168082 | 36 | 568944 | 2022-10 |
| B2_ensemble | high | 1-3 | 0.492785 | 0.507215 | 36 | 284472 | 2022-01 |
| B2_ensemble | high | 4-6 | 0.659162 | 0.340838 | 36 | 284472 | 2022-04 |
| B2_ensemble | high | 7-12 | 0.682345 | 0.317655 | 36 | 568944 | 2022-10 |
| B2_individual | low | 1-3 | 0.178435 | 0.821565 | 36 | 284472 | 2022-01 |
| B2_individual | low | 4-6 | 0.529712 | 0.470288 | 36 | 284472 | 2022-04 |
| B2_individual | low | 7-12 | 0.798103 | 0.201897 | 36 | 568944 | 2022-10 |
| B2_individual | medium | 1-3 | 0.725397 | 0.274603 | 36 | 284472 | 2022-01 |
| B2_individual | medium | 4-6 | 0.815548 | 0.184452 | 36 | 284472 | 2022-04 |
| B2_individual | medium | 7-12 | 0.853405 | 0.146595 | 36 | 568944 | 2022-10 |
| B2_individual | high | 1-3 | 0.560211 | 0.439789 | 36 | 284472 | 2022-01 |
| B2_individual | high | 4-6 | 0.701622 | 0.298378 | 36 | 284472 | 2022-04 |
| B2_individual | high | 7-12 | 0.714386 | 0.285614 | 36 | 568944 | 2022-10 |

## Bias by forecast origin and horizon

Mean signed error is forecast minus actual, averaged over observed areas. The three main series are B2 real's seed ensemble and both boosting seed ensembles. Averaging signed errors over seeds is equivalent to using the mean forecast. Positive is overprediction. [Origin/horizon heatmaps](../../data/explore/t03/b2_ensemble_combination/bias_origin_horizon.png) / [CSV](../../data/explore/t03/b2_ensemble_combination/bias_origin_horizon.csv) include target month, mean forecast, mean actual and maturity group. [Horizon/maturity summary](../../data/explore/t03/b2_ensemble_combination/bias_horizon_maturity.png) / [CSV](../../data/explore/t03/b2_ensemble_combination/bias_horizon_maturity.csv). These localise error patterns, not causal drivers.

| model | maturity | horizon | mean_forecast | mean_actual | mean_signed_error |
| --- | --- | --- | --- | --- | --- |
| B2_real_ensemble | all | 1 | 10.788334 | 10.768687 | 0.019646 |
| B2_real_ensemble | all | 6 | 11.376147 | 10.924544 | 0.451603 |
| B2_real_ensemble | all | 12 | 10.991362 | 11.153653 | -0.162291 |
| gradient_boosting_neighbours_ensemble | all | 1 | 10.770292 | 10.768687 | 0.001605 |
| gradient_boosting_neighbours_ensemble | all | 6 | 11.009878 | 10.924544 | 0.085334 |
| gradient_boosting_neighbours_ensemble | all | 12 | 11.050786 | 11.153653 | -0.102867 |
| gradient_boosting_own_ensemble | all | 1 | 10.781804 | 10.768687 | 0.013117 |
| gradient_boosting_own_ensemble | all | 6 | 11.011727 | 10.924544 | 0.087182 |
| gradient_boosting_own_ensemble | all | 12 | 11.029722 | 11.153653 | -0.123931 |

Horizon-12 signed error by forecast-origin year (all areas, all available origins in that calendar year; descriptive grouping):

| model | origin_year | horizon | mean_forecast | mean_actual | mean_signed_error |
| --- | --- | --- | --- | --- | --- |
| B2_real_ensemble | 2018 | 12 | 7.753911 | 11.288155 | -3.534244 |
| B2_real_ensemble | 2019 | 12 | 8.448672 | 11.714977 | -3.266305 |
| B2_real_ensemble | 2020 | 12 | 12.466149 | 11.940711 | 0.525437 |
| B2_real_ensemble | 2021 | 12 | 12.920335 | 9.508694 | 3.411641 |
| gradient_boosting_neighbours_ensemble | 2018 | 12 | 8.464892 | 11.288155 | -2.823263 |
| gradient_boosting_neighbours_ensemble | 2019 | 12 | 8.924019 | 11.714977 | -2.790958 |
| gradient_boosting_neighbours_ensemble | 2020 | 12 | 11.768622 | 11.940711 | -0.172089 |
| gradient_boosting_neighbours_ensemble | 2021 | 12 | 13.258681 | 9.508694 | 3.749987 |
| gradient_boosting_own_ensemble | 2018 | 12 | 8.231734 | 11.288155 | -3.056421 |
| gradient_boosting_own_ensemble | 2019 | 12 | 8.916328 | 11.714977 | -2.798649 |
| gradient_boosting_own_ensemble | 2020 | 12 | 11.745205 | 11.940711 | -0.195506 |
| gradient_boosting_own_ensemble | 2021 | 12 | 13.266812 | 9.508694 | 3.758118 |

[All origin-year/horizon values](../../data/explore/t03/b2_ensemble_combination/bias_origin_year.csv).

Largest six horizon-12 overprediction origins (display selection only; all origins remain scored):

| model | origin | horizon | target_month | maturity | areas | mean_forecast | mean_actual | mean_signed_error |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| B2_real_ensemble | 2021-01 | 12 | 2022-01 | all | 2634 | 14.537049 | 6.608580 | 7.928469 |
| B2_real_ensemble | 2021-04 | 12 | 2022-04 | all | 2634 | 13.311866 | 8.077069 | 5.234797 |
| B2_real_ensemble | 2021-05 | 12 | 2022-05 | all | 2634 | 13.398849 | 8.895216 | 4.503632 |
| B2_real_ensemble | 2020-11 | 12 | 2021-11 | all | 2634 | 16.440736 | 12.140471 | 4.300265 |
| B2_real_ensemble | 2021-02 | 12 | 2022-02 | all | 2634 | 13.305629 | 9.409643 | 3.895986 |
| B2_real_ensemble | 2020-12 | 12 | 2021-12 | all | 2634 | 16.242962 | 12.476841 | 3.766121 |

## Outputs and verification

[All individual score rows](../../data/processed/t03_b2_ensemble_combination/individual_scores.csv), [individual seeds](../../data/processed/t03_b2_ensemble_combination/individual_seed.csv), [ensemble score rows](../../data/processed/t03_b2_ensemble_combination/ensemble_scores.csv), [ensemble origin losses](../../data/processed/t03_b2_ensemble_combination/ensemble_origin.csv.gz), [weight/availability ledger](../../data/explore/t03/b2_ensemble_combination/expanding_weights.csv), [combination error curves](../../data/explore/t03/b2_ensemble_combination/combination_errors.png) / [CSV](../../data/explore/t03/b2_ensemble_combination/combination_errors.csv), [B2 seed-average curves](../../data/explore/t03/b2_ensemble_combination/ensemble_errors.png) / [CSV](../../data/explore/t03/b2_ensemble_combination/ensemble_errors.csv), [index](../../data/explore/t03/b2_ensemble_combination/index.md). Private paper candidates and visual copies use the same values. Full verification and input/source hashes: [checks](t03_b2_ensemble_combination_checks.json).

Reproduced 312 existing B2/baseline pooled score rows and 156 earlier-B/reference rows. There are 648 expanding weight records (324 per variant), 18 all-validation weights and 5184 origin/horizon/maturity bias rows. All expanding latest-target dates are no later than their forecast origin; warm-ups remain included. Model/source/protocol/input hashes are retained. No model refits, GPU use or test forecasts/losses.

Generators: `evaluation.b2_ensemble_combination`, `visuals.b2_ensemble_combination`. Stop for researcher review; no further combination, architecture, weight selection or final-test work is initiated.

## Final verification

**164 tests passed**, one upstream warning; targeted eight tests passed. Source: `logs/t03_b2_ensemble_full_tests.log` and `logs/t03_b2_ensemble_targeted_tests.log`. Independent saved-output audit checked 936 pooled score rows, all derived ensemble/combination algebra, 648 expanding weights, 18 descriptive all-validation weights and 5,184 bias rows. Frozen rules/input hashes match; all artifact files are below 5 MB and report links resolve. [Verification JSON](t03_b2_ensemble_combination_verification.json); `evaluation.b2_ensemble_verify`, log `logs/t03_b2_ensemble_verification_complete.log`. No fits, GPU or final-test use.
