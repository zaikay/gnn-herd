# Protocol v1 — accepted decisions, 28 October 2026

**Status: approved by the researcher on 28 October 2026; commit and `protocol-v1` tag pending.** P1–P7 are accepted with the revisions recorded here. Part A only: no model fitting, forecast evaluation, GNN implementation or GPU allocation has occurred. Do not start Part B. Later work requires a separate instruction and the protocol freeze.

## Accepted protocol decisions (P1–P7)

**No approval requested for the descriptive figures or measured data summaries.** They are evidence for your review. Resource estimates are planning assumptions, not measured results.

**Already fixed at Gate A:** April 2001 panel start; certificate backed installation target; ASGS Edition 3; unmatched postcodes outside the panel and retained in the ledger; all isolated nodes and components retained without artificial links; zero-total deductions for 1825/4513; seven record-free areas kept in the graph; evaluation targets end by September 2025. None of those decisions needs repeating.

**All decisions below were approved on 28 October 2026.** Detailed sections are the operative definitions. No further protocol approval is requested now; the Task 3 timing gate is a later mandatory check.

| ID | Accepted choice | Approval and material limitation | Detail |
| --- | --- | --- | --- |
| P1 — Model eligibility | Seven areas without records: zero placeholder inputs plus missing flag, no outgoing messages, no loss or evaluation. Observed isolates remain evaluated, with zero neighbour mean plus empty-neighbour flag. | **Approved.** Avoids treating unknown targets as measured zeros while retaining the approved graph. | Section 3 |
| P2 — Forecast calendar | Dates unchanged: training targets from January 2011; 24-month inputs; validation origins November 2018–October 2021 (36); sealed test origins October 2022–September 2024 (24); predict months 1–12. A sample s contributes horizon h when s+h is observed by the fit origin; later target months are loss-masked identically in boosting and GNN. | **Approved with the horizon-mask revision.** Include every eligible target, not just complete vectors. Record battery-scheme timing for July–September 2025 test targets as a limitation. | Section 4 |
| P3 — Objective and predictors | Shared Poisson objective for boosting and GNN. Use the listed own-history/base/calendar inputs; spatial boosting adds the listed neighbour inputs. No area IDs or extra covariates. | **Approved.** A direct nonnegative-count objective keeps the comparison simple. It does not establish Poisson dispersion or uncertainty calibration. | Section 5 |
| P4 — Scoring and comparisons | Report horizons 1/6/12 and twelve-month totals, equal-area MAE and seasonal MASE with the pooled zero-scale fallback, origin-specific maturity groups, corrected origin-level DM and Holm adjustment. | **Approved with the stated caveats.** MASE is explicitly modified for zero scales; overlapping origins and few origins limit DM power. Validation tests remain descriptive. | Section 5 |
| P5 — Compute budget | Six configurations, two tuning anchors, one tuning seed; three evaluation seeds; monthly forecasts with quarterly refits; GNN cap 75 epochs. Each boosting and GNN condition gets the identical 46-fit validation budget. | **Approved.** Task 3 starts with 2–4 timing fits on the full-run machine, at the smallest/largest widths, one seed and one tuning anchor. Measure fit time, peak VRAM and training-only loss curves. No configuration, epoch or objective changes. Above 24 projected GPU hours for the three GNN conditions: stop and propose protocol v2. | Sections 5–6 |
| P6 — GNN design | T-GCN-style graph GRU, six input channels, hidden width 32/64/96 and direct twelve-rate head. Same design under real/no/shuffled graphs. | **Approved; memory to be confirmed by the Task 3 pilot.** Planning memory is 2–4 GB VRAM and 8–16 GB system RAM; your laptop appears suitable, but peak usage has not been measured. | Section 6 |
| P7 — State/shuffle rule | Assign state using existing LGA state fields and largest POA land-area overlap. Rewire within-state edges preserving degrees; keep cross-state edges fixed. No extra download. | **Approved with stop-on-failure checks.** Audit cross-border overlaps and achieved shuffle mixing before using the control. This tests within-state geography while retaining existing cross-border links. | Section 7 |

Approval records the protocol choices; it does not authorise starting Part B or a pilot now. The researcher commits and tags the accepted files. The pilot runs only at the start of Task 3 on the full-run machine, before any full GNN workload.

