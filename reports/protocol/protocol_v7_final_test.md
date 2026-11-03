# Protocol v7: final test - draft for researcher approval

3 November 2026. **DRAFT. NOT APPROVED. DO NOT TAG OR RUN.** This combines the supplied six-part draft with the subsequent instruction to replace its five-test Holm family with two fixed-sequence chains. Both chain orders remain unset. Proposed eventual tag name: `protocol-v7-test`; no tag command is authorised at this stage.

## 1. Fits and sealed-test dates

Fit both boosting baselines using their frozen selected configurations, and B2 real, no graph, within-state shuffled, and real without installed base. B2 uses configuration 3: width 64, learning rate 0.003, weight decay 0.0001, 100 epochs, original per-area scaling, channels, masks, 24-month input window and raw-count Poisson objective. Boosting stays CPU-only, with the historical eight-thread setting recorded in the baseline report. No tuning, architecture change, epoch extension or learned/identity graph condition.

Seeds: **11, 29, 47**. Eight expanding-window quarterly refits: October 2022; January, April, July and October 2023; January, April and July 2024. Monthly forecast origins **October 2022 through September 2024**, serving horizons 1-12; targets through **September 2025**. Each refit serves its origin and the following two origins. Training-target eligibility remains s+h <= fit origin, including partially observed horizon vectors. Training targets start January 2011. Features at each monthly origin use only history through that origin; input scales and fitted parameters stay fixed until the next scheduled refit. Per-area scale remains one plus the area's own mean training count through fit origin, and output rates are multiplied back before scoring. Unknown areas remain masked from loss, evaluation and outgoing messages; isolates remain in the panel.

Each model/condition has 8 x 3 = **24 fits**. Total: **48 CPU boosting fits, 96 GPU B2 fits, 144 fit identities**. No validation checkpoint can replace a later test refit. Retain every completed checkpoint and within-fit checkpoints every five epochs, with deterministic data order and RNG/Adam restoration. Record fit seconds, training curves, peak allocated/reserved GPU memory, input/source hashes and machine/software inventory. Resume completed work rather than refitting it.

The test block remains sealed during drafting. No test forecast, error, interval, p-value or model fit is produced by this document.

## 2. Forecast ensembles and descriptive seed results

For **every model**, average the three saved seed forecasts at each origin, area and horizon **before scoring**. These single forecast ensembles are the primary comparisons and the inputs to confirmatory tests. Report individual seed scores alongside them; do not treat three seeds as three independent time-series observations or substitute their mean loss for ensemble loss. A single ensemble forecast has no seed SD. Use float64 averaging and combination arithmetic, then sum monthly ensemble forecasts for twelve-month totals.

For each origin, first average the applicable loss across observed areas (or the specified maturity group). Confirmatory tests use **24 origin-level ensemble losses**. For pooled horizons 1-3, average the three monthly losses within origin, rather than taking absolute error of a three-month total or treating 72 horizon/origin cells as independent.

MASE retains the accepted training-only seasonal denominator, pooled fallback for zero scales and twelve times the monthly scale for total. Maturity terciles are recomputed at each forecast origin using observed history and the existing tie rule. No test outcomes may change the denominator rule, weights, membership rule or model choices.

## 3. Frozen combination

At each origin/area/horizon, forecast

`w x neighbour-boosting forecast ensemble + (1-w) x B2-real forecast ensemble`.

Select w using that origin's maturity tercile and the horizon band 1-3, 4-6 or 7-12. Freeze the **nine B2_ensemble weights estimated on all 36 validation origins**, exactly as printed in [b2_ensemble_and_combination.md](../experiments/b2_ensemble_and_combination.md):

| Maturity | Horizon band | Neighbour boosting weight w | B2 real weight 1-w |
| --- | --- | ---: | ---: |
| low | 1-3 | 0.100818 | 0.899182 |
| low | 4-6 | 0.486487 | 0.513513 |
| low | 7-12 | 0.780161 | 0.219839 |
| medium | 1-3 | 0.687581 | 0.312419 |
| medium | 4-6 | 0.784779 | 0.215221 |
| medium | 7-12 | 0.831918 | 0.168082 |
| high | 1-3 | 0.492785 | 0.507215 |
| high | 4-6 | 0.659162 | 0.340838 |
| high | 7-12 | 0.682345 | 0.317655 |

