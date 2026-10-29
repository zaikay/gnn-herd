# Task 3 pilot report — 29 October 2026

**Historical v1.1 pilot review:** the resource stop and 20/15-epoch proposals below were superseded by the researcher decisions of 29 October 2026. [Protocol v2](../protocol/protocol_v2.md) removes the hour limit and fixes 65 epochs from the approved training-curve rule. Original pilot measurements remain unchanged.

**Original v1.1 finding:** the projection exceeded the then-applicable 24-hour limit. The historical alternatives below were not adopted; protocol v2 is now the current decision.

## Measurements and verification

Two real-graph fits, seed 11, August 2020 anchor, 75 epochs, learning rate 0.001, weight decay 0.0001, FP32 and batch two. Same Windows RTX 4070 Laptop GPU (8 GB), declared RAM 32 GB. Saved protocol/source/panel hashes and common machine inventory match; all 75 epochs are present and finite. Pilot weights are discarded. No validation/test forecast or loss was computed.

| hidden_size | fit_minutes | mean_epoch_seconds | peak_allocated_gib | peak_reserved_gib | parameter_count |
| --- | --- | --- | --- | --- | --- |
| 32 | 10.795523 | 8.630335 | 0.182231 | 0.203125 | 4140 |
| 96 | 17.707031 | 14.155421 | 0.405233 | 0.535156 | 30828 |

Memory figures are PyTorch peak allocated/reserved device memory, not total GPU occupancy including the driver/display and other applications. Memory is comfortably below the device capacity for these pilot fits; the later-window activation batch shape stays fixed, but full-run peaks have not been measured. GPU time below means measured fit wall time projected to sequential GPU work; it is not hardware utilisation time.

[Measurements CSV](../../data/explore/t03/pilot_measurements.csv) · [Training loss curves](../../data/explore/t03/pilot_training_curves.png) / [CSV](../../data/explore/t03/pilot_training_curves.csv). Source: saved complete.json/training_curve.csv under data/processed/t03_gnn/pilot/, verified by `evaluation.pilot_report`; plots by `visuals.t03_pilot`. Negative Poisson loss is valid because the target-only factorial term is omitted. Curves are training diagnostics, not forecast accuracy or model-selection evidence.

The PowerShell transcript exists but contains no native Python test/epoch output in this session. Saved fit manifests/curves are the timing authority. A CPU-only test rerun after installation is recorded separately in logs/t03_pilot_review_tests.log; no GPU or fit was rerun.

## Projection under unchanged v1.1

The slower pilot fit is the reference (17.707 minutes, 64 batches/epoch). For each scheduled fit, multiply that cost by ceil(training sample origins/2)/64. The input window remains 24 months; the number of training origins grows. Use the slower width for all configurations and all graph conditions, even though narrower/no-graph conditions may be faster. Use the larger of full-fit time and the last-ten-epoch mean extrapolated to 75 epochs plus measured overhead. Add actual pilot time (0.475 hours) once.

Per condition: 12 tuning fits + 36 selected quarterly fits − 2 reused selected/seed-11 anchor fits = 46 validation fits; eight future test refits × three seeds = 24 additional fits. Thus three conditions mean 138 validation + 72 future test fits (210); optional fourth means 184 + 96 (280). Future test dates are used only for resource arithmetic, never test targets.

| conditions | epochs_proposed | full_fit_hours | pilot_hours_already_spent | total_hours_without_margin | total_hours_with_margin |
| --- | --- | --- | --- | --- | --- |
| 3 | 75 | 66.290697 | 0.475043 | 66.765739 | 80.023879 |
| 4 | 75 | 88.387596 | 0.475043 | 88.862638 | 106.540157 |

The final column adds a transparent 20% scheduling/thermal allowance to projected full-fit time, then actual pilot overhead. This is a planning margin, not a measured slowdown or statistical bound. Projection from one anchor/seed/graph cannot prove exact runtimes; graph conditions and laptop power/thermals can differ. Even without the margin, the conservative slower-width projection is well above 24 hours.

[Exact fit calendar and batch counts](../../data/explore/t03/pilot_projection_schedule.csv) · [Projection figure](../../visuals/t03/pilot_projection.png) / [Scenario CSV](../../data/explore/t03/pilot_projection_scenarios.csv) · [Verification JSON](t03_pilot_verification.json).

## Protocol v2 proposals — not approved or implemented

**Recommended A: retain the three core conditions, six configurations, quarterly refits, all three seeds, objective and dates; replace 75 fixed epochs with 20 fixed epochs under a new protocol v2.** This preserves the main comparisons and changes one compute limit. The cost projection scales epoch-dependent work linearly; checkpoints/setup overhead can make it optimistic, so this is a planning projection rather than a runtime guarantee. Training at 20 epochs may underfit relative to 75; the pilot does not establish forecast quality. This is a resource proposal, not a selection made using validation scores.

**Alternative B: if the optional installed-base ablation is essential, propose 15 fixed epochs for all four conditions under v2.** Its projected cost is shown below; it sacrifices more optimisation for every condition and needs explicit optional-condition approval. It is not recommended over A without a clear priority for that ablation.

| conditions | epochs_proposed | total_hours_without_margin | total_hours_with_margin |
| --- | --- | --- | --- |
| 3 | 20 | 18.152562 | 21.688066 |
| 4 | 20 | 24.045068 | 28.759073 |
| 4 | 15 | 18.152562 | 21.688066 |

A 20-epoch fourth condition still exceeds 24 hours in this projection. Another option is to revise the resource ceiling while retaining 75 epochs, but that requires explicit protocol approval and acceptance of the larger budget. No epoch cap, configuration, seed, objective or frozen file has been changed.

## Historical approval request (superseded by protocol v2)

Approve proposal A (three core conditions, fixed 20 epochs, protocol v2), choose another explicit v2 budget, or retain v1.1 and explicitly revise the 24-hour resource rule. Until then all full runs and the optional fourth condition remain blocked by the timing gate. Task 3 step 5 is complete; steps 6–8 have not started.
