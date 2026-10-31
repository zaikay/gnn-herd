# Architecture screen — protocol v3 screen

Gate C remains open. Twelve seed-11 GPU fits completed. Selected by the fixed rule: **B**. This is an exploratory two-anchor screen, not a confirmatory gate decision. No sealed-test forecasts/losses.

## Selection and cost

| candidate | mae | gpu_fit_seconds | allocated_base_cpu_seconds | cost_seconds | beats_own_no_graph_both_anchors | training_loss_worse_both_anchors | selected |
| --- | --- | --- | --- | --- | --- | --- | --- |
| A | 4.359734 | 2226.693745 | 0.000000 | 556.673436 | False | False | False |
| B | 4.208487 | 1016.177852 | 0.000000 | 254.044463 | True | False | True |
| C | 4.173492 | 909.815916 | 2390.204425 | 825.005085 | False | False | False |

Selection MAE averages the two anchors and all twelve monthly horizons. Candidates within 2% of the minimum use lower total measured cost per fit. C includes all necessary base-fit CPU seconds, including original measured cost of reused fits, allocated over its four GPU fits; CPU/GPU seconds are summed as elapsed compute cost, not converted to equivalent hardware work. Shared base fits are charged once across the four C fits. Newly executed base fit seconds: 1973.138; total attributable base seconds: 2390.204.

At least one candidate beats its own no graph at both anchors; flags in the table remain relevant. No full campaign is authorised by selection alone.

## Per-anchor metrics

MAE, MASE and RMSE are in the [complete per-anchor table](../../data/explore/t03/architecture_screen/origin.csv), every horizon 1–12 and the twelve-month total, all/low/medium/high maturity. C_base is the frozen v1.1 selected own-lag boosting base alone. [Pooled scores](../../data/explore/t03/architecture_screen/scores.csv). Single seed: no seed uncertainty estimate.

