# Learned combination rules — 1 November 2026

Concrete implementation choices following the researcher's request for expanding weights, documented before computing them. No older detailed rule file was found; these do not claim to recover one. CPU-only saved validation forecasts; no neural/boosting refits or test-block access.

- Forecast = w × neighbour-lag boosting + (1−w) × B real; w constrained to [0,1].
- Update at each validation origin. One weight per current maturity tercile and band 1–3, 4–6, 7–12. Estimate by pooled raw MAE, the primary metric, across matched seeds 11/29/47.
- Training uses earlier forecast origins only, and only target cells whose target month is no later than the current forecast origin. Partially observed bands contribute observed cells. Keep each earlier sample's original maturity group. The current origin's group selects the weight for its forecast.
- Require three distinct prior origins with observed target cells in the stratum/band. Otherwise use w=0.5. Retain warm-up predictions in all reported scores.
- Exact convex MAE minimisation is a weighted-median problem. If a flat interval minimises MAE, choose the minimiser closest to 0.5. Identical base forecasts receive weight 0.5.
- Use the same group/band weights for all three seed-paired combinations; do not optimise separately per seed or use later outcomes. This follows the existing revised-data availability convention, not CER publication vintages.
- Report MAE/MASE/RMSE at every horizon and total, by maturity, with base-model seed spread and an audit of weight paths/available targets. No additional DM family or test protocol is introduced.

MASE robustness retains the explicit definitions in reports/experiments/mase_robustness.md: nonfallback-only MASE, average of per-origin medians (with and without fallback), and per-area error divided by own training mean, with zero denominators undefined and coverage counted. The learned combination is included after its validation forecasts are saved.
