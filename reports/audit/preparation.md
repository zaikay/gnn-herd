# Task 1 preparation

Historical preparation note. Current findings and commands are in [the completed Gate A audit](audit_week1.md).

Step 1 only. The data audit and Gate A verdict are pending real input validation.
No records have been excluded and no isolate links have been added.

## Sources checked

- [ABS Edition 3 download page](https://www.abs.gov.au/statistics/standards/australian-statistical-geography-standard-asgs/edition-3-july-2021-june-2026/access-and-downloads/digital-boundary-files): GDA2020 Non ABS Structures GeoPackage ZIP. The header request produced no Content-Length. See `reports/audit/abs_header.json` and `logs/t01_abs_header_retry.log`. Therefore its transfer size is unknown under the download rule. The page labels it 671.39 MB; this label is source metadata, not a measured download size.
- [ABS Edition 4 Postal Areas](https://www.abs.gov.au/statistics/standards/australian-statistical-geography-standard-asgs/edition-4-july-2026-june-2031/non-abs-structures/postal-areas): released 14 October 2026. Keep Edition 3 as instructed.
- [CER source page](https://cer.gov.au/markets/reports-and-data/small-scale-installation-postcode-data): download script selects SGU Solar installations by URL, not SWH Solar or capacity. The page snapshot, retrieval date, checksums and sizes are recorded during download. The audit compares the saved national Solar PV annual table, not a later live page.

## Reproduction after the preparation pause

Use Python 3.13. The exact dependency set is in `requirements.lock`; direct dependencies are also pinned in `pyproject.toml`. No environment has been created or packages installed by the agent.

After the researcher commands in STATUS.md, the remaining entry points are:

```powershell
.venv\Scripts\python.exe -m download.fetch cer 2>&1 | Tee-Object logs/t01_download_cer.log
.venv\Scripts\python.exe -m audit.profile 2>&1 | Tee-Object logs/t01_profile.log
.venv\Scripts\python.exe -m geography.graph 2>&1 | Tee-Object logs/t01_graph.log
.venv\Scripts\python.exe -m audit.lag 2>&1 | Tee-Object logs/t01_lag.log
```

Do not run these automatically at this pause. The graph command may exceed the time limit and belongs to the researcher. Inspect the layer manifest if the default layer name differs from the downloaded archive. Outputs include all unmatched postcodes, graph nodes including isolates, point-contact extra edges, annual discrepancies and historical-total discrepancies. The loader fails on invalid counts, duplicate keys, missing months or unexpected rows. It retains issue rows for review and makes no blank-to-zero assumption. Missing POA observations remain missing; no zero panel is invented.

`audit_week1.md` is deliberately not written yet: its measurements and verdict need the real files, logs and researcher review. The scripts need a live-file smoke test after download; synthetic tests cannot establish the actual CER header layout or ABS layer schema.
