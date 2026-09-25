"""Promote the v3 notebook artifacts to the canonical contract paths (root README table).
Run from research/:  python promote_v3.py
Then wire development:  bash ../development/scripts/sync_model.sh && (cd .. && make batch-predict)

What it does (content changes only - no contract path renamed):
  churn_model_v3.pkl      -> outputs/models/churn_model.pkl
  model_card_v3.json      -> outputs/models/model_card.json   (+ semver, + resolved threshold)
  features_v3.parquet     -> ../data/processed/features.parquet
  regenerates               ../data/processed/feature_metadata.json (v3 schema)

The v3 card defines the operating point as budget_K=0.10 (label the top 10% risk scores).
development/ needs a concrete `threshold` in the card for the ONLINE /predict path, so we
resolve it here: threshold = quantile(proba over the full scored population, 1 - budget_K).
The batch path recomputes the same quantile per run - the two stay consistent by seed."""
import hashlib
import json
import shutil
from datetime import datetime, timezone
from pathlib import Path

import joblib
import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
MODELS = HERE / "outputs/models"
PROCESSED = HERE.parent / "data/processed"
SEMVER = "3.0.0"


def main():
    card = json.load(open(MODELS / "model_card_v3.json"))
    features = pd.read_parquet(PROCESSED / "features_v3.parquet")
    model = joblib.load(MODELS / "churn_model_v3.pkl")

    # Guardrail: the promoted table must contain every column the model was trained on.
    missing = [c for c in card["features"] if c not in features.columns]
    assert not missing, f"features_v3.parquet is missing model columns: {missing}"

    # Resolve the operating point into a concrete threshold for the online path.
    proba = model.predict_proba(features[card["features"]])[:, 1]
    budget_k = float(card.get("operating_point", {}).get("budget_K", 0.10))
    threshold = float(np.quantile(proba, 1 - budget_k))
    card.update({
        "semver": SEMVER,
        "threshold": round(threshold, 4),
        "promoted_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
    })

    # 1) model + card -> canonical names
    shutil.copy2(MODELS / "churn_model_v3.pkl", MODELS / "churn_model.pkl")
    json.dump(card, open(MODELS / "model_card.json", "w"), indent=2)

    # 2) features table -> canonical name
    shutil.copy2(PROCESSED / "features_v3.parquet", PROCESSED / "features.parquet")

    # 3) feature_metadata.json (consumed by development monitoring/batch)
    row_hash = hashlib.sha1(pd.util.hash_pandas_object(features, index=False).values).hexdigest()[:12]
    metadata = {
        "version": f"{SEMVER}+{row_hash}",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "row_count": int(len(features)),
        "target": "churn",
        "feature_list": card["features"],
        "schema": {c: str(t) for c, t in features.dtypes.items()},
        "row_hash": row_hash,
    }
    json.dump(metadata, open(PROCESSED / "feature_metadata.json", "w"), indent=2)

    print(f"[promote] churn_model.pkl + model_card.json (semver={SEMVER}, threshold={threshold:.4f})")
    print(f"[promote] features.parquet ({len(features)} rows) + feature_metadata.json ({row_hash})")
    print("[promote] next: bash ../development/scripts/sync_model.sh && (cd .. && make batch-predict)")


if __name__ == "__main__":
    main()
