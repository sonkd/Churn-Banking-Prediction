"""Module 4 — Feature engineering. Build RFM + behavioral trend features from the monthly
transactions, encode/scale, address imbalance (SMOTE) inside the modeling CV (M5), select.
Outputs data/processed/features.parquet (also the monitoring reference distribution) and
data/processed/feature_metadata.json (schema, feature list, version, created_at, row hash) -
the hand-off contract read by both the batch prediction pipeline and monitoring (see P1)."""
import hashlib
from datetime import datetime, timezone

import numpy as np, pandas as pd
from src.common.io import load_config, rpath, read_csv, save_json


def _row_hash(df: pd.DataFrame) -> str:
    return hashlib.sha256(pd.util.hash_pandas_object(df, index=False).values.tobytes()).hexdigest()[:12]


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

    row_hash = _row_hash(feats)
    metadata = {
        "version": f"1.0.0+{row_hash}",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "row_count": int(len(feats)),
        "target": cfg["target"],
        "feature_list": [c for c in feats.columns if c not in ("customer_id", cfg["target"])],
        "schema": {c: str(dt) for c, dt in feats.dtypes.items()},
        "row_hash": row_hash,
    }
    save_json(metadata, "../data/processed/feature_metadata.json")

    print(f"[M4] features={feats.shape} -> {out}")
    print(f"[M4] feature_metadata version={metadata['version']} -> data/processed/feature_metadata.json")
    return feats

if __name__ == "__main__":
    build()
