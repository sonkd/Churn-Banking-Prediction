"""Module 5 Branch B — Behavioral segmentation. K-Means on RFM/behavioral features;
assign interpretable persona names; analyze churn rate by segment (RQ2/RQ3).
Tracks each run with Weights & Biases; WANDB_MODE defaults to "offline" (P2)."""
import os
import pandas as pd
import wandb
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
from sklearn.pipeline import Pipeline
from src.common.io import load_config, rpath, save_model, save_json

os.environ.setdefault("WANDB_MODE", "offline")

PERSONAS = {0: "Loyal High-Value", 1: "Dormant At-Risk", 2: "New Explorer", 3: "Price-Sensitive"}

def train():
    cfg = load_config()
    df = pd.read_parquet(rpath("../data/processed/features.parquet"))
    feats = cfg["segmentation"]["features"]
    X = df[feats].fillna(0)
    k = cfg["segmentation"]["k"]

    run = wandb.init(project="churn-banking-prediction", job_type="train_segments",
                      config={"k": k, "seed": cfg["seed"], "features": feats})

    model = Pipeline([("scale", StandardScaler()),
                      ("km", KMeans(n_clusters=k, n_init=10, random_state=cfg["seed"]))])
    labels = model.fit_predict(X)
    sil = float(silhouette_score(model.named_steps["scale"].transform(X), labels))
    df["segment"] = labels
    by_seg = df.groupby("segment")[cfg["target"]].mean().round(3).to_dict()

    wandb.log({"silhouette": sil})
    seg_table = wandb.Table(data=[[seg, rate] for seg, rate in by_seg.items()],
                             columns=["segment", "churn_rate"])
    wandb.log({"churn_rate_by_segment": wandb.plot.bar(
        seg_table, "segment", "churn_rate", title="Churn rate by segment")})

    save_model(model, cfg["paths"]["models"] + "/segmentation_model.pkl")
    save_json({"k": k, "silhouette": sil, "personas": PERSONAS,
               "churn_rate_by_segment": by_seg, "features": feats,
               "wandb_run_id": run.id},
              cfg["paths"]["metrics"] + "/segments.json")
    run.finish()
    print(f"[M5-B] k={k} silhouette={sil:.3f} churn_by_segment={by_seg}")
    return sil, by_seg

if __name__ == "__main__":
    train()
