"""Smoke test: the contract artifacts exist and look sane after run_pipeline."""
import json, subprocess, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]

def test_pipeline_runs_and_emits_contract():
    subprocess.run([sys.executable, "run_pipeline.py"], cwd=ROOT, check=True)
    for f in ["outputs/models/churn_model.pkl", "outputs/models/segmentation_model.pkl",
              "outputs/models/model_card.json", "outputs/metrics/metrics.json"]:
        assert (ROOT / f).exists(), f"missing artifact: {f}"
    m = json.load(open(ROOT / "outputs/metrics/metrics.json"))
    assert 0.0 <= m["churn"]["auc_roc"] <= 1.0
    # anti-leakage guard: a perfect AUC on synthetic data signals leakage
    assert m["churn"]["auc_roc"] < 0.99, "AUC too high — check for data leakage"