The constants above use the report's six-decimal precision, following "exactly as listed". Its linked CSV retains additional digits; those must not silently replace these printed constants. This precision choice is explicit for approval. Apply 1-w as the complement of the frozen w. No test-period weight updating, seed-specific optimisation, clipping changes or re-estimation. No additional model fits are needed for the combination.

**Validation evidence distinction:** the candidate evidence in section 4 uses the saved **expanding-window** combination forecasts, whose weights used only earlier observed validation targets. It does not retrospectively apply the nine all-validation weights to those same validation observations. The final test will use the fixed nine constants above. The validation table therefore describes the leakage-controlled development procedure; it is not an independent performance estimate for weights fitted on all validation outcomes.

## 4. Confirmatory testing: two fixed-sequence chains

Replace the earlier five-test Holm family with **two chains, each at alpha = 0.025**: Accuracy and Behavioural. Within each chain, test in the order fixed by the researcher and **stop that chain at the first non-rejection**. It cannot restart later; no alpha moves between chains. An undefined test cannot reject and stops that chain. Do not choose or reorder tests after examining test results. No Holm adjustment is used within these chains.

**Accuracy order: UNSET. Behavioural order: UNSET.** The A/B identifiers below reproduce the candidate listing only; they are not a chosen sequence. Final orders must be written and approved before any test-block computation or tagging.

### Statistical conventions

Use the pinned Diebold Mariano adapter (dieboldmariano 1.1.0), Harvey-Leybourne-Newbold correction, Bartlett HAC through lag h-1, and Student t reference with n-1 degrees of freedom. Use ensemble losses from section 2. For h1 use h=1; for h6 h=6; for twelve-month total h=12. For pooled h1-3, use h=3, hence HAC lags 0-2. Low-maturity tests use the current origin's low tercile, with equal-area loss averaging within that group.

Superiority tests are **two-sided**, retaining the supplied draft's convention. A superiority rejection supporting improvement requires p < 0.025 and lower mean candidate loss. One-sided lower-loss p-values are included in the linked evidence CSV for transparency, but are not silently substituted for the two-sided tests. Non-inferiority uses the one-sided procedure below. These inferential conventions are draft provisions for approval; the researcher still fixes the two orders.

For the non-inferiority candidate, let Lc and Lo be origin-level twelve-month total MAE losses. Test **H0: E[Lc - 1.01 Lo] >= 0**, against **H1: E[Lc - 1.01 Lo] < 0**. Apply h=12 HLN/Bartlett DM to Lc and 1.01 Lo, then use the lower-tail one-sided p-value. Include baseline-loss variation and covariance in the differential. The margin is **1% of own boosting's mean loss**, not an absolute one-system margin and not a shift by a fixed sample mean when estimating variance. Positive margin slack = 1.01 mean(Lo) - mean(Lc) favours non-inferiority.

### Candidate validation evidence: forecast ensembles

Computed **before the supplied full-draft message**, from saved validation forecasts, not test observations. This is descriptive evidence after extensive validation development; it must not be presented as confirmation. No final chain is executed on validation here. All p-values are raw, without Holm. The validation sample has **36 origins**; final-test tests will have **24**. Effect = reference loss minus candidate loss, so positive is improvement. Monthly MAE units systems/area/month; total MAE systems/area/twelve-month window; MASE unitless.

