# EXPLORATORY post-test analyses

4 November 2026. Every analysis below is exploratory, after review of the final test. No fits, tuning, new weights or confirmatory amendments. Saved forecast-derived loss tables are the inputs; national actuals reuse the existing CER summary. No target matrix is reopened.

## EXPLORATORY conventions

Three-seed forecasts are averaged before scoring in the main test and validation comparisons. Equal-area losses are averaged per origin, then equally over origins. Maturity terciles and training-only MASE denominators are inherited unchanged. RMSE is the square root of pooled MSE, not mean origin RMSE. Total errors score the sum of twelve forecasts. All DM tests use the existing HLN/Bartlett adapter, lag h-1, n-1 t reference; h=12 for total. Negative candidate-minus-reference differences favour the candidate. Pointwise 95% intervals use the approved HAC/HLN-inverted method. Descriptive p-values are two-sided and unadjusted; exploratory B1/B2 lower-tail p-values are also shown. Multiplicity and post-test selection preclude confirmatory interpretation. Undefined values remain missing.

## EXPLORATORY 1. Claim checks

Strictly lower is required: ties and higher errors are flagged `not_lower`. Percentage gain = 100(reference-candidate)/reference; zero denominators are undefined. Ranges below cover monthly horizons 1-12; total is reported separately in the complete cell table. Broad improvement claims must be limited by every flagged cell.

| candidate | reference | metric | group | min_gain_percent | max_gain_percent | not_lower_horizons |
| --- | --- | --- | --- | --- | --- | --- |
| B2_real | gradient_boosting_neighbours | mae | all | 2.784153 | 11.699706 | 0 |
| B2_real | gradient_boosting_neighbours | mae | high | 1.997641 | 12.324328 | 0 |
| B2_real | gradient_boosting_neighbours | mae | low | 0.958438 | 3.459081 | 0 |
| B2_real | gradient_boosting_neighbours | mae | medium | 5.286656 | 12.523296 | 0 |
| B2_real | gradient_boosting_neighbours | mase | all | 3.531792 | 6.545243 | 0 |
| B2_real | gradient_boosting_neighbours | mase | high | 3.326929 | 15.229843 | 0 |
| B2_real | gradient_boosting_neighbours | mase | low | -6.509574 | 7.689688 | 6 |
| B2_real | gradient_boosting_neighbours | mase | medium | 4.963777 | 11.557999 | 0 |
| B2_real | gradient_boosting_neighbours | rmse | all | -6.881779 | 1.526712 | 11 |
| B2_real | gradient_boosting_neighbours | rmse | high | -7.530515 | 1.482872 | 11 |
| B2_real | gradient_boosting_neighbours | rmse | low | 0.140638 | 1.346656 | 0 |
| B2_real | gradient_boosting_neighbours | rmse | medium | 0.533351 | 5.093843 | 0 |
| B2_real | gradient_boosting_own | mae | all | 3.204444 | 12.136303 | 0 |
| B2_real | gradient_boosting_own | mae | high | 2.526890 | 12.657816 | 0 |
| B2_real | gradient_boosting_own | mae | low | 4.496841 | 5.793417 | 0 |
| B2_real | gradient_boosting_own | mae | medium | 4.774188 | 12.373957 | 0 |
| B2_real | gradient_boosting_own | mase | all | 7.841027 | 9.892085 | 0 |
| B2_real | gradient_boosting_own | mase | high | 3.489072 | 15.411520 | 0 |
| B2_real | gradient_boosting_own | mase | low | 5.361243 | 14.379561 | 0 |
| B2_real | gradient_boosting_own | mase | medium | 4.530428 | 11.523761 | 0 |
| B2_real | gradient_boosting_own | rmse | all | -6.562638 | 1.649260 | 11 |
| B2_real | gradient_boosting_own | rmse | high | -7.198788 | 1.624429 | 11 |
| B2_real | gradient_boosting_own | rmse | low | 1.475512 | 3.801714 | 0 |
| B2_real | gradient_boosting_own | rmse | medium | 0.314416 | 5.119083 | 0 |
| combination | gradient_boosting_neighbours | mae | all | 4.682896 | 8.043734 | 0 |
| combination | gradient_boosting_neighbours | mae | high | 5.646583 | 9.811248 | 0 |
| combination | gradient_boosting_neighbours | mae | low | 0.438303 | 3.219208 | 0 |
| combination | gradient_boosting_neighbours | mae | medium | 2.738527 | 3.990202 | 0 |
| combination | gradient_boosting_neighbours | mase | all | 2.777047 | 5.462374 | 0 |
| combination | gradient_boosting_neighbours | mase | high | 5.911809 | 10.735739 | 0 |
| combination | gradient_boosting_neighbours | mase | low | -1.306232 | 6.967087 | 5 |
| combination | gradient_boosting_neighbours | mase | medium | 2.435444 | 3.585690 | 0 |
| combination | gradient_boosting_neighbours | rmse | all | 2.196271 | 5.487284 | 0 |
| combination | gradient_boosting_neighbours | rmse | high | 2.228573 | 5.694908 | 0 |
| combination | gradient_boosting_neighbours | rmse | low | 0.471313 | 1.277853 | 0 |
| combination | gradient_boosting_neighbours | rmse | medium | 1.772441 | 3.024277 | 0 |
| combination | gradient_boosting_own | mae | all | 5.218700 | 8.498408 | 0 |
| combination | gradient_boosting_own | mae | high | 6.293061 | 10.154294 | 0 |
| combination | gradient_boosting_own | mae | low | 3.606501 | 5.343195 | 0 |
| combination | gradient_boosting_own | mae | medium | 1.969663 | 3.826296 | 0 |
| combination | gradient_boosting_own | mase | all | 6.619077 | 8.847995 | 0 |
| combination | gradient_boosting_own | mase | high | 6.146394 | 10.927048 | 0 |
| combination | gradient_boosting_own | mase | low | 8.918304 | 13.709328 | 0 |
| combination | gradient_boosting_own | mase | medium | 1.806820 | 3.548365 | 0 |
| combination | gradient_boosting_own | rmse | all | 2.398421 | 5.536638 | 0 |
| combination | gradient_boosting_own | rmse | high | 2.456150 | 5.733195 | 0 |
| combination | gradient_boosting_own | rmse | low | 1.536317 | 3.377876 | 0 |
| combination | gradient_boosting_own | rmse | medium | 1.380099 | 3.050068 | 0 |

