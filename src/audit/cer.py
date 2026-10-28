"""Strict CER wide-file reader; never infer blank counts as zero."""
import csv
import io
import re
from datetime import datetime
from pathlib import Path

import pandas as pd


def month_label(value):
    value = re.sub(r"\s+", " ", value.strip())
    value = re.sub(r"\s*-\s*Installations? Quantity$", "", value, flags=re.I)
    for fmt in ("%b %Y", "%B %Y", "%b-%Y", "%B-%Y", "%b-%y", "%B-%y",
                "%Y-%m", "%m/%Y", "%Y %b", "%Y %B", "%d/%m/%Y"):
        try:
            return datetime.strptime(value, fmt).strftime("%Y-%m")
        except ValueError:
            pass
    return None


def dates_in(text):
    return sorted(set(re.findall(r"\b\d{1,2}\s+[A-Za-z]+\s+20\d{2}\b|\b\d{1,2}/\d{1,2}/20\d{2}\b", text)))


def read_wide(path):
    text = Path(path).read_text(encoding="utf-8-sig")
    rows = list(csv.reader(io.StringIO(text)))
    header_index = next((i for i, row in enumerate(rows)
                         if row and row[0].strip().lower() in {"postcode", "small unit installation postcode"}), None)
    if header_index is None:
        raise ValueError(f"No postcode header: {path}")
    header = [v.strip() for v in rows[header_index]]
    if len(set(header)) != len(header):
        raise ValueError("Duplicate column labels; inspect raw layout")
    meta = " ".join(" ".join(row) for row in rows[:header_index])
    # Product identity comes from original source URL plus any embedded labels.
    if re.search(r"\bSWH\b|water heater|capacity", meta, re.I):
        raise ValueError("Wrong product: expected SGU Solar installation counts")
    records = rows[header_index + 1:]
    if any(len(row) != len(header) for row in records):
        raise ValueError("Ragged/footer rows: review required; no rows excluded")
    wide = pd.DataFrame(records, columns=header)
    wide = wide.rename(columns={header[0]: "postcode"})
    bad_codes = ~wide.postcode.str.fullmatch(r"\d{4}")
    months = {c: month_label(c) for c in header[1:] if month_label(c)}
    if not months or len(set(months.values())) != len(months):
        raise ValueError("Missing or duplicate monthly columns")
    panel = wide.melt(id_vars="postcode", value_vars=list(months),
                      var_name="source_column", value_name="raw_count")
    panel["month"] = panel.source_column.map(months)
    panel["count"] = pd.to_numeric(panel.raw_count.str.replace(",", "", regex=False), errors="coerce")
    issues = panel[panel["count"].isna() | (panel["count"] < 0) |
                   (panel["count"] % 1 != 0) | ~panel.postcode.str.fullmatch(r"\d{4}")].copy()
    issues["reason"] = "invalid postcode, blank, nonnumeric, negative or fractional count; retained pending review"
    expected = pd.period_range(min(months.values()), max(months.values()), freq="M").astype(str)
    summary = {
        "file": str(path), "layout": "wide", "units": "certificate backed installations (systems)",
        "columns": header, "rows": len(wide), "months": sorted(months.values()),
        "months_in_source_order": list(months.values()),
        "missing_month_columns": sorted(set(expected) - set(months.values())),
        "duplicate_postcode_rows": int(wide.postcode.duplicated(keep=False).sum()),
        "invalid_postcode_rows": int(bad_codes.sum()), "issue_cells": len(issues),
        "blank_cells": int(panel.raw_count.str.strip().eq("").sum()),
        "explicit_zero_cells": int(panel["count"].eq(0).sum()),
        "current_as_at_candidates": dates_in(meta), "preamble": meta,
        "nonmonthly_columns": [c for c in header[1:] if c not in months],
    }
    return wide, panel, issues, summary


def validate_panel(panel):
    if not panel.postcode.map(lambda p: isinstance(p, str) and bool(re.fullmatch(r"\d{4}", p))).all():
        raise ValueError("Postcodes must be four character strings")
    if panel.duplicated(["postcode", "month"]).any():
        raise ValueError("Duplicate postcode-month keys")
    if panel["count"].isna().any() or (panel["count"] < 0).any() or (panel["count"] % 1 != 0).any():
        raise ValueError("Invalid counts; researcher review required")
    if not panel.groupby("postcode", sort=False).month.apply(lambda s: s.is_monotonic_increasing).all():
        raise ValueError("Months must be ordered within postcode")


def historical_check(recent, early_panel):
    candidates = [c for c in recent.columns if re.search(r"2001\s*(?:[-–]|to)\s*2010", c, re.I)]
    if len(candidates) != 1:
        raise ValueError("Cannot identify unique 2001-2010 total column")
    left = recent[["postcode", candidates[0]]].copy().rename(columns={candidates[0]: "reported_total"})
    left["reported_total"] = pd.to_numeric(left.reported_total.str.replace(",", "", regex=False), errors="coerce")
    right = early_panel.groupby("postcode")["count"].sum(min_count=1).rename("monthly_sum")
    result = left.merge(right, on="postcode", how="outer", indicator=True)
    result["difference"] = result.reported_total - result.monthly_sum
    result["matches"] = result["_merge"].eq("both") & result.difference.eq(0)
    return result
