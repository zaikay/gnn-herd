# Protocol v7 implementation and preparation checks

3 November 2026. Researcher decisions are recorded as **FINAL** in [protocol_v7_final_test.md](../protocol/protocol_v7_final_test.md) and [protocol_v7_test.json](../../configs/protocol_v7_test.json). All final fits remain researcher-run commands requiring the tag `protocol-v7-test`. The agent did not create a tag or run a final fit/evaluation.

## Frozen decisions

- Accuracy order: **A7, A2, A1, A4, A3, A6, A5**.
- Behavioural order: **B3, B1, B2**. B4 is dropped because its validation effect pointed the wrong way.
- Both chains use alpha 0.025 and one-sided lower-loss superiority tests. Reason: every hypothesis is directional and was predicted before the test. Non-inferiority remains one-sided on the differential combination loss minus 1.01 times own-boosting loss.
- Stop each chain at its first non-rejection, including undefined tests. Later p-values are not computed. No Holm adjustment or transfer of alpha.
- The nine approved six-decimal weights and the descriptive Bartlett-HAC/HLN-inverted 95% interval method remain fixed.
- All fits run on the original Windows RTX 4070 laptop, 8 GB VRAM and 32 GB RAM; no seed split or RTX 5090 server change. [Hardware/software inventory](../protocol/protocol_v7_inventory.json) records the original GPU UUID/driver and current CPU-visible Python/packages. No new GPU query was made by the agent; GPU commands revalidate the original inventory.

## Implemented entry points

`models.final_test --boosting` fits both frozen CPU baselines, eight refits and three seeds each. Configurations are fixed at learning rate 0.03, leaf counts 15/31, L2 1, 300 iterations and no early stopping. CPU thread limit is eight. Each model and its identity are saved atomically in one checkpoint bundle. Completed fits are reused; an interrupted unfinished CPU fit restarts. Sessions and per-fit progress are recorded.

`models.final_test --condition real|shuffled|no_graph|without_base` runs the four B2 conditions in order after boosting. Each has 24 unique fit identities, fixed configuration 3 and 100 epochs. It uses the unchanged B2 architectures/features and shared five-epoch checkpoint engine, including optimiser/RNG restoration and replay-time journalling. All old validation runners/checkpoints remain untouched.

`evaluation.final_test --run` is one locked evaluation. It requires complete 24-fit checkpoints/forecasts for all six models and validates their hashes, signatures, dates/codes and forecast values BEFORE releasing targets. It scores three-seed forecast ensembles, individual seeds/spread, the fixed real combination and same-weight no-graph sensitivity; executes the two chains; and reports all horizons/total/maturity metrics, 26 descriptive intervals, battery target-month coverage and figures. A receipt binds the tagged signature and forecast hashes before target access. Only identical inputs may resume an interrupted evaluation. A completed evaluation returns after checking existing outputs, without reopening targets.

Every production CLI mode, including `--plan`, checks `protocol-v7-test` before data or device access. Working protocol/configuration/inventory, executable/statistical/feature sources and dependency locks must equal their tagged versions. Source panel and shuffled-graph hashes, host/software versions and original GPU inventory are enforced. The private figure generator remains ignored by Git; its hash is frozen inside the tagged inventory. No model settings can be changed through CLI flags.

## Target access boundary

The existing `load_panel(through=...)` decodes the entire target matrix before slicing. New production/preparation code uses `features.sealed_panel` instead. It reads only requested target prefixes; skipped future cells are never converted into arrays. For row-major ZIP storage, seeking can traverse compressed bytes without interpreting skipped targets. The tests check actual read ranges for both row- and column-major layouts. Metadata and opaque file hashes do not decode target values.

Without tagged authorisation, any request after October 2022 fails before opening the panel. Production fits can access only permitted history, through each fit/input origin. Only the locked, completeness-checked evaluation can extend the prefix to September 2025. Preparation materialised real history through **October 2019 only**. All other end-to-end target values were explicitly synthetic on validation dates.

## Verification

**188 tests passed**, no skips, one upstream Shapely deprecation warning, **22.18 seconds**. Log: `logs/t03_v7_final_verified_suite.log`. An earlier full-suite run passed 187 tests in 22.88 seconds; after adding the undefined-test/threshold edge-case check, the final run passed 188. Both were below AGENTS.md's five-minute **per-command** limit. The full-suite choice was the agent's implementation verification choice, not a separate explicit user request for a full suite. Testing is finished; no more testing commands are needed for this handover.

Tests cover positive/missing/changed tag authority, every production CLI gate, both prefix-storage layouts, refusal before future file access, exact calendars/budgets/orders, atomic CPU checkpoint reuse without another fit, synthetic scheduling, forecast averaging, fixed constants, per-chain stopping and untested later p-values, undefined tests, p equal to alpha, approved interval arithmetic, target-month subgroup coverage and changed-input evaluation refusal. Existing CPU checkpoint/resume and feature-leakage tests also passed.

Synthetic end-to-end checks produced **416 ensemble score rows, 10 chain rows and 26 interval rows**, with 22 table/figure/report files. They are labelled synthetic/preflight and are not final-test results. The pipeline used six synthetic model forecast sets and validation-date calendars.

CPU inference replay used saved seed-11 August 2019 checkpoints and August-October 2019 inputs. Both boosting models reproduced saved forecasts exactly. B2 real differed from saved GPU forecasts by at most **0.00006103515625 systems**, below the stated absolute/relative tolerance 0.0002. No model was refitted and no GPU operation was performed.

Evidence: [preparation checks JSON](t03_v7_execution_preparation_checks.json); `logs/t03_v7_final_preflight.log`. The first preparation run emitted a joblib warning about missing Windows WMIC physical-core discovery. The final preflight uses an explicit one-core limit; production CPU fits explicitly use eight. The successful final preflight exited normally.

## Resources and artifacts

Calendar-only arithmetic confirms 738 per-epoch minibatches per seed over validation refits and 656 over final-test refits: work ratio 8/9. Saved B2 fit times project **13.565846 GPU fit hours** in total. The existing frozen-baseline projection is **2.121117 CPU fit hours**. No future target values or new training entered these estimates. Preparation records the condition-specific values; final feature preparation, inference, evaluation and session breaks are additional and throughput may vary.

[Execution-flow SVG/CSV/Mermaid](../../visuals/t03/v7_execution_preparation/index.md), [synthetic/validation-only preparation outputs](../../data/explore/t03/v7_execution_preflight/index.md), and private paper-preview copies in reports/figures/v7_preparation/. These are implementation/preparation artifacts. No study final-test output/report has been created.

Exact researcher commit/tag and ordered run commands are in internal/STATUS.md and protocol section 7. No install is required. Nothing was staged, committed or tagged by the agent. Stop here for researcher execution; no further protocol decision or approval is being requested.
