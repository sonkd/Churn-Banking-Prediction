"""Module 6 — Churn prediction API (FastAPI). Health/readiness per MLOps checklist."""
import pandas as pd
from fastapi import FastAPI
from api.schema import Customer, Prediction
from api.model_loader import load_churn, load_segments, model_card

app = FastAPI(title="Digital Bank Churn API", version="0.1.0")
_churn, _src = load_churn()
_seg, _ = load_segments()
_card = model_card()
_thr = float(_card.get("threshold", 0.3))

@app.get("/health")          # liveness
def health(): return {"status": "ok"}

@app.get("/ready")           # readiness: model loaded?
def ready(): return {"ready": _churn is not None, "model_source": _src}

@app.post("/predict", response_model=Prediction)
def predict(c: Customer):
    X = pd.DataFrame([c.model_dump()])
    p = float(_churn.predict_proba(X)[0, 1])
    seg = None
    if _seg is not None:
        feats = ["recency","frequency","monetary","app_logins_mean","complaints_sum"]
        seg = int(_seg.predict(X[feats])[0])
    return Prediction(churn_probability=round(p, 4), churn_label=int(p >= _thr),
                      segment=seg, threshold=_thr, model_source=_src)
