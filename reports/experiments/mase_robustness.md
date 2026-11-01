# MASE robustness — 1 November 2026

CPU-only, no model refits. Saved validation predictions, 36 origins and matched seeds 11/29/47; final test untouched. Aggregation definitions are explicit below. The learned expanding combination follows the concrete rules in reports/protocol/learned_weight_rules.md and is included when its saved validation forecasts are present.

Raw seasonal scale uses January 2011 through each scheduled fit origin. `mase_without_fallback` excludes only area/origin pairs with zero raw seasonal scale from this diagnostic; it does not remove data from any model or the accepted evaluation. Coverage below records all such pairs. No epsilon or replacement denominator is introduced.

Median scaled error is the within-origin/group median of per-area absolute scaled error, then an equal-origin and equal-seed average. Report both with the accepted fallback denominator and without fallback areas. This is explicitly an average of per-origin medians, not a median of per-area origin-mean errors. Mean-level-scaled error averages absolute error divided by each area's own mean target count from January 2011 through fit origin. Zero training means are undefined and excluded from that diagnostic with coverage reported, never changed to one. Total errors use twelve times each monthly denominator. Maturity groups remain origin-dependent. Seed SD is computed after origin aggregation.

These diagnostic filters affect metrics only, not panel membership or training. They are exploratory robustness views, not new confirmatory tests. The full monthly horizons and groups are in [summary](../../data/explore/t03/mase_robustness/summary.csv), [seeds](../../data/explore/t03/mase_robustness/seed_metrics.csv) and [coverage](../../data/explore/t03/mase_robustness/coverage.csv).

## all maturity

| model | outcome | mase_without_fallback | median_scaled_error_without_fallback | median_scaled_error_with_fallback | mean_level_scaled_error |
| --- | --- | --- | --- | --- | --- |
| gnn_no_base | 1 | 1.040994 | 0.722813 | 0.721100 | 1.177933 |
| gnn_no_base | 12 | 1.296149 | 0.892881 | 0.890735 | 1.449233 |
| gnn_no_base | 6 | 1.197785 | 0.833720 | 0.831679 | 1.351574 |
| gnn_no_base | total_12 | 0.720874 | 0.471416 | 0.470193 | 0.794574 |
| gnn_no_graph | 1 | 1.047490 | 0.730731 | 0.729248 | 1.188113 |
| gnn_no_graph | 12 | 1.350652 | 0.861615 | 0.859945 | 1.553250 |
| gnn_no_graph | 6 | 1.196941 | 0.835094 | 0.833421 | 1.360569 |
| gnn_no_graph | total_12 | 0.703038 | 0.430574 | 0.429525 | 0.784353 |
| gnn_real | 1 | 0.985538 | 0.710765 | 0.709235 | 1.092292 |
| gnn_real | 12 | 1.181354 | 0.857098 | 0.855337 | 1.283134 |
| gnn_real | 6 | 1.117824 | 0.833523 | 0.831817 | 1.237104 |
| gnn_real | total_12 | 0.632144 | 0.438827 | 0.437756 | 0.669394 |
| gnn_shuffled | 1 | 0.997972 | 0.717224 | 0.715724 | 1.105395 |
| gnn_shuffled | 12 | 1.185974 | 0.861972 | 0.860199 | 1.282331 |
| gnn_shuffled | 6 | 1.111841 | 0.819479 | 0.817679 | 1.218301 |
| gnn_shuffled | total_12 | 0.641832 | 0.447930 | 0.446784 | 0.675878 |
| gradient_boosting_neighbours | 1 | 1.011208 | 0.706574 | 0.704976 | 1.163215 |
| gradient_boosting_neighbours | 12 | 1.201131 | 0.844791 | 0.842965 | 1.345546 |
| gradient_boosting_neighbours | 6 | 1.120800 | 0.789360 | 0.787626 | 1.262822 |
| gradient_boosting_neighbours | total_12 | 0.627845 | 0.403069 | 0.402031 | 0.692773 |
| gradient_boosting_own | 1 | 1.056365 | 0.720564 | 0.718872 | 1.231469 |
| gradient_boosting_own | 12 | 1.276776 | 0.868789 | 0.866868 | 1.465140 |
| gradient_boosting_own | 6 | 1.172481 | 0.807342 | 0.805458 | 1.342411 |
| gradient_boosting_own | total_12 | 0.681774 | 0.418365 | 0.417332 | 0.780517 |
| half_neighbour_B | 1 | 0.985365 | 0.706698 | 0.705169 | 1.118680 |
| half_neighbour_B | 12 | 1.177349 | 0.849792 | 0.847912 | 1.304036 |
| half_neighbour_B | 6 | 1.108683 | 0.808276 | 0.806560 | 1.242402 |
| half_neighbour_B | total_12 | 0.610199 | 0.410712 | 0.409734 | 0.661825 |
| half_own_B | 1 | 1.008451 | 0.717229 | 0.715658 | 1.152568 |
| half_own_B | 12 | 1.215579 | 0.868102 | 0.866145 | 1.363626 |
| half_own_B | 6 | 1.134059 | 0.819988 | 0.818339 | 1.281442 |
| half_own_B | total_12 | 0.634859 | 0.419750 | 0.418685 | 0.701630 |
| learned_neighbour_B | 1 | 1.003868 | 0.707091 | 0.705441 | 1.152280 |
| learned_neighbour_B | 12 | 1.194234 | 0.848043 | 0.846489 | 1.334586 |
| learned_neighbour_B | 6 | 1.119082 | 0.792354 | 0.790481 | 1.260525 |
| learned_neighbour_B | total_12 | 0.622337 | 0.405754 | 0.404801 | 0.684567 |
| seasonal_naive | 1 | 1.103063 | 0.713662 | 0.711448 | 1.127358 |
| seasonal_naive | 12 | 1.192673 | 0.755983 | 0.753177 | 1.239691 |
| seasonal_naive | 6 | 1.147667 | 0.742110 | 0.739989 | 1.173124 |
| seasonal_naive | total_12 | 0.572297 | 0.398958 | 0.398030 | 0.589200 |

