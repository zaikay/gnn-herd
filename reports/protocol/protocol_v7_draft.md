# Protocol v7 draft - confirmatory testing amendment

**Superseded section-only working note.** The researcher subsequently supplied the full draft. Use [protocol_v7_final_test.md](protocol_v7_final_test.md), which incorporates the six sections, forecast-ensemble convention and the later two-chain change. Candidate CSVs below retain both aggregation views for audit; only forecast ensembles are primary in the full draft. No tag or run is authorised.

3 November 2026. **DRAFT - DO NOT TAG.** No existing v7 draft was found in this workspace. This file records only the requested replacement section 4 and validation evidence; no other final-test provisions are invented. Final chain order remains for the researcher. Test block stays sealed.

## 4. Confirmatory testing

Replace the proposed five-test Holm family with **two separate fixed-sequence chains, each at alpha = 0.025**: Accuracy and Behavioural. Within each chain, test in the researcher's fixed order and stop that chain at its first non-rejection. A stopped chain cannot restart at a later candidate; no alpha is transferred between chains. Undefined tests cannot reject and stop their chain. Orders must be written before any final-test scoring and remain unchanged afterward. **Both orders are currently UNSET.** Candidate IDs below are labels in the supplied listing, not a chosen sequence; the validation tables do not execute or rank chains.

### Conventions and unresolved draft context

Use the existing origin-averaged Diebold Mariano adapter (dieboldmariano 1.1.0), Harvey-Leybourne-Newbold correction, Bartlett HAC through lag h-1 and Student t reference with n-1 degrees of freedom. All validation evidence uses 36 origins, not 108 seed-origin observations. For pooled horizons 1-3, average absolute errors over those three horizons within each origin/group and then over seeds; **h=3** (HAC lags 0-2). This is not absolute error of a three-month sum and not three independent tests. Horizon 1 uses h=1, horizon 6 h=6, and twelve-month total h=12. MASE retains the existing training-only seasonal scales and pooled fallback. Low maturity is the dynamic group at each origin; no area is dropped from other comparisons.

The historical convention scores each seed's forecast, averages area/horizon losses within origin, and then averages the three seed losses before DM. Its results are shown first. A separate forecast-ensemble view averages forecasts across seeds BEFORE scoring. These are different estimands: the absence of the referenced v7 draft means its final aggregation cannot be inferred. Both are explicitly shown rather than silently replacing one with the other. The researcher can identify the intended aggregation when supplying the final orders.

Combination means the already saved **expanding-window learned mixture of neighbour boosting and the B2 real ensemble**, with one shared weight per maturity/band pooled across three boosting-seed pairs. It is not the matched-individual-B2 mixture and does not use descriptive all-36-origin weights. In the forecast-ensemble view, average its three boosting-seed-paired combination forecasts; each boosting/B2 control is also averaged across its three seeds first. No weights are re-estimated for this task.

Superiority evidence retains the existing **two-sided** DM p-value. The directional lower-loss p-value is also displayed to make the alternative explicit; changing superiority tests to one-sided is not silently assumed by this amendment. Under the existing convention, a superiority rejection requires the two-sided p < 0.025 and the candidate's mean loss to be lower. Non-inferiority is necessarily directional, as specified next. No Holm adjustment is applied to these candidate evidence tables or within a fixed-sequence chain.

### One-percent non-inferiority candidate

Let Lc and Lo be the origin-level twelve-month total MAE losses of the combination and own-lag boosting. Test **H0: E[Lc - 1.01 Lo] >= 0**, versus **H1: E[Lc - 1.01 Lo] < 0**. Apply the same h=12 HLN/Bartlett DM calculation to Lc and 1.01 Lo; the p-value for this candidate is the **one-sided lower tail**. This uses a 1% relative mean-loss margin and includes reference-loss variation/covariance. The unshifted gain and percentage gain remain reported. Positive margin slack = 1.01 mean(Lo) - mean(Lc) favours non-inferiority. The displayed two-sided NI p-value concerns this shifted boundary, not equality with unscaled own boosting.

### Validation candidate evidence - descriptive only

