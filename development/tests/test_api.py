"""Offline smoke test — boots the API with the stub model, checks the contract."""
import sys; from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from fastapi.testclient import TestClient
from api.main import app
client = TestClient(app)

def test_health():
    assert client.get("/health").json()["status"] == "ok"

def test_ready():
    assert client.get("/ready").json()["ready"] is True

def test_predict_contract():
    r = client.post("/predict", json={"age": 55, "complaints_sum": 4, "frequency": 5}).json()
    assert 0.0 <= r["churn_probability"] <= 1.0
    assert r["churn_label"] in (0, 1)