## low maturity

| model | outcome | mase_without_fallback | median_scaled_error_without_fallback | median_scaled_error_with_fallback | mean_level_scaled_error |
| --- | --- | --- | --- | --- | --- |
| gnn_no_base | 1 | 1.509171 | 0.940857 | 0.934820 | 2.345080 |
| gnn_no_base | 12 | 1.829812 | 1.095212 | 1.087745 | 2.832660 |
| gnn_no_base | 6 | 1.724808 | 1.068553 | 1.062116 | 2.688896 |
| gnn_no_base | total_12 | 0.983507 | 0.545186 | 0.540420 | 1.540881 |
| gnn_no_graph | 1 | 1.554916 | 0.921879 | 0.917668 | 2.400232 |
| gnn_no_graph | 12 | 2.051216 | 0.976957 | 0.971418 | 3.207513 |
| gnn_no_graph | 6 | 1.782641 | 1.020440 | 1.016468 | 2.765773 |
| gnn_no_graph | total_12 | 1.006298 | 0.465765 | 0.462328 | 1.579905 |
| gnn_real | 1 | 1.366745 | 0.873134 | 0.868632 | 2.107467 |
| gnn_real | 12 | 1.554388 | 0.980402 | 0.975586 | 2.398716 |
| gnn_real | 6 | 1.542554 | 1.023521 | 1.019604 | 2.389097 |
| gnn_real | total_12 | 0.784827 | 0.483889 | 0.480040 | 1.222102 |
| gnn_shuffled | 1 | 1.396407 | 0.898460 | 0.893248 | 2.140007 |
| gnn_shuffled | 12 | 1.562950 | 0.997072 | 0.991808 | 2.391988 |
| gnn_shuffled | 6 | 1.519548 | 0.999369 | 0.995304 | 2.328631 |
| gnn_shuffled | total_12 | 0.802016 | 0.496671 | 0.493241 | 1.230760 |
| gradient_boosting_neighbours | 1 | 1.532352 | 0.938304 | 0.933072 | 2.377637 |
| gradient_boosting_neighbours | 12 | 1.702574 | 1.013905 | 1.008642 | 2.650370 |
| gradient_boosting_neighbours | 6 | 1.618894 | 0.973815 | 0.969075 | 2.513447 |
| gradient_boosting_neighbours | total_12 | 0.856445 | 0.436906 | 0.433490 | 1.349215 |
| gradient_boosting_own | 1 | 1.657407 | 0.992945 | 0.988105 | 2.573189 |
| gradient_boosting_own | 12 | 1.923569 | 1.101797 | 1.096310 | 3.000440 |
| gradient_boosting_own | 6 | 1.766259 | 1.037941 | 1.032553 | 2.743276 |
| gradient_boosting_own | total_12 | 1.022193 | 0.492307 | 0.488129 | 1.610487 |
| half_neighbour_B | 1 | 1.444733 | 0.913856 | 0.909580 | 2.236551 |
| half_neighbour_B | 12 | 1.621218 | 1.010313 | 1.005384 | 2.515528 |
| half_neighbour_B | 6 | 1.575655 | 1.004370 | 0.999422 | 2.444953 |
| half_neighbour_B | total_12 | 0.797501 | 0.451567 | 0.447860 | 1.251527 |
| half_own_B | 1 | 1.505882 | 0.949437 | 0.944810 | 2.332077 |
| half_own_B | 12 | 1.730534 | 1.063976 | 1.058737 | 2.688910 |
| half_own_B | 6 | 1.648001 | 1.041059 | 1.036189 | 2.558141 |
| half_own_B | total_12 | 0.873046 | 0.482053 | 0.478150 | 1.370360 |
| learned_neighbour_B | 1 | 1.512506 | 0.934512 | 0.929804 | 2.345344 |
| learned_neighbour_B | 12 | 1.679322 | 1.016898 | 1.011806 | 2.615053 |
| learned_neighbour_B | 6 | 1.612799 | 0.976628 | 0.971706 | 2.505747 |
| learned_neighbour_B | total_12 | 0.840233 | 0.440513 | 0.437238 | 1.325446 |
| seasonal_naive | 1 | 1.270197 | 0.071733 | 0.056172 | 1.867734 |
| seasonal_naive | 12 | 1.409681 | 0.104399 | 0.086425 | 2.104488 |
| seasonal_naive | 6 | 1.331559 | 0.112264 | 0.076968 | 1.952825 |
| seasonal_naive | total_12 | 0.659233 | 0.376075 | 0.372081 | 1.000145 |

