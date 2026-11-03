# Protocol v7: final test

Status: FINAL - researcher decisions recorded 3 November 2026. Implementation verified on synthetic data and validation dates only. Execution requires the researcher-created tag `protocol-v7-test`. No final-test data or fits have been opened/run by the agent.

## 1. Fits and sealed-test dates

Fit both boosting baselines using their frozen selected configurations, and B2 real, no graph, within-state shuffled, and real without installed base. B2 uses configuration 3: width 64, learning rate 0.003, weight decay 0.0001, 100 epochs, original per-area scaling, channels, masks, 24-month input window and raw-count Poisson objective. Boosting stays CPU-only, with the historical eight-thread setting recorded in the baseline report. No tuning, architecture change, epoch extension or learned/identity graph condition.

Seeds: **11, 29, 47**. Eight expanding-window quarterly refits: October 2022; January, April, July and October 2023; January, April and July 2024. Monthly forecast origins **October 2022 through September 2024**, serving horizons 1-12; targets through **September 2025**. Each refit serves its origin and the following two origins. Training-target eligibility remains s+h <= fit origin, including partially observed horizon vectors. Training targets start January 2011. Features at each monthly origin use only history through that origin; input scales and fitted parameters stay fixed until the next scheduled refit. Per-area scale remains one plus the area's own mean training count through fit origin, and output rates are multiplied back before scoring. Unknown areas remain masked from loss, evaluation and outgoing messages; isolates remain in the panel.

Each model/condition has 8 x 3 = **24 fits**. Total: **48 CPU boosting fits, 96 GPU B2 fits, 144 fit identities**. No validation checkpoint can replace a later test refit. Retain every completed checkpoint and within-fit checkpoints every five epochs, with deterministic data order and RNG/Adam restoration. Record fit seconds, training curves, peak allocated/reserved GPU memory, input/source hashes and machine/software inventory. Resume completed work rather than refitting it.

The test block remains sealed during implementation verification. Final-test fits/evaluation are researcher commands gated on protocol-v7-test. No such command was run by the agent.

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

The constants above use the report's six-decimal precision, following "exactly as listed". Its linked CSV retains additional digits; those must not silently replace these printed constants. These six-decimal constants were explicitly approved by the researcher. Apply 1-w as the complement of the frozen w. No test-period weight updating, seed-specific optimisation, clipping changes or re-estimation. No additional model fits are needed for the combination.

**Validation evidence distinction:** the candidate evidence in section 4 uses the saved **expanding-window** combination forecasts, whose weights used only earlier observed validation targets. It does not retrospectively apply the nine all-validation weights to those same validation observations. The final test will use the fixed nine constants above. The validation table therefore describes the leakage-controlled development procedure; it is not an independent performance estimate for weights fitted on all validation outcomes.

## 4. Confirmatory testing: two fixed-sequence chains

Two separate fixed-sequence chains, **each at alpha 0.025**. Their orders were fixed by the researcher before final-test access:

- **Accuracy: A7, A2, A1, A4, A3, A6, A5.**
- **Behavioural: B3, B1, B2.**

Within each chain, test in that exact order and stop at the first non-rejection. Do not compute p-values for later hypotheses in the stopped chain, restart it, move alpha between chains, or change ordering from test results. Undefined tests stop their chain as a non-rejection. **B4 is dropped:** its validation effect pointed in the wrong direction. Its historical row below is not a registered final hypothesis.

All superiority tests are **one-sided in the predicted lower-loss direction**: combination below its stated boosting reference, or B2 real below without-installed-base. **Reason:** every hypothesis is directional and was predicted before the test. Non-inferiority remains the one-sided relative-margin procedure below. No Holm adjustment is used.

### Statistical conventions

Use the pinned Diebold Mariano adapter (dieboldmariano 1.1.0), Harvey-Leybourne-Newbold correction, Bartlett HAC through lag h-1, and Student t reference with n-1 degrees of freedom. Use ensemble losses from section 2. For h1 use h=1; for h6 h=6; for twelve-month total h=12. For pooled h1-3, use h=3, hence HAC lags 0-2. Low-maturity tests use the current origin's low tercile, with equal-area loss averaging within that group.