Effects: gain = reference mean loss minus candidate mean loss; positive means lower candidate error. Percentage gain divides that gain by the reference mean loss. Monthly MAE units are systems/area/month; total MAE units systems/area/twelve-month window; MASE unitless. These validation p-values follow model/combination development and are not confirmatory evidence. No final-test observations are opened. All raw p-values are unadjusted. No chain order is recommended from these tables.

#### Historical convention: seed-averaged origin losses

| candidate_id | chain | comparison | metric | outcome | group | candidate_loss | reference_loss | gain_reference_minus_candidate | gain_percent |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| A1 | Accuracy | combination vs own | mae | 1 | all | 3.145794 | 3.256133 | 0.110339 | 3.388657 |
| A2 | Accuracy | combination vs neighbours | mae | 1 | all | 3.145794 | 3.240554 | 0.094760 | 2.924195 |
| A3 | Accuracy | combination vs own | mae | 1-3 | all | 3.350644 | 3.426964 | 0.076319 | 2.227026 |
| A4 | Accuracy | combination vs neighbours | mae | 1-3 | all | 3.350644 | 3.414595 | 0.063951 | 1.872873 |
| A5 | Accuracy | combination vs own | mae | 6 | all | 3.918923 | 3.961972 | 0.043050 | 1.086571 |
| A6 | Accuracy | combination vs own | mae | total_12 | all | 30.809576 | 30.866269 | 0.056693 | 0.183674 |
| A7 | Accuracy | combination vs own | mase | 1 | all | 0.973150 | 1.054212 | 0.081062 | 7.689350 |
| B1 | Behavioural | real vs without_base | mae | 1 | all | 3.219297 | 3.373779 | 0.154483 | 4.578922 |
| B2 | Behavioural | real vs without_base | mae | total_12 | all | 32.758551 | 36.378953 | 3.620402 | 9.951914 |
| B3 | Behavioural | real vs without_base | mae | 1-3 | all | 3.460165 | 3.696113 | 0.235948 | 6.383681 |
| B4 | Behavioural | real vs without_base | mae | 1 | low | 0.658197 | 0.652571 | -0.005626 | -0.862170 |

| candidate_id | test | DM_h | dm_statistic | p_two_sided | p_lower_loss | p_same_convention | noninferiority_margin_slack |
| --- | --- | --- | --- | --- | --- | --- | --- |
| A1 | superiority | 1 | -4.119750 | 0.00022047914 | 0.00011023957 | 0.00022047914 | nan |
| A2 | superiority | 1 | -4.748155 | 3.4249155e-05 | 1.7124578e-05 | 3.4249155e-05 | nan |
| A3 | superiority | 3 | -2.430833 | 0.020326822 | 0.010163411 | 0.020326822 | nan |
| A4 | superiority | 3 | -3.249452 | 0.0025559936 | 0.0012779968 | 0.0025559936 | nan |
| A5 | superiority | 6 | -0.531965 | 0.5981112 | 0.2990556 | 0.5981112 | nan |
| A6 | NI 1 percent | 12 | -0.328035 | 0.74483958 | 0.37241979 | 0.37241979 | 0.365356 |
| A7 | superiority | 1 | -11.710291 | 1.1664823e-13 | 5.8324114e-14 | 1.1664823e-13 | nan |
| B1 | superiority | 1 | -3.217036 | 0.0027886174 | 0.0013943087 | 0.0027886174 | nan |
| B2 | superiority | 12 | -2.330273 | 0.025682596 | 0.012841298 | 0.025682596 | nan |
| B3 | superiority | 3 | -3.439224 | 0.0015244147 | 0.00076220734 | 0.0015244147 | nan |
| B4 | superiority | 1 | 1.549338 | 0.13029658 | 0.93485171 | 0.13029658 | nan |

#### Separate view: seed-average forecasts scored once