## 1. Background — project methodology, pipeline and scope

RQ1 tests geographic predictive value; RQ2 tests whether parts derived from imitation, neighbour influence and inertia add predictive value. Own cumulative base represents within-area imitation as a model input, the rook graph supplies neighbour messages, and lag length/temporal recurrence represents inertia. These are aggregate predictive channels and cannot identify individual behaviour. The future hybrid register remains H1–H7 candidate and H8 postponed; no hybrid is selected here.

| Visual | Rendered view | Text and plotted definitions |
| --- | --- | --- |
| Methodology and gates A–D | [SVG](../../visuals/00_overview/methodology.svg) / [PNG](../../visuals/00_overview/methodology.png) | [Mermaid](../../visuals/00_overview/methodology.mmd), [nodes](../../visuals/00_overview/methodology_nodes.csv), [edges](../../visuals/00_overview/methodology_edges.csv) |
| Data-to-report pipeline | [SVG](../../visuals/00_overview/pipeline.svg) / [PNG](../../visuals/00_overview/pipeline.png) | [Mermaid](../../visuals/00_overview/pipeline.mmd), [nodes](../../visuals/00_overview/pipeline_nodes.csv), [edges](../../visuals/00_overview/pipeline_edges.csv) |
| Proposed splits | [SVG](../../visuals/t02/split_timeline.svg) / [PNG](../../visuals/t02/split_timeline.png) | [Mermaid](../../visuals/t02/split_timeline.mmd), [timeline CSV](../../visuals/t02/split_timeline.csv), [all origins](../../visuals/t02/split_origins.csv) |
| Proposed GNN | [SVG](../../visuals/t02/gnn_architecture.svg) / [PNG](../../visuals/t02/gnn_architecture.png) | [Mermaid](../../visuals/t02/gnn_architecture.mmd), [nodes](../../visuals/t02/gnn_architecture_nodes.csv), [edges](../../visuals/t02/gnn_architecture_edges.csv) |

The diagrams are generated by `python -m visuals.t02`. Mermaid and native SVG exports share a declarative text graph; no external diagram exporter or installation is required. Current modules and folders are named in the pipeline; Part B and Task 3 modules are explicitly labelled future. [configs/style.yaml](../../configs/style.yaml) fixes one colour per model for all subsequent figures. [configs/experiments.yaml](../../configs/experiments.yaml) is the approved machine-readable protocol pending commit/tag.

## 2. Findings — exploration and data interpretation (no approval needed)

The required national history, zero shares, dynamic maturity series and isolate totals are full-source descriptive views. They do not compute test forecasts, test losses or model selection scores. Protocol-facing count distributions, seasonal means, lag correlations and the cumulative map use training history through the first proposed validation origin only. Yearly spatial autocorrelation uses complete years before that origin. No feature or model is selected from held-out test errors. These distinctions also appear in [the exploration index](../../data/explore/t02/index.md).

| Exploratory view | Figure | Plotted values / details |
| --- | --- | --- |
| National monthly installations; evaluation cutoff marked | [national_monthly.png](../../data/explore/t02/national_monthly.png) | [national_monthly.csv](../../data/explore/t02/national_monthly.csv) |
| Share of explicit zero area-month counts by year | [zero_share_year.png](../../data/explore/t02/zero_share_year.png) | [zero_share_year.csv](../../data/explore/t02/zero_share_year.csv) |
| Monthly-count distribution, log scale; training only | [count_distribution.png](../../data/explore/t02/count_distribution.png) | [count_distribution.csv](../../data/explore/t02/count_distribution.csv) |
| Cumulative installations map; seven missing and sixteen isolates marked | [cumulative_map.png](../../data/explore/t02/cumulative_map.png) | [cumulative_map.csv](../../data/explore/t02/cumulative_map.csv) |
| Month-of-year pattern; training only | [month_of_year.png](../../data/explore/t02/month_of_year.png) | [month_of_year.csv](../../data/explore/t02/month_of_year.csv) |
| Dynamic installed-base terciles over time | [maturity_over_time.png](../../data/explore/t02/maturity_over_time.png) | [maturity_over_time.csv](../../data/explore/t02/maturity_over_time.csv) |
| Lagged-neighbour count correlations; training only | [spatial_lag_correlation_histogram.png](../../data/explore/t02/spatial_lag_correlation_histogram.png) | [spatial_lag_correlation_histogram.csv](../../data/explore/t02/spatial_lag_correlation_histogram.csv) |
| Global Moran I of yearly counts; complete training years | [yearly_moran.png](../../data/explore/t02/yearly_moran.png) | [yearly_moran.csv](../../data/explore/t02/yearly_moran.csv) |
| Zero training naive-error scales by proposed validation origin | [training_zero_scales.png](../../data/explore/t02/training_zero_scales.png) | [training_zero_scales.csv](../../data/explore/t02/training_zero_scales.csv) |

