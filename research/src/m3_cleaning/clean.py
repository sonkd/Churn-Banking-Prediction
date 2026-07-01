"""Module 3 — Data cleaning. Missing/dupes/inconsistent categories, outlier treatment
(invalid age, negative balance). Document every decision with before/after counts."""
import pandas as pd
from src.common.io import load_config, rpath, read_csv

def clean():
    cfg = load_config()
    base = read_csv(cfg["paths"]["raw"])
    before = len(base)
    log = {"rows_before": before}
    base = base.drop_duplicates("customer_id")
    base = base[(base.age.between(18, 100)) & (base.balance >= 0)]   # outlier rules
    log["rows_after"] = len(base); log["dropped"] = before - len(base)
    out = rpath(cfg["paths"]["processed"]) / "base_clean.parquet"
    base.to_parquet(out, index=False)
    print(f"[M3] cleaned {log}  -> {out}")
    return base, log

if __name__ == "__main__":
    clean()
