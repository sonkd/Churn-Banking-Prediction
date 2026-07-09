"""Module 7 — Data drift + performance monitoring (the Bucket -> Monitoring feedback loop in
the FTI diagram). Reads the latest incoming batch from BUCKET_URI, compares it against the
training reference data/processed/features.parquet, always computes PSI (dependency-free), and
writes the retrain-trigger decision to BUCKET_URI/monitoring/metrics.json - plus an Evidently
HTML report when the bucket is a local directory (best-effort; PSI is the guaranteed contract)."""
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import fsspec
import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))  # make `common` importable when run as a plain script
from common.bucket import default_bucket_uri

REF = Path(__file__).resolve().parents[2] / "data/processed/features.parquet"
NUM = ["age", "balance", "frequency", "monetary", "app_logins_mean", "complaints_sum", "recency", "txn_trend"]
PSI_THRESHOLD = 0.2


def psi(ref, cur, bins=10):
    q = np.quantile(ref, np.linspace(0, 1, bins + 1))
    q[0], q[-1] = -np.inf, np.inf
    r = np.histogram(ref, q)[0] / len(ref) + 1e-6
    c = np.histogram(cur, q)[0] / len(cur) + 1e-6
    return float(np.sum((c - r) * np.log(c / r)))


def run():
    bucket = default_bucket_uri()
    fs, base = fsspec.core.url_to_fs(bucket)
    incoming_path = f"{base}/incoming/latest.parquet"
    if not fs.exists(incoming_path):
        raise FileNotFoundError(
            f"No incoming batch at {bucket}/incoming/latest.parquet - run "
            "`python monitoring/generate_drift_batch.py` first to simulate one."
        )

    ref = pd.read_parquet(REF)
    with fs.open(incoming_path, "rb") as f:
        cur = pd.read_parquet(f)

    psis = {c: round(psi(ref[c], cur[c]), 3) for c in NUM if c in cur and c in ref}
    drifted = [c for c, v in psis.items() if v > PSI_THRESHOLD]
    trigger = len(drifted) > 0
    decision = {
        "checked_at": datetime.now(timezone.utc).isoformat(),
        "n_incoming": int(len(cur)),
        "psi": psis,
        "drifted_features": drifted,
        "retrain_trigger": trigger,
        "rule": f"retrain if any feature PSI > {PSI_THRESHOLD} OR recall drops > 10%",
    }

    fs.makedirs(f"{base}/monitoring", exist_ok=True)
    with fs.open(f"{base}/monitoring/metrics.json", "w") as f:
        json.dump(decision, f, indent=2)

    # Evidently HTML report (optional, richer). save_html() needs a real filesystem path, so
    # this only runs when the bucket resolves to the local filesystem (the default today).
    try:
        from evidently.legacy.report import Report
        from evidently.legacy.metric_preset import DataDriftPreset
        if fs.protocol in ("file", ("file", "local"), "local"):
            rep = Report(metrics=[DataDriftPreset()])
            rep.run(reference_data=ref[NUM], current_data=cur[NUM])
            html_path = Path(f"{base}/monitoring/evidently_drift.html")
            html_path.parent.mkdir(parents=True, exist_ok=True)
            rep.save_html(str(html_path))
            print(f"[M7] Evidently report -> {bucket}/monitoring/evidently_drift.html")
        else:
            print("[M7] Evidently HTML skipped (non-local bucket); PSI metrics.json is authoritative.")
    except Exception as e:
        print(f"[M7] Evidently unavailable ({type(e).__name__}); PSI fallback used.")

    print(f"[M7] drifted={drifted} retrain_trigger={trigger}")
    return decision


if __name__ == "__main__":
    run()
