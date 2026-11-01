# Equal-weight combination validation — 1 November 2026

**Descriptive and exploratory; CPU only, no fits. Gate C accepted by the researcher on 1 November 2026.** Final-test targets/forecasts/losses remain untouched. All results below use the 36 frozen validation origins, November 2018–October 2021, twelve horizons, 2,634 observed areas and seeds 11/29/47.

## Accepted Gate C findings

- B real beats B no graph on MAE at every reported outcome, with Holm p below 0.05 at horizons 1 and 6.
- B real and B shuffled cannot be distinguished (all Holm p = 1). The gain is consistent with pooling information within states, rather than adjacency specifically; this does not identify a causal mechanism.
- Both boosting baselines beat B real on MAE at every reported outcome. B real has lower MASE than own-lag boosting at every outcome, most clearly in low-maturity areas.
- Removing installed base worsens MASE at every outcome, most in low-maturity areas; the MAE tests are not significant.

## Fixed combinations and scoring

`half_own_B` is 0.5 × own-lag boosting + 0.5 × B real. `half_neighbour_B` is 0.5 × neighbour-lag boosting + 0.5 × B real. Each seed is paired with the same seed; no weight is estimated and forecasts are not averaged across seeds before scoring. Arithmetic is float64 on saved forecasts, including summation of combination totals. Existing float32 baseline/B total conventions are retained for those references. Tiny rounding differences are possible, without an economic change to the weights.

Absolute/squared errors average areas within each origin/group, then origins and seeds. RMSE roots pooled squared errors. MASE uses shared training-only seasonal scales, including the existing pooled fallback for zero scales; total scale is twelve times monthly scale. Maturity is recomputed at each origin; unknown areas remain masked and isolates retained. Seed spread is sample SD/min/max of individually scored seeds. Monthly units: systems/area/month; total: systems/area/twelve-month window; MASE unitless.

## Descriptive result summary

Both combinations have lower MAE than B real at all four tested outcomes. 8/8 comparisons against B real have Holm p < 0.05; 0/8 against own-lag boosting do. Differences against own-lag boosting vary by horizon; the combinations do not establish an improvement over that baseline. These are validation-development comparisons, not final-test confirmation.

### Maturity: all