## medium maturity

| model | outcome | mase_without_fallback | median_scaled_error_without_fallback | median_scaled_error_with_fallback | mean_level_scaled_error |
| --- | --- | --- | --- | --- | --- |
| gnn_no_base | 1 | 0.849639 | 0.673212 | 0.673212 | 0.745194 |
| gnn_no_base | 12 | 1.050956 | 0.830685 | 0.830685 | 0.923737 |
| gnn_no_base | 6 | 0.942706 | 0.743756 | 0.743756 | 0.826890 |
| gnn_no_base | total_12 | 0.542707 | 0.412593 | 0.412593 | 0.474504 |
| gnn_no_graph | 1 | 0.824398 | 0.655373 | 0.655373 | 0.723667 |
| gnn_no_graph | 12 | 0.972223 | 0.773990 | 0.773990 | 0.851606 |
| gnn_no_graph | 6 | 0.897308 | 0.717265 | 0.717265 | 0.788552 |
| gnn_no_graph | total_12 | 0.467261 | 0.367808 | 0.367808 | 0.408063 |
| gnn_real | 1 | 0.832267 | 0.660880 | 0.660880 | 0.729999 |
| gnn_real | 12 | 0.974709 | 0.775512 | 0.775512 | 0.854676 |
| gnn_real | 6 | 0.907808 | 0.727081 | 0.727081 | 0.797106 |
| gnn_real | total_12 | 0.488495 | 0.386888 | 0.386888 | 0.426181 |
| gnn_shuffled | 1 | 0.838602 | 0.667510 | 0.667510 | 0.735934 |
| gnn_shuffled | 12 | 0.977886 | 0.773935 | 0.773935 | 0.857554 |
| gnn_shuffled | 6 | 0.909553 | 0.725379 | 0.725379 | 0.799040 |
| gnn_shuffled | total_12 | 0.497482 | 0.392222 | 0.392222 | 0.435319 |
| gradient_boosting_neighbours | 1 | 0.800762 | 0.633535 | 0.633535 | 0.703351 |
| gradient_boosting_neighbours | 12 | 0.923334 | 0.712956 | 0.712956 | 0.812040 |
| gradient_boosting_neighbours | 6 | 0.874218 | 0.687414 | 0.687414 | 0.767618 |
| gradient_boosting_neighbours | total_12 | 0.445815 | 0.340888 | 0.340888 | 0.390217 |
| gradient_boosting_own | 1 | 0.810321 | 0.638502 | 0.638502 | 0.711952 |
| gradient_boosting_own | 12 | 0.936209 | 0.727238 | 0.727238 | 0.824523 |
| gradient_boosting_own | 6 | 0.886775 | 0.697029 | 0.697029 | 0.779117 |
| gradient_boosting_own | total_12 | 0.454350 | 0.347738 | 0.347738 | 0.398944 |
| half_neighbour_B | 1 | 0.806138 | 0.639690 | 0.639690 | 0.707911 |
| half_neighbour_B | 12 | 0.937388 | 0.735337 | 0.735337 | 0.823336 |
| half_neighbour_B | 6 | 0.883310 | 0.701475 | 0.701475 | 0.775659 |
| half_neighbour_B | total_12 | 0.452886 | 0.352978 | 0.352978 | 0.395714 |
| half_own_B | 1 | 0.811681 | 0.643701 | 0.643701 | 0.712763 |
| half_own_B | 12 | 0.943613 | 0.741401 | 0.741401 | 0.829335 |
| half_own_B | 6 | 0.888674 | 0.704402 | 0.704402 | 0.780578 |
| half_own_B | total_12 | 0.456243 | 0.354204 | 0.354204 | 0.399117 |
| learned_neighbour_B | 1 | 0.801586 | 0.634880 | 0.634880 | 0.704176 |
| learned_neighbour_B | 12 | 0.930987 | 0.727961 | 0.727961 | 0.818163 |
| learned_neighbour_B | 6 | 0.875453 | 0.690028 | 0.690028 | 0.768738 |
| learned_neighbour_B | total_12 | 0.446059 | 0.345199 | 0.345199 | 0.390127 |
| seasonal_naive | 1 | 1.066349 | 0.802956 | 0.802956 | 0.938109 |
| seasonal_naive | 12 | 1.124344 | 0.831959 | 0.831959 | 0.991517 |
| seasonal_naive | 6 | 1.093415 | 0.821298 | 0.821298 | 0.961971 |
| seasonal_naive | total_12 | 0.471949 | 0.353360 | 0.353360 | 0.416808 |

