"""Loads the churn model from development/models/ (synced from research/).
Falls back to a deterministic STUB so the service boots with zero research code."""
from pathlib import Path
import joblib, numpy as np, json

MODELS = Path(__file__).resolve().parents[1] / "models"

class StubModel:
    """Deterministic placeholder. Replace by running scripts/sync_model.sh."""
    feature_names_ = ["age","balance","credit_score","tenure","frequency","monetary",
                      "app_logins_mean","complaints_sum","recency","txn_trend","country","gender"]
    def predict_proba(self, X):
        # toy logic: more complaints + low frequency -> higher risk
        import pandas as pd
        df = pd.DataFrame(X)
        risk = (0.2 + 0.05*df.get("complaints_sum",0).astype(float)
                - 0.001*df.get("frequency",0).astype(float)).clip(0.01,0.99)
        return np.c_[1-risk, risk]

def load_churn():
    p = MODELS / "churn_model.pkl"
    if p.exists():
        return joblib.load(p), "research"
    return StubModel(), "stub"

def load_segments():
    p = MODELS / "segmentation_model.pkl"
    return (joblib.load(p), "research") if p.exists() else (None, "stub")

def model_card():
    p = MODELS / "model_card.json"
    return json.load(open(p)) if p.exists() else {"model_type": "stub", "threshold": 0.3}
