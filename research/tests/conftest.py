"""Session-wide guard: research tests run the REAL pipeline (test_pipeline.py), which writes
to the canonical contract paths. Without this fixture, `make test` silently clobbers whatever
model/features were promoted (e.g. the notebook-v3 artifacts) - development/ then reads a
features.parquet that no longer matches development/models/model_card.json.

Backup before the session, restore after: the pipeline test still exercises the artifact
contract end-to-end, but the repo state is left exactly as it was."""
import shutil
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]          # research/
CANONICAL = [
    ROOT / "outputs/models/churn_model.pkl",
    ROOT / "outputs/models/segmentation_model.pkl",
    ROOT / "outputs/models/model_card.json",
    ROOT / "outputs/metrics/metrics.json",
    ROOT.parent / "data/processed/features.parquet",
    ROOT.parent / "data/processed/feature_metadata.json",
]


@pytest.fixture(scope="session", autouse=True)
def preserve_promoted_artifacts(tmp_path_factory):
    backup_dir = tmp_path_factory.mktemp("canonical_backup")
    saved = {}
    for p in CANONICAL:
        if p.exists():
            dst = backup_dir / p.name
            shutil.copy2(p, dst)
            saved[p] = dst
    yield
    for p, dst in saved.items():
        shutil.copy2(dst, p)