## high maturity

| model | outcome | mase_without_fallback | median_scaled_error_without_fallback | median_scaled_error_with_fallback | mean_level_scaled_error |
| --- | --- | --- | --- | --- | --- |
| gnn_no_base | 1 | 0.767241 | 0.576288 | 0.576288 | 0.452473 |
| gnn_no_base | 12 | 1.011223 | 0.792555 | 0.792555 | 0.602095 |
| gnn_no_base | 6 | 0.929348 | 0.712253 | 0.712253 | 0.549346 |
| gnn_no_base | total_12 | 0.638194 | 0.478285 | 0.478285 | 0.374195 |
| gnn_no_graph | 1 | 0.766520 | 0.576452 | 0.576452 | 0.449853 |
| gnn_no_graph | 12 | 1.033163 | 0.822445 | 0.822445 | 0.613523 |
| gnn_no_graph | 6 | 0.914813 | 0.701998 | 0.701998 | 0.538422 |
| gnn_no_graph | total_12 | 0.637642 | 0.483974 | 0.483974 | 0.371389 |
| gnn_real | 1 | 0.760110 | 0.571858 | 0.571858 | 0.447188 |
| gnn_real | 12 | 1.017492 | 0.806400 | 0.806400 | 0.604791 |
| gnn_real | 6 | 0.905941 | 0.694717 | 0.694717 | 0.534050 |
| gnn_real | total_12 | 0.624199 | 0.470135 | 0.470135 | 0.364282 |
| gnn_shuffled | 1 | 0.761522 | 0.573964 | 0.573964 | 0.448135 |
| gnn_shuffled | 12 | 1.019604 | 0.806734 | 0.806734 | 0.606051 |
| gnn_shuffled | 6 | 0.909156 | 0.698311 | 0.698311 | 0.535861 |
| gnn_shuffled | total_12 | 0.627128 | 0.476656 | 0.476656 | 0.365906 |
| gradient_boosting_neighbours | 1 | 0.703889 | 0.534896 | 0.534896 | 0.417872 |
| gradient_boosting_neighbours | 12 | 0.980766 | 0.778738 | 0.778738 | 0.584258 |
| gradient_boosting_neighbours | 6 | 0.872568 | 0.675393 | 0.675393 | 0.517011 |
| gradient_boosting_neighbours | total_12 | 0.582812 | 0.455025 | 0.455025 | 0.343947 |
| gradient_boosting_own | 1 | 0.705266 | 0.533470 | 0.533470 | 0.419472 |
| gradient_boosting_own | 12 | 0.974782 | 0.772960 | 0.772960 | 0.582293 |
| gradient_boosting_own | 6 | 0.868310 | 0.673025 | 0.673025 | 0.515609 |
| gradient_boosting_own | total_12 | 0.571029 | 0.451031 | 0.451031 | 0.338497 |
| half_neighbour_B | 1 | 0.708216 | 0.538190 | 0.538190 | 0.420095 |
| half_neighbour_B | 12 | 0.976382 | 0.774258 | 0.774258 | 0.582655 |
| half_neighbour_B | 6 | 0.870172 | 0.670662 | 0.670662 | 0.515876 |
| half_neighbour_B | total_12 | 0.581494 | 0.449974 | 0.449974 | 0.342834 |
| half_own_B | 1 | 0.711029 | 0.539111 | 0.539111 | 0.421862 |
| half_own_B | 12 | 0.975998 | 0.774808 | 0.774808 | 0.582939 |
| half_own_B | 6 | 0.868894 | 0.669503 | 0.669503 | 0.515461 |
| half_own_B | total_12 | 0.576897 | 0.446698 | 0.446698 | 0.340614 |
| learned_neighbour_B | 1 | 0.700811 | 0.531918 | 0.531918 | 0.416381 |
| learned_neighbour_B | 12 | 0.975552 | 0.773406 | 0.773406 | 0.580335 |
| learned_neighbour_B | 6 | 0.872240 | 0.676363 | 0.676363 | 0.516647 |
| learned_neighbour_B | total_12 | 0.582176 | 0.454040 | 0.454040 | 0.343044 |
| seasonal_naive | 1 | 0.973725 | 0.738699 | 0.738699 | 0.581758 |
| seasonal_naive | 12 | 1.045388 | 0.799401 | 0.799401 | 0.629638 |
| seasonal_naive | 6 | 1.019275 | 0.783705 | 0.783705 | 0.610568 |
| seasonal_naive | total_12 | 0.586257 | 0.469636 | 0.469636 | 0.353746 |

