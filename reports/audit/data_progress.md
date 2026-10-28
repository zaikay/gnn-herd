# Task 1 data progress

Historical progress note. Superseded by [the completed Gate A audit](audit_week1.md), including confirmed dates and graph validation.

Graph statistics and Gate A verdict are pending. This is a data check, not a scientific conclusion.

## Approved geography treatment

The researcher approved retaining ABS special rows in the audit and excluding only their NULL geometries from graph construction. Codes 9494, 9797 and ZZZZ are preserved in `abs_special_rows.csv`. The graph-only exclusions and approval are recorded in `exclusions.csv`. No CER record is excluded. Source: `logs/t01_approved_special_rows.log`, reproduced with `python -m geography.graph --prepare-only`.

## CER checks

The recent CSV covers January 2011 through September 2026; the earlier CSV covers April 2001 through December 2010. The earlier file does not provide January through March 2001. Those months have not been invented or imputed. Monthly validation found no bad count cells or internal missing month columns. CSV files contain no embedded date candidates in their header preambles. The saved source-page date candidates are in `cer_page_dates.json`; the precise current-as-at field still needs separate confirmation.

The panel contains 859,932 observed postcode-month cells, 2,811 distinct postcodes and 306 distinct months. Its zero share is 0.5244042552201802 of observed cells, not a share of an imputed rectangular panel. Annual national sums have no discrepancies against the saved CER national Solar PV table. Historical totals have 2 nonmatching postcode comparisons; all comparison rows are preserved in `historical_totals.csv`. These are not silently reconciled.

Sources: `logs/t01_profile_live_layout.log` and `logs/t01_data_progress.log`. Reproduce the profiles with `python -m audit.profile`. Raw source URLs, retrieval dates, byte sizes and SHA256 values are in `configs/sources.yaml`. The immutable downloads were logged in `logs/t01_download_cer.log`.

## Postcode join

Of 2,811 CER postcodes, 2,634 match spatial Postal Areas and 177 do not. Matched postcode share is 0.9370330843116329; matched installation share is 0.9995094469814769. The spatial layer contains 2,641 rows after the approved graph-only exclusions. Every CER postcode, including unmatched codes and its total count, remains in `postcode_poa_join.csv`. Any observed special CER codes are listed separately in `cer_special_codes.csv`.

Source: `logs/t01_join.log` and `join_summary.json`. Reproduce with `python -m geography.graph --join-only` after profiling. This command does not build graph edges.

## Reporting lag

The recent national series is in `reporting_lag.csv` and `../figures/reporting_lag.png`. Reproduce with `python -m audit.lag`; output is logged in `logs/t01_lag.log`. The recent tail may be incomplete under the certificate creation period; no correction has been applied.

## Next step

The researcher runs the longer graph command in `internal/STATUS.md`. After that log is reviewed, finish `audit_week1.md`, confirm the source-page current-as-at date, report all graph checks and unresolved coverage questions, and stop at Gate A. No isolate rule has been applied.
