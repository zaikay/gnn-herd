# Task 3 Part A — implementation and pilot handoff

**Status: steps 1–4 prepared; stop for researcher dependency installation, CPU tensor tests and pilot.** No training or GPU use was performed by the agent. No full-run approval is implied. PyTorch is absent here; the PyTorch test module is skipped until researcher installation.

## Authority and machine

Frozen tag `protocol-v1.1`, normalised config SHA256 `f1693a5b0226095c5331a4e0830ddb9da15007b7c01dfe9d2b3779d826f98d82`. No protocol field was changed. The pilot and every later GNN condition must use the researcher’s Windows RTX 4070 Laptop GPU (8 GB VRAM), with 32 GB RAM. `models.gnn_fit.lock_machine` records the computer, OS, NVIDIA UUID/name/driver, CUDA runtime and torch version at the first fit; a different machine/software inventory is rejected on later fits.

## 1. State assignment

Assigned all 2,641 POAs to 9 state classes by greatest EPSG:9473 land-area overlap with dissolved 2021 LGA state polygons, ties by state code. 15 cross-border areas; 0 coverage failures; 0.000000 square metres uncovered. Other Territories is retained. 19 nonspatial LGA carrier rows are separately recorded; no CER records or graph nodes are excluded.

Validity is checked before and after projection. One square metre is a numerical overlay tolerance, not permission to fill gaps; actual uncovered area is zero. Bounded local intersections preserve the land-area rule. Earlier slower attempts were stopped before five minutes; only the completed bounded-overlay log supplies results. No geometry repair or postcode-prefix shortcut was used.

[Every POA and overlap shares](../../data/explore/t03/state_assignment.csv) · [State map](../../visuals/t03/state_assignment.png) / [CSV](../../visuals/t03/state_assignment.csv) · [Carrier rows](../../data/explore/t03/nonspatial_state_carrier_rows.csv). Script: `geography.states`; figure: `visuals.t03_states`.

## 2. Graph controls

The real rook graph remains 7,051 undirected edges. All 190 cross-state edges stay fixed. Within each state and seed 11/29/47, ten accepted degree-preserving swaps per intra-state edge were completed. No loops or duplicate edges. Node degrees, isolates and missing-area mask were independently checked against saved artifacts. Other Territories has no intra-state edge; its retention fraction is undefined, not zero.

The completion rule flags unmet swap targets or a completely unchanged nonempty state graph. This is an operational check, not a proof of independent graph samples or uniform sampling. Small states retain more edges because their degree constraints are stronger. No null definition was relaxed.

| state_code | seed | within_state_edges | attempted_swaps | accepted_swaps | original_edge_share |
| --- | --- | --- | --- | --- | --- |
| 1 | 11 | 1613 | 16576 | 16130 | 0.014879 |
| 2 | 11 | 1873 | 19138 | 18730 | 0.012814 |
| 3 | 11 | 1109 | 11598 | 11090 | 0.019838 |
| 4 | 11 | 905 | 9464 | 9050 | 0.028729 |
| 5 | 11 | 999 | 10386 | 9990 | 0.024024 |
| 6 | 11 | 250 | 2830 | 2500 | 0.064000 |
| 7 | 11 | 63 | 1398 | 630 | 0.317460 |
| 8 | 11 | 49 | 881 | 490 | 0.244898 |
| 9 | 11 | 0 | 0 | 0 | undefined |
| 1 | 29 | 1613 | 16593 | 16130 | 0.014879 |
| 2 | 29 | 1873 | 19163 | 18730 | 0.011212 |
| 3 | 29 | 1109 | 11654 | 11090 | 0.020739 |
| 4 | 29 | 905 | 9400 | 9050 | 0.024309 |
| 5 | 29 | 999 | 10379 | 9990 | 0.017017 |
| 6 | 29 | 250 | 2857 | 2500 | 0.060000 |
| 7 | 29 | 63 | 1413 | 630 | 0.349206 |
| 8 | 29 | 49 | 911 | 490 | 0.285714 |
| 9 | 29 | 0 | 0 | 0 | undefined |
| 1 | 47 | 1613 | 16547 | 16130 | 0.016119 |
| 2 | 47 | 1873 | 19138 | 18730 | 0.012814 |
| 3 | 47 | 1109 | 11663 | 11090 | 0.028855 |
| 4 | 47 | 905 | 9436 | 9050 | 0.019890 |
| 5 | 47 | 999 | 10380 | 9990 | 0.024024 |
| 6 | 47 | 250 | 2822 | 2500 | 0.068000 |
| 7 | 47 | 63 | 1409 | 630 | 0.301587 |
| 8 | 47 | 49 | 904 | 490 | 0.306122 |
| 9 | 47 | 0 | 0 | 0 | undefined |

