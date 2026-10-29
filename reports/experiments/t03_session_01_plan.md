# Task 3 session 1 — real graph

Protocol-v2 is frozen at researcher commit `a195e6e`. The session command runs only the real-graph condition. It never advances to shuffled/no-graph/no-base conditions. No sealed-test fitting or forecast option is exposed.

The runner first fits the six frozen configurations at each of the two tuning anchors with seed 11. It selects by mean MAE over observed areas, all twelve horizons and both anchors, with lower-index tie breaks. It then uses the selected configuration at twelve quarterly refits with seeds 11, 29 and 47 and produces forecasts at all 36 validation origins. Two selected seed-11 anchor fits are reused: 12 + 36 − 2 = 46 unique fits. Every fit has 65 fixed epochs. The last validation target is October 2022.

The researcher controls session duration with Ctrl+C. Completed fit checkpoints remain available. The current fit resumes from its last atomic five-epoch checkpoint; work since that checkpoint may repeat. Rerunning the same condition command reuses complete fits and cached predictions. It does not restart the campaign. No dependency installation or pilot rerun is required.

After normal completion or an interruption, the runner writes [progress JSON](t03_session_progress.json) and [per-condition CSV](../../data/explore/t03/session_progress.csv) / [fit records](../../data/explore/t03/session_fit_records.csv). Measured fit hours include recorded replay work and exclude between-session breaks and inference. Open/hard-killed attempts are flagged as timing lower bounds. Remaining validation fit hours use condition-specific measured seconds per batch/epoch, scaled to remaining training-window batches and checkpointed epochs. Before completed condition-specific fits exist, estimates use the explicitly labelled slower-width pilot fallback. They are planning estimates, not runtime bounds.

The initial real-graph projection is about 11.29 fit hours without a margin, from `evaluation.gnn_progress`, using the width-96 pilot and the frozen validation fit calendar. Session 1 may be stopped whenever the researcher chooses; completing all 46 fits in one session is not required. The former 24-hour cap is removed. The optional fourth condition is counted separately and remains last/cancellable.

Run the single command in internal/STATUS.md. It captures stdout and stderr to logs/t03_session_01_real.log with append mode. After stopping and returning to the PowerShell prompt, return the log/progress message for the agent to read and update STATUS.md. Future sessions should use a new session log filename. Do not edit fit/feature code between sessions without reviewing checkpoint fingerprints.

Implementation: `models.gnn_validation`; progress: `evaluation.gnn_progress`; existing checkpoint engine: `models.gnn_checkpoint`. CPU-only plan/preflight: logs/t03_session_01_plan.log. Full CPU test suite: logs/t03_session_runner_full_tests.log (78 passed). No model fitting or GPU use was performed by the agent to prepare this handoff.

Current [protocol/session diagrams](../../visuals/00_overview/index.md) and [exploration index](../../data/explore/t03/index.md) remain applicable. Figures and plotting source are local-only.
