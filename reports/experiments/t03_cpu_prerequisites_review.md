# CPU prerequisites review — 31 October 2026

Read-only review of saved fits/forecasts, no refits, predictions, GPU operation or sealed-test access. All 46 prerequisite jobs complete: eight extra anchor fits and 38 C-base quarterly jobs (31 new fits, seven reused). Total new fitting time 1.014744 CPU wall hours, excluding inference/serialization/startup. Gate C remains open; no screen GPU result exists.

## Extra configuration results

| condition | frozen_tuning_mae | new_rate | new_leaves | extra_tuning_mae | beats_frozen |
| --- | --- | --- | --- | --- | --- |
| gradient_boosting_own | 3.909813 | 0.050000 | 31 | 3.920623 | False |
| gradient_boosting_own | 3.909813 | 0.050000 | 63 | 3.937697 | False |
| gradient_boosting_neighbours | 3.915465 | 0.050000 | 31 | 3.921499 | False |
| gradient_boosting_neighbours | 3.915465 | 0.050000 | 63 | 3.939086 | False |

Neither new configuration beats its frozen selection. Retain own-lag rate 0.03 / 15 leaves and neighbour-lag rate 0.03 / 31 leaves, both L2=1, 300 iterations. No updated full-validation run is needed or claimed; their existing validation scores remain authoritative. Tuning score is systems/area/month, averaged equally across the two anchors and all twelve horizons. All four extra tuning scores and both frozen tuning scores were independently reproduced from saved forecasts against the anchor targets. [Baseline-only band preflight](../../data/explore/t03/architecture_screen/cpu_anchor_baseline_bands.csv) uses the new band calculations without opening any screen/GNN prediction.

C's base has 114 monthly origins, March 2011–August 2020, and 2,634 observed areas × twelve horizons. All fit dates are strictly earlier than their forecast origins; combined forecast hash matches its completion marker. Seven old base checkpoints are reused. Source: `c_base_complete.json` / `c_base_oos.npz`.

## Timing evidence

| condition | anchor | leaves | new_fit_seconds | historical_reference_seconds | ratio | historical_min_seconds | historical_max_seconds | expected_rows | features | actual_iterations | declared_threads |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| gradient_boosting_own | 2019-08 | 31 | 166.773851 | 53.201317 | 3.134769 | 51.142998 | 55.259636 | 3287232 | 33 | 300 | 8 |
| gradient_boosting_own | 2019-08 | 63 | 216.571969 | 77.109865 | 2.808616 | 66.938779 | 87.280950 | 3287232 | 33 | 300 | 8 |
| gradient_boosting_own | 2020-08 | 31 | 54.522814 | 128.002518 | 0.425951 | 118.674052 | 137.330983 | 3666528 | 33 | 300 | 8 |
| gradient_boosting_own | 2020-08 | 63 | 70.203635 | 110.688236 | 0.634247 | 72.904574 | 148.471898 | 3666528 | 33 | 300 | 8 |
| gradient_boosting_neighbours | 2019-08 | 31 | 205.218809 | 157.598537 | 1.302162 | 101.461907 | 213.735166 | 3287232 | 59 | 300 | 8 |
| gradient_boosting_neighbours | 2019-08 | 63 | 313.957274 | 172.553782 | 1.819475 | 140.294196 | 204.813369 | 3287232 | 59 | 300 | 8 |
| gradient_boosting_neighbours | 2020-08 | 31 | 278.331322 | 103.008573 | 2.702021 | 95.258899 | 110.758246 | 3666528 | 59 | 300 | 8 |
| gradient_boosting_neighbours | 2020-08 | 63 | 374.362121 | 109.703214 | 3.412499 | 80.644182 | 138.762247 | 3666528 | 59 | 300 | 8 |

The 2.8–3.1× slowdown described earlier applies to the first two agent-run own-lag fits at August 2019. Across all eight fits, ratios span 0.426–3.412; the ratio of total new seconds to total reference seconds is 1.842. Later researcher-run own-lag August-2020 fits were faster than those historical references. This is not a uniform threefold penalty.

**Thread/settings checks:** both manifests request eight CPU threads. Both fitting implementations enter `threadpool_limits(8)` around fitting. Current loaded CPU backends report eight threads inside that context; this verifies today's configuration, not historical effective utilisation. Installed baseline-library versions match the historical manifest. All saved new estimators have 300 iterations, Poisson objective, early stopping disabled and their intended leaf limits. Horizon eligibility implies identical training row counts to their matched historical references; feature counts agree. The learning rate changes intentionally from 0.03/0.1 in the reference grid to 0.05, so these are not identical-model timing repeats. Different learned tree splits can have different costs.

**Timing boundaries:** new `fit_seconds` measures model.fit only. Old `seconds` also includes checkpoint compression/writing. Consequently the extra serialization in the reference cannot explain why a new fit was slower. The joblib missing-WMIC warning triggers logical-core discovery fallback; it does not remove the explicit eight-thread context. No evidence identifies that warning as the cause of a minutes-long fit difference.

**Known contention:** the agent launched targeted tests during the second initial own-lag fit. Approximate intervals reconstructed from log modification times and recorded durations confirm overlap; the [overlap table](../../data/explore/t03/architecture_screen/cpu_test_overlaps.csv) retains that evidence. This was avoidable concurrent CPU work and makes that timing less comparable. It does not establish its share of the slowdown, and cannot explain the first fit or all later timing variation.

**Single cause not established.** Historical per-process CPU utilisation, other concurrent workload, affinity, laptop power/thermal state and effective clock measurements were not recorded. Current process sampling cannot reconstruct those runs, so throttling or a sandbox effect cannot be asserted. No rerun was made to manufacture a diagnosis. Keep later timed CPU fits separate from test jobs and other fits; retain the eight-thread cap. Record threadpool state, process CPU/wall time and power/load context with future approved CPU jobs before interpreting timing ratios. No settings/environment changes are made now.

[Timing CSV](../../data/explore/t03/architecture_screen/cpu_timing_review.csv), [selection CSV](../../data/explore/t03/architecture_screen/cpu_selection_review.csv), [machine-readable audit](t03_cpu_prerequisites_review.json). Generator: `python -m evaluation.screen_cpu_review`. All 22 protected original file hashes match. No frozen protocol change and no further CPU/GPU work is required before commit/tag and the researcher GPU screen.