[Graph diagnostic figure](../../visuals/t03/graph_swap_diagnostics.png) / [CSV](../../data/explore/t03/graph_swap_diagnostics.csv) · [Paper/supplement candidate](../figures/t03_graph_control_diagnostics.png) / [CSV](../figures/t03_graph_control_diagnostics.csv). `geography.conditions` and `visuals.t03_preparation`.

## 3. Implemented core and recovery

The model graph-convolves concatenated node input/hidden state inside reset, update and candidate gates, with zero hidden state at each sample start. It uses one symmetric masked A+I operator, shared weights across nodes/time, and twelve direct softplus rates clamped at 1e-6. No extra embeddings or dense graph matrices. No graph uses identity only. Unknown nodes have zero inputs/hidden states and no incoming/outgoing messages, loss or evaluation. The graph operator is a computational object; raw border edges are unchanged.

Six input channels are historical log1p count, log1p cumulative base, month sine/cosine, observed flag and original-graph isolate flag. History length 24; every eligible target cell from January 2011 through fit origin contributes; unavailable horizon cells and seven record-free areas are masked. The same input definition, Poisson objective, six configurations, 75 epochs, Adam, batch two origin windows and FP32 apply to every core condition. The optional installed-base ablation is disabled and is rejected by the fit helper.

| width | parameters_analytic |
| --- | --- |
| 32 | 4140 |
| 64 | 14412 |
| 96 | 30828 |

At the pilot anchor, the shared training calendar has 127 sample origins and 1392 eligible sample/horizon positions before the observed-area mask. No validation/test target is loaded by pilot fitting: panel data is truncated to 2020-08.

Checkpoints are atomically replaced after each epoch and at fit completion, with model/Adam state, epoch count, training losses, wall/epoch time, peak allocated and reserved GPU memory. Recovery verifies protocol, data/edge/code hashes, settings and machine inventory. Completed fits return their recorded result without retraining; incomplete fits resume at the next epoch. There is no dropout or other stochastic operation after initialisation; epoch orders are independently determined by seed+epoch. Pilot checkpoints exist only for interruption recovery; completed pilot weights are discarded and never enter tuning. Full-validation checkpoints will be retained.

[Architecture SVG](../../visuals/t03/core_gnn_architecture.svg) / [Mermaid](../../visuals/t03/core_gnn_architecture.mmd) / [nodes](../../visuals/t03/core_gnn_architecture_nodes.csv) / [edges](../../visuals/t03/core_gnn_architecture_edges.csv). [Updated project overview](../../visuals/00_overview/index.md).

CPU verification: toy state tie/gap/invalid geometry tests; graph degree/cross-state/seed tests; six-channel window shape/masking; partial-horizon target eligibility; real-panel future mutation checks at 2018-11, 2020-08, 2021-10. See [real-panel checks](t03_preparation_checks.json). Current test log: `logs/t03_part_a_tests.log`. Tensor shapes, message masking, identity-only operation, fixed CPU seed and parameter counts have PyTorch tests prepared; these must pass after installation, before the pilot. No optimiser step was executed by the agent.

## 4. Researcher commands and pilot boundary

| width | seed | fit_origin | epochs | learning_rate | weight_decay | condition |
| --- | --- | --- | --- | --- | --- | --- |
| 32 | 11 | 2020-08 | 75 | 0.001000 | 0.000100 | real |
| 96 | 11 | 2020-08 | 75 | 0.001000 | 0.000100 | real |

Use the existing project environment on the full-run laptop. Install pinned GPU dependencies with `scripts/install_gnn.ps1`, then run `scripts/run_gnn_pilot.ps1`. Both transcribe to logs. The second script runs the complete CPU test suite first and aborts before GPU use if it fails; then runs only these two fixed fits, sequentially. Commands and durations are in internal/STATUS.md.

Install pins `torch==2.7.1+cu128` plus its additional dependencies, without changing the existing baseline lock. The [official CUDA 12.8 wheel index](https://download.pytorch.org/whl/cu128/torch/) includes Windows CPython 3.13 wheels. No torchvision, torchaudio or graph-extension package is needed. Installation and driver/runtime compatibility remain unverified until the researcher runs it; pip check and the fit preflight fail explicitly rather than falling back to CPU.

Expected fit time is unknown. The prior 2–4 GB VRAM and 8–16 GB RAM estimates are planning estimates, not measurements. Pilot records allocated and reserved GPU peaks, wall/epoch time and training-only loss curves under data/processed/t03_gnn/pilot/. It performs no validation or test scoring, no configuration/epoch/objective changes and no full fits.

After the pilot, STOP for Task 3 step 5: measured curves/report and conservative projection for 138 validation plus 72 future test fits (three conditions), including pilot overhead and later training-window growth; report optional fourth-condition cost separately. Above 24 projected GPU hours, propose protocol v2. All full runs and optional-condition approval remain pending. No scientific conclusion is made by this preparation report.