## Coverage

| origin | group | areas | nonfallback_areas | fallback_areas | positive_mean_areas | zero_mean_areas |
| --- | --- | --- | --- | --- | --- | --- |
| 2018-11 | all | 2634 | 2626 | 8 | 2624 | 10 |
| 2018-11 | low | 878 | 870 | 8 | 868 | 10 |
| 2018-11 | medium | 878 | 878 | 0 | 878 | 0 |
| 2018-11 | high | 878 | 878 | 0 | 878 | 0 |
| 2018-12 | all | 2634 | 2626 | 8 | 2624 | 10 |
| 2018-12 | low | 878 | 870 | 8 | 868 | 10 |
| 2018-12 | medium | 878 | 878 | 0 | 878 | 0 |
| 2018-12 | high | 878 | 878 | 0 | 878 | 0 |
| 2019-01 | all | 2634 | 2626 | 8 | 2624 | 10 |
| 2019-01 | low | 878 | 870 | 8 | 868 | 10 |
| 2019-01 | medium | 878 | 878 | 0 | 878 | 0 |
| 2019-01 | high | 878 | 878 | 0 | 878 | 0 |
| 2019-02 | all | 2634 | 2627 | 7 | 2625 | 9 |
| 2019-02 | low | 878 | 871 | 7 | 869 | 9 |
| 2019-02 | medium | 878 | 878 | 0 | 878 | 0 |
| 2019-02 | high | 878 | 878 | 0 | 878 | 0 |
| 2019-03 | all | 2634 | 2627 | 7 | 2625 | 9 |
| 2019-03 | low | 878 | 871 | 7 | 869 | 9 |
| 2019-03 | medium | 878 | 878 | 0 | 878 | 0 |
| 2019-03 | high | 878 | 878 | 0 | 878 | 0 |
| 2019-04 | all | 2634 | 2627 | 7 | 2625 | 9 |
| 2019-04 | low | 878 | 871 | 7 | 869 | 9 |
| 2019-04 | medium | 878 | 878 | 0 | 878 | 0 |
| 2019-04 | high | 878 | 878 | 0 | 878 | 0 |
| 2019-05 | all | 2634 | 2627 | 7 | 2625 | 9 |
| 2019-05 | low | 878 | 871 | 7 | 869 | 9 |
| 2019-05 | medium | 878 | 878 | 0 | 878 | 0 |
| 2019-05 | high | 878 | 878 | 0 | 878 | 0 |
| 2019-06 | all | 2634 | 2627 | 7 | 2625 | 9 |
| 2019-06 | low | 878 | 871 | 7 | 869 | 9 |
| 2019-06 | medium | 878 | 878 | 0 | 878 | 0 |
| 2019-06 | high | 878 | 878 | 0 | 878 | 0 |
| 2019-07 | all | 2634 | 2627 | 7 | 2625 | 9 |
| 2019-07 | low | 878 | 871 | 7 | 869 | 9 |
| 2019-07 | medium | 878 | 878 | 0 | 878 | 0 |
| 2019-07 | high | 878 | 878 | 0 | 878 | 0 |
| 2019-08 | all | 2634 | 2627 | 7 | 2625 | 9 |
| 2019-08 | low | 878 | 871 | 7 | 869 | 9 |
| 2019-08 | medium | 878 | 878 | 0 | 878 | 0 |
| 2019-08 | high | 878 | 878 | 0 | 878 | 0 |
| 2019-09 | all | 2634 | 2627 | 7 | 2625 | 9 |
| 2019-09 | low | 878 | 871 | 7 | 869 | 9 |
| 2019-09 | medium | 878 | 878 | 0 | 878 | 0 |
| 2019-09 | high | 878 | 878 | 0 | 878 | 0 |
| 2019-10 | all | 2634 | 2627 | 7 | 2625 | 9 |
| 2019-10 | low | 878 | 871 | 7 | 869 | 9 |
| 2019-10 | medium | 878 | 878 | 0 | 878 | 0 |
| 2019-10 | high | 878 | 878 | 0 | 878 | 0 |
| 2019-11 | all | 2634 | 2628 | 6 | 2626 | 8 |
| 2019-11 | low | 878 | 872 | 6 | 870 | 8 |
| 2019-11 | medium | 878 | 878 | 0 | 878 | 0 |
| 2019-11 | high | 878 | 878 | 0 | 878 | 0 |
| 2019-12 | all | 2634 | 2628 | 6 | 2626 | 8 |
| 2019-12 | low | 878 | 872 | 6 | 870 | 8 |
| 2019-12 | medium | 878 | 878 | 0 | 878 | 0 |
| 2019-12 | high | 878 | 878 | 0 | 878 | 0 |
| 2020-01 | all | 2634 | 2628 | 6 | 2626 | 8 |
| 2020-01 | low | 878 | 872 | 6 | 870 | 8 |
| 2020-01 | medium | 878 | 878 | 0 | 878 | 0 |
| 2020-01 | high | 878 | 878 | 0 | 878 | 0 |
| 2020-02 | all | 2634 | 2628 | 6 | 2626 | 8 |
| 2020-02 | low | 878 | 872 | 6 | 870 | 8 |
| 2020-02 | medium | 878 | 878 | 0 | 878 | 0 |
| 2020-02 | high | 878 | 878 | 0 | 878 | 0 |
| 2020-03 | all | 2634 | 2628 | 6 | 2626 | 8 |
| 2020-03 | low | 878 | 872 | 6 | 870 | 8 |
| 2020-03 | medium | 878 | 878 | 0 | 878 | 0 |
| 2020-03 | high | 878 | 878 | 0 | 878 | 0 |
| 2020-04 | all | 2634 | 2628 | 6 | 2626 | 8 |
| 2020-04 | low | 878 | 872 | 6 | 870 | 8 |
| 2020-04 | medium | 878 | 878 | 0 | 878 | 0 |
| 2020-04 | high | 878 | 878 | 0 | 878 | 0 |
| 2020-05 | all | 2634 | 2628 | 6 | 2627 | 7 |
| 2020-05 | low | 878 | 872 | 6 | 871 | 7 |
| 2020-05 | medium | 878 | 878 | 0 | 878 | 0 |
| 2020-05 | high | 878 | 878 | 0 | 878 | 0 |
| 2020-06 | all | 2634 | 2628 | 6 | 2627 | 7 |
| 2020-06 | low | 878 | 872 | 6 | 871 | 7 |
| 2020-06 | medium | 878 | 878 | 0 | 878 | 0 |
| 2020-06 | high | 878 | 878 | 0 | 878 | 0 |
| 2020-07 | all | 2634 | 2628 | 6 | 2627 | 7 |
| 2020-07 | low | 878 | 872 | 6 | 871 | 7 |
| 2020-07 | medium | 878 | 878 | 0 | 878 | 0 |
| 2020-07 | high | 878 | 878 | 0 | 878 | 0 |
| 2020-08 | all | 2634 | 2629 | 5 | 2629 | 5 |
| 2020-08 | low | 878 | 873 | 5 | 873 | 5 |
| 2020-08 | medium | 878 | 878 | 0 | 878 | 0 |
| 2020-08 | high | 878 | 878 | 0 | 878 | 0 |
| 2020-09 | all | 2634 | 2629 | 5 | 2629 | 5 |
| 2020-09 | low | 878 | 873 | 5 | 873 | 5 |
| 2020-09 | medium | 878 | 878 | 0 | 878 | 0 |
| 2020-09 | high | 878 | 878 | 0 | 878 | 0 |
| 2020-10 | all | 2634 | 2629 | 5 | 2629 | 5 |
| 2020-10 | low | 878 | 873 | 5 | 873 | 5 |
| 2020-10 | medium | 878 | 878 | 0 | 878 | 0 |
| 2020-10 | high | 878 | 878 | 0 | 878 | 0 |
| 2020-11 | all | 2634 | 2629 | 5 | 2629 | 5 |
| 2020-11 | low | 878 | 873 | 5 | 873 | 5 |
| 2020-11 | medium | 878 | 878 | 0 | 878 | 0 |
| 2020-11 | high | 878 | 878 | 0 | 878 | 0 |
| 2020-12 | all | 2634 | 2629 | 5 | 2629 | 5 |
| 2020-12 | low | 878 | 873 | 5 | 873 | 5 |
| 2020-12 | medium | 878 | 878 | 0 | 878 | 0 |
| 2020-12 | high | 878 | 878 | 0 | 878 | 0 |
| 2021-01 | all | 2634 | 2629 | 5 | 2629 | 5 |
| 2021-01 | low | 878 | 873 | 5 | 873 | 5 |
| 2021-01 | medium | 878 | 878 | 0 | 878 | 0 |
| 2021-01 | high | 878 | 878 | 0 | 878 | 0 |
| 2021-02 | all | 2634 | 2630 | 4 | 2630 | 4 |
| 2021-02 | low | 878 | 874 | 4 | 874 | 4 |
| 2021-02 | medium | 878 | 878 | 0 | 878 | 0 |
| 2021-02 | high | 878 | 878 | 0 | 878 | 0 |
| 2021-03 | all | 2634 | 2630 | 4 | 2630 | 4 |
| 2021-03 | low | 878 | 874 | 4 | 874 | 4 |
| 2021-03 | medium | 878 | 878 | 0 | 878 | 0 |
| 2021-03 | high | 878 | 878 | 0 | 878 | 0 |
| 2021-04 | all | 2634 | 2630 | 4 | 2630 | 4 |
| 2021-04 | low | 878 | 874 | 4 | 874 | 4 |
| 2021-04 | medium | 878 | 878 | 0 | 878 | 0 |
| 2021-04 | high | 878 | 878 | 0 | 878 | 0 |
| 2021-05 | all | 2634 | 2630 | 4 | 2630 | 4 |
| 2021-05 | low | 878 | 874 | 4 | 874 | 4 |
| 2021-05 | medium | 878 | 878 | 0 | 878 | 0 |
| 2021-05 | high | 878 | 878 | 0 | 878 | 0 |
| 2021-06 | all | 2634 | 2630 | 4 | 2630 | 4 |
| 2021-06 | low | 878 | 874 | 4 | 874 | 4 |
| 2021-06 | medium | 878 | 878 | 0 | 878 | 0 |
| 2021-06 | high | 878 | 878 | 0 | 878 | 0 |
| 2021-07 | all | 2634 | 2630 | 4 | 2630 | 4 |
| 2021-07 | low | 878 | 874 | 4 | 874 | 4 |
| 2021-07 | medium | 878 | 878 | 0 | 878 | 0 |
| 2021-07 | high | 878 | 878 | 0 | 878 | 0 |
| 2021-08 | all | 2634 | 2631 | 3 | 2631 | 3 |
| 2021-08 | low | 878 | 875 | 3 | 875 | 3 |
| 2021-08 | medium | 878 | 878 | 0 | 878 | 0 |
| 2021-08 | high | 878 | 878 | 0 | 878 | 0 |
| 2021-09 | all | 2634 | 2631 | 3 | 2631 | 3 |
| 2021-09 | low | 878 | 875 | 3 | 875 | 3 |
| 2021-09 | medium | 878 | 878 | 0 | 878 | 0 |
| 2021-09 | high | 878 | 878 | 0 | 878 | 0 |
| 2021-10 | all | 2634 | 2631 | 3 | 2631 | 3 |
| 2021-10 | low | 878 | 875 | 3 | 875 | 3 |
| 2021-10 | medium | 878 | 878 | 0 | 878 | 0 |
| 2021-10 | high | 878 | 878 | 0 | 878 | 0 |

Generator: `evaluation.mase_robustness`. No additional DM family is claimed.