Use the lower-tail one-sided p-value from the HLN-corrected DM statistic for superiority. A rejection requires p < 0.025 and a negative mean tested loss differential. The two-sided p-values retained in the historical CSV are not used for these chains. The same direction rule applies to non-inferiority's margin-shifted differential, not to its unshifted accuracy gain.

For the non-inferiority candidate, let Lc and Lo be origin-level twelve-month total MAE losses. Test **H0: E[Lc - 1.01 Lo] >= 0**, against **H1: E[Lc - 1.01 Lo] < 0**. Apply h=12 HLN/Bartlett DM to Lc and 1.01 Lo, then use the lower-tail one-sided p-value. Include baseline-loss variation and covariance in the differential. The margin is **1% of own boosting's mean loss**, not an absolute one-system margin and not a shift by a fixed sample mean when estimating variance. Positive margin slack = 1.01 mean(Lo) - mean(Lc) favours non-inferiority.

### Historical validation evidence: forecast ensembles; final directions shown

Computed **before the supplied full-draft message**, from saved validation forecasts, not test observations. This is descriptive evidence after extensive validation development; it must not be presented as confirmation. No final chain is executed on validation here. All p-values are raw, without Holm. The validation sample has **36 origins**; final-test tests will have **24**. Effect = reference loss minus candidate loss, so positive is improvement. Monthly MAE units systems/area/month; total MAE systems/area/twelve-month window; MASE unitless.

| ID | Chain | Candidate against reference | Metric/outcome | Group | Candidate loss | Reference loss | Improvement | Improvement % | Validation one-sided DM p |
| --- | --- | --- | --- | --- | ---: | ---: | ---: | ---: | ---: |
| A1 | Accuracy | Combination vs own boosting | MAE h1 | all | 3.143633 | 3.249231 | 0.105599 | 3.249954 | 0.00019227997 |
| A2 | Accuracy | Combination vs neighbour boosting | MAE h1 | all | 3.143633 | 3.231582 | 0.087950 | 2.721562 | 4.6163745e-05 |
| A3 | Accuracy | Combination vs own boosting | MAE pooled h1-3 | all | 3.348561 | 3.420354 | 0.071793 | 2.099005 | 0.01454513 |
| A4 | Accuracy | Combination vs neighbour boosting | MAE pooled h1-3 | all | 3.348561 | 3.405699 | 0.057138 | 1.677725 | 0.0034404416 |
| A5 | Accuracy | Combination vs own boosting | MAE h6 | all | 3.917040 | 3.957506 | 0.040466 | 1.022516 | 0.3100837 |
| A6 | Accuracy | Combination vs own boosting | Total MAE, NI 1% | all | 30.789967 | 30.811300 | 0.021333 | 0.069238 | 0.38443493 |
| A7 | Accuracy | Combination vs own boosting | MASE h1 | all | 0.972983 | 1.053722 | 0.080739 | 7.662272 | 6.2569221e-14 |
| B1 | Behavioural | B2 real vs without base | MAE h1 | all | 3.178828 | 3.304231 | 0.125403 | 3.795216 | 0.0052820634 |
| B2 | Behavioural | B2 real vs without base | Total MAE | all | 32.472620 | 35.801208 | 3.328588 | 9.297419 | 0.023950298 |
| B3 | Behavioural | B2 real vs without base | MAE pooled h1-3 | all | 3.420231 | 3.627889 | 0.207658 | 5.723941 | 0.0022152348 |
| B4 | Behavioural | B2 real vs without base - DROPPED | MAE h1 | low | 0.657236 | 0.651162 | -0.006074 | -0.932739 | 0.94954339 |

A6 has validation margin slack **0.329446 systems/area/twelve-month window**. Its one-sided non-inferiority p is not a superiority p. All other p-values in this table are lower-tail one-sided superiority values. B4 is historical and dropped. Lack of rejection is not evidence of equivalence. Final orders above are the researcher-approved orders, not a conclusion from this validation table.

Auditable [effects and both p-value tails](../../data/explore/t03/v7_chain_evidence/validation_evidence.csv), [origin losses/differentials](../../data/explore/t03/v7_chain_evidence/origin_losses.csv), [figure and plotted CSV](../../data/explore/t03/v7_chain_evidence/index.md), [provenance](../experiments/t03_v7_chain_evidence_checks.json). The CSV also retains the historical seed-averaged-loss view, which is **not** the final-test primary estimand now that section 2 specifies forecast ensembles. Generator: `evaluation.v7_chain_evidence`; log `logs/t03_v7_chain_evidence.log`. Seven candidate-evidence tests passed before the earlier no-run pause. Subsequent synthetic/validation-only implementation checks are explicitly authorised by the final protocol decisions.