| model | outcome | mae | mae_seed_sd | mase | mase_seed_sd | rmse | rmse_seed_sd |
| --- | --- | --- | --- | --- | --- | --- | --- |
| gnn_real | 1 | 3.653635 | 0.036387 | 0.983482 | 0.028933 | 10.107133 | 0.060918 |
| gnn_real | 10 | 4.561916 | 0.024510 | 1.157775 | 0.019446 | 11.557962 | 0.052212 |
| gnn_real | 11 | 4.610944 | 0.017952 | 1.157492 | 0.018797 | 11.654250 | 0.089601 |
| gnn_real | 12 | 4.642173 | 0.020120 | 1.178855 | 0.010867 | 11.600262 | 0.085140 |
| gnn_real | 2 | 3.818632 | 0.026631 | 1.027862 | 0.025234 | 10.446701 | 0.106656 |
| gnn_real | 3 | 3.945476 | 0.027983 | 1.051064 | 0.021872 | 10.602468 | 0.046123 |
| gnn_real | 4 | 4.042090 | 0.023320 | 1.088410 | 0.037295 | 10.708370 | 0.100267 |
| gnn_real | 5 | 4.114620 | 0.033547 | 1.095419 | 0.009645 | 10.869849 | 0.045891 |
| gnn_real | 6 | 4.217250 | 0.033493 | 1.115489 | 0.012543 | 10.997935 | 0.024151 |
| gnn_real | 7 | 4.289304 | 0.032146 | 1.122994 | 0.024529 | 11.118850 | 0.048054 |
| gnn_real | 8 | 4.352505 | 0.041594 | 1.119753 | 0.007630 | 11.230422 | 0.061941 |
| gnn_real | 9 | 4.443754 | 0.036103 | 1.129617 | 0.021726 | 11.363318 | 0.090994 |
| gnn_real | total_12 | 35.284584 | 0.331149 | 0.630839 | 0.015196 | 106.807272 | 1.010904 |
| gradient_boosting_neighbours | 1 | 3.240554 | 0.007218 | 1.009142 | 0.000562 | 7.542176 | 0.059252 |
| gradient_boosting_neighbours | 10 | 4.322596 | 0.003806 | 1.178558 | 0.000451 | 10.088578 | 0.015075 |
| gradient_boosting_neighbours | 11 | 4.382983 | 0.005858 | 1.190706 | 0.000962 | 10.241602 | 0.022600 |
| gradient_boosting_neighbours | 12 | 4.436481 | 0.003678 | 1.198639 | 0.000931 | 10.305286 | 0.016457 |
| gradient_boosting_neighbours | 2 | 3.430401 | 0.002626 | 1.039215 | 0.000124 | 8.321959 | 0.028189 |
| gradient_boosting_neighbours | 3 | 3.572831 | 0.004128 | 1.058143 | 0.000057 | 8.698590 | 0.031504 |
| gradient_boosting_neighbours | 4 | 3.667951 | 0.005675 | 1.075047 | 0.000194 | 8.755491 | 0.067373 |
| gradient_boosting_neighbours | 5 | 3.793711 | 0.003622 | 1.096390 | 0.000176 | 8.944661 | 0.030326 |
| gradient_boosting_neighbours | 6 | 3.954436 | 0.005485 | 1.118497 | 0.000230 | 9.365410 | 0.046755 |
| gradient_boosting_neighbours | 7 | 4.059939 | 0.003804 | 1.131507 | 0.000420 | 9.627048 | 0.027532 |
| gradient_boosting_neighbours | 8 | 4.142889 | 0.003429 | 1.142332 | 0.000131 | 9.730846 | 0.006115 |
| gradient_boosting_neighbours | 9 | 4.221453 | 0.003093 | 1.158034 | 0.000351 | 9.884193 | 0.006997 |
| gradient_boosting_neighbours | total_12 | 31.118270 | 0.026271 | 0.626576 | 0.000438 | 79.241504 | 0.289208 |
| gradient_boosting_own | 1 | 3.256133 | 0.007532 | 1.054212 | 0.000717 | 7.509802 | 0.075904 |
| gradient_boosting_own | 10 | 4.321570 | 0.005359 | 1.249963 | 0.000988 | 9.985700 | 0.008388 |
| gradient_boosting_own | 11 | 4.389334 | 0.001736 | 1.266868 | 0.000318 | 10.121758 | 0.016962 |
| gradient_boosting_own | 12 | 4.433081 | 0.002229 | 1.274145 | 0.000483 | 10.188115 | 0.007306 |
| gradient_boosting_own | 2 | 3.436575 | 0.005826 | 1.082926 | 0.000480 | 8.227003 | 0.054988 |
| gradient_boosting_own | 3 | 3.588183 | 0.006889 | 1.103930 | 0.000691 | 8.624669 | 0.057271 |
| gradient_boosting_own | 4 | 3.677378 | 0.007324 | 1.120563 | 0.000463 | 8.716010 | 0.042801 |
| gradient_boosting_own | 5 | 3.801002 | 0.009354 | 1.144709 | 0.000733 | 8.917932 | 0.052808 |
| gradient_boosting_own | 6 | 3.961972 | 0.006813 | 1.170082 | 0.000614 | 9.293712 | 0.033041 |
| gradient_boosting_own | 7 | 4.065762 | 0.004960 | 1.191030 | 0.000142 | 9.539665 | 0.018356 |
| gradient_boosting_own | 8 | 4.141646 | 0.004276 | 1.211394 | 0.000820 | 9.614836 | 0.018820 |
| gradient_boosting_own | 9 | 4.229105 | 0.008268 | 1.229930 | 0.000866 | 9.776743 | 0.021167 |
| gradient_boosting_own | total_12 | 30.866269 | 0.046997 | 0.680405 | 0.000553 | 77.106792 | 0.140563 |
| half_neighbour_B | 1 | 3.298367 | 0.012685 | 0.983331 | 0.012600 | 8.217315 | 0.053776 |
| half_neighbour_B | 10 | 4.291813 | 0.011043 | 1.155736 | 0.009637 | 10.217799 | 0.027695 |
| half_neighbour_B | 11 | 4.345138 | 0.008775 | 1.161148 | 0.010173 | 10.353673 | 0.054842 |
| half_neighbour_B | 12 | 4.384444 | 0.010019 | 1.174882 | 0.005597 | 10.375876 | 0.053548 |
| half_neighbour_B | 2 | 3.481267 | 0.007652 | 1.021491 | 0.010868 | 8.775950 | 0.043568 |
| half_neighbour_B | 3 | 3.621257 | 0.011560 | 1.043411 | 0.009741 | 9.040583 | 0.023062 |
| half_neighbour_B | 4 | 3.725067 | 0.012361 | 1.070963 | 0.018241 | 9.160667 | 0.018875 |
| half_neighbour_B | 5 | 3.821635 | 0.011151 | 1.085197 | 0.005782 | 9.358125 | 0.009245 |
| half_neighbour_B | 6 | 3.952916 | 0.016551 | 1.106386 | 0.007062 | 9.613108 | 0.011560 |
| half_neighbour_B | 7 | 4.037307 | 0.018997 | 1.116396 | 0.012721 | 9.767729 | 0.011282 |
| half_neighbour_B | 8 | 4.110750 | 0.019395 | 1.120257 | 0.003884 | 9.868497 | 0.021476 |
| half_neighbour_B | 9 | 4.186271 | 0.016979 | 1.132456 | 0.011402 | 9.996742 | 0.029246 |
| half_neighbour_B | total_12 | 31.343618 | 0.129126 | 0.608947 | 0.007632 | 84.712147 | 0.561620 |
| half_own_B | 1 | 3.319196 | 0.007924 | 1.006372 | 0.012549 | 8.234826 | 0.074861 |
| half_own_B | 10 | 4.310083 | 0.009064 | 1.191509 | 0.009480 | 10.265843 | 0.026993 |
| half_own_B | 11 | 4.363496 | 0.008414 | 1.199097 | 0.010624 | 10.379736 | 0.041537 |
| half_own_B | 12 | 4.401506 | 0.008678 | 1.213042 | 0.005903 | 10.409309 | 0.049492 |
| half_own_B | 2 | 3.491063 | 0.004669 | 1.043646 | 0.011163 | 8.743839 | 0.079632 |
| half_own_B | 3 | 3.633828 | 0.005195 | 1.066348 | 0.009889 | 9.018313 | 0.065742 |
| half_own_B | 4 | 3.737722 | 0.006571 | 1.093504 | 0.018582 | 9.175297 | 0.057069 |
| half_own_B | 5 | 3.834617 | 0.006791 | 1.109206 | 0.006080 | 9.377267 | 0.039814 |
| half_own_B | 6 | 3.964833 | 0.013790 | 1.131715 | 0.007452 | 9.621375 | 0.024929 |
| half_own_B | 7 | 4.051156 | 0.016566 | 1.145882 | 0.012863 | 9.798128 | 0.018214 |
| half_own_B | 8 | 4.124390 | 0.018984 | 1.154299 | 0.003802 | 9.915967 | 0.015505 |
| half_own_B | 9 | 4.205823 | 0.016846 | 1.168077 | 0.011232 | 10.052478 | 0.024659 |
| half_own_B | total_12 | 31.337050 | 0.119791 | 0.633561 | 0.008162 | 84.651917 | 0.675732 |