The map is also a paper candidate: [PNG](../figures/t02_cumulative_installations.png) / [CSV](../figures/t02_cumulative_installations.csv). It maps cumulative systems through the initial validation origin, not capacity, households or an adoption rate. Polygon simplification is for display only and never changes the border graph. Light grey means zero or absent counts; missing records have separate cross markers. The map retains offshore islands and uses separate isolate markers.

The initial training window has 9 areas with zero lag-one naive MAE and 8 with zero seasonal (lag-twelve) naive MAE. The latter pooled positive scale is 4.607744 systems. At the last validation origin, using its latest scheduled refit window, 3 seasonal scales are zero. These are training diagnostics, not baseline model runs.

Descriptive lag correlation: 2,611 area correlations are defined; their median is 0.609463. Each pairs y(i,t) with the mean of observed rook neighbours at t−1 through 2018-11. Empty neighbour sets and constant series are marked undefined, not silently set to zero. Full per-area values: [spatial_lag_correlations.csv](../../data/explore/t02/spatial_lag_correlations.csv). **Counts are not scaled by dwellings; both area size and installation volume enter this correlation. It has no causal interpretation.**

Global Moran I is computed on observed-area yearly totals using row-standardised rook weights and zero weight rows for observed isolates. I = (N/S0) sum(w_ij z_i z_j) / sum(z_i²), with N the observed areas and S0 the sum of weights. No permutation p-value is computed. In 2017, descriptive I is 0.369961; the full series is in the linked CSV. **Counts are not scaled by dwellings; both area size and installation volume enter this statistic. It does not measure behavioural transmission.**

The zero-month share is 99.34% in the first complete calendar year and 28.92% in 2011. This motivates proposing training targets from 2011, while keeping all earlier history for cumulative base and inputs. Month-of-year means mix secular growth and seasonality; dynamic terciles reassign membership each month and are not fixed cohorts.

## 3. Fixed panel decisions and approved model eligibility (P1)

Gate A fixes the panel start at April 2001, when certificate creation began, and the source end at September 2026. The target is certificate backed solar PV installations, including upgrades and off-grid systems. Own cumulative base is the sum since April 2001 through the origin, inclusive. It is a count of certificate backed systems, not a saturation rate or number of distinct households.

There are 2,634 observed spatial areas and 2,641 graph nodes. The 177 unmatched CER postcodes remain in the join ledger, with totals, and outside the spatial panel. Their installation share is 0.049055%. No additional exclusions are enacted by this proposal.

Postcodes 1825 and 4513 have zero CER historical totals and nonnegative counts, so April 2001–December 2010 counts are deduced to be zero. This is a Gate A deduction, not imputation. Both codes are unmatched and stay outside the spatial panel. The exploration view records the deduction in [historical_zero_deductions.csv](../../data/explore/t02/historical_zero_deductions.csv); raw and interim files are unchanged. No model-ready panel is built in Part A.

Seven graph nodes have no CER observations: 2331, 3920, 6182, 6470, 6712, 6762, 7139. **Approved handling:** keep them in every graph, use zero placeholders with observation flag zero, exclude them from training loss, tuning scores and evaluation, and suppress their outgoing feature/hidden-state messages. Zero placeholder is not an observed zero target. The loss mask has the same membership for every model and every origin. Preserve all components and isolate nodes. No targets or cumulative counts are inferred for these seven nodes.

**Approved empty-neighbour representation:** the mean over observed neighbours is zero with `has_observed_neighbour_flag=0`; own history remains available. The same rule applies when neighbours exist geometrically but all lack observations. Keep observed isolates in loss and evaluation. No geographic links are invented. Computational identity terms in GNN normalisation do not change the stored rook edge list.