## 5. Descriptive reporting and sensitivity checks

Report every horizon 1-12 and twelve-month total, MAE, MASE, RMSE, dynamic maturity terciles, forecast-ensemble scores and each individual seed. Do not add confirmatory tests or alpha spending for these summaries.

For B2 real minus no graph, and real minus shuffled, report the mean origin-level ensemble MAE difference and **95% intervals** for each monthly horizon and total, labelled descriptive. Approved interval method: use the same Bartlett HAC variance of the origin differential and invert the HLN-corrected t statistic: mean difference +/- t(0.975,n-1) x SE_HAC / HLN_factor. Use h equal to the monthly horizon, h=12 for total; n=24. State when a variance/interval is undefined. Negative favours real. These are pointwise intervals, not a simultaneous confidence family or new confirmatory gate. Overlapping horizons and only 24 origins limit precision.

Combination sensitivity: replace the B2 real ensemble with the B2 no-graph ensemble while keeping **exactly the same nine real-derived weights**. Do not estimate no-graph-specific weights from test outcomes. This sensitivity is descriptive and cannot replace the primary combination based on test performance.

Flag target months **July to September 2025**, after batteries became eligible on 1 July 2025. Report their available origin/horizon forecasts separately, with coverage counts and the unchanged PV target definition. Group by **target month**, not forecast origin. Keep these observations in the primary, unchanged-date evaluation. Do not conduct extra confirmatory tests or retune after this subset is inspected. State the certificate/revised-data limitation; no individual behavioural mechanism is identified by aggregate forecast accuracy.

## 6. Resource projection and fixed laptop inventory

The GPU estimates below use calendar/work arithmetic and saved measured B2 fit times, not new timing measurements. The subsequently authorised preparation script verified this arithmetic without test targets or new model fits. Sources: [B2 session progress](../experiments/t03_b2_session_progress.json), each condition's retained fit records, `evaluation.protocol.training_calendar`, and the existing [CPU cost summary](../../data/processed/t03_combination_validation/final_test_cost_summary.csv).

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

**All final-test fits, boosting and all four B2 conditions, run on the original Windows RTX 4070 laptop. No seed split or server switch.** The RTX 5090 option was considered and not selected. Full inventory: [protocol_v7_inventory.json](protocol_v7_inventory.json). GPU details are the inventory recorded during the completed B2 campaign; production GPU commands revalidate them rather than silently accepting another device/driver. No new GPU inventory query was performed by the agent.

| Inventory item | Approved value |
| --- | --- |
| Computer | ZK-SSIPC |
| OS | Windows-11-10.0.26200-SP0 |
| GPU | NVIDIA GeForce RTX 4070 Laptop GPU, 8 GB nominal; 8,585,281,536 bytes reported |
| System RAM | 32 GB, researcher-declared |
| NVIDIA driver | 610.60 |
| Python | 3.13.1 |
| PyTorch / CUDA runtime | 2.7.1+cu128 / 12.8 |
| NumPy / pandas | 2.2.6 / 2.2.3 |
| scikit-learn / SciPy | 1.6.1 / 1.15.3 |
| joblib / threadpoolctl | 1.5.1 / 3.6.0 |
| dieboldmariano / filelock | 1.1.0 / 3.18.0 |

## 7. Gated execution and locked evaluation

Implementation: `models.final_test` for both CPU baselines and each B2 condition; `evaluation.final_test` for one locked evaluation. Every production CLI mode, including `--plan`, validates **protocol-v7-test** before panel access, device initialisation or model work. It compares the working protocol, JSON decisions, inventory, executable/statistical/feature sources and dependency locks with their tagged versions, then checks panel/graph hashes and the original host/software inventory. GPU commands additionally use the original strict GPU inventory lock. Existing validation runners and their manifests remain unchanged.

