"""Shared bucket read helpers (BUCKET_URI via fsspec). Lives outside api/ and batch/ so both
can depend on it without a circular import (batch/predict.py already imports from api/)."""
import json
import os
from typing import Optional

import fsspec
import pandas as pd


def default_bucket_uri() -> str:
    return os.getenv("BUCKET_URI", "./bucket")


def _fs(uri: Optional[str]):
    return fsspec.core.url_to_fs(uri or default_bucket_uri())


def read_latest_predictions(uri: Optional[str] = None) -> Optional[pd.DataFrame]:
    fs, base = _fs(uri)
    path = f"{base}/predictions/latest.parquet"
    if not fs.exists(path):
        return None
    with fs.open(path, "rb") as f:
        return pd.read_parquet(f)


def read_json(rel_path: str, uri: Optional[str] = None) -> Optional[dict]:
    fs, base = _fs(uri)
    path = f"{base}/{rel_path}"
    if not fs.exists(path):
        return None
    with fs.open(path, "r") as f:
        return json.load(f)


HISTORY_PATH = "monitoring/history.json"


def read_history(uri: Optional[str] = None) -> list[dict]:
    """Per-run scoring history (prediction drift / accuracy over time). [] when absent."""
    fs, base = _fs(uri)
    path = f"{base}/{HISTORY_PATH}"
    if not fs.exists(path):
        return []
    with fs.open(path, "r") as f:
        return json.load(f)


def append_history(record: dict, uri: Optional[str] = None, keep_last: int = 200) -> None:
    """Read-append-rewrite (not append mode) so it works on object stores (GCS/S3) too."""
    fs, base = _fs(uri)
    history = read_history(uri)
    history.append(record)
    fs.makedirs(f"{base}/monitoring", exist_ok=True)
    with fs.open(f"{base}/{HISTORY_PATH}", "w") as f:
        json.dump(history[-keep_last:], f, indent=2)