The disconnected 112-area component contains postcodes **7000–7470**, all with prefix 7: Tasmania, including its connected Postal Areas. Its membership is in [component_112_members.csv](../../data/explore/t02/component_112_members.csv). It is not a spurious mainland split and must not be joined artificially across Bass Strait. Offshore Tasmanian isolates remain separate.

| Isolated Postal Area | CER installations through September 2026 (systems) | Observation status |
| --- | ---: | --- |
| 2898 | 44 | observed |
| 2899 | 885 | observed |
| 3921 | 93 | observed |
| 4025 | 271 | observed |
| 4183 | 763 | observed |
| 4184 | 3666 | observed |
| 4507 | 8717 | observed |
| 4819 | 946 | observed |
| 4875 | 178 | observed |
| 6161 | 4 | observed |
| 6712 | unknown | no CER records; total unknown |
| 6798 | 209 | observed |
| 6799 | 15 | observed |
| 7255 | 277 | observed |
| 7256 | 334 | observed |
| 7257 | 2 | observed |

[All isolate totals CSV](../../data/explore/t02/isolated_area_totals.csv). These full-source totals are descriptive audit totals, not forecasting inputs at earlier origins.

## 4. Approved expanding-window splits (P2)

An origin is the last observed installation month, inclusive. Inputs and preprocessing use only months at or before that origin. Targets are origin+1 through origin+12. The table contains calendar definitions, not evaluated test data.

| Block | Origins | Number | Target envelope |
| --- | --- | ---: | --- |
| Validation | 2018-11 to 2021-10 monthly | 36 | 2018-12 to 2022-10 |
| Final test; sealed | 2022-10 to 2024-09 monthly | 24 | 2022-11 to 2025-09 |

The last validation target equals the first test origin, October 2022, and is before the first test target. Origins between the blocks are not evaluated; their history can later be used when it is available at a fit origin. No validation target falls after the first test origin. The last test target is September 2025, respecting the reporting-lag cutoff.

Training is expanding, with first eligible target January 2011. At scheduled fit origin r, sample origin s contributes horizon h exactly when January 2011 <= s+h <= r and the area target is observed. Mask later target months; never replace them with zeros. Include samples with only some eligible horizons. Boosting uses only eligible (area,s,h) rows; GNN loss uses the identical mask and is normalised by the number of eligible observed cells, not padded vector length. Include early sample origins too: January 2010 contributes h=12 for January 2011. At the first validation fit in November 2018, there are 106 candidate sample origins, January 2010–October 2018, and 1140 eligible sample-horizon cells before multiplying by observed areas. Every horizon includes all observed targets January 2011–November 2018. The shared calendar-mask unit test checks both early and recent partial vectors.

Use 24-month input windows with cumulative base reaching April 2001. Fit a fresh model every three months from the first origin of each block and reuse weights between refits while updating available input history through the monthly forecast origin. Never warm-start from a later-origin model. There are twelve validation refits and eight final-test refits per seed. Both boosting conditions and all three GNN conditions use the same schedule and target eligibility. Seasonal naive updates its historical reference monthly.

These backtests use revised data available in the current snapshot. They are not real-time-vintage backtests. The reporting-lag cutoff prevents recent immature targets but does not recreate what each earlier publication contained. State this limitation in every future result report. Final test evaluation is run once at the end of the project with all choices frozen; no test forecasts are run in Task 2.

**Additional limitation accepted at protocol approval:** the last three test target months, July–September 2025, fall after batteries became eligible under the scheme on 1 July 2025. This timing may affect interpretation across the scheme change; it does not change the SGU Solar installation target or the approved dates. No causal effect or adjustment is inferred.

**24-month horizon:** feasible in data length but not proposed for protocol v1. Keeping 24 final test origins would move them to October 2021–September 2023. Validation must then end by October 2019, so keeping its proposed November 2018 start leaves only 12 origins instead of 36. To preserve 36 origins, move validation to November 2016–October 2019. This loses more recent validation regimes and requires new approval; it is not silently added after the tag.

## 5. Approved objective, scoring and tuning (P3–P5)

Predict monthly counts for horizons 1–12 directly. Report monthly horizons 1, 6 and 12 plus the sum of all twelve forecasts. Sum forecasts before measuring the twelve-month-total error; do not average monthly absolute errors and call that a total error. Seasonal naive uses y(o+h−12), which is observable for every proposed horizon. It is a fixed benchmark and has no tuning configurations or fitted objective.