EXPLORATORY: 59 of 624 metric/model/reference/maturity/outcome cells are not lower.

| candidate | reference | outcome | group | metric | candidate_loss | reference_loss | gain_percent | not_lower |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| combination | gradient_boosting_neighbours | 10 | low | mase | 1.397501 | 1.386158 | -0.818319 | True |
| combination | gradient_boosting_neighbours | 11 | low | mase | 1.396386 | 1.383680 | -0.918284 | True |
| combination | gradient_boosting_neighbours | 12 | low | mase | 1.407414 | 1.389267 | -1.306232 | True |
| combination | gradient_boosting_neighbours | 8 | low | mase | 1.373438 | 1.372396 | -0.075901 | True |
| combination | gradient_boosting_neighbours | 9 | low | mase | 1.384816 | 1.379824 | -0.361800 | True |
| B2_real | gradient_boosting_own | 10 | all | rmse | 7.229125 | 7.102716 | -1.779721 | True |
| B2_real | gradient_boosting_own | 10 | high | rmse | 12.100621 | 11.841087 | -2.191813 | True |
| B2_real | gradient_boosting_own | 11 | all | rmse | 7.410854 | 7.251381 | -2.199213 | True |
| B2_real | gradient_boosting_own | 11 | high | rmse | 12.427114 | 12.100573 | -2.698560 | True |
| B2_real | gradient_boosting_own | 12 | all | rmse | 7.521697 | 7.395125 | -1.711560 | True |
| B2_real | gradient_boosting_own | 12 | high | rmse | 12.616012 | 12.344815 | -2.196854 | True |
| B2_real | gradient_boosting_own | 2 | all | rmse | 5.724929 | 5.648705 | -1.349404 | True |
| B2_real | gradient_boosting_own | 2 | high | rmse | 9.449716 | 9.296842 | -1.644370 | True |
| B2_real | gradient_boosting_own | 3 | all | rmse | 6.080194 | 5.829173 | -4.306283 | True |
| B2_real | gradient_boosting_own | 3 | high | rmse | 10.084873 | 9.622152 | -4.808905 | True |
| B2_real | gradient_boosting_own | 4 | all | rmse | 6.288630 | 6.126551 | -2.645506 | True |
| B2_real | gradient_boosting_own | 4 | high | rmse | 10.450941 | 10.146042 | -3.005100 | True |
| B2_real | gradient_boosting_own | 5 | all | rmse | 6.513582 | 6.240891 | -4.369419 | True |
| B2_real | gradient_boosting_own | 5 | high | rmse | 10.845971 | 10.344133 | -4.851422 | True |
| B2_real | gradient_boosting_own | 6 | all | rmse | 6.688695 | 6.427850 | -4.058044 | True |
| B2_real | gradient_boosting_own | 6 | high | rmse | 11.145337 | 10.667457 | -4.479792 | True |
| B2_real | gradient_boosting_own | 7 | all | rmse | 6.982744 | 6.566169 | -6.344270 | True |
| B2_real | gradient_boosting_own | 7 | high | rmse | 11.658787 | 10.902462 | -6.937193 | True |
| B2_real | gradient_boosting_own | 8 | all | rmse | 7.147850 | 6.707651 | -6.562638 | True |
| B2_real | gradient_boosting_own | 8 | high | rmse | 11.953344 | 11.150634 | -7.198788 | True |
| B2_real | gradient_boosting_own | 9 | all | rmse | 7.143801 | 6.922166 | -3.201819 | True |
| B2_real | gradient_boosting_own | 9 | high | rmse | 11.951360 | 11.525434 | -3.695533 | True |
| B2_real | gradient_boosting_own | total_12 | all | rmse | 56.972452 | 54.299503 | -4.922603 | True |
| B2_real | gradient_boosting_own | total_12 | high | rmse | 96.706538 | 91.645600 | -5.522293 | True |
| B2_real | gradient_boosting_neighbours | 10 | all | rmse | 7.229125 | 7.081757 | -2.080955 | True |
| B2_real | gradient_boosting_neighbours | 10 | high | rmse | 12.100621 | 11.805198 | -2.502484 | True |
| B2_real | gradient_boosting_neighbours | 10 | low | mase | 1.445052 | 1.386158 | -4.248705 | True |
| B2_real | gradient_boosting_neighbours | 11 | all | rmse | 7.410854 | 7.247152 | -2.258856 | True |
| B2_real | gradient_boosting_neighbours | 11 | high | rmse | 12.427114 | 12.094775 | -2.747795 | True |
| B2_real | gradient_boosting_neighbours | 11 | low | mase | 1.449121 | 1.383680 | -4.729466 | True |
| B2_real | gradient_boosting_neighbours | 12 | all | rmse | 7.521697 | 7.391263 | -1.764700 | True |
| B2_real | gradient_boosting_neighbours | 12 | high | rmse | 12.616012 | 12.339803 | -2.238362 | True |
| B2_real | gradient_boosting_neighbours | 12 | low | mase | 1.479702 | 1.389267 | -6.509574 | True |
| B2_real | gradient_boosting_neighbours | 2 | all | rmse | 5.724929 | 5.629334 | -1.698147 | True |
| B2_real | gradient_boosting_neighbours | 2 | high | rmse | 9.449716 | 9.261033 | -2.037387 | True |
| B2_real | gradient_boosting_neighbours | 3 | all | rmse | 6.080194 | 5.817125 | -4.522319 | True |
| B2_real | gradient_boosting_neighbours | 3 | high | rmse | 10.084873 | 9.599755 | -5.053432 | True |
| B2_real | gradient_boosting_neighbours | 4 | all | rmse | 6.288630 | 6.090640 | -3.250721 | True |
| B2_real | gradient_boosting_neighbours | 4 | high | rmse | 10.450941 | 10.078546 | -3.694928 | True |
| B2_real | gradient_boosting_neighbours | 5 | all | rmse | 6.513582 | 6.200840 | -5.043548 | True |
| B2_real | gradient_boosting_neighbours | 5 | high | rmse | 10.845971 | 10.270483 | -5.603315 | True |
| B2_real | gradient_boosting_neighbours | 6 | all | rmse | 6.688695 | 6.410000 | -4.347815 | True |
| B2_real | gradient_boosting_neighbours | 6 | high | rmse | 11.145337 | 10.634816 | -4.800467 | True |
| B2_real | gradient_boosting_neighbours | 7 | all | rmse | 6.982744 | 6.562875 | -6.397639 | True |
| B2_real | gradient_boosting_neighbours | 7 | high | rmse | 11.658787 | 10.896879 | -6.991986 | True |
| B2_real | gradient_boosting_neighbours | 7 | low | mase | 1.376476 | 1.371690 | -0.348900 | True |
| B2_real | gradient_boosting_neighbours | 8 | all | rmse | 7.147850 | 6.687623 | -6.881779 | True |
| B2_real | gradient_boosting_neighbours | 8 | high | rmse | 11.953344 | 11.116235 | -7.530515 | True |
| B2_real | gradient_boosting_neighbours | 8 | low | mase | 1.383325 | 1.372396 | -0.796345 | True |
| B2_real | gradient_boosting_neighbours | 9 | all | rmse | 7.143801 | 6.909387 | -3.392687 | True |
| B2_real | gradient_boosting_neighbours | 9 | high | rmse | 11.951360 | 11.504426 | -3.884894 | True |
| B2_real | gradient_boosting_neighbours | 9 | low | mase | 1.409757 | 1.379824 | -2.169287 | True |
| B2_real | gradient_boosting_neighbours | total_12 | all | rmse | 56.972452 | 54.006799 | -5.491259 | True |
| B2_real | gradient_boosting_neighbours | total_12 | high | rmse | 96.706538 | 91.090892 | -6.164882 | True |

