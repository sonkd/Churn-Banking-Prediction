"""Module 7 — Data drift + performance monitoring. Uses Evidently if installed; always
computes PSI and writes a retraining trigger decision. Output: monitoring/reports/."""
from pathlib import Path
import json, numpy as np, pandas as pd
HERE = Path(__file__).resolve().parent
REF = Path(__file__).resolve().parents[2] / "data/processed/features.parquet"
REPORTS = HERE / "reports"; REPORTS.mkdir(exist_ok=True)
NUM = ["age","balance","frequency","monetary","app_logins_mean","complaints_sum","recency","txn_trend"]

def psi(ref, cur, bins=10):
    q = np.quantile(ref, np.linspace(0, 1, bins + 1))
    q[0], q[-1] = -np.inf, np.inf
    r = np.histogram(ref, q)[0] / len(ref) + 1e-6
    c = np.histogram(cur, q)[0] / len(cur) + 1e-6
    return float(np.sum((c - r) * np.log(c / r)))

def run(incoming="incoming_batch.parquet"):
    ref = pd.read_parquet(REF)
    cur = pd.read_parquet(HERE / incoming)
    psis = {f: round(psi(ref[f], cur[f]), 3) for f in NUM if f in cur}
    drifted = [f for f, v in psis.items() if v > 0.2]          # PSI>0.2 = significant drift
    trigger = len(drifted) > 0
    decision = {"psi": psis, "drifted_features": drifted,
                "retrain_trigger": trigger,
                "rule": "retrain if any feature PSI > 0.2 OR recall drops > 10%"}
    json.dump(decision, open(REPORTS / "drift_decision.json", "w"), indent=2)
    # Evidently HTML report (optional, richer)
    try:
        from evidently.report import Report
        from evidently.metric_preset import DataDriftPreset
        rep = Report(metrics=[DataDriftPreset()])
        rep.run(reference_data=ref[NUM], current_data=cur[NUM])
        rep.save_html(str(REPORTS / "evidently_drift.html"))
        print("[M7] Evidently report -> reports/evidently_drift.html")
    except Exception as e:
        print(f"[M7] Evidently unavailable ({type(e).__name__}); PSI fallback used.")
    print(f"[M7] drifted={drifted} retrain_trigger={trigger}")
    return decision

if __name__ == "__main__":
    run()