### Maturity: low

| model | outcome | mae | mae_seed_sd | mase | mase_seed_sd | rmse | rmse_seed_sd |
| --- | --- | --- | --- | --- | --- | --- | --- |
| gnn_real | 1 | 0.669171 | 0.025617 | 1.358069 | 0.063920 | 1.140096 | 0.010106 |
| gnn_real | 10 | 0.753880 | 0.014504 | 1.519863 | 0.053208 | 1.400172 | 0.005788 |
| gnn_real | 11 | 0.739235 | 0.014037 | 1.499668 | 0.064606 | 1.407565 | 0.007340 |
| gnn_real | 12 | 0.749614 | 0.008600 | 1.544362 | 0.043638 | 1.421042 | 0.001874 |
| gnn_real | 2 | 0.693727 | 0.019010 | 1.422988 | 0.059914 | 1.190070 | 0.009538 |
| gnn_real | 3 | 0.699820 | 0.015861 | 1.441837 | 0.054756 | 1.219841 | 0.007565 |
| gnn_real | 4 | 0.721608 | 0.028524 | 1.515697 | 0.104796 | 1.276176 | 0.011869 |
| gnn_real | 5 | 0.721633 | 0.007664 | 1.511843 | 0.052840 | 1.301551 | 0.005442 |
| gnn_real | 6 | 0.734195 | 0.006476 | 1.532720 | 0.062691 | 1.347653 | 0.004045 |
| gnn_real | 7 | 0.737971 | 0.016152 | 1.529736 | 0.080037 | 1.352480 | 0.006152 |
| gnn_real | 8 | 0.733027 | 0.007228 | 1.499401 | 0.025961 | 1.357221 | 0.003635 |
| gnn_real | 9 | 0.733669 | 0.014442 | 1.486916 | 0.066023 | 1.373247 | 0.004788 |
| gnn_real | total_12 | 4.242877 | 0.149868 | 0.779824 | 0.045276 | 7.160394 | 0.099121 |
| gradient_boosting_neighbours | 1 | 0.669236 | 0.000327 | 1.522775 | 0.001178 | 1.123627 | 0.000132 |
| gradient_boosting_neighbours | 10 | 0.725617 | 0.000192 | 1.663059 | 0.001505 | 1.383324 | 0.000253 |
| gradient_boosting_neighbours | 11 | 0.727311 | 0.000281 | 1.680370 | 0.002123 | 1.400239 | 0.000545 |
| gradient_boosting_neighbours | 12 | 0.729146 | 0.000347 | 1.691817 | 0.002010 | 1.408581 | 0.000644 |
| gradient_boosting_neighbours | 2 | 0.680842 | 0.000054 | 1.545274 | 0.000177 | 1.173065 | 0.000892 |
| gradient_boosting_neighbours | 3 | 0.686462 | 0.000118 | 1.553781 | 0.000489 | 1.201799 | 0.000802 |
| gradient_boosting_neighbours | 4 | 0.693601 | 0.000172 | 1.572085 | 0.000350 | 1.253548 | 0.000438 |
| gradient_boosting_neighbours | 5 | 0.699931 | 0.000080 | 1.592026 | 0.000884 | 1.278423 | 0.000953 |
| gradient_boosting_neighbours | 6 | 0.705782 | 0.000147 | 1.608706 | 0.001501 | 1.317585 | 0.001404 |
| gradient_boosting_neighbours | 7 | 0.708415 | 0.000280 | 1.614015 | 0.002000 | 1.318707 | 0.001260 |
| gradient_boosting_neighbours | 8 | 0.711689 | 0.000200 | 1.617851 | 0.001144 | 1.330534 | 0.001016 |
| gradient_boosting_neighbours | 9 | 0.719163 | 0.000194 | 1.636932 | 0.001580 | 1.358610 | 0.000318 |
| gradient_boosting_neighbours | total_12 | 3.889148 | 0.001581 | 0.851100 | 0.000930 | 6.869953 | 0.005201 |
| gradient_boosting_own | 1 | 0.693392 | 0.000192 | 1.647050 | 0.000428 | 1.136751 | 0.000344 |
| gradient_boosting_own | 10 | 0.765925 | 0.000286 | 1.870385 | 0.001340 | 1.397046 | 0.000092 |
| gradient_boosting_own | 11 | 0.771496 | 0.000093 | 1.900269 | 0.000955 | 1.419166 | 0.000126 |
| gradient_boosting_own | 12 | 0.774594 | 0.000204 | 1.911445 | 0.000514 | 1.431625 | 0.000436 |
| gradient_boosting_own | 2 | 0.705488 | 0.000196 | 1.670429 | 0.000833 | 1.183147 | 0.000619 |
| gradient_boosting_own | 3 | 0.712010 | 0.000180 | 1.683115 | 0.001253 | 1.212568 | 0.000592 |
| gradient_boosting_own | 4 | 0.719599 | 0.000157 | 1.699630 | 0.000519 | 1.265549 | 0.000479 |
| gradient_boosting_own | 5 | 0.728582 | 0.000311 | 1.728312 | 0.000116 | 1.295907 | 0.000146 |
| gradient_boosting_own | 6 | 0.736364 | 0.000518 | 1.755160 | 0.000022 | 1.342536 | 0.000681 |
| gradient_boosting_own | 7 | 0.741781 | 0.000560 | 1.786345 | 0.001196 | 1.345214 | 0.002470 |
| gradient_boosting_own | 8 | 0.747845 | 0.000112 | 1.818798 | 0.001528 | 1.342439 | 0.000698 |
| gradient_boosting_own | 9 | 0.758133 | 0.000267 | 1.842459 | 0.001000 | 1.371677 | 0.000596 |
| gradient_boosting_own | total_12 | 4.318011 | 0.002326 | 1.015836 | 0.000532 | 7.122706 | 0.002854 |
| half_neighbour_B | 1 | 0.664915 | 0.012244 | 1.435638 | 0.030842 | 1.122454 | 0.003970 |
| half_neighbour_B | 10 | 0.733963 | 0.007033 | 1.584994 | 0.026750 | 1.380927 | 0.002791 |
| half_neighbour_B | 11 | 0.727736 | 0.007122 | 1.583645 | 0.033146 | 1.393098 | 0.003268 |
| half_neighbour_B | 12 | 0.733238 | 0.004116 | 1.610875 | 0.022773 | 1.402693 | 0.000473 |
| half_neighbour_B | 2 | 0.683195 | 0.008637 | 1.479519 | 0.028996 | 1.173211 | 0.003719 |
| half_neighbour_B | 3 | 0.689203 | 0.007198 | 1.493425 | 0.026694 | 1.202794 | 0.002904 |
| half_neighbour_B | 4 | 0.703247 | 0.013372 | 1.538608 | 0.051198 | 1.256429 | 0.004462 |
| half_neighbour_B | 5 | 0.706352 | 0.003395 | 1.546913 | 0.027160 | 1.282189 | 0.001977 |
| half_neighbour_B | 6 | 0.715378 | 0.003220 | 1.565677 | 0.032266 | 1.324620 | 0.001973 |
| half_neighbour_B | 7 | 0.718101 | 0.008094 | 1.566179 | 0.040961 | 1.326835 | 0.002268 |
| half_neighbour_B | 8 | 0.717218 | 0.002733 | 1.552803 | 0.014520 | 1.334627 | 0.000835 |
| half_neighbour_B | 9 | 0.721467 | 0.007273 | 1.556491 | 0.033622 | 1.356486 | 0.002705 |
| half_neighbour_B | total_12 | 3.932374 | 0.071327 | 0.792460 | 0.025514 | 6.812700 | 0.047367 |
| half_own_B | 1 | 0.676399 | 0.012507 | 1.496405 | 0.031404 | 1.127422 | 0.004923 |
| half_own_B | 10 | 0.753408 | 0.007172 | 1.687078 | 0.026481 | 1.385341 | 0.003420 |
| half_own_B | 11 | 0.748880 | 0.007658 | 1.691554 | 0.033708 | 1.399754 | 0.004663 |
| half_own_B | 12 | 0.755299 | 0.004481 | 1.719514 | 0.022885 | 1.412073 | 0.001658 |
| half_own_B | 2 | 0.694909 | 0.008777 | 1.541140 | 0.029002 | 1.176377 | 0.004085 |
| half_own_B | 3 | 0.701245 | 0.007428 | 1.557113 | 0.026486 | 1.205019 | 0.003661 |
| half_own_B | 4 | 0.715596 | 0.013621 | 1.601051 | 0.051625 | 1.259877 | 0.005421 |
| half_own_B | 5 | 0.719935 | 0.003482 | 1.613959 | 0.026662 | 1.287776 | 0.001637 |
| half_own_B | 6 | 0.729788 | 0.002981 | 1.637576 | 0.031475 | 1.332588 | 0.001247 |
| half_own_B | 7 | 0.734052 | 0.008136 | 1.651191 | 0.039655 | 1.335171 | 0.002736 |
| half_own_B | 8 | 0.734283 | 0.002916 | 1.651540 | 0.013061 | 1.338171 | 0.000438 |
| half_own_B | 9 | 0.739834 | 0.007455 | 1.657072 | 0.032994 | 1.360245 | 0.003443 |
| half_own_B | total_12 | 4.123449 | 0.076358 | 0.867545 | 0.026736 | 6.900056 | 0.058138 |