## EXPLORATORY 2. B2/boosting and combination/B2 descriptive DM and intervals

| candidate | reference | group | outcome | origins | mean_MAE_difference | lower95 | upper95 | candidate_loss | reference_loss | gain_reference_minus_candidate | gain_percent | relative_excess_percent | null_reference_multiplier | mean_test_differential | noninferiority_margin_slack | dm_statistic | p_two_sided | p_lower_loss | p_same_convention | status |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| B2_real | gradient_boosting_own | all | 1 | 24 | -0.170401 | -0.277793 | -0.063010 | 2.761449 | 2.931850 | 0.170401 | 5.812069 | -5.812069 | 1.000000 | -0.170401 | nan | -3.282399 | 0.0032656026 | 0.0016328013 | 0.0032656026 | defined |
| B2_real | gradient_boosting_own | all | 2 | 24 | -0.133205 | -0.260652 | -0.005759 | 2.870197 | 3.003403 | 0.133205 | 4.435152 | -4.435152 | 1.000000 | -0.133205 | nan | -2.162131 | 0.041252994 | 0.020626497 | 0.041252994 | defined |
| B2_real | gradient_boosting_own | all | 3 | 24 | -0.097892 | -0.250471 | 0.054687 | 2.956987 | 3.054879 | 0.097892 | 3.204444 | -3.204444 | 1.000000 | -0.097892 | nan | -1.327210 | 0.19746431 | 0.098732154 | 0.19746431 | defined |
| B2_real | gradient_boosting_own | all | 4 | 24 | -0.148326 | -0.354487 | 0.057834 | 3.030969 | 3.179295 | 0.148326 | 4.665382 | -4.665382 | 1.000000 | -0.148326 | nan | -1.488335 | 0.15024644 | 0.075123222 | 0.15024644 | defined |
| B2_real | gradient_boosting_own | all | 5 | 24 | -0.154936 | -0.449349 | 0.139476 | 3.077486 | 3.232422 | 0.154936 | 4.793196 | -4.793196 | 1.000000 | -0.154936 | nan | -1.088644 | 0.28758683 | 0.14379341 | 0.28758683 | defined |
| B2_real | gradient_boosting_own | all | 6 | 24 | -0.179735 | -0.530873 | 0.171404 | 3.133856 | 3.313590 | 0.179735 | 5.424165 | -5.424165 | 1.000000 | -0.179735 | nan | -1.058868 | 0.30065412 | 0.15032706 | 0.30065412 | defined |
| B2_real | gradient_boosting_own | all | 7 | 24 | -0.184686 | -0.714057 | 0.344684 | 3.197812 | 3.382498 | 0.184686 | 5.460056 | -5.460056 | 1.000000 | -0.184686 | nan | -0.721711 | 0.47774569 | 0.23887285 | 0.47774569 | defined |
| B2_real | gradient_boosting_own | all | 8 | 24 | -0.208334 | -0.864768 | 0.448100 | 3.246549 | 3.454883 | 0.208334 | 6.030133 | -6.030133 | 1.000000 | -0.208334 | nan | -0.656534 | 0.51799577 | 0.25899788 | 0.51799577 | defined |
| B2_real | gradient_boosting_own | all | 9 | 24 | -0.284260 | -0.997826 | 0.429305 | 3.288124 | 3.572385 | 0.284260 | 7.957160 | -7.957160 | 1.000000 | -0.284260 | nan | -0.824083 | 0.41835671 | 0.20917835 | 0.41835671 | defined |
| B2_real | gradient_boosting_own | all | 10 | 24 | -0.369085 | -1.248602 | 0.510432 | 3.282453 | 3.651538 | 0.369085 | 10.107659 | -10.107659 | 1.000000 | -0.369085 | nan | -0.868103 | 0.39430615 | 0.19715308 | 0.39430615 | defined |
| B2_real | gradient_boosting_own | all | 11 | 24 | -0.402488 | -1.532801 | 0.727824 | 3.322387 | 3.724875 | 0.402488 | 10.805416 | -10.805416 | 1.000000 | -0.402488 | nan | -0.736620 | 0.46880116 | 0.23440058 | 0.46880116 | defined |
| B2_real | gradient_boosting_own | all | 12 | 24 | -0.460599 | -1.854106 | 0.932908 | 3.334618 | 3.795217 | 0.460599 | 12.136303 | -12.136303 | 1.000000 | -0.460599 | nan | -0.683758 | 0.50095925 | 0.25047962 | 0.50095925 | defined |
| B2_real | gradient_boosting_own | all | total_12 | 24 | -3.389906 | -16.491372 | 9.711560 | 23.022026 | 26.411932 | 3.389906 | 12.834752 | -12.834752 | 1.000000 | -3.389906 | nan | -0.535250 | 0.59761503 | 0.29880752 | 0.59761503 | defined |
| B2_real | gradient_boosting_neighbours | all | 1 | 24 | -0.156747 | -0.256475 | -0.057019 | 2.761449 | 2.918196 | 0.156747 | 5.371369 | -5.371369 | 1.000000 | -0.156747 | nan | -3.251395 | 0.0035180301 | 0.001759015 | 0.0035180301 | defined |
| B2_real | gradient_boosting_neighbours | all | 2 | 24 | -0.115236 | -0.235055 | 0.004582 | 2.870197 | 2.985434 | 0.115236 | 3.859958 | -3.859958 | 1.000000 | -0.115236 | nan | -1.989557 | 0.058659209 | 0.029329604 | 0.058659209 | defined |
| B2_real | gradient_boosting_neighbours | all | 3 | 24 | -0.084685 | -0.238791 | 0.069422 | 2.956987 | 3.041671 | 0.084685 | 2.784153 | -2.784153 | 1.000000 | -0.084685 | nan | -1.136770 | 0.26733988 | 0.13366994 | 0.26733988 | defined |
| B2_real | gradient_boosting_neighbours | all | 4 | 24 | -0.130455 | -0.328623 | 0.067714 | 3.030969 | 3.161423 | 0.130455 | 4.126451 | -4.126451 | 1.000000 | -0.130455 | nan | -1.361798 | 0.18645245 | 0.093226226 | 0.18645245 | defined |
| B2_real | gradient_boosting_neighbours | all | 5 | 24 | -0.134151 | -0.432227 | 0.163925 | 3.077486 | 3.211637 | 0.134151 | 4.177028 | -4.177028 | 1.000000 | -0.134151 | nan | -0.931012 | 0.36151731 | 0.18075866 | 0.36151731 | defined |
| B2_real | gradient_boosting_neighbours | all | 6 | 24 | -0.159157 | -0.518658 | 0.200344 | 3.133856 | 3.293013 | 0.159157 | 4.833179 | -4.833179 | 1.000000 | -0.159157 | nan | -0.915829 | 0.36925942 | 0.18462971 | 0.36925942 | defined |
| B2_real | gradient_boosting_neighbours | all | 7 | 24 | -0.163712 | -0.684749 | 0.357326 | 3.197812 | 3.361524 | 0.163712 | 4.870165 | -4.870165 | 1.000000 | -0.163712 | nan | -0.649979 | 0.52214538 | 0.26107269 | 0.52214538 | defined |
| B2_real | gradient_boosting_neighbours | all | 8 | 24 | -0.179806 | -0.817537 | 0.457925 | 3.246549 | 3.426355 | 0.179806 | 5.247740 | -5.247740 | 1.000000 | -0.179806 | nan | -0.583251 | 0.56539998 | 0.28269999 | 0.56539998 | defined |
| B2_real | gradient_boosting_neighbours | all | 9 | 24 | -0.254214 | -0.929634 | 0.421206 | 3.288124 | 3.542339 | 0.254214 | 7.176452 | -7.176452 | 1.000000 | -0.254214 | nan | -0.778600 | 0.44415244 | 0.22207622 | 0.44415244 | defined |
| B2_real | gradient_boosting_neighbours | all | 10 | 24 | -0.342931 | -1.176030 | 0.490168 | 3.282453 | 3.625384 | 0.342931 | 9.459168 | -9.459168 | 1.000000 | -0.342931 | nan | -0.851528 | 0.40325516 | 0.20162758 | 0.40325516 | defined |
| B2_real | gradient_boosting_neighbours | all | 11 | 24 | -0.379340 | -1.461895 | 0.703216 | 3.322387 | 3.701727 | 0.379340 | 10.247641 | -10.247641 | 1.000000 | -0.379340 | nan | -0.724881 | 0.47583572 | 0.23791786 | 0.47583572 | defined |
| B2_real | gradient_boosting_neighbours | all | 12 | 24 | -0.441834 | -1.774692 | 0.891025 | 3.334618 | 3.776452 | 0.441834 | 11.699706 | -11.699706 | 1.000000 | -0.441834 | nan | -0.685746 | 0.49972752 | 0.24986376 | 0.49972752 | defined |
| B2_real | gradient_boosting_neighbours | all | total_12 | 24 | -3.156899 | -15.987231 | 9.673433 | 23.022026 | 26.178925 | 3.156899 | 12.058933 | -12.058933 | 1.000000 | -3.156899 | nan | -0.508993 | 0.61560588 | 0.30780294 | 0.61560588 | defined |
| combination | B2_real | all | 1 | 24 | 0.010318 | -0.042050 | 0.062687 | 2.771767 | 2.761449 | -0.010318 | -0.373654 | 0.373654 | 1.000000 | 0.010318 | nan | 0.407592 | 0.68734226 | 0.65632887 | 0.68734226 | defined |
| combination | B2_real | all | 2 | 24 | -0.030757 | -0.102957 | 0.041443 | 2.839440 | 2.870197 | 0.030757 | 1.071603 | -1.071603 | 1.000000 | -0.030757 | nan | -0.881247 | 0.38730076 | 0.19365038 | 0.38730076 | defined |
| combination | B2_real | all | 3 | 24 | -0.066017 | -0.158408 | 0.026375 | 2.890970 | 2.956987 | 0.066017 | 2.232561 | -2.232561 | 1.000000 | -0.066017 | nan | -1.478113 | 0.15294231 | 0.076471156 | 0.15294231 | defined |
| combination | B2_real | all | 4 | 24 | -0.017592 | -0.163529 | 0.128345 | 3.013377 | 3.030969 | 0.017592 | 0.580396 | -0.580396 | 1.000000 | -0.017592 | nan | -0.249361 | 0.80529494 | 0.40264747 | 0.80529494 | defined |
| combination | B2_real | all | 5 | 24 | -0.041625 | -0.263534 | 0.180283 | 3.035860 | 3.077486 | 0.041625 | 1.352576 | -1.352576 | 1.000000 | -0.041625 | nan | -0.388036 | 0.70155736 | 0.35077868 | 0.70155736 | defined |
| combination | B2_real | all | 6 | 24 | -0.025139 | -0.299458 | 0.249181 | 3.108717 | 3.133856 | 0.025139 | 0.802165 | -0.802165 | 1.000000 | -0.025139 | nan | -0.189572 | 0.85130756 | 0.42565378 | 0.85130756 | defined |
| combination | B2_real | all | 7 | 24 | -0.033063 | -0.430135 | 0.364010 | 3.164749 | 3.197812 | 0.033063 | 1.033910 | -1.033910 | 1.000000 | -0.033063 | nan | -0.172248 | 0.86474912 | 0.43237456 | 0.86474912 | defined |
| combination | B2_real | all | 8 | 24 | -0.033206 | -0.512923 | 0.446510 | 3.213342 | 3.246549 | 0.033206 | 1.022819 | -1.022819 | 1.000000 | -0.033206 | nan | -0.143194 | 0.88738412 | 0.44369206 | 0.88738412 | defined |
| combination | B2_real | all | 9 | 24 | 0.037945 | -0.465651 | 0.541542 | 3.326070 | 3.288124 | -0.037945 | -1.154012 | 1.154012 | 1.000000 | 0.037945 | nan | 0.155871 | 0.87749488 | 0.56125256 | 0.87749488 | defined |
| combination | B2_real | all | 10 | 24 | 0.088565 | -0.513020 | 0.690151 | 3.371019 | 3.282453 | -0.088565 | -2.698147 | 2.698147 | 1.000000 | 0.088565 | nan | 0.304548 | 0.76344919 | 0.6182754 | 0.76344919 | defined |
| combination | B2_real | all | 11 | 24 | 0.103709 | -0.680158 | 0.887575 | 3.426096 | 3.322387 | -0.103709 | -3.121507 | 3.121507 | 1.000000 | 0.103709 | nan | 0.273691 | 0.78676472 | 0.60661764 | 0.78676472 | defined |
| combination | B2_real | all | 12 | 24 | 0.138066 | -0.820028 | 1.096160 | 3.472684 | 3.334618 | -0.138066 | -4.140385 | 4.140385 | 1.000000 | 0.138066 | nan | 0.298104 | 0.76830029 | 0.61584985 | 0.76830029 | defined |
| combination | B2_real | all | total_12 | 24 | -0.123686 | -9.741080 | 9.493708 | 22.898340 | 23.022026 | 0.123686 | 0.537251 | -0.537251 | 1.000000 | -0.123686 | nan | -0.026604 | 0.97900482 | 0.48950241 | 0.97900482 | defined |