| ID | Chain | Candidate against reference | Metric/outcome | Group | Candidate loss | Reference loss | Improvement | Improvement % | Validation DM p for proposed test |
| --- | --- | --- | --- | --- | ---: | ---: | ---: | ---: | ---: |
| A1 | Accuracy | Combination vs own boosting | MAE h1 | all | 3.143633 | 3.249231 | 0.105599 | 3.249954 | 0.00038455994 |
| A2 | Accuracy | Combination vs neighbour boosting | MAE h1 | all | 3.143633 | 3.231582 | 0.087950 | 2.721562 | 0.00009232749 |
| A3 | Accuracy | Combination vs own boosting | MAE pooled h1-3 | all | 3.348561 | 3.420354 | 0.071793 | 2.099005 | 0.029090259 |
| A4 | Accuracy | Combination vs neighbour boosting | MAE pooled h1-3 | all | 3.348561 | 3.405699 | 0.057138 | 1.677725 | 0.0068808833 |
| A5 | Accuracy | Combination vs own boosting | MAE h6 | all | 3.917040 | 3.957506 | 0.040466 | 1.022516 | 0.62016740 |
| A6 | Accuracy | Combination vs own boosting | Total MAE, NI margin 1% | all | 30.789967 | 30.811300 | 0.021333 | 0.069238 | 0.38443493, one-sided shifted NI |
| A7 | Accuracy | Combination vs own boosting | MASE h1 | all | 0.972983 | 1.053722 | 0.080739 | 7.662272 | 1.2513844e-13 |
| B1 | Behavioural | B2 real vs without installed base | MAE h1 | all | 3.178828 | 3.304231 | 0.125403 | 3.795216 | 0.010564127 |
| B2 | Behavioural | B2 real vs without installed base | Total MAE | all | 32.472620 | 35.801208 | 3.328588 | 9.297419 | 0.047900595 |
| B3 | Behavioural | B2 real vs without installed base | MAE pooled h1-3 | all | 3.420231 | 3.627889 | 0.207658 | 5.723941 | 0.0044304696 |
| B4 | Behavioural | B2 real vs without installed base | MAE h1 | low only | 0.657236 | 0.651162 | -0.006074 | -0.932739 | 0.10091323 |

A6 has validation margin slack **0.329446 systems/area/twelve-month window**. Its one-sided non-inferiority p is not a superiority p. All other p-values in this table are two-sided. Lack of rejection is not evidence of equivalence. No sequence recommendation is made.

Auditable [effects and both p-value tails](../../data/explore/t03/v7_chain_evidence/validation_evidence.csv), [origin losses/differentials](../../data/explore/t03/v7_chain_evidence/origin_losses.csv), [figure and plotted CSV](../../data/explore/t03/v7_chain_evidence/index.md), [provenance](../experiments/t03_v7_chain_evidence_checks.json). The CSV also retains the historical seed-averaged-loss view, which is **not** the final-test primary estimand now that section 2 specifies forecast ensembles. Generator: `evaluation.v7_chain_evidence`; log `logs/t03_v7_chain_evidence.log`. Seven targeted tests passed before the subsequent no-run instruction; no further test/calculation script was run after it.

## 5. Descriptive reporting and sensitivity checks

Report every horizon 1-12 and twelve-month total, MAE, MASE, RMSE, dynamic maturity terciles, forecast-ensemble scores and each individual seed. Do not add confirmatory tests or alpha spending for these summaries.

For B2 real minus no graph, and real minus shuffled, report the mean origin-level ensemble MAE difference and **95% intervals** for each monthly horizon and total, labelled descriptive. Proposed interval method, for approval: use the same Bartlett HAC variance of the origin differential and invert the HLN-corrected t statistic: mean difference +/- t(0.975,n-1) x SE_HAC / HLN_factor. Use h equal to the monthly horizon, h=12 for total; n=24. State when a variance/interval is undefined. Negative favours real. These are pointwise intervals, not a simultaneous confidence family or new confirmatory gate. Overlapping horizons and only 24 origins limit precision.

Combination sensitivity: replace the B2 real ensemble with the B2 no-graph ensemble while keeping **exactly the same nine real-derived weights**. Do not estimate no-graph-specific weights from test outcomes. This sensitivity is descriptive and cannot replace the primary combination based on test performance.

Flag target months **July to September 2025**, after batteries became eligible on 1 July 2025. Report their available origin/horizon forecasts separately, with coverage counts and the unchanged PV target definition. Group by **target month**, not forecast origin. Keep these observations in the primary, unchanged-date evaluation. Do not conduct extra confirmatory tests or retune after this subset is inspected. State the certificate/revised-data limitation; no individual behavioural mechanism is identified by aggregate forecast accuracy.

## 6. Resource projection and optional seed split

No cost script was run after the no-run instruction. The GPU estimates below are transparent calendar/work arithmetic using saved measured B2 fit times, not new timing measurements. Sources: [B2 session progress](../experiments/t03_b2_session_progress.json), each condition's retained fit records, `evaluation.protocol.training_calendar`, and the existing [CPU cost summary](../../data/processed/t03_combination_validation/final_test_cost_summary.csv).