**MAE:** average absolute error across observed areas at each origin, then across origins; units systems per area for monthly horizons and systems per area per twelve-month window for the aggregate. Also show each fixed seed and the mean and spread across seeds. No installation-volume weighting.

**MASE:** seasonal training scale s_i(r) = mean over t from January 2011 through the latest scheduled refit origin r of |y(i,t)−y(i,t−12)|. Historical references may precede 2011. If s_i(r)>0 use it unchanged; if it is exactly zero use the mean of strictly positive area scales from that training window. If all scales are zero, use one installation. Use no arbitrary tiny epsilon and exclude no observed area for zero scale. Denominators are recomputed at each scheduled refit and frozen between refits, shared across conditions. Call this **seasonal MASE with pooled zero-scale fallback**, since the fallback modifies ordinary MASE. For the twelve-month-total outcome divide its absolute error by twelve times the monthly scale, explicitly a sum-scale convention rather than a separately fitted annual benchmark. Do not interpret MASE<1 as beating seasonal naive for fallback areas.

Maturity breakdowns use cumulative base through the forecast origin only. Rank observed areas by base, break ties by four-character postcode and partition into equal-count terciles. Recompute membership at each origin; no final-period grouping or capacity normalisation. Report area counts beside each group result.

**Approved comparison:** use `dieboldmariano.dm_test`, version **1.1.0**, with `harvey_correction=True`, `variance_estimator="bartlett"`, `one_sided=False`, and `h` equal to 1, 6 or 12 (12 for the aggregate). First average absolute losses across the common observed areas at each origin, then average those losses across the same seeds; the testing unit is an origin, not an area-month or seed. To pass already-computed loss sequences to the API, use `V=zeros`, `P1=loss_A`, `P2=loss_B`, and `loss=lambda actual,predicted: predicted`; this reproduces the origin loss difference rather than testing errors of a national mean series. The package computes autocovariances through h−1 and the Harvey–Leybourne–Newbold correction, with a t reference. Report undefined results for nonpositive/zero estimated variance, not invented p values. Monthly origins overlap and 36 validation / 24 test origins provide limited power at h=12; state that limitation.

**DM adapter unit check:** `tests/test_dm_adapter.py` uses origin loss differences [1,2,1,3,2,3], n=6 and h=2. Hand calculation gives mean 2, centred lag-zero covariance 2/3 and lag-one covariance −1/6. Bartlett long-run variance is 1/2, variance of the mean 1/12, and HLN factor sqrt(5/9); the corrected statistic is **sqrt(80/3)**. The test applies `evaluation.dm.dm_loss_inputs` to the toy losses and checks that statistic and the sign reversal. This is a dependency-free adapter/unit test, not an integration test of the external package or its p-values; dieboldmariano 1.1.0 is not installed in the current environment. `dm_from_losses` requires that exact version at runtime. No forecasts or fitted models are used.

Predeclare the three Part B comparisons: neighbour boosting versus own boosting, own boosting versus seasonal naive, and neighbour boosting versus seasonal naive. Report raw p values and Holm-adjusted values over the three pairs times four reported outcomes; alpha 0.05. In Task 3 apply the same origin-aggregation and correction to real versus no graph and real versus shuffled, with its own predeclared outcome family. Validation is a development set used for tuning; its p values are descriptive screening evidence. Confirmatory comparisons belong to the untouched final test.

**Shared objective:** Poisson negative log likelihood (omit the target-only factorial constant), mean(mu−y log(mu)) over observed node/sample/horizon cells. Gradient boosting proposes one pooled direct-horizon `HistGradientBoostingRegressor(loss="poisson")` with horizon as a feature; the GNN emits twelve softplus rates. Apply a common rate floor of 1e−6 for numerical evaluation. Predict unrounded nonnegative expected counts. The objective is a count scoring rule, not a claim of Poisson dispersion or calibrated intervals. The same mask, target vectors, loss weights, split dates and configuration count apply to boosting and GNN conditions.