### Maturity: medium

| model | outcome | mae | mae_seed_sd | mase | mase_seed_sd | rmse | rmse_seed_sd |
| --- | --- | --- | --- | --- | --- | --- | --- |
| gnn_real | 1 | 2.112850 | 0.039535 | 0.832267 | 0.016810 | 3.163820 | 0.018568 |
| gnn_real | 10 | 2.481700 | 0.059192 | 0.961063 | 0.022743 | 3.849401 | 0.056490 |
| gnn_real | 11 | 2.492925 | 0.035722 | 0.965292 | 0.012907 | 3.852687 | 0.042408 |
| gnn_real | 12 | 2.517553 | 0.046594 | 0.974709 | 0.017264 | 3.873258 | 0.049086 |
| gnn_real | 2 | 2.183436 | 0.034283 | 0.857759 | 0.013861 | 3.298739 | 0.026818 |
| gnn_real | 3 | 2.228970 | 0.033701 | 0.873283 | 0.013363 | 3.378137 | 0.021680 |
| gnn_real | 4 | 2.267997 | 0.036140 | 0.887276 | 0.014945 | 3.445470 | 0.023897 |
| gnn_real | 5 | 2.292742 | 0.035392 | 0.895176 | 0.013119 | 3.514202 | 0.029640 |
| gnn_real | 6 | 2.328341 | 0.042958 | 0.907808 | 0.015241 | 3.588602 | 0.042182 |
| gnn_real | 7 | 2.354431 | 0.054664 | 0.916055 | 0.020558 | 3.640049 | 0.049669 |
| gnn_real | 8 | 2.367354 | 0.057034 | 0.919876 | 0.021289 | 3.676815 | 0.050413 |
| gnn_real | 9 | 2.415788 | 0.058071 | 0.936803 | 0.021363 | 3.761530 | 0.055356 |
| gnn_real | total_12 | 15.376453 | 0.653760 | 0.488495 | 0.021155 | 23.977755 | 0.698931 |
| gradient_boosting_neighbours | 1 | 2.035803 | 0.000278 | 0.800762 | 0.000048 | 3.081380 | 0.001150 |
| gradient_boosting_neighbours | 10 | 2.368005 | 0.000214 | 0.915490 | 0.000053 | 3.802129 | 0.003722 |
| gradient_boosting_neighbours | 11 | 2.380207 | 0.000884 | 0.921346 | 0.000353 | 3.811487 | 0.006177 |
| gradient_boosting_neighbours | 12 | 2.388459 | 0.001329 | 0.923334 | 0.000487 | 3.833280 | 0.008636 |
| gradient_boosting_neighbours | 2 | 2.096313 | 0.000854 | 0.821456 | 0.000332 | 3.218088 | 0.003668 |
| gradient_boosting_neighbours | 3 | 2.137829 | 0.001101 | 0.835829 | 0.000404 | 3.296829 | 0.004834 |
| gradient_boosting_neighbours | 4 | 2.168725 | 0.000487 | 0.846585 | 0.000183 | 3.364948 | 0.001918 |
| gradient_boosting_neighbours | 5 | 2.212853 | 0.000581 | 0.862475 | 0.000215 | 3.448182 | 0.001218 |
| gradient_boosting_neighbours | 6 | 2.247032 | 0.001581 | 0.874218 | 0.000548 | 3.518911 | 0.002318 |
| gradient_boosting_neighbours | 7 | 2.275842 | 0.001187 | 0.883910 | 0.000336 | 3.589947 | 0.003828 |
| gradient_boosting_neighbours | 8 | 2.299265 | 0.000171 | 0.892112 | 0.000120 | 3.643366 | 0.001667 |
| gradient_boosting_neighbours | 9 | 2.330658 | 0.000395 | 0.903774 | 0.000174 | 3.718381 | 0.002649 |
| gradient_boosting_neighbours | total_12 | 14.222212 | 0.012784 | 0.445815 | 0.000337 | 23.255112 | 0.063675 |
| gradient_boosting_own | 1 | 2.059580 | 0.001986 | 0.810321 | 0.000721 | 3.108866 | 0.003394 |
| gradient_boosting_own | 10 | 2.395157 | 0.001959 | 0.927676 | 0.000768 | 3.812040 | 0.001234 |
| gradient_boosting_own | 11 | 2.407293 | 0.001008 | 0.934168 | 0.000473 | 3.812106 | 0.003066 |
| gradient_boosting_own | 12 | 2.415790 | 0.001287 | 0.936209 | 0.000443 | 3.828124 | 0.004621 |
| gradient_boosting_own | 2 | 2.114872 | 0.001431 | 0.829457 | 0.000508 | 3.235980 | 0.001917 |
| gradient_boosting_own | 3 | 2.159754 | 0.001691 | 0.845070 | 0.000641 | 3.316942 | 0.002706 |
| gradient_boosting_own | 4 | 2.194969 | 0.000315 | 0.858121 | 0.000155 | 3.399027 | 0.000577 |
| gradient_boosting_own | 5 | 2.240934 | 0.001793 | 0.874687 | 0.000576 | 3.483473 | 0.008255 |
| gradient_boosting_own | 6 | 2.276109 | 0.001004 | 0.886775 | 0.000157 | 3.549353 | 0.003058 |
| gradient_boosting_own | 7 | 2.300583 | 0.000510 | 0.895139 | 0.000089 | 3.606114 | 0.005126 |
| gradient_boosting_own | 8 | 2.327807 | 0.001412 | 0.905030 | 0.000547 | 3.662652 | 0.001159 |
| gradient_boosting_own | 9 | 2.363477 | 0.001309 | 0.918123 | 0.000545 | 3.740737 | 0.002550 |
| gradient_boosting_own | total_12 | 14.415432 | 0.014659 | 0.454350 | 0.000346 | 23.042983 | 0.021843 |
| half_neighbour_B | 1 | 2.048529 | 0.015126 | 0.806138 | 0.006581 | 3.080168 | 0.000676 |
| half_neighbour_B | 10 | 2.401750 | 0.026827 | 0.928585 | 0.010344 | 3.788558 | 0.021593 |
| half_neighbour_B | 11 | 2.411074 | 0.015067 | 0.932849 | 0.005544 | 3.790061 | 0.012887 |
| half_neighbour_B | 12 | 2.424989 | 0.018614 | 0.937388 | 0.006872 | 3.804857 | 0.013023 |
| half_neighbour_B | 2 | 2.117380 | 0.011572 | 0.830492 | 0.004771 | 3.222456 | 0.004374 |
| half_neighbour_B | 3 | 2.162485 | 0.012059 | 0.846049 | 0.004778 | 3.305053 | 0.002903 |
| half_neighbour_B | 4 | 2.199077 | 0.014665 | 0.859026 | 0.006146 | 3.375380 | 0.006640 |
| half_neighbour_B | 5 | 2.234087 | 0.014527 | 0.871080 | 0.005258 | 3.452678 | 0.011271 |
| half_neighbour_B | 6 | 2.269342 | 0.019488 | 0.883310 | 0.006849 | 3.523463 | 0.017262 |
| half_neighbour_B | 7 | 2.296923 | 0.025120 | 0.892280 | 0.009407 | 3.584920 | 0.019177 |
| half_neighbour_B | 8 | 2.314732 | 0.025612 | 0.898212 | 0.009403 | 3.631102 | 0.020777 |
| half_neighbour_B | 9 | 2.353183 | 0.026708 | 0.911966 | 0.009880 | 3.707560 | 0.023058 |
| half_neighbour_B | total_12 | 14.405666 | 0.273586 | 0.452886 | 0.008835 | 23.005358 | 0.237065 |
| half_own_B | 1 | 2.062290 | 0.014969 | 0.811681 | 0.006651 | 3.096950 | 0.001537 |
| half_own_B | 10 | 2.413893 | 0.028280 | 0.934174 | 0.010964 | 3.791919 | 0.024249 |
| half_own_B | 11 | 2.423531 | 0.015584 | 0.938753 | 0.005843 | 3.789417 | 0.015111 |
| half_own_B | 12 | 2.438038 | 0.019230 | 0.943613 | 0.007125 | 3.804519 | 0.016086 |
| half_own_B | 2 | 2.127908 | 0.012819 | 0.834864 | 0.005339 | 3.233445 | 0.006946 |
| half_own_B | 3 | 2.173898 | 0.013205 | 0.850845 | 0.005310 | 3.317110 | 0.005700 |
| half_own_B | 4 | 2.211425 | 0.015548 | 0.864428 | 0.006540 | 3.392063 | 0.008523 |
| half_own_B | 5 | 2.246454 | 0.014014 | 0.876575 | 0.005118 | 3.468027 | 0.009393 |
| half_own_B | 6 | 2.281332 | 0.018703 | 0.888674 | 0.006634 | 3.535409 | 0.016170 |
| half_own_B | 7 | 2.306789 | 0.025220 | 0.896915 | 0.009616 | 3.589225 | 0.019744 |
| half_own_B | 8 | 2.325756 | 0.026506 | 0.903311 | 0.009842 | 3.638519 | 0.022655 |
| half_own_B | 9 | 2.367639 | 0.028268 | 0.918351 | 0.010534 | 3.717553 | 0.025320 |
| half_own_B | total_12 | 14.475443 | 0.278579 | 0.456243 | 0.009160 | 22.926517 | 0.271021 |

