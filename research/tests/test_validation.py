"""P1 — pandera validation gate + feature_metadata.json contract.
Assumes run_pipeline.py (or `make features`) has already produced data/processed/base_clean.parquet
and data/processed/feature_metadata.json at least once (test_pipeline.py does this)."""
import json
import sys
from pathlib import Path

import pandas as pd
import pandera
import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.m3_cleaning.validate import validate_base  # noqa: E402


@pytest.fixture
def clean_base():
    return pd.read_parquet(ROOT / "../data/processed/base_clean.parquet")


def test_valid_base_passes(clean_base):
    validate_base(clean_base)  # must not raise


def test_injected_schema_violation_fails_closed(clean_base):
    corrupted = clean_base.copy()
    corrupted.loc[corrupted.index[0], "age"] = 999  # out of documented range 18-92
    with pytest.raises(pandera.errors.SchemaErrors):
        validate_base(corrupted)


def test_injected_null_fails_closed(clean_base):
    corrupted = clean_base.copy()
    corrupted.loc[corrupted.index[0], "balance"] = None  # null-rate > 0 on a required column
    with pytest.raises(pandera.errors.SchemaErrors):
        validate_base(corrupted)


def test_feature_metadata_written_and_readable():
    meta_path = ROOT / "../data/processed/feature_metadata.json"
    assert meta_path.exists(), "feature_metadata.json missing - run `make features` first"
    meta = json.load(open(meta_path))
    for key in ("version", "created_at", "row_count", "target", "feature_list", "schema", "row_hash"):
        assert key in meta, f"feature_metadata.json missing key: {key}"

    feats = pd.read_parquet(ROOT / "../data/processed/features.parquet")
    assert meta["row_count"] == len(feats)
    assert set(meta["feature_list"]) == set(feats.columns) - {"customer_id", meta["target"]}
    assert meta["version"].endswith(meta["row_hash"])
