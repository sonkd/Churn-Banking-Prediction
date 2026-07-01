"""Shared paths + load/save helpers. The ONLY module imported across M1-M5."""
from pathlib import Path
import json, yaml, joblib, pandas as pd

RESEARCH = Path(__file__).resolve().parents[2]      # research/
ROOT = RESEARCH.parent                              # repo root

def load_config(p="config/config.yaml"):
    with open(RESEARCH / p) as f:
        return yaml.safe_load(f)

def rpath(rel: str) -> Path:
    """Resolve a path relative to research/ and ensure parent exists for outputs."""
    p = (RESEARCH / rel).resolve()
    if "outputs" in rel or "processed" in rel:
        p.parent.mkdir(parents=True, exist_ok=True)
    return p

def save_json(obj, rel):
    with open(rpath(rel), "w") as f:
        json.dump(obj, f, indent=2, default=str)

def save_model(model, rel):
    joblib.dump(model, rpath(rel))

def read_csv(rel): return pd.read_csv(rpath(rel))