### Maturity: high

| model | outcome | mae | mae_seed_sd | mase | mase_seed_sd | rmse | rmse_seed_sd |
| --- | --- | --- | --- | --- | --- | --- | --- |
| gnn_real | 1 | 8.178883 | 0.046084 | 0.760110 | 0.010531 | 17.180012 | 0.109340 |
| gnn_real | 10 | 10.450169 | 0.071763 | 0.992397 | 0.013754 | 19.595435 | 0.103453 |
| gnn_real | 11 | 10.600673 | 0.087178 | 1.007517 | 0.009189 | 19.764619 | 0.164893 |
| gnn_real | 12 | 10.659352 | 0.081031 | 1.017492 | 0.010687 | 19.664098 | 0.159954 |
| gnn_real | 2 | 8.578733 | 0.027431 | 0.802838 | 0.010152 | 17.751133 | 0.189405 |
| gnn_real | 3 | 8.907639 | 0.037305 | 0.838072 | 0.010186 | 18.009363 | 0.082986 |
| gnn_real | 4 | 9.136665 | 0.063204 | 0.862257 | 0.009937 | 18.179870 | 0.181189 |
| gnn_real | 5 | 9.329483 | 0.064769 | 0.879239 | 0.011039 | 18.450398 | 0.081764 |
| gnn_real | 6 | 9.589216 | 0.065062 | 0.905941 | 0.014747 | 18.659300 | 0.049324 |
| gnn_real | 7 | 9.775509 | 0.066764 | 0.923191 | 0.015272 | 18.862856 | 0.094819 |
| gnn_real | 8 | 9.957135 | 0.082838 | 0.939983 | 0.014179 | 19.052719 | 0.115626 |
| gnn_real | 9 | 10.181807 | 0.097419 | 0.965131 | 0.016345 | 19.270185 | 0.169531 |
| gnn_real | total_12 | 86.234423 | 1.092744 | 0.624199 | 0.012693 | 183.295325 | 1.852761 |
| gradient_boosting_neighbours | 1 | 7.016623 | 0.021636 | 0.703889 | 0.000637 | 12.644992 | 0.105905 |
| gradient_boosting_neighbours | 10 | 9.874166 | 0.011595 | 0.957125 | 0.000868 | 16.999073 | 0.027177 |
| gradient_boosting_neighbours | 11 | 10.041431 | 0.016853 | 0.970402 | 0.001843 | 17.267980 | 0.039298 |
| gradient_boosting_neighbours | 12 | 10.191837 | 0.009680 | 0.980766 | 0.000925 | 17.375805 | 0.027367 |
| gradient_boosting_neighbours | 2 | 7.514047 | 0.007464 | 0.750915 | 0.000091 | 14.001172 | 0.050100 |
| gradient_boosting_neighbours | 3 | 7.894201 | 0.013162 | 0.784820 | 0.000252 | 14.652065 | 0.056789 |
| gradient_boosting_neighbours | 4 | 8.141527 | 0.017447 | 0.806471 | 0.000795 | 14.733690 | 0.120349 |
| gradient_boosting_neighbours | 5 | 8.468350 | 0.011482 | 0.834671 | 0.000706 | 15.049803 | 0.054393 |
| gradient_boosting_neighbours | 6 | 8.910495 | 0.017958 | 0.872568 | 0.001038 | 15.780177 | 0.083764 |
| gradient_boosting_neighbours | 7 | 9.195562 | 0.012551 | 0.896595 | 0.000809 | 16.230016 | 0.049940 |
| gradient_boosting_neighbours | 8 | 9.417715 | 0.010567 | 0.917034 | 0.001009 | 16.401941 | 0.011331 |
| gradient_boosting_neighbours | 9 | 9.614539 | 0.009778 | 0.933395 | 0.001056 | 16.655918 | 0.012982 |
| gradient_boosting_neighbours | total_12 | 75.243451 | 0.068418 | 0.582812 | 0.000629 | 135.091271 | 0.503821 |
| gradient_boosting_own | 1 | 7.015428 | 0.020600 | 0.705266 | 0.001177 | 12.579115 | 0.135120 |
| gradient_boosting_own | 10 | 9.803629 | 0.014822 | 0.951829 | 0.001645 | 16.812473 | 0.015028 |
| gradient_boosting_own | 11 | 9.989214 | 0.004213 | 0.966167 | 0.001235 | 17.052969 | 0.030879 |
| gradient_boosting_own | 12 | 10.108860 | 0.006931 | 0.974782 | 0.000684 | 17.166507 | 0.013976 |
| gradient_boosting_own | 2 | 7.489364 | 0.016126 | 0.748893 | 0.000440 | 13.826762 | 0.097751 |
| gradient_boosting_own | 3 | 7.892785 | 0.019592 | 0.783603 | 0.000794 | 14.514900 | 0.101522 |
| gradient_boosting_own | 4 | 8.117566 | 0.021893 | 0.803937 | 0.001123 | 14.654402 | 0.076219 |
| gradient_boosting_own | 5 | 8.433490 | 0.026861 | 0.831128 | 0.001665 | 14.992484 | 0.092567 |
| gradient_boosting_own | 6 | 8.873443 | 0.020789 | 0.868310 | 0.001810 | 15.643494 | 0.058356 |
| gradient_boosting_own | 7 | 9.154923 | 0.015240 | 0.891605 | 0.001473 | 16.068664 | 0.031969 |
| gradient_boosting_own | 8 | 9.349284 | 0.011560 | 0.910354 | 0.000730 | 16.190061 | 0.033296 |
| gradient_boosting_own | 9 | 9.565705 | 0.024351 | 0.929207 | 0.001723 | 16.458417 | 0.037523 |
| gradient_boosting_own | total_12 | 73.865364 | 0.129433 | 0.571029 | 0.000915 | 131.356995 | 0.244071 |
| half_neighbour_B | 1 | 7.181657 | 0.015162 | 0.708216 | 0.003914 | 13.850107 | 0.095840 |
| half_neighbour_B | 10 | 9.739726 | 0.033152 | 0.953628 | 0.005600 | 17.232241 | 0.053843 |
| half_neighbour_B | 11 | 9.896603 | 0.041544 | 0.966951 | 0.003097 | 17.472560 | 0.099845 |
| half_neighbour_B | 12 | 9.995105 | 0.043861 | 0.976382 | 0.004182 | 17.508054 | 0.097695 |
| half_neighbour_B | 2 | 7.643227 | 0.015100 | 0.754461 | 0.003825 | 14.808486 | 0.077193 |
| half_neighbour_B | 3 | 8.012082 | 0.019754 | 0.790760 | 0.004132 | 15.258647 | 0.040933 |
| half_neighbour_B | 4 | 8.272877 | 0.017802 | 0.815254 | 0.004196 | 15.452561 | 0.035124 |
| half_neighbour_B | 5 | 8.524467 | 0.018898 | 0.837597 | 0.004688 | 15.784756 | 0.018565 |
| half_neighbour_B | 6 | 8.874028 | 0.033391 | 0.870172 | 0.007066 | 16.219314 | 0.021174 |
| half_neighbour_B | 7 | 9.096896 | 0.036958 | 0.890728 | 0.007644 | 16.480699 | 0.024186 |
| half_neighbour_B | 8 | 9.300300 | 0.035398 | 0.909757 | 0.006960 | 16.649191 | 0.041574 |
| half_neighbour_B | 9 | 9.484162 | 0.036815 | 0.928912 | 0.007350 | 16.858781 | 0.056184 |
| half_neighbour_B | total_12 | 75.692815 | 0.511196 | 0.581494 | 0.005069 | 144.750766 | 1.023891 |
| half_own_B | 1 | 7.218900 | 0.015190 | 0.711029 | 0.003182 | 13.877135 | 0.133287 |
| half_own_B | 10 | 9.762949 | 0.031724 | 0.953275 | 0.005211 | 17.316605 | 0.053185 |
| half_own_B | 11 | 9.918077 | 0.038740 | 0.966984 | 0.002459 | 17.518498 | 0.076824 |
| half_own_B | 12 | 10.011181 | 0.044433 | 0.975998 | 0.003689 | 17.566810 | 0.091236 |
| half_own_B | 2 | 7.650374 | 0.007886 | 0.754934 | 0.003147 | 14.748733 | 0.141730 |
| half_own_B | 3 | 8.026340 | 0.008491 | 0.791085 | 0.003179 | 15.216262 | 0.117727 |
| half_own_B | 4 | 8.286145 | 0.010503 | 0.815033 | 0.003329 | 15.474652 | 0.103687 |
| half_own_B | 5 | 8.537461 | 0.008251 | 0.837083 | 0.003410 | 15.814987 | 0.072926 |
| half_own_B | 6 | 8.883377 | 0.025837 | 0.868894 | 0.006448 | 16.230763 | 0.047194 |
| half_own_B | 7 | 9.112628 | 0.028275 | 0.889541 | 0.006649 | 16.533140 | 0.036474 |
| half_own_B | 8 | 9.313131 | 0.035089 | 0.908046 | 0.006373 | 16.731697 | 0.031940 |
| half_own_B | 9 | 9.509995 | 0.040549 | 0.928807 | 0.007247 | 16.955427 | 0.049148 |
| half_own_B | total_12 | 75.412258 | 0.548821 | 0.576897 | 0.004562 | 144.653397 | 1.229929 |