| model | origin | outcome | mae | mase | mean_signed_error | rmse |
| --- | --- | --- | --- | --- | --- | --- |
| A_real | 2019-08 | 1 | 3.156648 | 1.003993 | 0.401365 | 7.513253 |
| A_real | 2019-08 | 6 | 3.647032 | 0.956312 | -1.401112 | 10.255394 |
| A_real | 2019-08 | 12 | 4.436785 | 1.089920 | -1.022656 | 10.828998 |
| A_real | 2019-08 | total_12 | 31.615466 | 0.563798 | -16.034144 | 105.193592 |
| A_real | 2020-08 | 1 | 4.180576 | 1.094327 | -0.687430 | 10.582220 |
| A_real | 2020-08 | 6 | 4.606419 | 1.117967 | -1.625115 | 12.936961 |
| A_real | 2020-08 | 12 | 5.065829 | 1.148618 | 0.717638 | 12.753774 |
| A_real | 2020-08 | total_12 | 41.549685 | 0.630567 | -11.344539 | 134.996799 |
| A_no_graph | 2019-08 | 1 | 3.014044 | 0.927267 | 0.058544 | 7.453233 |
| A_no_graph | 2019-08 | 6 | 3.666163 | 0.974451 | -2.031779 | 10.411166 |
| A_no_graph | 2019-08 | 12 | 4.561384 | 1.150375 | -1.728699 | 11.110557 |
| A_no_graph | 2019-08 | total_12 | 32.775022 | 0.582525 | -23.020970 | 107.633746 |
| A_no_graph | 2020-08 | 1 | 4.287340 | 1.046906 | -0.824988 | 10.671889 |
| A_no_graph | 2020-08 | 6 | 4.469472 | 1.111163 | -1.626883 | 12.852339 |
| A_no_graph | 2020-08 | 12 | 4.730420 | 1.209952 | 0.407961 | 12.410211 |
| A_no_graph | 2020-08 | total_12 | 37.994733 | 0.621658 | -12.175904 | 132.714674 |
| B_real | 2019-08 | 1 | 2.992552 | 0.908490 | 0.320968 | 7.143055 |
| B_real | 2019-08 | 6 | 3.527911 | 0.947778 | -1.513448 | 9.940909 |
| B_real | 2019-08 | 12 | 4.478891 | 1.107449 | -1.402735 | 10.708181 |
| B_real | 2019-08 | total_12 | 30.825844 | 0.575506 | -17.905922 | 101.154989 |
| B_real | 2020-08 | 1 | 4.290159 | 1.061968 | -0.909858 | 10.545495 |
| B_real | 2020-08 | 6 | 4.474745 | 1.126019 | -1.749246 | 12.680778 |
| B_real | 2020-08 | 12 | 4.710919 | 1.181299 | 0.397976 | 12.143594 |
| B_real | 2020-08 | total_12 | 37.365802 | 0.607641 | -14.131652 | 129.989472 |
| B_no_graph | 2019-08 | 1 | 3.014044 | 0.927267 | 0.058544 | 7.453233 |
| B_no_graph | 2019-08 | 6 | 3.666163 | 0.974451 | -2.031779 | 10.411166 |
| B_no_graph | 2019-08 | 12 | 4.561384 | 1.150375 | -1.728699 | 11.110557 |
| B_no_graph | 2019-08 | total_12 | 32.775022 | 0.582525 | -23.020970 | 107.633746 |
| B_no_graph | 2020-08 | 1 | 4.287340 | 1.046906 | -0.824988 | 10.671889 |
| B_no_graph | 2020-08 | 6 | 4.469472 | 1.111163 | -1.626883 | 12.852339 |
| B_no_graph | 2020-08 | 12 | 4.730420 | 1.209952 | 0.407961 | 12.410211 |
| B_no_graph | 2020-08 | total_12 | 37.994733 | 0.621658 | -12.175904 | 132.714674 |
| C_real | 2019-08 | 1 | 2.847619 | 0.902426 | 0.641068 | 5.963728 |
| C_real | 2019-08 | 6 | 3.532742 | 0.938929 | -1.700609 | 8.945018 |
| C_real | 2019-08 | 12 | 4.449225 | 1.086901 | 1.441807 | 9.343739 |
| C_real | 2019-08 | total_12 | 26.930146 | 0.539851 | -7.705910 | 69.540848 |
| C_real | 2020-08 | 1 | 4.011802 | 1.078532 | 1.315294 | 9.033553 |
| C_real | 2020-08 | 6 | 4.629918 | 1.124927 | 1.314722 | 10.350889 |
| C_real | 2020-08 | 12 | 5.911955 | 1.216462 | 3.981431 | 13.501268 |
| C_real | 2020-08 | total_12 | 39.425312 | 0.608365 | 19.634910 | 99.061884 |
| C_no_graph | 2019-08 | 1 | 2.983272 | 0.928844 | 1.151751 | 6.006757 |
| C_no_graph | 2019-08 | 6 | 3.431532 | 0.918325 | -1.149208 | 8.334854 |
| C_no_graph | 2019-08 | 12 | 4.629438 | 1.063225 | 1.697514 | 10.488226 |
| C_no_graph | 2019-08 | total_12 | 26.573635 | 0.526780 | -3.299080 | 68.417319 |
| C_no_graph | 2020-08 | 1 | 4.089402 | 1.093307 | 1.302715 | 9.179670 |
| C_no_graph | 2020-08 | 6 | 4.473339 | 1.108787 | 1.516258 | 10.060690 |
| C_no_graph | 2020-08 | 12 | 5.648162 | 1.146317 | 3.800677 | 13.574109 |
| C_no_graph | 2020-08 | total_12 | 39.337033 | 0.601197 | 21.835222 | 101.857659 |
| C_base | 2019-08 | 1 | 2.555227 | 0.957194 | -0.108126 | 5.252164 |
| C_base | 2019-08 | 6 | 3.560919 | 1.064114 | -2.091733 | 8.640804 |
| C_base | 2019-08 | 12 | 4.396612 | 1.175944 | -1.907977 | 9.953096 |
| C_base | 2019-08 | total_12 | 30.015279 | 0.659406 | -22.722291 | 74.089520 |
| C_base | 2020-08 | 1 | 3.948763 | 1.166794 | -0.472623 | 8.434142 |
| C_base | 2020-08 | 6 | 4.168833 | 1.232386 | -1.667422 | 10.518705 |
| C_base | 2020-08 | 12 | 4.237739 | 1.200375 | 0.602634 | 10.402548 |
| C_base | 2020-08 | total_12 | 30.876192 | 0.688248 | -9.741280 | 94.062491 |

## Descriptive comparisons with anchor-matched boosting