The restricted target loader reads only authorised prefix cells rather than loading the full target matrix and slicing afterward. Development access is limited to validation history; production fits require tagged authorisation and cannot read after the last permitted input month. Quarterly training builders see history only through their fit origin. The evaluation releases targets through September 2025 ONLY inside the workflow lock, after all six model sets have 24 fit identities each and their checkpoint, forecast, date/code and hash inventories pass.

CPU fits resume between completed fits; an interrupted unfinished boosting fit restarts. Each CPU model and its identity record are saved atomically together. B2 resumes from five-epoch checkpoints using the existing tested optimizer/RNG restoration. Completion markers retain hashes for every fit and forecast. Per-fit records/progress logs update as work finishes. No completed validation fit substitutes for a final fit.

The evaluation lock is shared with fitting. It records the tagged signature and forecast hashes before target access. An interrupted evaluation can resume only with those identical inputs. A completed evaluation verifies its result hashes and returns without reopening targets or rescoring. It writes forecast-ensemble scores, individual seed scores/spread, the frozen real combination, the same-weight no-graph sensitivity, ten chain rows with later p-values missing after a stop, 26 descriptive intervals, battery target-month coverage/metrics, figures and a final report. No automatic model/protocol changes follow the report.

### Researcher commands, after committing and tagging

All from project root on the original laptop; each command writes a separate log. No environment install is required. Expected fit hours are the planning references in section 6, not limits. CPU feature preparation/inference and final evaluation time are additional.

```powershell
& .venv\Scripts\python.exe -m models.final_test --plan 2>&1 | Tee-Object -FilePath logs/t03_v7_test_plan.log
& .venv\Scripts\python.exe -u -m models.final_test --boosting 2>&1 | Tee-Object -FilePath logs/t03_v7_test_boosting.log -Append
& .venv\Scripts\python.exe -u -m models.final_test --condition real 2>&1 | Tee-Object -FilePath logs/t03_v7_test_real.log -Append
& .venv\Scripts\python.exe -u -m models.final_test --condition shuffled 2>&1 | Tee-Object -FilePath logs/t03_v7_test_shuffled.log -Append
& .venv\Scripts\python.exe -u -m models.final_test --condition no_graph 2>&1 | Tee-Object -FilePath logs/t03_v7_test_no_graph.log -Append
& .venv\Scripts\python.exe -u -m models.final_test --condition without_base 2>&1 | Tee-Object -FilePath logs/t03_v7_test_without_base.log -Append
& .venv\Scripts\python.exe -u -m evaluation.final_test --run 2>&1 | Tee-Object -FilePath logs/t03_v7_test_evaluation.log
```

Run sequentially and stop on any error. Ctrl+C once, wait for the prompt, then repeat the same fit command to resume. The plan is metadata-only and expected under one minute. Combined CPU fit planning reference is 2.12 hours; B2 real 2.30, shuffled 5.01, no graph 3.37, without base 2.89 GPU fit hours. Final locked evaluation duration is unmeasured, expected minutes rather than fit hours. Never start concurrent copies. Final artifacts: data/processed/t03_final_test/; final report reports/experiments/protocol_v7_final_test_results.md. These do not exist as study results before researcher execution.

### Preparation checks and stop

Synthetic tests exercise the same scheduling, combination, chain-stop and interval functions, tag failure before data access, changed-input evaluation refusal, and both row/column-major restricted target readers. The synthetic end-to-end output is explicitly a fixture, not final-test evidence. Validation replay uses saved August-October 2019 forecasts/checkpoints only, CPU inference, no refits. Boosting forecasts reproduce exactly; B2 CPU inference differs from saved GPU forecasts by at most 0.0000610352 systems, within the predeclared 0.0002 tolerance. Latest real target materialised during this preparation: October 2019. No test target was materialised and no GPU operation or final-test fit/evaluation was executed by the agent.

[Preparation checks](../experiments/t03_v7_execution_preparation_checks.json), [synthetic/validation-date outputs](../../data/explore/t03/v7_execution_preflight/index.md); logs/t03_v7_execution_preflight_verified.log. Seven earlier candidate-evidence tests preceded the supplied draft's earlier no-run instruction; this implementation's synthetic/validation-only testing is explicitly authorised by the subsequent final decisions. Record final test-suite results in STATUS.md and the preparation report.

**Protocol is final by researcher decision. Stop after implementation verification and hand over commit/tag/run commands. The agent does not stage, commit, tag, fit final models or score the test.**