All monthly horizons 1–12, totals and seed min/max are in [scores](../../data/processed/t03_combination_validation/scores.csv), [per-seed metrics](../../data/processed/t03_combination_validation/seed_metrics.csv) and [origin losses](../../data/processed/t03_combination_validation/origin_metrics.csv.gz). [Horizon/total figure](../../data/explore/t03/combination_validation/errors.png); [maturity figure](../../data/explore/t03/combination_validation/maturity.png).

## Separate descriptive DM/Holm family

Exactly 16 two-sided MAE-loss tests: each of the two combinations against frozen own-lag boosting and against B real, at horizons 1, 6, 12 and the twelve-month total. No test against neighbour boosting was added. This family is separate from the accepted B 20-test family. Average area losses per origin and then average over the same three seeds before DM; HLN/Bartlett h−1 covariance convention, total h=12. One Holm adjustment across all 16; undefined tests reserve slots. No RMSE/MASE testing family. Inspection of already-used validation data makes all p-values descriptive.

| model_a | model_b | outcome | h | origins | statistic | p_raw | status | family_size | p_holm |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| half_own_B | gradient_boosting_own | 1 | 1 | 36 | 2.247595 | 0.0310061 | defined | 16 | 0.248049 |
| half_own_B | gradient_boosting_own | 6 | 6 | 36 | 0.040129 | 0.968219 | defined | 16 | 1 |
| half_own_B | gradient_boosting_own | 12 | 12 | 36 | -0.288355 | 0.774776 | defined | 16 | 1 |
| half_own_B | gradient_boosting_own | total_12 | 12 | 36 | 0.331660 | 0.742124 | defined | 16 | 1 |
| half_own_B | gnn_real | 1 | 1 | 36 | -12.609988 | 1.41793e-14 | defined | 16 | 2.12689e-13 |
| half_own_B | gnn_real | 6 | 6 | 36 | -5.540693 | 3.1144e-06 | defined | 16 | 4.04872e-05 |
| half_own_B | gnn_real | 12 | 12 | 36 | -3.382186 | 0.00178273 | defined | 16 | 0.0160446 |
| half_own_B | gnn_real | total_12 | 12 | 36 | -4.588156 | 5.52886e-05 | defined | 16 | 0.000608175 |
| half_neighbour_B | gradient_boosting_own | 1 | 1 | 36 | 1.347543 | 0.186464 | defined | 16 | 1 |
| half_neighbour_B | gradient_boosting_own | 6 | 6 | 36 | -0.130997 | 0.896528 | defined | 16 | 1 |
| half_neighbour_B | gradient_boosting_own | 12 | 12 | 36 | -0.421253 | 0.676146 | defined | 16 | 1 |
| half_neighbour_B | gradient_boosting_own | total_12 | 12 | 36 | 0.329581 | 0.743681 | defined | 16 | 1 |
| half_neighbour_B | gnn_real | 1 | 1 | 36 | -14.152047 | 4.76638e-16 | defined | 16 | 7.62621e-15 |
| half_neighbour_B | gnn_real | 6 | 6 | 36 | -5.968217 | 8.50221e-07 | defined | 16 | 1.19031e-05 |
| half_neighbour_B | gnn_real | 12 | 12 | 36 | -4.018171 | 0.000296203 | defined | 16 | 0.00296203 |
| half_neighbour_B | gnn_real | total_12 | 12 | 36 | -5.014015 | 1.53778e-05 | defined | 16 | 0.000184534 |

