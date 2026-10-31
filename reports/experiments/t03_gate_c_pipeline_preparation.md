# Gate C evaluation pipeline preparation — 31 October 2026

Historical preparation record. Condition 4 subsequently completed; the released results are now in [gnn_validation.md](gnn_validation.md). The hold and limited-test statements below describe the earlier preparation stage.

**Prepared while condition 4 runs. Study GNN comparisons remain withheld.** No GNN forecast file was opened or scored. No full test suite, training, GPU query or checkpoint operation was performed. Work used the saved baselines and small synthetic arrays only, with the numerical preflights limited to one thread.

## Ready for evaluation after release

- Common observed areas, validation origins, historical maturity terciles and training-only MASE scales. Unknown targets stay excluded; no missing prediction, area, origin or seed is silently dropped.
- MAE, seasonal MASE and RMSE for all twelve monthly horizons and the twelve-month total; reported tables at 1, 6, 12 and total; all/low/medium/high maturity groups. Equal-area, then equal-origin/seed weighting. Total errors sum months before taking absolute/squared loss. Original float32 forecast-sum conventions are retained for baseline comparability.
- RMSE takes the root after pooling MSE. Seed SD (ddof=1), min/max and independently scored seed tables are supplied. This does not score an ensemble or average seed RMSE in place of pooled RMSE.
- Predeclared MAE DM comparisons: real versus no graph, shuffled, own boosting and neighbour boosting; also real versus no-base if retained. One whole-family Holm adjustment: 16 or 20 tests. Origin losses average areas then seeds; HLN, Bartlett and the approved package adapter are reused. Undefined statistics reserve family slots without invented p-values.
- Per-area absolute/scaled/signed errors and row-standardised rook Moran I for reported outcomes. Observed isolates have zero weight rows. Horizon-12 real scaled-error and real-minus-shuffled scaled-error maps; negative difference favours real. No population normalisation, permutation significance or causal reading.
- All-model horizon, total and maturity figures; core graph comparisons as a Figure 3 candidate; scaled/signed Moran figure. Maps use approved ASGS3 geometry in Australian Albers when actual evaluation is released.
- A combined `gnn_validation.md` report writer with score/seed tables, comparison family, spatial diagnostics, provenance and figure links. It has not generated the study report in this turn.

## Release safeguard

`evaluation.gate_c_io.comparison_release` requires a valid fourth-condition completion marker, or a dated JSON record of a formal researcher drop with condition name, reason and `approved_by: researcher`. No drop decision was created. An incomplete fourth condition is never silently excluded.

The evaluation entry point checks release **before** loading any study GNN forecasts or computing GNN losses. The figure and report writers repeat the guard. The released loader checks frozen protocol/panel/source hashes, same machine/software inventory, expected 46-fit/reuse identities, retained checkpoints, 65 epochs and matching seed/codes/origin forecast identifiers. Tests verify that an unreleased loader cannot call `numpy.load` on a GNN forecast.

Future entry point is `evaluation.gate_c evaluate`, but it is **not a command to run now**. Full-suite verification is also deferred until between sessions. The user requested preparation only; no GNN evaluation is run even if condition 4 finishes during this preparation turn.

## Checks performed

| Check | Result | Evidence |
| --- | --- | --- |
| Saved baseline MAE/MASE and seed SD | 48 score rows match | logs/t03_gate_c_baseline_check.log |
| Saved baseline RMSE | 48 amendment rows match | same log |
| Saved baseline per-seed MAE/MASE | 144 rows match | same log |
| Existing own-boosting horizon-12 Moran | Reproduced | same log |
| Targeted new tests only | 18 passed | logs/t03_gate_c_final_targeted_tests.log |
| Synthetic end-to-end cases | Seven model aliases, 18 origins, six observed areas; both 16/20-test families | logs/t03_gate_c_synthetic_preflight.log |
| Synthetic figure/CSV smoke checks | 14 paired files checked, unknown map area preserved, report links valid | same log |
| Protected existing files | 34 source/config/protocol files unchanged | logs/t03_gate_c_protected_hashes_after.json |

No baseline was refit. Synthetic model aliases in fixture figures are fictional and every figure/report title marks them as synthetic. No study GNN comparison metric or p-value is included in this preparation report or displayed by the preflight commands.

## Files and local previews

Core: new `evaluation.gate_c_metrics`, `gate_c_io`, `gate_c`, `gate_c_fixtures` and `gate_c_preflight` modules. Existing evaluation/model/feature/config/protocol files were not edited. Tests: new Gate C metric/release modules and local-only visual checks.

- [Baseline check JSON](t03_gate_c_baseline_check.json) and [synthetic check JSON](t03_gate_c_synthetic_check.json).
- [Baseline-only metrics directory](../../data/explore/t03/gate_c_preflight/baselines/).
- [Synthetic report fixture](../../data/explore/t03/gate_c_preflight/synthetic/SYNTHETIC_report_fixture.md), [synthetic figure index](../../visuals/t03/gate_c_preflight/synthetic/index.md) and [synthetic exploration index](../../data/explore/t03/gate_c_preflight/synthetic/exploration/index.md). These are test outputs, not study results or paper candidates.
- [Prepared flow diagram](../../visuals/t03/gate_c_evaluation_flow.svg) / [Mermaid](../../visuals/t03/gate_c_evaluation_flow.mmd) / [nodes](../../visuals/t03/gate_c_evaluation_flow_nodes.csv) / [edges](../../visuals/t03/gate_c_evaluation_flow_edges.csv).

All data, figures, synthetic previews and visual source remain ignored under the researcher policy. The optional model uses the existing unused Okabe-Ito purple, recorded by the new visual module and its output palette CSV; live `configs/style.yaml` was not changed. Actual paper candidate figures will be created only after release. No preview image was displayed as a study result.

The active run was not paused, stopped, resumed or otherwise altered. After condition 4 completes or is formally dropped, the next step is the full test suite between sessions, then guarded combined evaluation and Gate C review. Nothing was staged or committed.
