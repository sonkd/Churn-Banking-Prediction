"""Module 4 — Feature engineering. Build RFM + behavioral trend features from the monthly
transactions, encode/scale, address imbalance (SMOTE) inside the modeling CV (M5), select.
Outputs data/processed/features.parquet (also the monitoring reference distribution)."""
import numpy as np, pandas as pd
from src.common.io import load_config, rpath, read_csv

def build():
    cfg = load_config()
    tx = read_csv(cfg["paths"]["synthetic"])
    base = pd.read_parquet(rpath(cfg["paths"]["processed"]) / "base_clean.parquet")
    # RFM-style aggregation per customer
    agg = tx.groupby("customer_id").agg(
        frequency=("txn_count", "sum"),
        monetary=("txn_amount", "sum"),
        app_logins_mean=("app_logins", "mean"),
        complaints_sum=("complaints", "sum"),
    ).reset_index()
    # recency proxy: months since last active txn
    last = tx[tx.txn_count > 0].groupby("customer_id")["month"].max()
    agg["recency"] = (tx.month.max() - agg.customer_id.map(last)).fillna(tx.month.max())
    # behavioral trend: slope of txn_count over months (declining = churn risk hypothesis)
    slope = tx.groupby("customer_id").apply(
        lambda g: np.polyfit(g.month, g.txn_count, 1)[0], include_groups=False)
    agg["txn_trend"] = agg.customer_id.map(slope)
    feats = base.merge(agg, on="customer_id", how="inner")
    out = rpath("../data/processed/features.parquet")
    feats.to_parquet(out, index=False)
    print(f"[M4] features={feats.shape} -> {out}")
    return feats

if __name__ == "__main__":
    build()