## Final-test cost estimate — not execution authorisation

Resource totals:

| device | hours_low | hours_central | hours_high |
| --- | --- | --- | --- |
| CPU boosting | 1.672888 | 2.121117 | 2.661088 |
| GPU B | 7.243182 | 7.821067 | 8.492083 |

Per condition:

| device | condition | fits | hours_low | hours_central | hours_high |
| --- | --- | --- | --- | --- | --- |
| CPU boosting | gradient_boosting_neighbours | 24 | 1.206473 | 1.498520 | 1.788644 |
| CPU boosting | gradient_boosting_own | 24 | 0.466415 | 0.622597 | 0.872444 |
| GPU B | no_graph | 24 | 1.534497 | 1.921194 | 2.278741 |
| GPU B | real | 24 | 1.368656 | 1.373384 | 1.380075 |
| GPU B | shuffled | 24 | 2.137692 | 2.314273 | 2.609522 |
| GPU B | without_base | 24 | 2.202337 | 2.212216 | 2.223745 |

Calendar arithmetic only: eight quarterly test refits, October 2022–July 2024, serving 24 test origins through September 2024. Each condition requires 8 × 3 = 24 fits: 48 CPU fits for both boosting baselines, 96 GPU fits for the four B conditions, 144 fits overall. No validation checkpoint can substitute for a later expanding-window test refit. No retuning/search, C model or additional blending fit is included. Equal-weight combinations add only arithmetic after forecasts, not fitted models.