Approved own features for Part B: 24 monthly lags, trailing means over 3/6/12 months, month-of-year sine/cosine, cumulative base through origin, observation and isolate flags, and the requested horizon. Lag k at origin o is y(o−k+1), independent of forecast horizon; rolling means end at o inclusive. Boosting uses the known target-month calendar and horizon. The GNN uses historical calendar channels with a horizon-specific head, and cumulative base at each historical input month. Spatial boosting adds means of observed neighbours at the same lagged months and cumulative base through o, plus the empty-neighbour flag. No area IDs, coordinates, state indicators, Census or policy predictors. Count/base inputs use log1p; targets remain counts. Any fitted preprocessing uses training history only. Feature builders and their leakage tests are Part B, not implemented here.

**Approved identical budget:** 6 Cartesian-grid configurations per tunable condition, tuning seed [11] at two anchors 2019-08, 2020-08. Select by mean MAE across observed areas, twelve horizons and anchors; ties use the lower configuration index. Then evaluate the selected configuration at all monthly validation origins with seeds [11, 29, 47] and quarterly refits. **46 = (6 configurations x 1 seed x 2 anchors) + (12 quarterly refits x 3 evaluation seeds) − 2 reused selected-configuration/seed-11 anchor fits.** Thus 12 tuning + 36 selected evaluation − 2 reused = 46 unique validation fits per condition. All forecast origins remain monthly. No warm starts or extra configuration searches. Final-test fits are additional and remain sealed; eight quarterly test refits x three seeds = 24 later fits per condition. Counting future test fits for resource planning does not access their target values.

| Tunable condition | Tuning fits | Selected validation fits | Reused fits | Unique validation fits |
| --- | ---: | ---: | ---: | ---: |
| Boosting: own lags | 12 | 36 | 2 | 46 |
| Boosting: own and neighbour lags | 12 | 36 | 2 | 46 |
| GNN: real graph | 12 | 36 | 2 | 46 |
| GNN: no graph | 12 | 36 | 2 | 46 |
| GNN: within-state shuffled | 12 | 36 | 2 | 46 |

The seasonal-naive rule is fixed and requires no tuning fits. The GNN timing pilot is separately recorded resource measurement, not extra validation-scored search. Both boosting conditions and all three GNN conditions have identical configuration counts, anchor origins, tuning seeds, evaluation seeds, refit dates and horizon eligibility. Their algorithms have different fixed iteration/epoch caps, not different numbers of searches.

The approved boosting grid is learning rate {0.03,0.1} x maximum leaves {15,31,63}, L2 fixed at 1, with 300 iterations and automatic early stopping disabled. The GNN grid is width {32,64,96} x learning rate {0.001,0.003}, weight decay fixed at 1e−4, 75 fixed epochs, no early stopping, Adam, batch two origin-windows, FP32, sequential fits. Relative to the earlier draft, this reduces search breadth, refit frequency and the GNN epoch cap. It may adapt more slowly or underfit; it is a practical compromise, not a guarantee of equal accuracy. Do not increase epochs or configurations after seeing validation results without an approved protocol revision.

## 6. Approved GNN design and unmeasured resource requirements (P5–P6)

Use a **T-GCN-style graph-convolutional GRU encoder**, an established GCN+GRU family, adapted to a direct twelve-horizon Poisson-rate head. No architecture is implemented here. Graph-convolve the concatenation of current node input and previous hidden state inside reset/update/candidate gates; weights are shared across all nodes and time steps. Start hidden states at zero for each training sample. One graph hop per recurrent update is fixed; recurrence can carry information across updates and is not a pure single-hop receptive field over the whole window. A shared node embedding makes a later diffusion-parameter output head possible, but no Bass parameters or recurrence are included in protocol v1.

Inputs are 24 months x 2,641 nodes x six channels: log1p count, log1p cumulative base, calendar sine/cosine, observation flag and isolate flag. Normalise the sparse masked rook adjacency plus a computational identity symmetrically. Mask unavailable nodes before every message step and hold their hidden states at zero. The no-graph condition replaces the adjacency term with zero, leaving only the identity/self-history operator. Use the same weights/shapes, objective and budget under real/no/shuffled graphs; never change the stored rook edge list to add self links.

Analytic size: 4,140, 14,412 or 30,828 parameters for hidden widths 32/64/96. Formula: (F+H)·3H + 3H gate/candidate biases + H·12 + 12 output biases, F=6. See [gnn_size_memory.csv](../../visuals/t02/gnn_size_memory.csv). This assumes one shared first-order graph filter per gate projection and no extra embedding matrices; changing that implementation requires updating the estimate before approval.

