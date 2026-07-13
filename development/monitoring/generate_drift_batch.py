"""Module 7 helper — synthesize a 'next quarter' batch WITH intentional drift, so drift
detection has something to detect. Writes to BUCKET_URI/incoming/latest.parquet - the bucket
is the shared hand-off point for the whole Bucket -> Monitoring feedback loop (P6), same as
the predictions batch/predict.py writes to BUCKET_URI/predictions/."""
import sys
from pathlib import Path

import fsspec
import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))  # make `common` importable when run as a plain script
from common.bucket import default_bucket_uri

REF = Path(__file__).resolve().parents[2] / "data/processed/features.parquet"


def make(drift=True, seed=7):
    rng = np.random.default_rng(seed)
    df = pd.read_parquet(REF).sample(frac=1.0, replace=True, random_state=seed).reset_index(drop=True)
    if drift:
        # Guarded per column: the v3 features table keeps the behavioral block but drops raw
        # `age` (replaced by age_band one-hots) - only drift the columns that exist.
        if "frequency" in df.columns:
            df["frequency"] = (df["frequency"] * rng.uniform(0.6, 0.8)).round()      # engagement drop
        if "complaints_sum" in df.columns:
            df["complaints_sum"] = df["complaints_sum"] + rng.poisson(1.0, len(df))  # more complaints
        if "age" in df.columns:
            df["age"] = df["age"] + 3                                                # cohort shift
        elif "age_band_60+" in df.columns:
            bump = rng.random(len(df)) < 0.15                                        # cohort shift, encoded
            df.loc[bump, "age_band_60+"] = 1

    bucket = default_bucket_uri()
    fs, base = fsspec.core.url_to_fs(bucket)
    fs.makedirs(f"{base}/incoming", exist_ok=True)
    out_path = f"{base}/incoming/latest.parquet"
    with fs.open(out_path, "wb") as f:
        df.to_parquet(f, index=False)

    print(f"[M7] incoming batch (drift={drift}) -> {bucket}/incoming/latest.parquet")
    return df

if __name__ == "__main__":
    make()
