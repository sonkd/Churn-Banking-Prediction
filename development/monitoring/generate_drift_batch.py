"""Module 7 helper — synthesize a 'next quarter' batch WITH intentional drift,
so drift detection has something to detect. Saves to monitoring/incoming_batch.parquet."""
from pathlib import Path
import numpy as np, pandas as pd
REF = Path(__file__).resolve().parents[2] / "data/processed/features.parquet"
OUT = Path(__file__).resolve().parent / "incoming_batch.parquet"

def make(drift=True, seed=7):
    rng = np.random.default_rng(seed)
    df = pd.read_parquet(REF).sample(frac=1.0, replace=True, random_state=seed).reset_index(drop=True)
    if drift:
        df["frequency"] = (df["frequency"] * rng.uniform(0.6, 0.8)).round()   # engagement drop
        df["complaints_sum"] = df["complaints_sum"] + rng.poisson(1.0, len(df)) # more complaints
        df["age"] = df["age"] + 3                                              # cohort shift
    df.to_parquet(OUT, index=False)
    print(f"[M7] incoming batch (drift={drift}) -> {OUT}")
    return df

if __name__ == "__main__":
    make()