Projected times use the last four observed validation refit dates for each condition/seed. B uses measured seconds per epoch/origin batch × 65 epochs and future calendar batch counts. Boosting uses historical selected-configuration seconds per eligible training row × future calendar row counts. Central is the median per-seed rate; low/high use its empirical 25th/75th percentiles, not confidence intervals or guaranteed bounds. CPU historical times include serialization; B times exclude inference. Training-set growth may be nonlinear for boosting. Power/load/thermal variation, inference, setup, final scoring and session breaks are not forecast here. CPU hours and GPU hours are separate resources; serial wall time would approximately sum them, without parallelism.

[Refit calendar](../../data/processed/t03_combination_validation/final_test_refit_calendar.csv), [per-fit scenarios](../../data/processed/t03_combination_validation/final_test_cost_details.csv), [cost summary](../../data/processed/t03_combination_validation/final_test_cost_summary.csv), [cost figure](../../visuals/t03/combination_validation/final_test_cost.png). No panel, feature or target array is read by the cost module: it uses protocol dates and saved fit records only. No test runner or test command is implemented or executed.

## Reproducibility and stop

Sources: `evaluation.combination_validation`, `evaluation.final_test_cost`, `visuals.combination_validation`. [Provenance](../../data/processed/t03_combination_validation/manifest.json), [exploration index](../../data/explore/t03/combination_validation/index.md). No frozen fit/config/protocol source was changed. Stop for researcher review; Gate C acceptance does not itself authorise touching the final test.
