"""Batch Prediction Pipeline (Pipeline #3 in the FTI diagram). Scores every customer in
data/processed/features.parquet with the churn + segmentation models - falling back to the
same stub model development/api uses when development/models/ hasn't been synced yet - and
writes the result to the bucket (BUCKET_URI env, default ./bucket). The bucket is accessed
through fsspec so swapping to gs://... or s3://... later needs no code change."""
import json
from datetime import datetime, timezone
from pathlib import Path

import fsspec
import pandas as pd

from api.model_loader import load_churn, load_segments, model_card
from common.bucket import append_history, default_bucket_uri

FEATURES_PARQUET = Path(__file__).resolve().parents[2] / "data/processed/features.parquet"
SEG_FEATURES = ["recency", "frequency", "monetary", "app_logins_mean", "complaints_sum"]


def run():
    df = pd.read_parquet(FEATURES_PARQUET)
    churn_model, churn_source = load_churn()
    seg_model, seg_source = load_segments()
    card = model_card()
    model_version = card.get("semver") or card.get("version") or card.get("model_type", churn_source)

    feature_cols = card.get("features") or [c for c in df.columns if c not in ("customer_id", "churn")]
    missing = [c for c in feature_cols if c not in df.columns]
    if missing and churn_source == "research":
        raise ValueError(
            f"features.parquet is missing columns the model was trained on: {missing}. "
            "Re-run the research pipeline / promote the matching features table."
        )
    X = df[[c for c in feature_cols if c in df.columns]]
    proba = churn_model.predict_proba(X)[:, 1]

    # Threshold: explicit card value wins; otherwise resolve the v3 operating point
    # (top budget_K share of the scored population, i.e. quantile(proba, 1 - budget_K)).
    if "threshold" in card:
        threshold = float(card["threshold"])
    elif "operating_point" in card and "budget_K" in card["operating_point"]:
        import numpy as np
        threshold = float(np.quantile(proba, 1 - float(card["operating_point"]["budget_K"])))
    else:
        threshold = 0.3

    segment = seg_model.predict(df[SEG_FEATURES]) if seg_model is not None else None

    scored_at = datetime.now(timezone.utc).isoformat()
    out = pd.DataFrame({
        "customer_id": df["customer_id"],
        "churn_proba": proba.round(4),
        "churn_label": (proba >= threshold).astype(int),
        "segment": segment if segment is not None else -1,
        "model_version": model_version,
        "scored_at": scored_at,
    })

    bucket = default_bucket_uri()
    fs, base = fsspec.core.url_to_fs(bucket)
    fs.makedirs(f"{base}/predictions", exist_ok=True)

    latest_path = f"{base}/predictions/latest.parquet"
    with fs.open(latest_path, "wb") as f:
        out.to_parquet(f, index=False)

    snapshot_name = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ") + ".parquet"
    snapshot_path = f"{base}/predictions/{snapshot_name}"
    with fs.open(snapshot_path, "wb") as f:
        out.to_parquet(f, index=False)

    metadata = {
        "scored_at": scored_at,
        "n_customers": int(len(out)),
        "model_version": model_version,
        "model_source": churn_source,
        "segmentation_source": seg_source,
        "threshold": threshold,
    }
    with fs.open(f"{base}/metadata.json", "w") as f:
        json.dump(metadata, f, indent=2)

    # Prediction-drift history: one quality record per scoring run. Ground truth is available
    # here because the (synthetic) features table carries `churn`; with real data this record
    # is appended later, once labels mature - the schema stays the same.
    record = {
        "scored_at": scored_at,
        "model_version": str(model_version),
        "n_customers": int(len(out)),
        "threshold": round(threshold, 4),
        "mean_proba": round(float(proba.mean()), 4),
        "share_flagged": round(float(out["churn_label"].mean()), 4),
    }
    if "churn" in df.columns:
        from sklearn.metrics import accuracy_score, recall_score, roc_auc_score
        y = df["churn"].astype(int)
        record.update({
            "accuracy": round(float(accuracy_score(y, out["churn_label"])), 4),
            "recall": round(float(recall_score(y, out["churn_label"])), 4),
            "auc_roc": round(float(roc_auc_score(y, proba)), 4),
        })
    append_history(record, bucket)

    print(f"[Batch] scored {len(out)} customers -> {bucket}/predictions/latest.parquet "
          f"(model={model_version}, source={churn_source}, segmentation={seg_source})")
    return out


if __name__ == "__main__":
    run()