Hardware supplied by the researcher: RTX 4070 Laptop GPU and 32 GB system RAM. NVIDIA lists 8 GB VRAM for this laptop GPU; system RAM is separate and does not substitute for VRAM. With sparse operators, batch two and width at most 96, a saved FP32 hidden sequence is about 46.4 MiB; an intentionally conservative 24-tensor activation allowance is about 1.09 GiB before framework/workspace overhead. **Planning requirement: about 2–4 GB VRAM, at least 4 GB free recommended, and 8–16 GB system RAM for sequential fits.** The standard 8 GB GPU and supplied 32 GB RAM appear sufficient for this compact design, but these are analytic/planning estimates, not a measured guarantee. Avoid dense adjacency tensors, concurrent fits and materialising every overlapping GNN window on the GPU. Build CPU boosting tables one fit at a time.

**Is a 200-hour runtime established? No.** The earlier upper-end calculation was 207 full fits per condition x 3 GNN conditions x an assumed 20 minutes per fit / 60 = 207 hours. The 20-minute assumption was never benchmarked. That arithmetic was valid, but presenting it as an expected runtime was too strong. It is superseded as a runtime forecast. Parameter count alone cannot predict training speed: sparse kernels, graph size, windows, epochs, laptop power and thermals all matter.

**Approved Task 3 timing gate:** at the start of Task 3, before any full GNN workload, run **two to four pilot fits on the same machine used for the full runs**. Default: one width-32 fit and one width-96 fit, seed 11, tuning anchor August 2020, real graph, learning rate 0.001 and weight decay 1e−4. Each fit uses the frozen 75 epochs and objective; up to two additional fits may repeat those same timing configurations. Measure time per fit, peak GPU memory and the training loss curve on training data only. Do not compute validation/test scores or use the pilot to change configurations, epochs or objective. Keep pilot measurements separate from search trials, and discard pilot weights.

**Hard resource stop:** project the total GPU hours for all three GNN conditions using the slower pilot width and account explicitly for training-window growth beyond the single pilot anchor. Report the 138 validation fits, the 72 future final-test fits (210 full fits in total), measured pilot overhead, and a conservative combined GPU-hour total. This includes final-test cost only as a calendar-based resource projection, not test evaluation. If the projected combined total exceeds **24 GPU hours**, stop before the full workload and propose **protocol v2**. Do not reduce configurations, seeds, epochs, change the objective or omit conditions under protocol v1. Memory estimates are also to be confirmed by this pilot. No pilot is run now.

**Sensitivity arithmetic, not predicted runtime:** the table below shows the consequences of assumed average full-fit durations under the smaller plan. Actual duration could lie outside these examples. Pilot time, CPU preprocessing and final-test fits are additional. See [compute_sensitivity.csv](../../visuals/t02/compute_sensitivity.csv).

| Assumed average minutes per full fit | Hours per condition (46 fits) | Hours for all three GNN conditions (138 fits) |
| ---: | ---: | ---: |
| 1 | 0.77 | 2.30 |
| 5 | 3.83 | 11.50 |
| 10 | 7.67 | 23.00 |

All future training, including the timing pilot, is a researcher command regardless of duration. P1–P7 are approved, but the current instruction is to finish the protocol record, commit/tag proposal and stop. It does not start Part B or Task 3.

## 7. Approved state assignment and shuffled control (P7)

The already-approved Non ABS GeoPackage contains `LGA_2021_AUST_GDA2020` with `STATE_CODE_2021` and `STATE_NAME_2021`; [available_state_attributes.csv](../../visuals/t02/available_state_attributes.csv) confirms those attributes locally. No extra download is proposed or performed. Use the LGA geometry only as a state-boundary carrier, never as a predictor or added covariate. This proposal does not assign states yet.

After approval, dissolve spatial 2021 LGA polygons by state; project to Australian Albers EPSG:9473; intersect each POA and assign the state with greatest land-area overlap. Record all overlap shares, cross-border flags and deterministic state-code tie breaks. Retain Other Territories as a separate state class. Special nonspatial LGA rows do not define state polygons; record them as geometry-free state-carrier rows, without changing the approved POA graph ledger. Stop for review on invalid polygons, no overlap or unexplained coverage gaps. Do not guess from first postcode digits: some POAs cross state borders. No population or dwelling weighting is used.

