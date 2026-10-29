# Protocol v2 — 29 October 2026

**Approved researcher decisions, pending commit and `protocol-v2` tag.** This supersedes the resource rule, GNN epoch cap, checkpoint schedule and optional-condition approval in v1.1. This turn records the revision and stops. No full run is started. Tags `protocol-v1` and `protocol-v1.1` remain unchanged; their completed baseline and pilot records retain their original authority.

## 1. Resource rule and sessions

The 24 GPU hour limit is removed. The researcher starts and stops sessions on the same Windows RTX 4070 Laptop GPU (8 GB VRAM, 32 GB RAM) used for the pilot. All conditions use that machine and environment. The large pilot projection is planning information, not a stop rule. Laptop sessions allow the researcher to manage elapsed time without reducing configurations, seeds or comparisons to meet the former limit.

After every session, read its logs and fit/checkpoint records and update `internal/STATUS.md` with:

- Unique completed fits for each condition, against 46 planned validation fits per condition. A reused selected tuning-anchor fit counts once. Partial fits are listed separately.
- Measured fit wall hours so far, including completed fits and interrupted/replayed work. Pilot time is separate. Calendar breaks between sessions are excluded.
- Projected remaining validation hours from measured fit times, adjusted for training-window batch counts and saved partial-fit epochs. Prefer measurements from the same condition; label pilot/other-condition fallbacks and uncertainty. Later final-test cost may be projected from its calendar separately, without reading test targets.

The epoch journal records each attempt and elapsed observations, including work after the last saved checkpoint. For a hard kill or power loss, time since the last flushed observation is unknown; report the measured value as a lower bound. Do not silently treat it as zero compute or count replayed epochs as additional completed fits.

## 2. Checkpoint and recovery rule

Retain a checkpoint after every fit, and replace the recovery checkpoint atomically every five completed epochs within a fit. Save at the final epoch even if it is not divisible by five. Restore model weights, Adam state, completed epoch, epoch records and Python/NumPy/CPU/CUDA random-number-generator states. Epoch sample orders remain deterministic from seed plus epoch. Protocol, data, source-code, graph and machine fingerprints must match before reuse.

A stopped fit resumes from its last checkpoint; up to the unsaved interval may repeat. A completed fit is reused without refitting. Completed fit checkpoints remain available for forecasts and audit. Historical pilot weights were already discarded under v1.1; no new pilot is required to reconstruct them.

The production epoch engine is shared with `tests/test_gnn_resume.py`. On synthetic CPU data, an uninterrupted ten-epoch core-GNN/Adam fit is compared with a fit stopped after epoch 7, loaded from epoch 5, then resumed. Weights, Adam state and training losses match bit for bit, and the CPU RNG stream is restored. Another test checks a final checkpoint at epoch 7. These are the CPU fit tests explicitly requested by the researcher, not scientific model runs or GPU use. The result does not claim cross-device or GPU bit equality.

## 3. One fixed epoch count, chosen before full runs

Use only the two existing 75-epoch pilot training curves. For loss `L_t`, use a trailing five-epoch rolling mean `S_t`, with `min_periods=1` at the left edge. Thus `S_1 = L_1`; epochs 2–4 average the available preceding epochs. No centring, look-ahead smoothing, validation scores or test scores enter this choice.

For each width, take the **first** epoch `E` with:

`(S_1 - S_E) / (S_1 - S_75) >= 0.98`.

This measures the share of the positive total decrease. It is not 98% of the negative loss value. The Poisson loss omits the target-only constant and can be negative. A curve without a positive total decrease would require review; both observed curves have a positive decrease.

| Pilot width | First E | Share of total decrease at E |
| --- | ---: | ---: |
| 32 | 63 | 0.982011929 |
| 96 | 60 | 0.980632432 |

**Fixed epochs = min(75, 5 × ceil(max(63, 60) / 5)) = 65.** Use 65 epochs for every GNN configuration, seed, refit and condition, including the optional fourth condition if run. This is chosen once. It is not adaptive early stopping and is not reconsidered from subsequent training/validation curves. The original pilot remains a historical 75-epoch measurement.

Reproduction: `evaluation.epoch_selection`. [Selection evidence and original-curve hashes](protocol_v2_epoch_selection.json) · [Curves and values](../../data/explore/t03/protocol_v2_epoch_selection.png) / [CSV](../../data/explore/t03/protocol_v2_epoch_selection.csv) · [Summary figure](../../visuals/t03/protocol_v2_epoch_selection.png) · [Paper/supplement copy](../figures/t03_protocol_v2_epoch_selection.png) / [CSV](../figures/t03_protocol_v2_epoch_selection.csv). The smoothing/threshold rule is a training-cost decision; it does not demonstrate predictive convergence or forecast quality. The earlier suggested 20/15-epoch alternatives were not adopted.

## 4. Conditions and run order

1. Real graph.
2. Within-state shuffled graph, using the approved seeds 11, 29 and 47.
3. No graph, with computational identity only.
4. Optional real graph without the explicit installed-base channel, last.

The fourth condition is approved to run last; the researcher may omit it if time runs short. Record any omission and its time-related reason. All remaining conditions retain their full budgets. Removing the installed-base input leaves five channels; it does not remove information in the count history or prove an individual imitation mechanism. No hybrid is introduced.

The Task 3 DM family remains real versus no graph, shuffled graph and each boosting baseline, plus real versus the no-base condition if completed. One Holm adjustment covers all four outcomes across all included pairs: 20 tests if the fourth condition completes, otherwise 16. No separate favourable comparison family is created.

## Unchanged and execution boundary

Data sources, ASGS Edition 3, graph rules, unknown-area masks, target definition, splits, partial-horizon eligibility, features apart from the approved ablation, Poisson objective, MAE tuning/primary score, MASE/RMSE, six configurations, three seeds, quarterly refits and baseline results remain unchanged. Existing baselines need no refit. All model choices precede the sealed final test; no test forecasts or losses are authorised here.

The current code includes five-epoch/final checkpoint recovery and its CPU tests. Full-session run commands and model evaluation are outside this turn. The researcher commits and tags this revision; the agent then stops as requested. No staging or Git mutation is performed by the agent.

[Current session pipeline and methodology](../../visuals/00_overview/index.md) · [Historical pilot report](../experiments/t03_pilot.md) · [Configuration](../../configs/experiments.yaml). Validation fit budget per completed condition remains 12 tuning + 36 selected refits − 2 reused anchor fits = 46; later sealed-test fitting is 24 additional fits per condition and remains separate.
