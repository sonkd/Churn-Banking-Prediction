"""P4 — read-only, batch-serving endpoints (GET /predictions*, /segments, /monitoring/metrics).
Covers both the bucket-empty (404) and bucket-populated (200) cases, per the P4 DoD."""
import importlib
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))


@pytest.fixture
def empty_bucket(tmp_path, monkeypatch):
    monkeypatch.setenv("BUCKET_URI", str(tmp_path / "empty_bucket"))
    from fastapi.testclient import TestClient
    import api.main as main
    importlib.reload(main)
    return TestClient(main.app)


@pytest.fixture
def populated_bucket(tmp_path, monkeypatch):
    monkeypatch.setenv("BUCKET_URI", str(tmp_path / "bucket"))
    from batch.predict import run
    run()  # scores data/processed/features.parquet into the temp bucket (stub model is fine)
    from fastapi.testclient import TestClient
    import api.main as main
    importlib.reload(main)
    return TestClient(main.app)


def test_predictions_404_when_bucket_empty(empty_bucket):
    assert empty_bucket.get("/predictions").status_code == 404
    assert empty_bucket.get("/predictions/1").status_code == 404
    assert empty_bucket.get("/segments").status_code == 404
    assert empty_bucket.get("/monitoring/metrics").status_code == 404
    assert empty_bucket.get("/monitoring/history").status_code == 404


def test_ready_reports_bucket_state(empty_bucket):
    r = empty_bucket.get("/ready").json()
    assert r["bucket_state"] == "empty"


def test_predictions_200_when_bucket_populated(populated_bucket):
    r = populated_bucket.get("/predictions?top_k=5")
    assert r.status_code == 200
    rows = r.json()
    assert len(rows) == 5
    assert rows == sorted(rows, key=lambda r: r["churn_proba"], reverse=True)

    cid = rows[0]["customer_id"]
    r2 = populated_bucket.get(f"/predictions/{cid}")
    assert r2.status_code == 200
    assert r2.json()["customer_id"] == cid

    r3 = populated_bucket.get("/predictions/999999999")
    assert r3.status_code == 404

    r4 = populated_bucket.get("/segments")
    assert r4.status_code == 200
    assert isinstance(r4.json(), list)

    r5 = populated_bucket.get("/ready").json()
    assert r5["bucket_state"] == "populated"


def test_monitoring_history_after_batch_run(populated_bucket):
    """batch/predict.py must append one quality record per run (prediction drift)."""
    r = populated_bucket.get("/monitoring/history")
    assert r.status_code == 200
    history = r.json()
    assert len(history) >= 1
    rec = history[-1]
    for key in ("scored_at", "model_version", "mean_proba", "share_flagged", "threshold"):
        assert key in rec
    # features.parquet carries the synthetic ground-truth `churn` -> quality metrics present
    if "accuracy" in rec:
        assert 0.0 <= rec["accuracy"] <= 1.0
        assert 0.0 <= rec["auc_roc"] <= 1.0