## EXPLORATORY 3. Neighbour boosting: test and validation side by side

| group | outcome | candidate_loss_test | candidate_loss_validation | reference_loss_test | reference_loss_validation | gain_percent_test | gain_percent_validation | p_two_sided_test | p_two_sided_validation |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| all | 1 | 2.918196 | 3.231582 | 2.931850 | 3.249231 | 0.465716 | 0.543175 | 0.18287046 | 0.35178702 |
| all | 10 | 3.625384 | 4.316946 | 3.651538 | 4.316449 | 0.716241 | -0.011527 | 0.39103336 | 0.99060622 |
| all | 11 | 3.701727 | 4.377040 | 3.724875 | 4.384874 | 0.621460 | 0.178656 | 0.47067037 | 0.85121911 |
| all | 12 | 3.776452 | 4.431376 | 3.795217 | 4.428632 | 0.494446 | -0.061954 | 0.64558103 | 0.93566671 |
| all | 2 | 2.985434 | 3.421221 | 3.003403 | 3.430161 | 0.598288 | 0.260642 | 0.1892729 | 0.69097828 |
| all | 3 | 3.041671 | 3.564294 | 3.054879 | 3.581670 | 0.432328 | 0.485134 | 0.51232532 | 0.46866939 |
| all | 4 | 3.161423 | 3.659590 | 3.179295 | 3.671711 | 0.562128 | 0.330132 | 0.33628358 | 0.55292036 |
| all | 5 | 3.211637 | 3.785614 | 3.232422 | 3.795270 | 0.643027 | 0.254423 | 0.33561472 | 0.69356296 |
| all | 6 | 3.293013 | 3.948055 | 3.313590 | 3.957506 | 0.621000 | 0.238809 | 0.3887746 | 0.79701058 |
| all | 7 | 3.361524 | 4.053740 | 3.382498 | 4.061155 | 0.620090 | 0.182583 | 0.34976527 | 0.85086083 |
| all | 8 | 3.426355 | 4.137186 | 3.454883 | 4.136876 | 0.825725 | -0.007500 | 0.27347649 | 0.99439013 |
| all | 9 | 3.542339 | 4.216102 | 3.572385 | 4.224274 | 0.841067 | 0.193470 | 0.31834033 | 0.84788517 |
| all | total_12 | 26.178925 | 31.041908 | 26.411932 | 30.811300 | 0.882203 | -0.748450 | 0.25409745 | 0.49129351 |
| high | 1 | 6.031395 | 6.990253 | 6.064940 | 6.995263 | 0.553104 | 0.071617 | 0.2419753 | 0.92439358 |
| high | 10 | 7.889371 | 9.857724 | 7.946139 | 9.788640 | 0.714417 | -0.705762 | 0.49761848 | 0.59378871 |
| high | 11 | 8.090438 | 10.024070 | 8.138407 | 9.976221 | 0.589414 | -0.479626 | 0.59707699 | 0.70952415 |
| high | 12 | 8.292699 | 10.177069 | 8.324362 | 10.095880 | 0.380365 | -0.804180 | 0.78905874 | 0.46029954 |
| high | 2 | 6.202809 | 7.487094 | 6.250869 | 7.470554 | 0.768862 | -0.221394 | 0.19501436 | 0.7896448 |
| high | 3 | 6.366288 | 7.869390 | 6.400855 | 7.873768 | 0.540037 | 0.055607 | 0.50508515 | 0.94750353 |
| high | 4 | 6.678441 | 8.116941 | 6.731537 | 8.101044 | 0.788774 | -0.196236 | 0.25999598 | 0.78516949 |
| high | 5 | 6.812930 | 8.444669 | 6.868641 | 8.416709 | 0.811097 | -0.332202 | 0.30458127 | 0.68621219 |
| high | 6 | 7.023188 | 8.891849 | 7.075365 | 8.860429 | 0.737447 | -0.354608 | 0.39018462 | 0.76574137 |
| high | 7 | 7.192236 | 9.177513 | 7.241216 | 9.141542 | 0.676403 | -0.393493 | 0.39636136 | 0.7535797 |
| high | 8 | 7.359447 | 9.401127 | 7.425954 | 9.335340 | 0.895608 | -0.704709 | 0.32296343 | 0.61667442 |
| high | 9 | 7.667643 | 9.599040 | 7.736436 | 9.551596 | 0.889218 | -0.496703 | 0.40288542 | 0.7129175 |
| high | total_12 | 59.763192 | 75.022650 | 60.489958 | 73.705874 | 1.201464 | -1.786527 | 0.26732104 | 0.2343689 |
| low | 1 | 0.645175 | 0.669201 | 0.659652 | 0.693366 | 2.194637 | 3.485184 | 1.041929e-10 | 5.7275194e-14 |
| low | 10 | 0.665233 | 0.725583 | 0.692485 | 0.765875 | 3.935515 | 5.260868 | 1.1657304e-08 | 8.9803271e-16 |
| low | 11 | 0.665094 | 0.727279 | 0.692698 | 0.771470 | 3.985019 | 5.728233 | 2.5746399e-11 | 3.9206672e-21 |
| low | 12 | 0.664147 | 0.729101 | 0.692823 | 0.774554 | 4.139062 | 5.868397 | 6.7272051e-15 | 8.401582e-26 |
| low | 2 | 0.651244 | 0.680818 | 0.666369 | 0.705469 | 2.269729 | 3.494339 | 5.0581892e-10 | 5.9057116e-14 |
| low | 3 | 0.651166 | 0.686433 | 0.667562 | 0.711989 | 2.456150 | 3.589313 | 3.9747308e-07 | 3.4265699e-14 |
| low | 4 | 0.655937 | 0.693567 | 0.673317 | 0.719576 | 2.581307 | 3.614431 | 1.5898583e-06 | 7.428553e-14 |
| low | 5 | 0.658123 | 0.699912 | 0.676235 | 0.728565 | 2.678392 | 3.932773 | 6.2657149e-06 | 1.4787953e-11 |
| low | 6 | 0.663135 | 0.705755 | 0.682424 | 0.736334 | 2.826525 | 4.152906 | 1.763458e-06 | 1.8697387e-11 |
| low | 7 | 0.665963 | 0.708377 | 0.686795 | 0.741754 | 3.033301 | 4.499661 | 6.7820924e-07 | 3.8377721e-14 |
| low | 8 | 0.665925 | 0.711654 | 0.690399 | 0.747818 | 3.544952 | 4.835957 | 6.047516e-07 | 4.3881291e-13 |
| low | 9 | 0.665935 | 0.719132 | 0.691571 | 0.758111 | 3.706920 | 5.141594 | 1.3844377e-07 | 5.0904561e-14 |
| low | total_12 | 3.747494 | 3.888301 | 4.006210 | 4.317597 | 6.457857 | 9.942939 | 3.6459191e-09 | 8.8869701e-29 |
| medium | 1 | 2.078017 | 2.035292 | 2.070957 | 2.059064 | -0.340911 | 1.154510 | 0.094004351 | 6.0017075e-05 |
| medium | 10 | 2.321550 | 2.367532 | 2.315990 | 2.394832 | -0.240072 | 1.139959 | 0.66067689 | 0.033349247 |
| medium | 11 | 2.349649 | 2.379771 | 2.343521 | 2.406929 | -0.261455 | 1.128341 | 0.65771279 | 0.041456846 |
| medium | 12 | 2.372510 | 2.387957 | 2.368466 | 2.415461 | -0.170719 | 1.138663 | 0.74231533 | 0.095592794 |
| medium | 2 | 2.102249 | 2.095750 | 2.092970 | 2.114459 | -0.443306 | 0.884821 | 0.11697489 | 0.0069045066 |
| medium | 3 | 2.107561 | 2.137060 | 2.096219 | 2.159253 | -0.541073 | 1.027848 | 0.2320514 | 0.00026744252 |
| medium | 4 | 2.149893 | 2.168261 | 2.133031 | 2.194514 | -0.790513 | 1.196303 | 0.079218297 | 1.3121584e-05 |
| medium | 5 | 2.163856 | 2.212261 | 2.152389 | 2.240537 | -0.532781 | 1.262010 | 0.32076036 | 0.00015965455 |
| medium | 6 | 2.192715 | 2.246561 | 2.182981 | 2.275755 | -0.445893 | 1.282789 | 0.42752239 | 0.00036684588 |
| medium | 7 | 2.226372 | 2.275330 | 2.219483 | 2.300170 | -0.310380 | 1.079912 | 0.49924915 | 0.010534218 |
| medium | 8 | 2.253693 | 2.298777 | 2.248295 | 2.327469 | -0.240104 | 1.232757 | 0.6926198 | 0.025184295 |
| medium | 9 | 2.293438 | 2.330134 | 2.289146 | 2.363116 | -0.187466 | 1.395709 | 0.74839669 | 0.019605775 |
| medium | total_12 | 15.026089 | 14.214772 | 14.739629 | 14.410430 | -1.943468 | 1.357751 | 0.071301003 | 0.10515132 |