For the shuffled condition, degree-preserving double-edge swaps rewire only within-state edges; cross-state edges remain unchanged. Each replacement edge must have endpoints in the same assigned state, with no loops or duplicate edges. This preserves node degrees, isolates, the unobserved-node mask and cross-state links. It cannot make every existing cross-border real edge intra-state without changing the original degree/control definition; holding them fixed makes the control explicit. The aim is to disrupt within-state geography, not to guarantee every original component stays connected after shuffling. Fixed graph seeds are 11/29/47; target ten accepted swaps per intra-state edge and record attempts, accepted swaps and original-edge overlap. If constrained states cannot mix adequately, stop and ask rather than silently changing the null graph. This interpretation of within-state shuffling is an approval item.

## Approval boundary

All P1–P7 decisions are accepted on 28 October 2026, with the horizon-mask, battery-timing limitation, DM adapter test and Task 3 timing-gate revisions recorded above. No further protocol approval is requested now. The researcher commits and tags `protocol-v1`; Part B is not started. Model runs and the Task 3 pilot require later instructions. The directory-casing fix is packaging, not a research decision.

## Reproduce the Part A artifacts

Use the existing project environment, with no package installation. Each command is expected below five minutes and writes its own log. They create descriptive/proposal artifacts only. Do not rerun unchanged inputs when these logs already exist.

```powershell
python -m explore.t02_panel 2>&1 | Tee-Object logs/t02_exploration.log
python -m visuals.t02 2>&1 | Tee-Object logs/t02_visuals.log
python -m visuals.t02_report 2>&1 | Tee-Object logs/t02_protocol_report.log
python -m pytest -q 2>&1 | Tee-Object logs/t02_tests_part_a.log
```

Exploration is read-only over raw/interim histories; the authorised deductions exist only in its analysis view and deduction CSV. No `data/processed` model panel is written. Model features, model-panel loss masks, model-fitting code and leakage tests for constructed features belong to Part B. Current tests validate the proposal date boundaries and origin-only diagnostic calculations; they do not claim feature leakage tests already exist.

Local-only visual policy, updated by the researcher on 28 October 2026: data/, visuals/, reports/figures/, src/explore/, src/visuals/, the older src/audit/lag.py generator, configs/style.yaml and their dedicated visual tests are ignored by Git. The visual artifact manifest is also local-only. The written protocol, experiments configuration, evaluation utilities and core protocol tests remain versioned. Shared nonvisual calendar, eligibility and scoring helpers live in evaluation.protocol so core tests do not require private plotting code. Figure links and reproduction commands refer to the local workspace; a repository clone does not include the private generators or assets. This explicit researcher instruction supersedes the earlier tracked-exploration rule.

## Primary references checked for this proposal

- [T-GCN primary paper](https://arxiv.org/abs/1811.05320): GCN and GRU family; proposed direct count head is an explicit adaptation.
- [dieboldmariano 1.1.0](https://pypi.org/project/dieboldmariano/1.1.0/): dm_test API, Bartlett estimator and Harvey correction; version verified, not installed.
- [DM package implementation](https://github.com/edoannunziata/dieboldmariano): origin-wise loss adapter and horizon autocovariance convention.
- [HistGradientBoostingRegressor 1.6.1](https://scikit-learn.org/1.6/modules/generated/sklearn.ensemble.HistGradientBoostingRegressor.html): proposed Poisson-capable CPU baseline; no install or fit.
- [NVIDIA laptop specifications](https://www.nvidia.com/en-us/geforce/laptops/compare/): RTX 4070 Laptop standard memory is 8 GB, distinct from 32 GB system RAM.
- [ABS Edition 3 Postal Areas](https://www.abs.gov.au/statistics/standards/australian-statistical-geography-standard-asgs/edition-3-july-2021-june-2026/non-abs-structures/postal-areas): cross-border POAs preclude a reliable first-digit state shortcut.

These are methodology/software references, not additional data sources. No library above was installed by the agent. Future model/evaluation dependencies must be pinned and installed by the researcher after approval; the current exploration environment and lockfile are unchanged.
