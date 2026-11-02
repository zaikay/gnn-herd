# Protocol v6: B2 learned graph screen and validation campaign

Date: 2 November 2026. Researcher-specified amendment, recorded before the new screen and campaign. Proposed tag: `protocol-v6-b2-graph-campaign`. The accepted B2 scaling screen, frozen v2 data/objective/masks, and v1.1 metrics remain the authority except for the explicit changes below. Final test remains sealed.

## Four-fit screen

Configuration 3: width 64, learning rate 0.003, weight decay 0.0001; 100 epochs, Adam without schedule, batch size two. Seed 11, fit origins August 2019 and August 2020. Two learned and two identity fits. Compare against the four saved eligible B2 real/no-graph 100-epoch anchor fits. No renewed grid or epoch choice. Keep the original per-area scaling, input windows/channels, raw-count Poisson objective, training-target horizon masks and validation definitions.

Learned: two node embedding matrices E1 and E2, each 2,641 by 10. Initialise independent normal values with standard deviation 0.01. Joint training on training loss only, with the same Adam weight decay as other parameters. Compute logits ReLU(E1 E2 transpose), mask the diagonal and all unknown-area source columns to minus infinity, then row softmax. Rows sum to one. This time-invariant adjacency is computed once per forward pass and replaces the fixed neighbour mean in B2's late correction, including the subtraction of the receiver's own hidden state. Geographic isolates receive learned neighbours; their original isolate input flag is unchanged. Unknown receivers remain masked from loss/output and unknown sources have zero weight.

Identity: the same two embedding matrices and initialisation. Concatenate their two ten-dimensional rows into twenty extra local input channels, repeated at every local GRU timestep. Remove the neighbour correction entirely. The original six scaled/calendar/flag channels remain unchanged. Embedding counts match exactly; total counts differ because GRU input width increases and the neighbour head is removed. Tests and machine-readable counts are produced by `models.b2_adaptive.parameter_counts`.

All screen fits retain complete checkpoints, five-epoch within-fit checkpoints, training-only curves, fit seconds and peak allocated/reserved GPU memory. Screen report: `reports/experiments/b2_graph_screen.md`; per-anchor MAE, MASE, pooled RMSE for all horizons and total, overall and maturity terciles, plus signed errors and costs. One seed: no seed-spread inference. Curves and plotted CSVs: `data/explore/t03/b2_graph_screen/`. No test forecasts.

## Main model, inclusion and review rule

Score each graph variant by real monthly MAE averaged equally over both anchors, observed areas and horizons 1 to 12. No graph stays a control. Exact ties retain B2 real.

First, if identity MAE is at least 2% lower than B2 real on this score, stop for researcher review before any campaign fit. Otherwise include learned and identity in the campaign only if learned strictly beats both real and identity. In that case learned is main. If learned beats real but fails to beat identity, retain real as main and continue without either learned or identity. Report both screen results. If learned does not beat real, real is main. There is no automatic further architecture search.

## Full validation campaign

One machine only: original Windows RTX 4070 Laptop, 8 GB VRAM and 32 GB RAM, same pinned software as the B2 screen. All seeds/conditions stay there. No multi-machine transfer or merge in this amendment.

Fixed configuration 3, 100 epochs, seeds 11, 29 and 47. Same twelve quarterly validation refits and 36 monthly origins as v2. Run order: real, shuffled within state, no graph, real without installed base; then learned and identity only if included by the screen. Per-area scales use each refit's own training history through its fit origin, fixed for all three subsequent origins. Without-base drops only the explicit base input; count scaling and output scaling remain. Shuffled edges are the existing audited seed-specific graphs.

Each condition has 36 fit identities, not a new tuning search. Reuse the exact seed-11 August 2019/2020 100-epoch screen checkpoints for real/no graph and, if included, learned/identity. Four conditions: 144 identities, four reused, 140 new. Six conditions: 216 identities, eight reused, 208 new. No checkpoint copying or modification; reuse by immutable source pointer. Sources, panel, shuffled graphs, protocol, hardware and reused artifacts are fingerprinted. Resume from the last five-epoch checkpoint after interruption. Completed fits are retained.

## Predeclared DM family and evaluation

One family of two-sided MAE-loss Diebold Mariano tests, with HLN correction and Bartlett variance at lag h minus one. Average origin losses over the fixed seeds first. Holm adjustment covers the whole family, retaining undefined slots. Outcomes: horizons 1, 6, 12, and twelve-month total (h=12).

- Main against B2 no graph, B2 shuffled, frozen own-lag boosting, frozen neighbour-lag boosting, and B2 without installed base: 20 tests.
- If learned and identity are included, add learned against real and learned against identity: eight further tests; one family of 28.

Do not add an independent RMSE/MASE family. Report MAE, seasonal MASE and pooled RMSE at every horizon and total, dynamic maturity terciles, individual-seed scores and SD/min/max. All retained campaign conditions must be complete before combined comparisons are released. Seasonal naive remains in descriptive tables. Report: `reports/experiments/b2_validation.md`. Results are validation development evidence after screen selection; no individual behavioural mechanism is identified.

## Execution and limits

Agent prepares and CPU-tests only; researcher runs all GPU commands. CPU-only default/plan modes never initialise CUDA. Commit and tag this note and implementation before the screen command. The screen command writes its report and stops; read its decision before starting the campaign. Identity's 2% review stop cannot be bypassed by a campaign command. No environment install, frozen source/config modification, test-block access, fits by the agent, or git mutations by the agent.

Implementations: `models.b2_adaptive`, `models.b2_runtime`, `models.b2_graph_screen`, `models.b2_validation`, `evaluation.b2_graph_screen_report`, `evaluation.b2_gate_c`, `evaluation.b2_campaign_plan`. Preparation diagrams/count CSVs: `visuals/t03/b2_campaign_preparation/`, `data/explore/t03/b2_campaign_preparation/`. Private visual generators remain ignored under the researcher's repository policy.
