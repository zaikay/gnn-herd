# Architecture screen preparation — 31 October 2026

Gate C is open. The three-candidate screen is approved, but no GPU fit has been run by the agent. Results and selection are pending all twelve fits. The future completed report is `t03_architecture_screen.md`; this is a preparation/CPU-progress report, not a screen result.

Full pre-run suite: 114 passed, one upstream deprecation warning (`logs/t03_v3_full_tests.log`). The CPU job ledger below is refreshed from completion markers. A source-revision record and original CPU manifest are retained for the anchor-forecast expansion fix; fitting settings and original frozen sources were unchanged.

## Parameter counts

| candidate | condition | parameters |
| --- | --- | --- |
| A | real | 27852 |
| A | no_graph | 27852 |
| B | real | 15180 |
| B | no_graph | 15180 |
| C | real | 15180 |
| C | no_graph | 15180 |

Counts include inactive neighbour weights in no graph. C does not include the separately fitted boosting trees in its neural parameter count; base fit costs are charged separately. Tests: `logs/t03_v3_screen_pre_run_tests.log`; full-suite result is recorded in STATUS.md after final preparation. CPU toy forward tests use no optimisation.

## CPU progress

| kind | jobs | completed | new_fits | fit_seconds |
| --- | --- | --- | --- | --- |
| base | 38 | 38 | 31 | 1973.137906 |
| extra | 8 | 8 | 8 | 1679.941796 |

The C base needs 38 quarterly fits, of which seven exact existing own-lag seed-11 fits can be reused. Earliest C sample March 2011; first target April 2011. Each base fit precedes its forecast origin strictly. Source and panel hashes are cached in `data/processed/t03_screen_v3/cpu_manifest.json`. Original baseline/GNN forecasts are never overwritten. The separate extra search cannot alter C's frozen base configuration.

## Extra boosting selection

| condition | old_score | new_score | new_leaves | improved | full_validation_complete |
| --- | --- | --- | --- | --- | --- |
| gradient_boosting_own | 3.909813 | 3.920623 | 31 | False | False |
| gradient_boosting_neighbours | 3.915465 | 3.921499 | 31 | False | False |

Neither extra configuration improved either baseline. Both frozen selections remain in force. No new full-validation run is required. The existing full-validation scores remain authoritative; there are no new-selection full-validation scores to report. [Independent CPU completion and timing audit](t03_cpu_prerequisites_review.md).

## Next commands and stop point

CPU prerequisites and summary are complete; do not rerun them. The next steps are researcher commit/tag and the GPU command in `internal/STATUS.md`. It runs A/B/C in one resumable session and writes the final report after twelve fits. The report now includes frozen and any improved boosting references at the same anchors, horizon bands and maturity terciles, plus C's gain over its own base. The selection rule is unchanged. No further architecture or full campaign starts. The final test remains sealed.

[Parameter counts](../../data/explore/t03/architecture_screen/parameter_counts.csv), [CPU job ledger](../../data/explore/t03/architecture_screen/cpu_progress.csv), [screen note](../protocol/protocol_v3_screen.md). Generator: `evaluation.screen_cpu_report`.
