"""National recent tail; no interpretation of individual behaviour."""
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd


def recent_tail(panel):
    return panel.groupby("month")["count"].sum().sort_index().tail(24)


def main():
    panel = pd.read_csv("data/interim/cer_panel.csv", dtype={"postcode": str, "month": str})
    tail = recent_tail(panel)
    tail.to_csv("reports/audit/reporting_lag.csv")
    fig, ax = plt.subplots(figsize=(11, 4))
    tail.plot(ax=ax, marker="o")
    ax.set(xlabel="Installation month", ylabel="Certificate backed installations (systems)",
           title="Recent national counts: last 12 months may be incomplete")
    ax.tick_params(axis="x", rotation=60)
    fig.tight_layout()
    Path("reports/figures").mkdir(parents=True, exist_ok=True)
    fig.savefig("reports/figures/reporting_lag.png", dpi=160)
    plt.close(fig)
    print(tail.to_string())


if __name__ == "__main__":
    main()
