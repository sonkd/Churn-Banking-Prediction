"""P3 — batch prediction pipeline. Runs against whatever model is available in
development/models/ (falls back to the stub model development/api also uses when empty),
and writes to a temp bucket via BUCKET_URI so this test never touches the real ./bucket."""
import sys
from pathlib import Path

import pandas as pd
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

EXPECTED_COLS = {"customer_id", "churn_proba", "churn_label", "segment", "model_version", "scored_at"}


@pytest.fixture
def tmp_bucket(tmp_path, monkeypatch):
    bucket_dir = tmp_path / "bucket"
    monkeypatch.setenv("BUCKET_URI", str(bucket_dir))
    return bucket_dir


def test_batch_predict_writes_predictions_and_metadata(tmp_bucket):
    from batch.predict import run
    out = run()

    assert EXPECTED_COLS <= set(out.columns)
    assert len(out) > 0
    assert out["churn_proba"].between(0, 1).all()
    assert out["churn_label"].isin([0, 1]).all()

    latest = tmp_bucket / "predictions" / "latest.parquet"
    assert latest.exists()
    meta_path = tmp_bucket / "metadata.json"
    assert meta_path.exists()

    df = pd.read_parquet(latest)
    assert len(df) == len(out)

    import json
    meta = json.load(open(meta_path))
    assert meta["n_customers"] == len(out)
    assert "model_source" in meta and "threshold" in meta

    # a timestamped snapshot alongside latest.parquet
    snapshots = list((tmp_bucket / "predictions").glob("*.parquet"))
    assert len(snapshots) >= 2  # latest.parquet + at least one timestamped snapshot
