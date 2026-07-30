"""Module 6 — Churn prediction API (FastAPI). Health/readiness per MLOps checklist.
Keeps POST /predict (online demo) and adds read-only, batch-serving endpoints that read
pre-computed results from the bucket written by development/batch/predict.py (Pipeline #3) -
this API never imports anything from research/."""
from typing import Optional

import pandas as pd
from fastapi import Depends, FastAPI, HTTPException, Query

from api.encoding import encode_for_model, needs_encoding
from api.model_loader import load_churn, load_segments, model_card
from api.schema import BatchPrediction, Customer, Prediction
from api.settings import Settings, get_settings
from common.bucket import read_history, read_json, read_latest_predictions

app = FastAPI(title="Digital Bank Churn API", version="0.2.0")
_churn, _src = load_churn()
_seg, _ = load_segments()
_card = model_card()
_thr = float(_card.get("threshold", 0.3))


def _to_batch_prediction(row: pd.Series) -> BatchPrediction:
    return BatchPrediction(
        customer_id=int(row["customer_id"]),
        churn_proba=float(row["churn_proba"]),
        churn_label=int(row["churn_label"]),
        segment=int(row["segment"]),
        model_version=str(row["model_version"]),
        scored_at=str(row["scored_at"]),
    )


def _require_bucket(settings: Settings) -> pd.DataFrame:
    df = read_latest_predictions(settings.bucket_uri)
    if df is None:
        raise HTTPException(status_code=404, detail="bucket is empty - run `make batch-predict` first")
    return df


@app.get("/health")          # liveness
def health(): return {"status": "ok"}


@app.get("/ready")           # readiness: model + bucket state
def ready(settings: Settings = Depends(get_settings)):
    bucket_df = read_latest_predictions(settings.bucket_uri)
    return {
        "ready": _churn is not None,
        "model_source": _src,
        "bucket_state": "populated" if bucket_df is not None else "empty",
        "bucket_uri": settings.bucket_uri,
    }


@app.post("/predict", response_model=Prediction)
def predict(c: Customer):
    raw = c.model_dump()
    X = pd.DataFrame([raw])
    # v3+ models are trained on encoded/engineered columns -> replicate the research encoding.
    # The stub and pre-v3 models take the raw fields directly.
    X_churn = encode_for_model(raw, _card["features"]) if needs_encoding(_card, set(raw)) else X
    p = float(_churn.predict_proba(X_churn)[0, 1])
    seg = None
    if _seg is not None:
        feats = ["recency","frequency","monetary","app_logins_mean","complaints_sum"]
        seg = int(_seg.predict(X[feats])[0])
    return Prediction(churn_probability=round(p, 4), churn_label=int(p >= _thr),
                      segment=seg, threshold=_thr, model_source=_src)


@app.get("/predictions/{customer_id}", response_model=BatchPrediction)
def get_prediction(customer_id: int, settings: Settings = Depends(get_settings)):
    df = _require_bucket(settings)
    row = df[df["customer_id"] == customer_id]
    if row.empty:
        raise HTTPException(status_code=404, detail=f"customer_id {customer_id} not in the latest batch")
    return _to_batch_prediction(row.iloc[0])


@app.get("/predictions", response_model=list[BatchPrediction])
def list_predictions(
    segment: Optional[int] = None,
    top_k: int = Query(20, ge=1, le=1000, description="highest churn_proba first"),
    settings: Settings = Depends(get_settings),
):
    df = _require_bucket(settings)
    if segment is not None:
        df = df[df["segment"] == segment]
    df = df.sort_values("churn_proba", ascending=False).head(top_k)
    return [_to_batch_prediction(row) for _, row in df.iterrows()]


@app.get("/segments", response_model=list[int])
def list_segments(settings: Settings = Depends(get_settings)):
    df = _require_bucket(settings)
    return sorted(int(s) for s in df["segment"].unique())


@app.get("/monitoring/metrics")
def monitoring_metrics(settings: Settings = Depends(get_settings)):
    metrics = read_json("monitoring/metrics.json", settings.bucket_uri)
    if metrics is None:
        raise HTTPException(status_code=404, detail="no monitoring metrics yet - run `make monitor` first")
    return metrics


@app.get("/monitoring/history")
def monitoring_history(settings: Settings = Depends(get_settings)):
    """Prediction drift: one quality record (accuracy/recall/AUC/mean_proba) per batch run."""
    history = read_history(settings.bucket_uri)
    if not history:
        raise HTTPException(status_code=404, detail="no scoring history yet - run `make batch-predict` first")
    return history