## EXPLORATORY 4. Installed-base B1/B2 after the stopped chain

| candidate | reference | group | outcome | origins | mean_MAE_difference | lower95 | upper95 | candidate_loss | reference_loss | gain_reference_minus_candidate | gain_percent | relative_excess_percent | null_reference_multiplier | mean_test_differential | noninferiority_margin_slack | dm_statistic | p_two_sided | p_lower_loss | p_same_convention | status | hypothesis |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| B2_real | B2_without_base | all | 1 | 24 | -0.043729 | -0.106534 | 0.019075 | 2.761449 | 2.805178 | 0.043729 | 1.558879 | -1.558879 | 1.000000 | -0.043729 | nan | -1.440365 | 0.1632389 | 0.081619451 | 0.1632389 | defined | B1 |
| B2_real | B2_without_base | all | total_12 | 24 | 0.322828 | -7.035537 | 7.681193 | 23.022026 | 22.699198 | -0.322828 | -1.422200 | 1.422200 | 1.000000 | 0.322828 | nan | 0.090757 | 0.92847172 | 0.53576414 | 0.92847172 | defined | B2 |

EXPLORATORY B1/B2 do not resume the stopped behavioural chain. Original B1/B2 remain untested confirmatorily. The complete installed-base tables include every maturity/horizon and signed errors for both models. Removing base is the candidate in the effect table: negative percentage gain means worse error after removal.