Summing per-epoch minibatch counts across the 12 validation refit calendars gives 738 minibatches per seed; across the eight test calendars it gives 656. Multiply both by 100 epochs and three seeds, which cancel in the ratio. Thus the projected test/validation work ratio is 656/738 = **8/9**. Apply that ratio to each condition's full 36-identity recorded fit hours **including reused anchors** (those are timing references, not new test reuse). This uses pooled measured seconds per origin minibatch; it assumes throughput remains comparable.

| Resource/condition | Final-test fits | Saved validation fit hours | Approximate final-test hours |
| --- | ---: | ---: | ---: |
| GPU B2 real | 24 | 2.586538 | 2.30 |
| GPU B2 shuffled | 24 | 5.630955 | 5.01 |
| GPU B2 no graph | 24 | 3.794703 | 3.37 |
| GPU B2 without installed base | 24 | 3.249379 | 2.89 |
| GPU total | 96 | 15.261576 | **13.57** |
| CPU own-lag boosting | 24 | historical selected-fit row rates | **0.62** |
| CPU neighbour-lag boosting | 24 | historical selected-fit row rates | **1.50** |
| CPU total | 48 | existing measured-row projection | **2.12** |

The published CPU projection has low/high throughput scenarios of **1.67-2.66 CPU hours**, not a confidence interval or guaranteed bound. Its central condition values are 0.622597 and 1.498520 hours, using the same frozen selections, dates and historical eight-thread setting. These CPU numbers are reused unchanged; the old report's **65-epoch original-B GPU estimates are not used for B2**. GPU estimates explicitly use 100-epoch B2 timings. CPU+GPU hours are different resources; a purely serial single-machine fit schedule is roughly **15.7 fit hours**, excluding feature preparation, inference, disk I/O not already in fit records, final scoring, breaks and verification. Shuffled and real timings differed materially; power, thermal state and background load make these planning references uncertain.

Default: all work on the original Windows RTX 4070 laptop, 8 GB VRAM and 32 GB RAM. Optional split, only if chosen before freezing:

| Machines | Original machine A | Optional machine B | Optional machine C |
| --- | --- | --- | --- |
| 1, default | seeds 11,29,47 | - | - |
| 2 | seed 11 | seeds 29,47 | - |
| 3 | seed 11 | seed 29 | seed 47 |

For each seed, keep **all model conditions and both baselines** on its assigned machine; do not move individual difficult fits opportunistically. Each seed carries 32 GPU fits and 16 CPU fits. Record and approve hardware/software inventories for additional machines, the identical source/protocol/data hashes, deterministic settings and non-overlapping output paths before running. Different device throughput is unmeasured; do not divide the laptop cost by the number of machines and promise that elapsed time. Merge only after checking seed/model/refit identities, dates/codes, checkpoint hashes and forecast completeness. No multi-machine execution or transfer is started by this draft.

## Execution readiness and approval boundary

**Do not run anything now.** The final chain orders and draft approval are pending. The proposed tag name is `protocol-v7-test`; do not create it yet. Existing model runners are validation-only and are not final-test commands. No final-test fit/evaluation runner currently exists in this workspace. Listing fictitious executable commands or pointing the validation commands at test data would be misleading.

After the researcher supplies the final orders and approves the protocol, implement and verify gated final-test commands for: (1) frozen CPU boosting fits, (2) the four resumable B2 conditions, (3) seed/machine merges if chosen, and (4) one locked evaluation that computes forecast ensembles, the fixed combination, both stop-on-non-rejection chains and the predeclared descriptive outputs. All will require the approved tagged protocol and write separate logs. Their **exact run commands remain pending implementation**, not an instruction to execute an unimplemented interface.

This is a concrete protocol proposal and candidate-evidence handover, not execution authorisation. No test targets, features, model fits, forecasts or losses were opened/computed during drafting. Earlier validation computations and their seven targeted tests preceded the supplied full-draft/no-run message; subsequent work was document preparation and read-only inspection of existing artifacts. **Stop for the researcher's final chain orders; no tagging.**
