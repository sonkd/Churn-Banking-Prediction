"""Module 2 — EDA. Distributions, outliers, correlations, churn by segment, RFM-style viz.
Discipline (eda-python): label each finding observation / hypothesis / causal-claim.
Run on raw data first to FIND problems; re-read after M3 cleaning."""
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt, seaborn as sns, pandas as pd
from src.common.io import load_config, rpath, read_csv

def run():
    cfg = load_config()
    base = read_csv(cfg["paths"]["raw"])
    fig_dir = rpath(cfg["paths"]["figures"])
    # churn rate by country (OBSERVATION only)
    ax = base.groupby("country")["churn"].mean().plot(kind="bar", title="Churn rate by country")
    plt.tight_layout(); plt.savefig(fig_dir / "churn_by_country.png", dpi=120); plt.close()
    # age distribution
    sns.histplot(base, x="age", hue="churn", bins=30)
    plt.title("Age distribution by churn"); plt.tight_layout()
    plt.savefig(fig_dir / "age_by_churn.png", dpi=120); plt.close()
    print(f"[M2] figures -> {fig_dir}")
    return ["churn_by_country.png", "age_by_churn.png"]

if __name__ == "__main__":
    run()