## EXPLORATORY 5. Signed errors and national actuals

Signed error is forecast minus actual, systems/area/month, averaged across observed matched areas. Heatmaps show origin by horizon; the adjacent national plot uses target month, November 2022-September 2025, without counting repeated forecast targets multiple times. National totals include unmatched CER postcodes; matched-panel totals are also supplied. The panels have different aggregation units and do not identify causes or battery effects.

![EXPLORATORY signed error and national actuals](../../data/explore/t03/test_exploratory/exploratory_signed_error.png)

## EXPLORATORY 6. Individual seed robustness

Both matched individual-seed boosting and primary boosting-ensemble references are supplied. These answer different questions; seeds are not independent origin replications. No seed is selected. All MAE, MASE and RMSE cells at horizons 1,6,12,total are in the CSV.

| candidate | reference | outcome | group | metric | candidate_loss | reference_loss | gain_percent | not_lower | seed | reference_view |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| B2_real | gradient_boosting_own | 1 | all | mae | 2.820338 | 2.935496 | 3.922942 | False | 11 | matched individual boosting seed |
| B2_real | gradient_boosting_own | 12 | all | mae | 3.424075 | 3.796892 | 9.818986 | False | 11 | matched individual boosting seed |
| B2_real | gradient_boosting_own | 6 | all | mae | 3.292598 | 3.315534 | 0.691771 | False | 11 | matched individual boosting seed |
| B2_real | gradient_boosting_own | total_12 | all | mae | 25.212580 | 26.481541 | 4.791869 | False | 11 | matched individual boosting seed |
| B2_real | gradient_boosting_neighbours | 1 | all | mae | 2.820338 | 2.926755 | 3.635980 | False | 11 | matched individual boosting seed |
| B2_real | gradient_boosting_neighbours | 12 | all | mae | 3.424075 | 3.783419 | 9.497851 | False | 11 | matched individual boosting seed |
| B2_real | gradient_boosting_neighbours | 6 | all | mae | 3.292598 | 3.298586 | 0.181524 | False | 11 | matched individual boosting seed |
| B2_real | gradient_boosting_neighbours | total_12 | all | mae | 25.212580 | 26.296682 | 4.122582 | False | 11 | matched individual boosting seed |
| B2_real | gradient_boosting_own | 1 | all | mae | 2.820338 | 2.931850 | 3.803449 | False | 11 | boosting three-seed forecast ensemble |
| B2_real | gradient_boosting_own | 12 | all | mae | 3.424075 | 3.795217 | 9.779199 | False | 11 | boosting three-seed forecast ensemble |
| B2_real | gradient_boosting_own | 6 | all | mae | 3.292598 | 3.313590 | 0.633507 | False | 11 | boosting three-seed forecast ensemble |
| B2_real | gradient_boosting_own | total_12 | all | mae | 25.212580 | 26.411932 | 4.540948 | False | 11 | boosting three-seed forecast ensemble |
| B2_real | gradient_boosting_neighbours | 1 | all | mae | 2.820338 | 2.918196 | 3.353351 | False | 11 | boosting three-seed forecast ensemble |
| B2_real | gradient_boosting_neighbours | 12 | all | mae | 3.424075 | 3.776452 | 9.330889 | False | 11 | boosting three-seed forecast ensemble |
| B2_real | gradient_boosting_neighbours | 6 | all | mae | 3.292598 | 3.293013 | 0.012585 | False | 11 | boosting three-seed forecast ensemble |
| B2_real | gradient_boosting_neighbours | total_12 | all | mae | 25.212580 | 26.178925 | 3.691310 | False | 11 | boosting three-seed forecast ensemble |
| B2_real | gradient_boosting_own | 1 | all | mae | 2.784843 | 2.945885 | 5.466692 | False | 29 | matched individual boosting seed |
| B2_real | gradient_boosting_own | 12 | all | mae | 3.375698 | 3.801518 | 11.201324 | False | 29 | matched individual boosting seed |
| B2_real | gradient_boosting_own | 6 | all | mae | 3.146007 | 3.320358 | 5.250983 | False | 29 | matched individual boosting seed |
| B2_real | gradient_boosting_own | total_12 | all | mae | 22.692967 | 26.513489 | 14.409730 | False | 29 | matched individual boosting seed |
| B2_real | gradient_boosting_neighbours | 1 | all | mae | 2.784843 | 2.925324 | 4.802245 | False | 29 | matched individual boosting seed |
| B2_real | gradient_boosting_neighbours | 12 | all | mae | 3.375698 | 3.779958 | 10.694843 | False | 29 | matched individual boosting seed |
| B2_real | gradient_boosting_neighbours | 6 | all | mae | 3.146007 | 3.299637 | 4.655967 | False | 29 | matched individual boosting seed |
| B2_real | gradient_boosting_neighbours | total_12 | all | mae | 22.692967 | 26.256723 | 13.572739 | False | 29 | matched individual boosting seed |
| B2_real | gradient_boosting_own | 1 | all | mae | 2.784843 | 2.931850 | 5.014139 | False | 29 | boosting three-seed forecast ensemble |
| B2_real | gradient_boosting_own | 12 | all | mae | 3.375698 | 3.795217 | 11.053902 | False | 29 | boosting three-seed forecast ensemble |
| B2_real | gradient_boosting_own | 6 | all | mae | 3.146007 | 3.313590 | 5.057457 | False | 29 | boosting three-seed forecast ensemble |
| B2_real | gradient_boosting_own | total_12 | all | mae | 22.692967 | 26.411932 | 14.080626 | False | 29 | boosting three-seed forecast ensemble |
| B2_real | gradient_boosting_neighbours | 1 | all | mae | 2.784843 | 2.918196 | 4.569705 | False | 29 | boosting three-seed forecast ensemble |
| B2_real | gradient_boosting_neighbours | 12 | all | mae | 3.375698 | 3.776452 | 10.611925 | False | 29 | boosting three-seed forecast ensemble |
| B2_real | gradient_boosting_neighbours | 6 | all | mae | 3.146007 | 3.293013 | 4.464180 | False | 29 | boosting three-seed forecast ensemble |
| B2_real | gradient_boosting_neighbours | total_12 | all | mae | 22.692967 | 26.178925 | 13.315896 | False | 29 | boosting three-seed forecast ensemble |
| B2_real | gradient_boosting_own | 1 | all | mae | 2.772775 | 2.932044 | 5.432014 | False | 47 | matched individual boosting seed |
| B2_real | gradient_boosting_own | 12 | all | mae | 3.318083 | 3.796702 | 12.606189 | False | 47 | matched individual boosting seed |
| B2_real | gradient_boosting_own | 6 | all | mae | 3.071803 | 3.315847 | 7.359952 | False | 47 | matched individual boosting seed |
| B2_real | gradient_boosting_own | total_12 | all | mae | 22.191399 | 26.435656 | 16.055046 | False | 47 | matched individual boosting seed |
| B2_real | gradient_boosting_neighbours | 1 | all | mae | 2.772775 | 2.918772 | 5.002025 | False | 47 | matched individual boosting seed |
| B2_real | gradient_boosting_neighbours | 12 | all | mae | 3.318083 | 3.777376 | 12.159065 | False | 47 | matched individual boosting seed |
| B2_real | gradient_boosting_neighbours | 6 | all | mae | 3.071803 | 3.292729 | 6.709529 | False | 47 | matched individual boosting seed |
| B2_real | gradient_boosting_neighbours | total_12 | all | mae | 22.191399 | 26.193756 | 15.279812 | False | 47 | matched individual boosting seed |
| B2_real | gradient_boosting_own | 1 | all | mae | 2.772775 | 2.931850 | 5.425757 | False | 47 | boosting three-seed forecast ensemble |
| B2_real | gradient_boosting_own | 12 | all | mae | 3.318083 | 3.795217 | 12.571999 | False | 47 | boosting three-seed forecast ensemble |
| B2_real | gradient_boosting_own | 6 | all | mae | 3.071803 | 3.313590 | 7.296846 | False | 47 | boosting three-seed forecast ensemble |
| B2_real | gradient_boosting_own | total_12 | all | mae | 22.191399 | 26.411932 | 15.979644 | False | 47 | boosting three-seed forecast ensemble |
| B2_real | gradient_boosting_neighbours | 1 | all | mae | 2.772775 | 2.918196 | 4.983249 | False | 47 | boosting three-seed forecast ensemble |
| B2_real | gradient_boosting_neighbours | 12 | all | mae | 3.318083 | 3.776452 | 12.137567 | False | 47 | boosting three-seed forecast ensemble |
| B2_real | gradient_boosting_neighbours | 6 | all | mae | 3.071803 | 3.293013 | 6.717562 | False | 47 | boosting three-seed forecast ensemble |
| B2_real | gradient_boosting_neighbours | total_12 | all | mae | 22.191399 | 26.178925 | 15.231817 | False | 47 | boosting three-seed forecast ensemble |