| candidate_id | chain | comparison | metric | outcome | group | candidate_loss | reference_loss | gain_reference_minus_candidate | gain_percent |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| A1 | Accuracy | combination vs own | mae | 1 | all | 3.143633 | 3.249231 | 0.105599 | 3.249954 |
| A2 | Accuracy | combination vs neighbours | mae | 1 | all | 3.143633 | 3.231582 | 0.087950 | 2.721562 |
| A3 | Accuracy | combination vs own | mae | 1-3 | all | 3.348561 | 3.420354 | 0.071793 | 2.099005 |
| A4 | Accuracy | combination vs neighbours | mae | 1-3 | all | 3.348561 | 3.405699 | 0.057138 | 1.677725 |
| A5 | Accuracy | combination vs own | mae | 6 | all | 3.917040 | 3.957506 | 0.040466 | 1.022516 |
| A6 | Accuracy | combination vs own | mae | total_12 | all | 30.789967 | 30.811300 | 0.021333 | 0.069238 |
| A7 | Accuracy | combination vs own | mase | 1 | all | 0.972983 | 1.053722 | 0.080739 | 7.662272 |
| B1 | Behavioural | real vs without_base | mae | 1 | all | 3.178828 | 3.304231 | 0.125403 | 3.795216 |
| B2 | Behavioural | real vs without_base | mae | total_12 | all | 32.472620 | 35.801208 | 3.328588 | 9.297419 |
| B3 | Behavioural | real vs without_base | mae | 1-3 | all | 3.420231 | 3.627889 | 0.207658 | 5.723941 |
| B4 | Behavioural | real vs without_base | mae | 1 | low | 0.657236 | 0.651162 | -0.006074 | -0.932739 |

| candidate_id | test | DM_h | dm_statistic | p_two_sided | p_lower_loss | p_same_convention | noninferiority_margin_slack |
| --- | --- | --- | --- | --- | --- | --- | --- |
| A1 | superiority | 1 | -3.927764 | 0.00038455994 | 0.00019227997 | 0.00038455994 | nan |
| A2 | superiority | 1 | -4.415753 | 9.232749e-05 | 4.6163745e-05 | 9.232749e-05 | nan |
| A3 | superiority | 3 | -2.275766 | 0.029090259 | 0.01454513 | 0.029090259 | nan |
| A4 | superiority | 3 | -2.872123 | 0.0068808833 | 0.0034404416 | 0.0068808833 | nan |
| A5 | superiority | 6 | -0.500053 | 0.6201674 | 0.3100837 | 0.6201674 | nan |
| A6 | NI 1 percent | 12 | -0.296144 | 0.76886986 | 0.38443493 | 0.38443493 | 0.329446 |
| A7 | superiority | 1 | -11.681006 | 1.2513844e-13 | 6.2569221e-14 | 1.2513844e-13 | nan |
| B1 | superiority | 1 | -2.701710 | 0.010564127 | 0.0052820634 | 0.010564127 | nan |
| B2 | superiority | 12 | -2.050134 | 0.047900595 | 0.023950298 | 0.047900595 | nan |
| B3 | superiority | 3 | -3.042381 | 0.0044304696 | 0.0022152348 | 0.0044304696 | nan |
| B4 | superiority | 1 | 1.684862 | 0.10091323 | 0.94954339 | 0.10091323 | nan |

The `p_same_convention` column is the existing two-sided p for superiority and the margin-shifted one-sided p for NI. Directional p-values are supplementary for superiority until explicitly chosen. The two aggregation views are alternative descriptive calculations, not additional registered hypotheses or extra alpha allocations.

Candidate listing: A1 combination/own MAE h1; A2 combination/neighbour MAE h1; A3 combination/own pooled MAE h1-3; A4 combination/neighbour pooled MAE h1-3; A5 combination/own MAE h6; A6 total-MAE 1% NI against own; A7 combination/own MASE h1. B1 real/without-base MAE h1; B2 same total; B3 same pooled MAE h1-3; B4 same h1, low maturity only.

Evidence CSV: [candidate effects and p-values](../../data/explore/t03/v7_chain_evidence/validation_evidence.csv), [origin losses and tested differentials](../../data/explore/t03/v7_chain_evidence/origin_losses.csv), [evidence figure and plotted CSV](../../data/explore/t03/v7_chain_evidence/index.md), [provenance](../experiments/t03_v7_chain_evidence_checks.json). Generator: `evaluation.v7_chain_evidence`; log `logs/t03_v7_chain_evidence.log`. No model fits, weight re-estimation, GPU use, test scoring, git mutation or tag. **Stop for researcher final orders; do not freeze or execute this draft.**