All models use **seed 11 at August 2019 and August 2020**, including each frozen boosting selection and any extra-search improved selection. The unchanged architecture-selection rule uses candidate real-graph monthly MAE only; these comparisons do not enter selection. C_base is C's strictly prior-quarter boosting forecast, which differs from the frozen own-lag baseline fitted at the anchor itself.

Bands 1–3, 4–6 and 7–12 pool individual monthly forecast errors, **not** sums of forecasts over each band. MAE/MASE average monthly cells within each area group and give equal weight to the two anchors; RMSE is the square root of pooled squared errors. MASE uses the same training-only anchor scales for every model. These are descriptive, single-seed comparisons; no significance tests or behavioural claims. Positive gain means the candidate lowers the reference error. A zero reference error has undefined percentage gain, retained as NaN.

[Every anchor, band and maturity group's scores](../../data/explore/t03/architecture_screen/anchor_band_scores.csv); [paired candidate/baseline errors and absolute/percentage gains](../../data/explore/t03/architecture_screen/anchor_band_comparisons.csv); [saved-baseline hashes](../../data/explore/t03/architecture_screen/anchor_baseline_provenance.json).

### Overall, pooled across both anchors

| model | band | mae | mase | rmse |
| --- | --- | --- | --- | --- |
| A_real | 1-3 | 4.077975 | 1.062145 | 12.057266 |
| A_real | 4-6 | 4.225829 | 1.066855 | 11.893513 |
| A_real | 7-12 | 4.567566 | 1.124213 | 12.171950 |
| A_no_graph | 1-3 | 4.064453 | 1.002604 | 12.107427 |
| A_no_graph | 4-6 | 4.153079 | 1.049161 | 11.887689 |
| A_no_graph | 7-12 | 4.465613 | 1.204518 | 12.113157 |
| B_real | 1-3 | 4.021045 | 1.009521 | 11.849189 |
| B_real | 4-6 | 4.087943 | 1.055222 | 11.575297 |
| B_real | 7-12 | 4.362481 | 1.139395 | 11.780407 |
| B_no_graph | 1-3 | 4.064453 | 1.002604 | 12.107427 |
| B_no_graph | 4-6 | 4.153079 | 1.049161 | 11.887689 |
| B_no_graph | 7-12 | 4.465613 | 1.204518 | 12.113157 |
| C_real | 1-3 | 3.670629 | 1.003809 | 9.194207 |
| C_real | 4-6 | 4.061543 | 1.033539 | 9.439668 |
| C_real | 7-12 | 4.480899 | 1.121677 | 10.509549 |
| C_no_graph | 1-3 | 3.761512 | 1.012289 | 9.210603 |
| C_no_graph | 4-6 | 4.061927 | 1.029141 | 9.450312 |
| C_no_graph | 7-12 | 4.377179 | 1.083526 | 10.407665 |
| C_base | 1-3 | 3.638447 | 1.092736 | 9.615545 |
| C_base | 4-6 | 3.792917 | 1.123916 | 9.627788 |
| C_base | 7-12 | 4.102998 | 1.245620 | 9.947247 |
| gradient_boosting_own_frozen | 1-3 | 3.664845 | 1.092104 | 9.791447 |
| gradient_boosting_own_frozen | 4-6 | 3.792077 | 1.120127 | 9.778394 |
| gradient_boosting_own_frozen | 7-12 | 4.091166 | 1.242484 | 9.876517 |
| gradient_boosting_neighbours_frozen | 1-3 | 3.601331 | 1.057316 | 9.786107 |
| gradient_boosting_neighbours_frozen | 4-6 | 3.800038 | 1.078946 | 9.914240 |
| gradient_boosting_neighbours_frozen | 7-12 | 4.130246 | 1.171796 | 10.122652 |

### Gains against each boosting reference (C also against its own base)

| candidate | condition | reference | band | mae_gain | mase_gain | rmse_gain |
| --- | --- | --- | --- | --- | --- | --- |
| A | real | gradient_boosting_own_frozen | 1-3 | -0.413131 | 0.029959 | -2.265819 |
| A | real | gradient_boosting_own_frozen | 4-6 | -0.433752 | 0.053271 | -2.115119 |
| A | real | gradient_boosting_own_frozen | 7-12 | -0.476400 | 0.118271 | -2.295433 |
| A | real | gradient_boosting_neighbours_frozen | 1-3 | -0.476644 | -0.004828 | -2.271159 |
| A | real | gradient_boosting_neighbours_frozen | 4-6 | -0.425791 | 0.012091 | -1.979272 |
| A | real | gradient_boosting_neighbours_frozen | 7-12 | -0.437320 | 0.047583 | -2.049298 |
| A | no_graph | gradient_boosting_own_frozen | 1-3 | -0.399608 | 0.089500 | -2.315980 |
| A | no_graph | gradient_boosting_own_frozen | 4-6 | -0.361001 | 0.070965 | -2.109295 |
| A | no_graph | gradient_boosting_own_frozen | 7-12 | -0.374447 | 0.037966 | -2.236640 |
| A | no_graph | gradient_boosting_neighbours_frozen | 1-3 | -0.463122 | 0.054712 | -2.321320 |
| A | no_graph | gradient_boosting_neighbours_frozen | 4-6 | -0.353040 | 0.029785 | -1.973449 |
| A | no_graph | gradient_boosting_neighbours_frozen | 7-12 | -0.335367 | -0.032722 | -1.990505 |
| B | real | gradient_boosting_own_frozen | 1-3 | -0.356200 | 0.082582 | -2.057742 |
| B | real | gradient_boosting_own_frozen | 4-6 | -0.295866 | 0.064905 | -1.796903 |
| B | real | gradient_boosting_own_frozen | 7-12 | -0.271315 | 0.103088 | -1.903890 |
| B | real | gradient_boosting_neighbours_frozen | 1-3 | -0.419713 | 0.047795 | -2.063082 |
| B | real | gradient_boosting_neighbours_frozen | 4-6 | -0.287905 | 0.023725 | -1.661057 |
| B | real | gradient_boosting_neighbours_frozen | 7-12 | -0.232235 | 0.032401 | -1.657755 |
| B | no_graph | gradient_boosting_own_frozen | 1-3 | -0.399608 | 0.089500 | -2.315980 |
| B | no_graph | gradient_boosting_own_frozen | 4-6 | -0.361001 | 0.070965 | -2.109295 |
| B | no_graph | gradient_boosting_own_frozen | 7-12 | -0.374447 | 0.037966 | -2.236640 |
| B | no_graph | gradient_boosting_neighbours_frozen | 1-3 | -0.463122 | 0.054712 | -2.321320 |
| B | no_graph | gradient_boosting_neighbours_frozen | 4-6 | -0.353040 | 0.029785 | -1.973449 |
| B | no_graph | gradient_boosting_neighbours_frozen | 7-12 | -0.335367 | -0.032722 | -1.990505 |
| C | real | gradient_boosting_own_frozen | 1-3 | -0.005784 | 0.088295 | 0.597240 |
| C | real | gradient_boosting_own_frozen | 4-6 | -0.269466 | 0.086588 | 0.338726 |
| C | real | gradient_boosting_own_frozen | 7-12 | -0.389733 | 0.120807 | -0.633031 |
| C | real | gradient_boosting_neighbours_frozen | 1-3 | -0.069298 | 0.053508 | 0.591901 |
| C | real | gradient_boosting_neighbours_frozen | 4-6 | -0.261505 | 0.045408 | 0.474572 |
| C | real | gradient_boosting_neighbours_frozen | 7-12 | -0.350653 | 0.050119 | -0.386897 |
| C | real | C_base | 1-3 | -0.032183 | 0.088927 | 0.421339 |
| C | real | C_base | 4-6 | -0.268626 | 0.090377 | 0.188120 |
| C | real | C_base | 7-12 | -0.377901 | 0.123943 | -0.562302 |
| C | no_graph | gradient_boosting_own_frozen | 1-3 | -0.096667 | 0.079814 | 0.580844 |
| C | no_graph | gradient_boosting_own_frozen | 4-6 | -0.269850 | 0.090985 | 0.328081 |
| C | no_graph | gradient_boosting_own_frozen | 7-12 | -0.286014 | 0.158958 | -0.531148 |
| C | no_graph | gradient_boosting_neighbours_frozen | 1-3 | -0.160181 | 0.045027 | 0.575505 |
| C | no_graph | gradient_boosting_neighbours_frozen | 4-6 | -0.261889 | 0.049805 | 0.463928 |
| C | no_graph | gradient_boosting_neighbours_frozen | 7-12 | -0.246934 | 0.088271 | -0.285013 |
| C | no_graph | C_base | 1-3 | -0.123066 | 0.080447 | 0.404943 |
| C | no_graph | C_base | 4-6 | -0.269010 | 0.094774 | 0.177475 |
| C | no_graph | C_base | 7-12 | -0.274181 | 0.162095 | -0.460418 |

### Maturity terciles, pooled across both anchors

| model | band | group | mae | mase | rmse |
| --- | --- | --- | --- | --- | --- |
| A_real | 1-3 | low | 0.703203 | 1.476168 | 1.174724 |
| A_real | 1-3 | medium | 2.197562 | 0.865224 | 3.570827 |
| A_real | 1-3 | high | 9.333161 | 0.845041 | 20.542692 |
| A_real | 4-6 | low | 0.668971 | 1.410598 | 1.216555 |
| A_real | 4-6 | medium | 2.257269 | 0.888597 | 3.430536 |
| A_real | 4-6 | high | 9.751247 | 0.901371 | 20.276054 |
| A_real | 7-12 | low | 0.712929 | 1.461238 | 1.370481 |
| A_real | 7-12 | medium | 2.388360 | 0.926067 | 3.959767 |
| A_real | 7-12 | high | 10.601408 | 0.985335 | 20.661828 |
| A_no_graph | 1-3 | low | 0.677645 | 1.314264 | 1.163345 |
| A_no_graph | 1-3 | medium | 2.186131 | 0.855954 | 3.519018 |
| A_no_graph | 1-3 | high | 9.329584 | 0.837594 | 20.640555 |
| A_no_graph | 4-6 | low | 0.665752 | 1.394159 | 1.211945 |
| A_no_graph | 4-6 | medium | 2.249130 | 0.882215 | 3.357377 |
| A_no_graph | 4-6 | high | 9.544354 | 0.871111 | 20.278330 |
| A_no_graph | 7-12 | low | 0.718276 | 1.758376 | 1.356434 |
| A_no_graph | 7-12 | medium | 2.352708 | 0.909947 | 3.885149 |
| A_no_graph | 7-12 | high | 10.325854 | 0.945231 | 20.573075 |
| B_real | 1-3 | low | 0.701855 | 1.337706 | 1.169014 |
| B_real | 1-3 | medium | 2.200005 | 0.863440 | 3.557238 |
| B_real | 1-3 | high | 9.161273 | 0.827417 | 20.178932 |
| B_real | 4-6 | low | 0.700273 | 1.406548 | 1.234147 |
| B_real | 4-6 | medium | 2.292643 | 0.902145 | 3.397475 |
| B_real | 4-6 | high | 9.270914 | 0.856972 | 19.720460 |
| B_real | 7-12 | low | 0.762372 | 1.569080 | 1.363949 |
| B_real | 7-12 | medium | 2.397548 | 0.931411 | 3.917550 |
| B_real | 7-12 | high | 9.927523 | 0.917696 | 19.978148 |
| B_no_graph | 1-3 | low | 0.677645 | 1.314264 | 1.163345 |
| B_no_graph | 1-3 | medium | 2.186131 | 0.855954 | 3.519018 |
| B_no_graph | 1-3 | high | 9.329584 | 0.837594 | 20.640555 |
| B_no_graph | 4-6 | low | 0.665752 | 1.394159 | 1.211945 |
| B_no_graph | 4-6 | medium | 2.249130 | 0.882215 | 3.357377 |
| B_no_graph | 4-6 | high | 9.544354 | 0.871111 | 20.278330 |
| B_no_graph | 7-12 | low | 0.718276 | 1.758376 | 1.356434 |
| B_no_graph | 7-12 | medium | 2.352708 | 0.909947 | 3.885149 |
| B_no_graph | 7-12 | high | 10.325854 | 0.945231 | 20.573075 |
| C_real | 1-3 | low | 0.672687 | 1.360964 | 1.170156 |
| C_real | 1-3 | medium | 2.172031 | 0.851401 | 3.658553 |
| C_real | 1-3 | high | 8.167169 | 0.799062 | 15.454644 |
| C_real | 4-6 | low | 0.636824 | 1.325608 | 1.203716 |
| C_real | 4-6 | medium | 2.278877 | 0.891922 | 3.542865 |
| C_real | 4-6 | high | 9.268928 | 0.883087 | 15.916066 |
| C_real | 7-12 | low | 0.694773 | 1.455483 | 1.355087 |
| C_real | 7-12 | medium | 2.395997 | 0.925676 | 4.013957 |
| C_real | 7-12 | high | 10.351926 | 0.983873 | 17.703213 |
| C_no_graph | 1-3 | low | 0.675029 | 1.366190 | 1.172420 |
| C_no_graph | 1-3 | medium | 2.173872 | 0.853538 | 3.634620 |
| C_no_graph | 1-3 | high | 8.435636 | 0.817140 | 15.489369 |
| C_no_graph | 4-6 | low | 0.639703 | 1.313584 | 1.209837 |
| C_no_graph | 4-6 | medium | 2.293610 | 0.897215 | 3.563655 |
| C_no_graph | 4-6 | high | 9.252468 | 0.876625 | 15.929905 |
| C_no_graph | 7-12 | low | 0.683627 | 1.371909 | 1.362114 |
| C_no_graph | 7-12 | medium | 2.394498 | 0.924212 | 4.085107 |
| C_no_graph | 7-12 | high | 10.053413 | 0.954455 | 17.504714 |
| C_base | 1-3 | low | 0.703366 | 1.616301 | 1.172943 |
| C_base | 1-3 | medium | 2.202351 | 0.860271 | 3.659641 |
| C_base | 1-3 | high | 8.009622 | 0.801637 | 16.205165 |
| C_base | 4-6 | low | 0.680725 | 1.660529 | 1.217027 |
| C_base | 4-6 | medium | 2.225081 | 0.870744 | 3.469966 |
| C_base | 4-6 | high | 8.472944 | 0.840474 | 16.265333 |
| C_base | 7-12 | low | 0.770693 | 1.926568 | 1.327070 |
| C_base | 7-12 | medium | 2.364419 | 0.914832 | 3.916470 |
| C_base | 7-12 | high | 9.173883 | 0.895462 | 16.725529 |
| gradient_boosting_own_frozen | 1-3 | low | 0.702006 | 1.611541 | 1.173080 |
| gradient_boosting_own_frozen | 1-3 | medium | 2.200440 | 0.859557 | 3.654544 |
| gradient_boosting_own_frozen | 1-3 | high | 8.092088 | 0.805213 | 16.519246 |
| gradient_boosting_own_frozen | 4-6 | low | 0.678484 | 1.654346 | 1.215488 |
| gradient_boosting_own_frozen | 4-6 | medium | 2.220687 | 0.869113 | 3.462698 |
| gradient_boosting_own_frozen | 4-6 | high | 8.477061 | 0.836922 | 16.534306 |
| gradient_boosting_own_frozen | 7-12 | low | 0.767272 | 1.914594 | 1.325996 |
| gradient_boosting_own_frozen | 7-12 | medium | 2.367347 | 0.915482 | 3.911676 |
| gradient_boosting_own_frozen | 7-12 | high | 9.138879 | 0.897376 | 16.600522 |
| gradient_boosting_neighbours_frozen | 1-3 | low | 0.686916 | 1.523234 | 1.168823 |
| gradient_boosting_neighbours_frozen | 1-3 | medium | 2.184796 | 0.853675 | 3.636153 |
| gradient_boosting_neighbours_frozen | 1-3 | high | 7.932283 | 0.795041 | 16.514113 |
| gradient_boosting_neighbours_frozen | 4-6 | low | 0.650504 | 1.523433 | 1.200270 |
| gradient_boosting_neighbours_frozen | 4-6 | medium | 2.207541 | 0.863668 | 3.471391 |
| gradient_boosting_neighbours_frozen | 4-6 | high | 8.542070 | 0.849738 | 16.774543 |
| gradient_boosting_neighbours_frozen | 7-12 | low | 0.727236 | 1.686630 | 1.332295 |
| gradient_boosting_neighbours_frozen | 7-12 | medium | 2.362557 | 0.912756 | 3.946217 |
| gradient_boosting_neighbours_frozen | 7-12 | high | 9.300944 | 0.916003 | 17.031049 |

Per-anchor maturity comparisons and C gains are retained in the complete linked CSVs. No improved-baseline column is manufactured if neither extra selection wins.



## Saved training fit and spatial diagnostics

| candidate | anchor | condition | epochs | parameter_count | fit_seconds | peak_gpu_memory_bytes | peak_reserved_gpu_memory_bytes | training_loss | training_samples | test_forecasts_or_losses |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| A | 2019-08 | real | 65 | 27852 | 623.271821 | 389108736 | 580911104 | -12.773699 | 115 | 0 |
| A | 2019-08 | no_graph | 65 | 27852 | 337.750460 | 390748672 | 568328192 | -12.487451 | 115 | 0 |
| A | 2020-08 | real | 65 | 27852 | 925.079552 | 397547520 | 580911104 | -13.954469 | 127 | 0 |
| A | 2020-08 | no_graph | 65 | 27852 | 340.591912 | 390748672 | 568328192 | -13.708426 | 127 | 0 |
| B | 2019-08 | real | 65 | 15180 | 244.417961 | 322240512 | 434110464 | -12.568917 | 115 | 0 |
| B | 2019-08 | no_graph | 65 | 15180 | 233.275530 | 316324352 | 434110464 | -12.487451 | 115 | 0 |
| B | 2020-08 | real | 65 | 15180 | 275.750328 | 322082304 | 434110464 | -13.760093 | 127 | 0 |
| B | 2020-08 | no_graph | 65 | 15180 | 262.734032 | 316324352 | 434110464 | -13.708426 | 127 | 0 |
| C | 2019-08 | real | 65 | 15180 | 219.976174 | 321870336 | 436207616 | -11.549981 | 101 | 0 |
| C | 2019-08 | no_graph | 65 | 15180 | 211.527953 | 316233216 | 436207616 | -11.506331 | 101 | 0 |
| C | 2020-08 | real | 65 | 15180 | 252.950097 | 322463232 | 434110464 | -12.960655 | 113 | 0 |
| C | 2020-08 | no_graph | 65 | 15180 | 225.361693 | 317171200 | 436207616 | -12.902328 | 113 | 0 |

[Training curves](../../data/explore/t03/architecture_screen/training_curves.png), [signed errors by maturity](../../data/explore/t03/architecture_screen/signed_errors.png), [isolates every horizon](../../data/explore/t03/architecture_screen/isolates.csv), [isolate figure](../../data/explore/t03/architecture_screen/isolates.png), [neighbour shift figure](../../data/explore/t03/architecture_screen/neighbour_shift.png), [per-area shifts](../../data/explore/t03/architecture_screen/neighbour_shift.csv.gz), [correlations](../../data/explore/t03/architecture_screen/neighbour_shift_summary.csv).

Only two screen origins exist: neighbour-shift correlations here are cross-area **at each anchor**, not the previous within-area 36-origin statistic. The gap uses observed origin-month neighbours' mean minus own count. Isolates have undefined gaps. These are descriptive, not behavioural identification. C trains from March 2011 origins with strict prior-quarter boosting forecasts; A/B retain the original training calendar, which limits direct causal attribution between architectures.

## Full-campaign projection, not authorisation

| condition | fits | projected_fit_hours | remaining_fits | remaining_projected_fit_hours | reference | already_completed_seed11_anchor_fits |
| --- | --- | --- | --- | --- | --- | --- |
| real | 36 | 2.622857 | 34 | 2.478366 | measured screen batch-scaled; shuffled/ablation use real proxy | 2 |
| shuffled | 36 | 2.622857 | 36 | 2.622857 | measured screen batch-scaled; shuffled/ablation use real proxy | 0 |
| no_graph | 36 | 2.500990 | 34 | 2.363210 | measured screen batch-scaled; shuffled/ablation use real proxy | 2 |
| optional_without_base | 36 | 2.622857 | 36 | 2.622857 | measured screen batch-scaled; shuffled/ablation use real proxy | 0 |

This is a fixed-selected-configuration campaign: 12 quarterly refits × three seeds = 36 fits per condition, not a renewed six-configuration grid. Two seed-11 anchor fits can be reused for real and no graph only if the screen configuration and input fingerprints stay fixed. A full 46-fit retuning campaign is not specified by this screen; it would need an approved grid. Shuffled and optional five-channel ablation timings are unmeasured proxies. If C wins, its validation base extends with five strictly prior quarterly fits from August 2020 to August 2021, serving origins through October 2021. Their original measured cost and checkpoint availability are in [the CPU extension table](../../data/explore/t03/architecture_screen/c_base_campaign_extension.csv); existing exact checkpoints can be reused, but prediction time is additional. No test block access and no full campaign launched.

Sources: `models.architecture_screen`, `evaluation.screen_report`, `visuals.architecture_screen`. [Output index](../../data/explore/t03/architecture_screen/index.md). All report numbers come from saved artifacts. Frozen v2 files remain unchanged.