## EXPLORATORY complete outputs and provenance

Generator: `evaluation.test_exploratory`; visual generator: `visuals.test_exploratory`. Log: `logs/t03_test_exploratory.log`. Every CSV has an explicit exploratory scope column. No frozen or confirmatory artifact is overwritten.

- [EXPLORATORY exploratory_claim_checks](../../data/explore/t03/test_exploratory/exploratory_claim_checks.csv)
- [EXPLORATORY exploratory_gain_ranges](../../data/explore/t03/test_exploratory/exploratory_gain_ranges.csv)
- [EXPLORATORY exploratory_model_dm](../../data/explore/t03/test_exploratory/exploratory_model_dm.csv)
- [EXPLORATORY exploratory_neighbour_dm](../../data/explore/t03/test_exploratory/exploratory_neighbour_dm.csv)
- [EXPLORATORY exploratory_neighbour_side_by_side](../../data/explore/t03/test_exploratory/exploratory_neighbour_side_by_side.csv)
- [EXPLORATORY exploratory_neighbour_metric_side_by_side](../../data/explore/t03/test_exploratory/exploratory_neighbour_metric_side_by_side.csv)
- [EXPLORATORY exploratory_installed_base](../../data/explore/t03/test_exploratory/exploratory_installed_base.csv)
- [EXPLORATORY exploratory_B1_B2](../../data/explore/t03/test_exploratory/exploratory_B1_B2.csv)
- [EXPLORATORY exploratory_installed_base_effect](../../data/explore/t03/test_exploratory/exploratory_installed_base_effect.csv)
- [EXPLORATORY exploratory_signed_error](../../data/explore/t03/test_exploratory/exploratory_signed_error.csv)
- [EXPLORATORY exploratory_national_actuals](../../data/explore/t03/test_exploratory/exploratory_national_actuals.csv)
- [EXPLORATORY exploratory_seed_robustness](../../data/explore/t03/test_exploratory/exploratory_seed_robustness.csv)

[EXPLORATORY output index](../../data/explore/t03/test_exploratory/index.md). Private copies: visuals/t03/test_exploratory/ and reports/figures/test_exploratory/.
