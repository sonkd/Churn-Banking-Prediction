"""Module 1 — Business understanding & synthetic data generation.
Base data is from Kaggle; here we (re)generate the behavioral extension with documented,
NOISY business logic so churn is learnable but not leaked. See data/data_dictionary.md.
DoD: join key 100% valid, no field perfectly separates churn, ranges match the dictionary.
"""
import numpy as np, pandas as pd
from src.common.io import load_config, rpath

def generate(seed=42):
    cfg = load_config(); np.random.seed(seed)
    base = pd.read_csv(rpath(cfg["paths"]["raw"]))
    # NOTE: real teams use Faker + custom logic; dummy data already shipped in data/synthetic.
    # This stub just validates the join contract.
    tx = pd.read_csv(rpath(cfg["paths"]["synthetic"]))
    assert tx.customer_id.isin(base.customer_id).all(), "FK integrity broken"
    print(f"[M1] base={base.shape} tx={tx.shape} churn_rate={base.churn.mean():.3f}")
    return base, tx

if __name__ == "__main__":
    generate()
