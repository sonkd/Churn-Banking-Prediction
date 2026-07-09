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
